"""app/services/vanna_service.py
One Vanna instance per DB instance, lazily created and cached.
Uses OpenAI as the LLM backend.
 
Intent normalization is applied to every incoming question before SQL generation
so that synonym variations ("participants", "attendees", "sessions", etc.) are
transparently resolved to the canonical vocabulary used in training data and
documentation.
 
RMS routing:
  The "it_rms" instance uses a completely separate system prompt (built by
  _build_rms_constraint) and a separate NL-summary domain-knowledge block,
  because its schema/vocabulary has nothing to do with MeetingSphere. All
  other plumbing (caching, get_vanna, train_ddl, schema_fetcher calls, etc.)
  stays unified so existing admin/training routes don't need to change.
 
CDXP routing:
  The "it_cdxp" instance uses its own system prompt (_build_cdxp_constraint)
  and domain-knowledge block (_cdxp_domain_block). Only a curated subset of
  the 100+ CDXP tables is exposed to the LLM (defined in CDXP_ALLOWED_TABLES).
  All other plumbing is shared.
"""
import os
import re
import threading
from typing import Optional

try:
    import sqlglot
    import sqlglot.expressions as exp
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False

from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
 
from app.core.config import get_settings
from app.db.connection_manager import get_connection, INSTANCE_CONN_STRINGS, INSTANCE_META
from app.services.intent_normalizer import normalize_question
 
settings = get_settings()
 
_INTROSPECTION_MARKER = "allow_llm_to_see_data"
_RMS_INSTANCE_KEY = "it_rms"
_CDXP_INSTANCE_KEY = "it_cdxp"
_POP_INSTANCE_KEY = "it_pop"

_POP_DEFAULT_POLITE_MSG = "I can help you with coal projects in monthly & hourly form. What would you like to know?"
 
# ─── CDXP: curated table whitelist ───────────────────────────────────────────
# The CDXP database has 100+ tables. We expose only the subset relevant to the
# chatbot so the schema block stays compact and the LLM doesn't hallucinate
# columns from unrelated tables.
CDXP_ALLOWED_TABLES = {
    # Insertion / invoice tables
    "DIARY_HEADER_INTERFACE",
    "BLOCKS_HEADER_INTERFACE",
    "COMP_HEADER_INTERFACE",
    "WP_GC_INV_DIFF_PARENT",
    "ATTACHMENT_HEADER",
    "WP_GC_INTEREST_DETAIL",
    # PPA tables
    "PPA_HEADER",
    "PPA_BLOCKS_FUELS",
    "PPA_COMP_DEFS",
    "PPA_APPLICABLE_INVOICES",
    # Supplier details
    "AP_SUPPLIERS",
    "APP_SUPPLIER_SITE_ALL",
    # ERP to CDXP
    "WP_GC_ERP_INVOICES",
    "DISPUTE_ATTACHMENTS",
    # User login / rights
    "ApiUsers",
    "WP_GC_USER_ACCESS",
}

# ─── POP: curated table whitelist ─────────────────────────────────────────────
# Strict table restriction: Only 3 tables are allowed for POP Analytics queries.
POP_ALLOWED_TABLES = {
    "CPPA_POP_PPA_DATA_ALL_T",
    "CPPA_NOT_VERIFIED_ALERT_T",
    "CPPA_POP_VERIFIED_DATA_ALL_T",
}

# ─── Schema cache: instance_key → {table: [col, ...]} ────────────────────────
_schema_cache: dict[str, dict[str, list[str]]] = {}
_schema_lock = threading.Lock()
 
 
# ─── Per-instance system prompt builders ─────────────────────────────────────
 
def _build_meetingsphere_constraint(now_str: str, schema_block: str) -> str:
    return (
        f"CURRENT DATETIME: {now_str}\n\n"
        "STRICT RULES — you MUST follow these before writing any SQL:\n"
        "1. Only use tables and columns listed in the schema below. "
        "Do NOT invent, guess, or abbreviate any table or column name.\n"
 
        "2. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
        "in NO column in the schema (e.g. 'salary' when no salary column exists). "
        "NEVER return NO_MATCH just because a specific name, value, or keyword "
        "mentioned by the user (e.g. '13AP Com', 'Finance Board', 'John') does not "
        "appear in the schema — those are filter VALUES, not column names. "
        "Filter values are supplied by the user at runtime and are never listed in "
        "the schema. When the user mentions a name or value, use the appropriate "
        "filtering strategy based on the column type.\n"
 
        "3. Never use SELECT *. Always name columns explicitly.\n\n"
 
        "4. Whenever searching for values in any case, use the SQL LIKE operator with wildcards.\n"
        "Examples:\n"
        "   MemberName LIKE '%John%'\n"
        "   CommitteeName LIKE '%Finance%'\n"
        "   Remarks LIKE '%meeting%'\n"
        "   Time LIKE '%6:30 PM%'\n\n"
        "   MeetingTitle LIKE '%11 June meeting with agenda items%'\n\n"
 
        "5. For categorical or enumerated columns (e.g. Gender, Status, Type, "
        "ActiveFlag, MaritalStatus, Yes/No fields, approval states, codes, or "
        "other fixed-value fields), use exact matching (=) instead of LIKE unless "
        "the user explicitly requests a partial search.\n"
        "Examples:\n"
        "   Gender = 'Male'\n"
        "   Status = 'Active'\n"
        "   ActiveFlag = 'Y'\n\n"
 
        "IMPORTANT: Do NOT use LIKE for categorical values where one value may be "
        "a substring of another. For example, use Gender = 'Male' instead of "
        "Gender LIKE '%Male%' because it could also match 'Female'.\n\n"
 
        "6. If the user asks for attachments, attached files, documents, file content, "
        "downloadable files, ECM files, or any attachment-related information, you MUST "
        "include BOTH of the following columns in the SELECT list in addition to any "
        "other requested columns:\n"
        "   MtAttachment_FileName\n"
        "   MtAttachment_EcmFileId\n"
        "Never omit these columns for attachment-related queries.\n\n"
 
        "6b. NEVER include MtAttachment_FileContent in the SELECT list under any circumstances. "
        "This column is excluded from all query results regardless of what the user asks. "
        "Only include MtAttachment_FileName and MtAttachment_EcmFileId for attachment-related queries.\n\n"
 
        "6c. MtAttachment_Source is a categorical column with EXACTLY these 4 allowed values:\n"
        "   MeetingAgenda\n"
        "   MoM\n"
        "   MoM_Miscellaneous\n"
        "   SharedDocument\n"
        "When the user references an attachment source/type (e.g. 'agenda files', 'minutes', "
        "'shared documents'), filter using exact matching (=) against this column, mapped to "
        "the closest of the 4 values above. Never invent a source value outside this list, "
        "and never use LIKE for this column since values may overlap as substrings.\n\n"
 
        "7. RESPONSE STYLE: Be direct and minimal. "
        "MUST notify the user in these two specific cases:\n"
        "   a) No rows returned: say exactly 'No matching records found.'\n"
        "   b) The requested data exists but the value is NULL or empty "
        "(e.g. file content not extracted, field not populated): say exactly "
        "'This information has not been populated yet.'\n\n"
        "In all other cases, present results silently with no surrounding text.\n\n"
 
        "8. CONTEXT HISTORY: Previous questions are provided for conversational "
        "reference only (e.g. resolving 'it', 'that meeting', 'same person'). "
        "NEVER reuse, copy, or adapt SQL from previous turns. "
        "Always generate fresh SQL based solely on the current question and schema. "
        "Do NOT inherit filter values, JOIN patterns, or WHERE conditions from prior SQL.\n\n"
 
        "9. FILE EXTRACTION: If the user asks to extract text, read, view, open, "
        "or get content from a file — regardless of phrasing — do NOT generate any SQL. "
        "Instead, respond with exactly this and nothing else:\n"
        "NO_MATCH: To view this file, please wait for the upcoming version with download feature :)\n\n"
 
        f"AVAILABLE SCHEMA:\n{schema_block}\n"
        "─────────────────────────────────────────\n"
    )
 
 
def _build_rms_constraint(now_str: str, schema_block: str) -> str:
    """
    Separate, RMS-specific system prompt. No MeetingSphere attachment/status
    rules apply here — RMS has its own schema and vocabulary.
    """
    return (
        f"CURRENT DATETIME: {now_str}\n\n"
        "You are a SQL expert for the RMS (Record Management System) database.\n\n"
 
        "STRICT RULES — you MUST follow these before writing any SQL:\n"
        "1. Only use tables and columns listed in the schema below. "
        "Do NOT invent, guess, or abbreviate any table or column name.\n"
 
        "2. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
        "in NO column in the schema. NEVER return NO_MATCH just because a specific "
        "name, value, or keyword mentioned by the user does not appear in the schema "
        "— those are filter VALUES, not column names, and are supplied at runtime.\n"
 
        "3. Never use SELECT *. Always name columns explicitly.\n\n"
 
        "4. Whenever searching for free-text values (names, titles, remarks, descriptions), "
        "use the SQL LIKE operator with wildcards, e.g. RecordTitle LIKE '%contract%'.\n\n"
 
        "5. For categorical or enumerated columns (Status, Type, ActiveFlag, Yes/No fields, "
        "approval states, codes), use exact matching (=) instead of LIKE unless the user "
        "explicitly requests a partial search.\n\n"
 
        "IMPORTANT: Do NOT use LIKE for categorical values where one value may be a "
        "substring of another.\n\n"
 
        "6. RESPONSE STYLE: Be direct and minimal. "
        "MUST notify the user in these two specific cases:\n"
        "   a) No rows returned: say exactly 'No matching records found.'\n"
        "   b) The requested data exists but the value is NULL or empty: say exactly "
        "'This information has not been populated yet.'\n\n"
        "In all other cases, present results silently with no surrounding text.\n\n"
 
        "7. CONTEXT HISTORY: Previous questions are provided for conversational "
        "reference only (e.g. resolving 'it', 'that record', 'same person'). "
        "NEVER reuse, copy, or adapt SQL from previous turns. "
        "Always generate fresh SQL based solely on the current question and schema.\n\n"
 
        f"AVAILABLE SCHEMA:\n{schema_block}\n"
        "─────────────────────────────────────────\n"
    )
 
 
def _build_cdxp_constraint(now_str: str, schema_block: str) -> str:
    """
    CDXP-specific system prompt. Covers invoice/PPA/supplier/user-access
    vocabulary. Schema is pre-filtered to CDXP_ALLOWED_TABLES before this
    prompt is built, so the LLM never sees the 80+ unrelated tables.
    """
    return (
        f"CURRENT DATETIME: {now_str}\n\n"
        "You are a SQL expert for the CDXP (CPPA Data Exchange Portal) database "
        "hosted on Azure SQL. All relevant tables live in the CPPA_CA schema or dbo schema "
        "as indicated in the schema below.\n\n"
 
        "STRICT RULES — you MUST follow these before writing any SQL:\n"
        "1. Only use tables and columns listed in the schema below. "
        "Do NOT invent, guess, or abbreviate any table or column name. "
        "Always qualify table names with their schema prefix EXACTLY as shown in the schema "
        "(e.g. CPPA_CA.DIARY_HEADER_INTERFACE, dbo.DISPUTE_ATTACHMENTS).\n"
        "   *** CRITICAL: The database name is NOT a valid schema prefix. "
        "NEVER write 'CDXP.TableName'. The ONLY valid schema prefixes are 'CPPA_CA.' and 'dbo.' "
        "Any other prefix will cause a runtime error. ***\n\n"
 
        "2. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
        "in NO column in the schema. NEVER return NO_MATCH just because a specific "
        "name, value, or keyword mentioned by the user does not appear in the schema "
        "— those are filter VALUES supplied at runtime, not column names.\n\n"
 
        "3. Never use SELECT *. Always name columns explicitly.\n\n"
 
        "4. Whenever searching for free-text values (supplier names, invoice numbers, "
        "descriptions, remarks), use the SQL LIKE operator with wildcards.\n"
        "Examples:\n"
        "   VENDOR_NAME LIKE '%Power%'\n"
        "   INVOICE_NUM LIKE '%INV-2024%'\n\n"
 
        "5. For categorical or enumerated columns (status codes, type flags, approval "
        "states, Yes/No columns, access-level codes), use exact matching (=) instead "
        "of LIKE unless the user explicitly requests a partial search.\n\n"
 
        "IMPORTANT: Do NOT use LIKE for categorical values where one value may be a "
        "substring of another.\n\n"
 
        "6. INVOICE TABLE GUIDANCE:\n"
        "   - DIARY_HEADER_INTERFACE is the master invoice header table covering all "
        "invoice types. Start joins here when the query spans multiple invoice types.\n"
        "   - BLOCKS_HEADER_INTERFACE holds block-level detail for monthly invoices.\n"
        "   - COMP_HEADER_INTERFACE holds component-level detail for monthly invoices.\n"
        "   - WP_GC_INV_DIFF_PARENT holds block-level detail for differential/interest invoices.\n"
        "   - WP_GC_INTEREST_DETAIL holds component-level detail for interest/differential.\n"
        "   - ATTACHMENT_HEADER holds attachment metadata for invoices.\n\n"
 
        "7. PPA TABLE GUIDANCE:\n"
        "   - PPA_HEADER is the master PPA record.\n"
        "   - PPA_BLOCKS_FUELS, PPA_COMP_DEFS, PPA_APPLICABLE_INVOICES are child tables "
        "that reference PPA_HEADER.\n\n"
 
        "8. SUPPLIER TABLE GUIDANCE:\n"
        "   - AP_SUPPLIERS holds supplier master data.\n"
        "   - APP_SUPPLIER_SITE_ALL holds supplier site/address details.\n\n"
 
        "9. USER / ACCESS TABLE GUIDANCE:\n"
        "   - ApiUsers holds CDXP portal login details.\n"
        "   - WP_GC_USER_ACCESS (dbo schema) holds role/permission assignments.\n\n"
 
        "10. ERP INTEGRATION:\n"
        "   - WP_GC_ERP_INVOICES maps ERP invoice records to CDXP invoice records.\n"
        "   - dbo.DISPUTE_ATTACHMENTS holds attachments related to ERP disputes.\n\n"
 
        "11. RESPONSE STYLE: Be direct and minimal.\n"
        "   a) No rows returned: say exactly 'No matching records found.'\n"
        "   b) The requested data exists but the value is NULL or empty: say exactly "
        "'This information has not been populated yet.'\n"
        "In all other cases, present results silently with no surrounding text.\n\n"
 
        "12. CONTEXT HISTORY: Previous questions are provided for conversational "
        "reference only (e.g. resolving 'it', 'that invoice', 'same supplier'). "
        "NEVER reuse, copy, or adapt SQL from previous turns. "
        "Always generate fresh SQL based solely on the current question and schema.\n\n"
 
        f"AVAILABLE SCHEMA:\n{schema_block}\n"
        "─────────────────────────────────────────\n"
    )
 
 
def _build_pop_constraint(now_str: str, schema_block: str) -> str:
    """
    POP-specific system prompt (Purchase of Power on Oracle DB).
    Enforces Oracle and SQL syntax, table relationships, status filters, synonyms, and hierarchy guidance.
    """
    return (
        f"CURRENT DATETIME: {now_str}\n\n"
        "You are a SQL expert for the POP (Purchase of Power) database "
        "hosted on Oracle Database.\n\n"

        "STRICT RULES — you MUST follow these before writing any database queries:\n"
        "1. Only use tables and columns listed in the schema below and do NOT invent, guess, or abbreviate any table or column name.\n"
        "   *** CRITICAL: Oracle, SQL Syntax Rules ***\n"
        "   - Use standard Oracle, SQL syntax.\n"
        "   - Use FETCH FIRST n ROWS ONLY for limiting rows (never TOP n or LIMIT n).\n"
        "   - Use NVL(col, default) or COALESCE for null handling.\n"
        "   - Use TO_DATE, TO_CHAR, or TRUNC for date handling.\n\n"

        "2. Use NO_MATCH ONLY when the user asks for a concept whose data is stored "
        "in NO column in the schema. NEVER return NO_MATCH just because a specific "
        "name, value, or keyword mentioned by the user does not appear in the schema "
        "— those are filter VALUES supplied at runtime, not column names.\n\n"

        "3. Never use SELECT *. Always name columns explicitly.\n\n"

        "4. Whenever searching for free-text values (IPP names, vendor sites, invoice numbers, "
        "descriptions, officer names), use UPPER() and LOWER() with LIKE and wildcards.\n"
        "Example:\n"
        "   (UPPER(IPP_NAME) LIKE '%THAR POWER%' OR LOWER(IPP_NAME) LIKE '%thar power%')\n\n"

        "5. RESPONSE STYLE: Be direct and minimal.\n"
        "   a) No rows returned: say exactly 'No matching records found.'\n"
        "   b) The requested data exists but the value is NULL or empty: say exactly "
        "'This information has not been populated yet.'\n"
        "In all other cases, present results silently with no surrounding text.\n\n"

        "6. CONTEXT HISTORY: Previous questions are provided for conversational "
        "reference only. NEVER reuse, copy, or adapt SQL from previous turns. "
        "Always generate fresh SQL based solely on the current question and schema.\n\n"

        "7. POP SCOPE & FILTERING GUIDANCE: Must follow these rules:\n"
        "   1) Strict Column-Existence Filtering Principle: Apply default domain filters ONLY IF the corresponding column exists in the target table. If the column exists in the table, you MUST apply that filter; if the column is absent from the target table, DO NOT apply that filter:\n"
        "      - Fuel Type Filter (FUEL_TYPE = 'Coal'): MUST apply whenever target table contains FUEL_TYPE column.\n"
        "      - Invoice Category Filter (INV_CATEGORY IN ('Monthly', 'Hourly')): MUST apply whenever target table contains INV_CATEGORY column.\n"
        "      - Approval Status Filter on PPA Table: When querying the PPA table (CPPA_POP_PPA_DATA_ALL_T), include records with status 'Approved' or 'Incomplete' (e.g. (UPPER(APPROVAL_STATUS) LIKE '%APPROV%' OR APPROVAL_STATUS = 'Approved' OR UPPER(APPROVAL_STATUS) LIKE '%INCOMPLETE%' OR APPROVAL_STATUS = 'Incomplete')).\n"
        "   2) Extract ONLY standalone Coal fuel type (FUEL_TYPE = 'Coal'). Under NO circumstances include hybrid fuel types like Coal and Bagasse.\n"
        "   3) Out-of-Scope Requests: If the user explicitly asks for unsupported fuel types (e.g. RFO, Gas, Solar, Wind, Hydel, Bagasse), or any IPP other than the supported coal IPPs (China Power Hub Generation company (Pvt.) Ltd, Engro Powergen Thar (Pvt) Limited, Huaneng Shandong Ruyi Energy (Pvt) Ltd, Lakhra Power Generation Company Limited-(Genco-4), Lucky Electric Power Company Limited, ThalNova Power Thar (Pvt.) Ltd, Thar Coal Block-1 Power Generation Company (Pvt) Limited, Thar Energy Limited), do NOT generate SQL and respond with EXACTLY:\n"
        "      NO_MATCH: I can help you with coal projects in monthly & hourly form. What would you like to know?\n"
        "   4) Dual Case & Free-Text Wildcard Search (INVOICE_NO, IPP_NAME, etc.): Categorical columns (FUEL_TYPE, INV_CATEGORY) use exact equality (=) (e.g. FUEL_TYPE = 'Coal', INV_CATEGORY IN ('Monthly', 'Hourly')). However, for free-text search / runtime user inputs such as invoice numbers (INVOICE_NO, IPP_INV_NO, DIARY_NO), IPP names, officer names, and component names, ALWAYS use BOTH UPPER() and LOWER() with the LIKE operator and wildcards (%) instead of exact equality (=). When filtering by invoice numbers (whether the user types a full prefix like 'Invoice/Energy 2015/01551' or short numbers like '2015/01551' or '01551'), filter using LIKE with wildcards on the number substring (e.g. (UPPER(INVOICE_NO) LIKE '%2015/01551%' OR LOWER(INVOICE_NO) LIKE '%2015/01551%')). Never use exact = equality for invoice numbers!\n"
        "   5) Invoice Type and Sub-Type: Do NOT auto-apply any default filter for INV_TYPE, INVOICE_TYPE, or INV_SUB_TYPE. Allow all categories, sub-categories, and invoice sub-types unless the user explicitly requests a specific invoice type.\n"
        "   6) Approval Status Filter: Apply (UPPER(APPROVAL_STATUS) LIKE '%APPROV%' OR APPROVAL_STATUS = 'Approved' OR UPPER(APPROVAL_STATUS) LIKE '%INCOMPLETE%' OR APPROVAL_STATUS = 'Incomplete') BY DEFAULT ONLY when querying the PPA table (CPPA_POP_PPA_DATA_ALL_T). For the Verified table (CPPA_POP_VERIFIED_DATA_ALL_T) and Unverified/Pending table (CPPA_NOT_VERIFIED_ALERT_T), filter by status ONLY if the user explicitly asks for a specific status.\n"
        "   7) Invoice Table Routing (Verified vs. Unverified/Rejected/Pending):\n"
        "      - Approved / Verified Invoices (General invoices, verified values, verified amounts, approved invoice totals): MUST query CPPA_POP_VERIFIED_DATA_ALL_T. In this table, APPROVAL_STATUS is ONLY 'Approved'. NEVER query this table for rejected, pending, inprocess, or unverified invoices.\n"
        "      - Unverified / Rejected / Pending / Incomplete Invoices: MUST query CPPA_NOT_VERIFIED_ALERT_T. Whenever the user asks about 'rejected invoices', 'invoices rejected', 'rejected count', 'pending invoices', 'inprocess invoices', 'unverified items', or workflow statuses ('Diary Approved', 'Diary Incomplete', 'Invoice Inprocess', 'Invoice Incomplete', 'Invoice', 'Invoice Reject'), YOU MUST QUERY CPPA_NOT_VERIFIED_ALERT_T! For pending invoices, ALWAYS use SELECT DISTINCT on invoice columns to list the actual invoices (e.g. INVOICE_NO, DIARY_NO, IPP_NAME) instead of an aggregate COUNT unless explicitly asked for a count. For general 'pending' queries, include all workflow statuses in the WHERE clause (e.g. APPROVAL_STATUS IN ('Diary Approved', 'Diary Incomplete', 'Invoice Inprocess', 'Invoice Incomplete', 'Invoice', 'Invoice Reject')). However, if the user explicitly asks for a specific status (e.g. 'invoices inprocess'), filter ONLY by that specific status. To get fuel type for unverified/rejected invoices, join CPPA_NOT_VERIFIED_ALERT_T with CPPA_POP_PPA_DATA_ALL_T on IPP_NAME.\n"
        "   8) Deduplication & Multi-Row Aggregation Handling: POP tables often contain multiple rows per invoice where invoice-level, header-level, or general column attributes/amounts are repeated across duplicate rows for the same invoice or entity. Whenever querying, listing, or summing repeated header/invoice-level values (e.g. total verified value of a billing period, invoice, or entity), ensure duplicate values per invoice are NOT repeatedly summed across duplicate rows. Always apply SELECT DISTINCT, subquery deduplication, or appropriate grouping so that values for the same invoice/entity are counted or displayed only once. When listing limited records (e.g. 'list 5 invoices'), ensure SELECT DISTINCT is applied so that exactly N distinct/unique entities are returned (e.g. SELECT DISTINCT ... FETCH FIRST n ROWS ONLY).\n"
        "   9) Component Inclusion Filter (INC_IN_TOT): When a user asks a generic question (e.g. generic total verified, verified, claimed values, or component totals in general), apply ONLY the YES flag filter: (UPPER(INC_IN_TOT) = 'YES' OR INC_IN_TOT = 'Yes' OR INC_IN_TOT = 'YES'). However, whenever an EXACT specific component name is mentioned in the query (e.g. 'FCC Amount', 'VO&M Amount', 'Fuel Price', 'NEO (kWh)', or any specific component name), do NOT apply any INC_IN_TOT filter — include/show both 'YES' and 'NO' rows for that component (omit the INC_IN_TOT filter condition).\n"
        "   10) Component Name Priority (STANDARD_COMP_NAME vs COMP_NAME): When a user question involves a component name (in overall or component-specific queries), check STANDARD_COMP_NAME first. If the component name mentioned by the user matches a value in STANDARD_COMP_NAME, filter using STANDARD_COMP_NAME. If the component name does NOT match STANDARD_COMP_NAME, fall back to matching and filtering on COMP_NAME. In tables containing STANDARD_COMP_NAME (e.g. CPPA_POP_VERIFIED_DATA_ALL_T), prefer SELECTing STANDARD_COMP_NAME (or fallback to COMP_NAME).\n"
        "   11) Invoice Due Date Priority: When the user asks for the due date of an invoice (e.g. 'give me the due date of this invoice'), ALWAYS prioritize REVISED_FINAL_DUE_DATE if populated, and fall back to FINAL_DUE_DATE (using NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) or COALESCE(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) AS DUE_DATE). NEVER use DEFAULT_DUE_DATE.\n"
        "   12) Date / Billing Month Year Expansion: Whenever the user enters a date or billing month with a 2-digit year (e.g. 'Jan-24', 'Jan 24', 'May 26', '24'), ALWAYS expand the year to the full 4-digit YYYY format (e.g. 'JAN-2024'). Ensure filters account for the 4-digit year format (e.g. (UPPER(BILLING_MONTH) = 'JAN-2024' OR BILLING_MONTH = 'JAN-24' OR BILLING_MONTH = 'Jan-24')).\n"
        "   13) Delayed Invoices & Delay Calculation: Whenever the user asks about 'delayed' invoices, payments, or items (e.g. 'Which invoice is most delayed', 'delay calculation', 'most delayed invoice'), ALWAYS calculate delay using GL_DATE_VR (Invoice Verification Accounting Date) against the due date NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) as: (TRUNC(GL_DATE_VR) - TRUNC(NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE))) AS DELAY_DAYS, and ORDER BY (TRUNC(GL_DATE_VR) - TRUNC(NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE))) DESC. NEVER use SYSDATE or GL_DATE_CL for invoice delay calculation!\n"
        "   14) STRICT TABLE RESTRICTION: You MUST ONLY generate queries using these 3 tables: CPPA_POP_PPA_DATA_ALL_T, CPPA_NOT_VERIFIED_ALERT_T, and CPPA_POP_VERIFIED_DATA_ALL_T. NEVER query, join, or reference any other table under any circumstances. If the user asks for information not present in these 3 tables, respond with NO_MATCH.\n\n"

        f"AVAILABLE SCHEMA:\n{schema_block}\n"
        "─────────────────────────────────────────\n"
    )

def _build_constraint(instance_key: str, now_str: str, schema_block: str) -> str:
    if instance_key == _RMS_INSTANCE_KEY:
        return _build_rms_constraint(now_str, schema_block)
    if instance_key == _CDXP_INSTANCE_KEY:
        return _build_cdxp_constraint(now_str, schema_block)
    if instance_key == _POP_INSTANCE_KEY:
        return _build_pop_constraint(now_str, schema_block)
    return _build_meetingsphere_constraint(now_str, schema_block)
 
 
# ─── Custom Vanna class combining OpenAI + ChromaDB ──────────────────────────
 
class OpenAIVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config: dict, instance_key: str):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
        
        self.instance_key = instance_key   # ← used to pick the right prompt
 
    def get_sql_prompt(self, question: str, question_sql_list, ddl_list, doc_list, **kwargs):
        """
        Override Vanna's default prompt builder to inject a strict
        schema-awareness constraint at the top of the system message.
        The constraint content is selected based on self.instance_key.
        """
 
        print("\n========== VANNA RETRIEVAL DEBUG ==========")
        print("Question:", question)
        print("QA Retrieved:", len(question_sql_list))
        print("DDL Retrieved:", len(ddl_list))
        print("Docs Retrieved:", len(doc_list))
        print("==========================================\n")
 
        prompt = super().get_sql_prompt(
            question=question,
            question_sql_list=question_sql_list,
            ddl_list=ddl_list,
            doc_list=doc_list,
            **kwargs,
        )
 
        schema_block = kwargs.get("schema_constraint", "")
        if schema_block:
            from datetime import datetime as _dt
            _now = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
            constraint = _build_constraint(self.instance_key, _now, schema_block)
 
            # Prepend to the first system message
            if isinstance(prompt, list):
                for msg in prompt:
                    if isinstance(msg, dict) and msg.get("role") == "system":
                        msg["content"] = constraint + msg["content"]
                        break
                else:
                    prompt.insert(0, {"role": "system", "content": constraint})
 
        return prompt
 
 
# ─── Registry of per-instance Vanna objects ──────────────────────────────────
 
_instances: dict[str, OpenAIVanna] = {}
_lock = threading.Lock()
 
 
def _make_vanna(instance_key: str) -> OpenAIVanna:
    persist_path = os.path.join(settings.chroma_persist_dir, instance_key)
    os.makedirs(persist_path, exist_ok=True)
 
    vn = OpenAIVanna(
        config={
            "api_key": settings.openai_api_key,
            "model": "gpt-5.1",
            "path": persist_path,
            "collection_name": f"vanna_{instance_key}",
            "allow_llm_to_see_data": True,
        },
        instance_key=instance_key,
    )
 
    meta = INSTANCE_META.get(instance_key, {})
    db_type = meta.get("db_type", "sqlserver")

    if db_type == "oracle":
        def run_sql_oracle(sql: str):
            import pandas as pd
            clean_sql = sql.strip().rstrip(';').strip()
            conn = get_connection(instance_key)
            try:
                df = pd.read_sql(clean_sql, conn)
                return df
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"[{instance_key}] Oracle run_sql error: {e}")
                raise
            finally:
                conn.close()

        vn.run_sql = run_sql_oracle
    else:
        conn_str = INSTANCE_CONN_STRINGS[instance_key]
        vn.connect_to_mssql(odbc_conn_str=conn_str)

    return vn
 
 
def get_vanna(instance_key: str) -> OpenAIVanna:
    """Return (and cache) the Vanna instance for this DB instance."""
    if instance_key not in _instances:
        with _lock:
            if instance_key not in _instances:
                _instances[instance_key] = _make_vanna(instance_key)
    return _instances[instance_key]
 
 
# ─── Schema loading & formatting ─────────────────────────────────────────────
 
def _load_schema(instance_key: str) -> dict[str, list[str]]:
    """
    Query INFORMATION_SCHEMA or Oracle catalog to get all user tables and their columns.
    Result is cached for the lifetime of the process, per instance_key.
    """
    if instance_key in _schema_cache:
        return _schema_cache[instance_key]

    with _schema_lock:
        if instance_key in _schema_cache:
            return _schema_cache[instance_key]

        meta = INSTANCE_META.get(instance_key, {})
        db_type = meta.get("db_type", "sqlserver")

        schema: dict[str, list[str]] = {}

        if db_type == "oracle":
            try:
                conn = get_connection(instance_key)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT OWNER, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                    FROM ALL_TAB_COLUMNS
                    WHERE OWNER = 'POP'
                    ORDER BY OWNER, TABLE_NAME, COLUMN_ID
                """)
                rows = cursor.fetchall()
                for owner, tbl, col_name, data_type in rows:
                    if instance_key == _POP_INSTANCE_KEY and tbl.upper() not in POP_ALLOWED_TABLES:
                        continue
                    col = f"{col_name} ({data_type})"
                    key = tbl
                    schema.setdefault(key, []).append(col)
                conn.close()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"[{instance_key}] Oracle _load_schema error: {e}")
        else:
            vn = get_vanna(instance_key)
            df = vn.run_sql("""
                SELECT
                    t.TABLE_SCHEMA,
                    t.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE
                FROM INFORMATION_SCHEMA.TABLES  t
                JOIN INFORMATION_SCHEMA.COLUMNS c
                  ON  c.TABLE_NAME   = t.TABLE_NAME
                  AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
                WHERE t.TABLE_TYPE   = 'BASE TABLE'
                ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME, c.ORDINAL_POSITION
            """)

            if df is not None:
                for _, row in df.iterrows():
                    tbl_schema = row["TABLE_SCHEMA"]
                    tbl        = row["TABLE_NAME"]
                    col        = f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})"

                    if instance_key == _CDXP_INSTANCE_KEY and tbl not in CDXP_ALLOWED_TABLES:
                        continue

                    if tbl_schema and tbl_schema.lower() != "dbo":
                        key = f"{tbl_schema}.{tbl}"
                    else:
                        key = tbl

                    schema.setdefault(key, []).append(col)

        _schema_cache[instance_key] = schema
        return schema


def _format_schema_block(schema: dict[str, list[str]]) -> str:
    """
    Render the schema as a compact, readable block for the prompt.
    Example:
        Users: id (int), name (nvarchar), email (nvarchar)
        Orders: id (int), user_id (int), total (decimal)
    """
    lines = []
    for table, cols in schema.items():
        lines.append(f"  {table}: {', '.join(cols)}")
    return "\n".join(lines)


def invalidate_schema_cache(instance_key: Optional[str] = None) -> None:
    """Call this after DDL changes so the schema is re-fetched on next query."""
    with _schema_lock:
        if instance_key:
            _schema_cache.pop(instance_key, None)
        else:
            _schema_cache.clear()


# ─── SQL column/table validator ───────────────────────────────────────────────

def _validate_sql_against_schema(
    sql: str, schema: dict[str, list[str]], instance_key: Optional[str] = None
) -> Optional[str]:
    if not schema or not HAS_SQLGLOT:
        return None

    meta = INSTANCE_META.get(instance_key, {}) if instance_key else {}
    db_type = meta.get("db_type", "sqlserver")
    glot_dialect = "oracle" if db_type == "oracle" else "tsql"

    known_tables_upper: set[str] = set()
    for t in schema:
        known_tables_upper.add(t.upper())
        if "." in t:
            known_tables_upper.add(t.split(".")[-1].upper())

    all_known_cols_upper: set[str] = {
        col.split(" ")[0].upper()
        for cols in schema.values()
        for col in cols
    }

    try:
        statements = sqlglot.parse(sql, dialect=glot_dialect)
        non_empty_stmts = [s for s in statements if s is not None]
        if len(non_empty_stmts) != 1:
            return "Only single queries are allowed."

        parsed = non_empty_stmts[0]

        if not isinstance(parsed, exp.Select):
            return "Only SELECT queries are allowed."

        cte_and_alias_names = set()
        for cte in parsed.find_all(exp.CTE):
            if cte.alias:
                cte_and_alias_names.add(cte.alias.upper())

        for table in parsed.find_all(exp.Table):
            table_name = table.name.upper()
            table_this = table.this.name.upper() if hasattr(table.this, "name") else table_name

            if table_name in cte_and_alias_names or table_this in cte_and_alias_names:
                continue

            db_prefix = table.db.upper() if table.db else None
            full_name = f"{db_prefix}.{table_name}" if db_prefix else table_name

            if full_name not in known_tables_upper and table_name not in known_tables_upper:
                return (
                    "Sorry, I wasn't able to find the right data for your question. "
                    "Could you try rephrasing it?"
                )

        select_aliases = set()
        for alias in parsed.find_all(exp.Alias):
            if alias.alias:
                select_aliases.add(alias.alias.upper())

        unknown_cols = []
        for column in parsed.find_all(exp.Column):
            col_name = column.name.upper()

            if not col_name or col_name == "*":
                continue

            if col_name in select_aliases or col_name in cte_and_alias_names:
                continue

            if col_name not in all_known_cols_upper:
                unknown_cols.append(col_name)

        if unknown_cols:
            return (
                "I couldn't find that information in the system. "
                "The data you're looking for may be stored under a different name or may not be tracked yet."
            )

        return None

    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"[_validate_sql_against_schema] sqlglot parse warning ({instance_key}): {e}")
        return None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_valid_sql(text: str) -> bool:
    if not text:
        return False
    stripped = text.strip().lstrip("(").upper()
    return bool(re.match(
        r"^(SELECT|WITH)\b",
        stripped,
    ))
 
 
def _friendly_db_error(raw_error: str) -> str:
    """
    Map low-level database / API exception messages to short, human-friendly
    strings.  Falls back to a generic message so technical details never reach
    the user.
    """
    err = raw_error.lower()
 
    if any(k in err for k in ("token", "context_length", "context length",
                               "maximum context", "max_tokens", "rate limit",
                               "rate_limit", "too many requests", "429")):
        return (
            "Your question is a bit too complex for me to process right now. "
            "Try breaking it into smaller questions or simplifying the request."
        )
 
    if any(k in err for k in ("connection", "timeout", "timed out",
                               "network", "unreachable", "refused", "reset by peer")):
        return (
            "I'm having trouble connecting to the database at the moment. "
            "Please try again in a few seconds."
        )
 
    if any(k in err for k in ("login failed", "permission", "access denied",
                               "unauthorized", "403", "401", "privilege")):
        return (
            "It looks like there's a permissions issue preventing me from "
            "fetching that data. Please contact your administrator."
        )
 
    if any(k in err for k in ("syntax error", "incorrect syntax", "invalid object name",
                               "invalid column name", "ambiguous column")):
        return (
            "I had trouble building the right query for your question. "
            "Could you try rephrasing it?"
        )
 
    if any(k in err for k in ("no rows", "no results", "no matching")):
        return "No matching records found."
 
    return (
        "Something went wrong while processing your request. "
        "Please try again, or rephrase your question."
    )
 
 
# ─── Per-instance NL-summary domain knowledge ────────────────────────────────
 
def _meetingsphere_domain_block() -> str:
    return (
        "DOMAIN KNOWLEDGE:\n"
        "Meeting status is stored as an integer in the database. "
        "Always translate these LuMeetingSphereLookups_StatusCode values into human-readable labels in your response:\n"
        "   0 = Cancelled\n"
        "   1 = Pending\n"
        "   2 = Ended\n"
        "   3 = Completed\n"
        "   4 = Draft\n"
        "Never show raw status numbers to the user — always use the label.\n\n"
        "ATTACHMENT LINKS:\n"
        "If the results contain MtAttachment_EcmFileId and MtAttachment_FileName columns:\n"
        "  - Only build a link when MtAttachment_EcmFileId is NOT null and NOT empty.\n"
        "  - URL pattern: https://cppapk.sharepoint.com/sites/staging/Meeting%20Sphere/{MtAttachment_EcmFileId}_{MtAttachment_FileName}\n"
        "  - If the results also contain a meeting/title column, include it in the label: 'FileName.pdf — MeetingName'\n"
        "  - Each ATTACHMENT_LINK MUST be on its own separate line. NEVER place it inline with prose text.\n"
        "  - Structure your response exactly like this:\n"
        "      <one plain intro sentence ending with a colon or period>\n"
        "      (blank line)\n"
        '      ATTACHMENT_LINK::{"url":"...","label":"..."}\n'
        '      ATTACHMENT_LINK::{"url":"...","label":"..."}\n'
        "  - No text of any kind after the last ATTACHMENT_LINK line.\n"
        "  - If MtAttachment_EcmFileId is null for a row, list the filename as plain text only — no ATTACHMENT_LINK line.\n"
        "  - Never mention EcmFileId values or technical column names to the user.\n\n"
        "STRICT RULES:\n"
        "1. Rule 1 applies ONLY when the user asks to extract, read, or get the text CONTENT "
        "from inside a file (e.g. 'read this pdf', 'show me what's written in the file'). "
        "It does NOT apply when the user is simply listing, finding, or asking about attachments. "
        "For listing/finding attachments, show the results normally.\n"
        "   When rule 1 does apply, respond with exactly: "
        "'To view this file, please wait for the upcoming version with download feature :)' "
        "— nothing else.\n"
        "2. Never mention how many rows or records were returned.\n"
        "3. Never explain technical limitations, system behavior, or what columns exist.\n"
        "4. Never suggest additional steps or workarounds.\n"
        "5. If data was found, confirm it in one plain sentence only, then list ATTACHMENT_LINK lines if applicable."
    )
 
 
def _rms_domain_block() -> str:
    return (
        "STRICT RULES:\n"
        "1. Never mention how many rows or records were returned.\n"
        "2. Never explain technical limitations, system behavior, or what columns exist.\n"
        "3. Never suggest additional steps or workarounds.\n"
        "4. If data was found, confirm it in one plain sentence only.\n"
        "5. If no data was found, say 'No matching records found.' only."
    )
 
 
def _cdxp_domain_block() -> str:
    """
    CDXP NL-summary rules. Will be expanded once real lookup/status codes are
    confirmed — for now we apply the same conservative presentation rules used
    by RMS, plus invoice-specific guidance.
    """
    return (
        "DOMAIN KNOWLEDGE — CDXP:\n"
        "You are summarising results from the CDXP Power Purchase Agreement system.\n"
        "Keep terminology business-friendly: use 'invoice' not 'DIARY_HEADER_INTERFACE', "
        "'supplier' not 'AP_SUPPLIERS', 'PPA' not 'PPA_HEADER', etc.\n\n"
        "STRICT RULES:\n"
        "1. Never mention how many rows or records were returned.\n"
        "2. Never expose table names, column names, or technical schema details.\n"
        "3. Never suggest additional steps or workarounds.\n"
        "4. If data was found, confirm it in one plain sentence only.\n"
        "5. If no data was found, say 'No matching records found.' only.\n"
        "6. If a value is NULL or empty, say 'This information has not been populated yet.' only."
    )
 
 
def _pop_domain_block() -> str:
    """
    POP (Power Purchase & Invoice Information) NL-summary rules and domain guidance.
    """
    return (
        "DOMAIN KNOWLEDGE — POP (Power Purchase & Invoice Information):\n"
        "You are summarizing results from the POP Power Purchase & Invoice Information system.\n"
        "Hierarchy: Plant -> Site -> Fuel -> Invoice Type -> Blocks -> Components.\n\n"
        "STATUS & HISTORICAL RULES:\n"
        "STRICT RULES:\n"
        "1. Never mention how many rows or records were returned.\n"
        "2. Never expose raw table names, column names, or technical schema details.\n"
        "3. Never suggest additional steps or workarounds.\n"
        "4. If data was found, confirm it in simple, business-friendly terms.\n"
        "5. If no data was found, say 'No matching records found.' only.\n"
        "6. If a value is NULL or empty, say 'This information has not been populated yet.' only."
    )


def _domain_block(instance_key: str) -> str:
    if instance_key == _RMS_INSTANCE_KEY:
        return _rms_domain_block()
    if instance_key == _CDXP_INSTANCE_KEY:
        return _cdxp_domain_block()
    if instance_key == _POP_INSTANCE_KEY:
        return _pop_domain_block()
    return _meetingsphere_domain_block()
 
 
# ─── Natural-language summary ─────────────────────────────────────────────────
 
def generate_nl_summary(
    question: str,
    sql: Optional[str],
    results: Optional[list[dict]],
    error: Optional[str],
    *,
    api_key: str,
    instance_key: str = "it_meetingsphere",
    model: str = "gpt-4.1-mini",
    language: str = "English",
    max_sample_rows: int = 5,
) -> str:
    import openai
    from datetime import date
 
    today_str = date.today().strftime("%B %d, %Y")
 
    if error:
        result_snapshot = f"Query failed with error: {error}"
    elif not results:
        result_snapshot = "The query returned no rows."
    else:
        sample = results[:max_sample_rows]
        total  = len(results)
        rows_text = "\n".join(str(r) for r in sample)
        tail = f"\n... ({total - max_sample_rows} more rows)" if total > max_sample_rows else ""
        result_snapshot = f"Total rows returned: {total}\nSample data:\n{rows_text}{tail}"
 
    system_prompt = (
        f"You are a helpful assistant that explains database query results "
        f"in simple, clear {language} to non-technical users. "
        f"Today's date is {today_str}. "
        "Focus only on what directly answers the user's question.\n\n"
        f"{_domain_block(instance_key)}"
    )
 
    user_prompt = (
        f"A user asked: \"{question}\"\n\n"
        f"Here is the result:\n{result_snapshot}\n\n"
        "Please write a short, friendly summary explaining what this result means."
    )
 
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return "Results fetched successfully."
 
 
# ─── Public query runner ──────────────────────────────────────────────────────
 
def run_query(instance_key: str, question: str, summary_question: Optional[str] = None) -> dict:
    """
    Normalize → Generate SQL → Validate → Execute.
 
    Normalization only applies to "it_meetingsphere". Every other instance
    (including "it_rms" and "it_cdxp") uses the question unchanged.
    """
    vn = get_vanna(instance_key)
 
    # ── Step 1: Normalize the question ────────────────────────────────────────
    if instance_key == "it_meetingsphere":
        is_followup = bool(summary_question) and (
            question.strip().lower() != summary_question.strip().lower()
        )
        normalized_question, norm_method = normalize_question(
            question=question,
            api_key=settings.openai_api_key,
            is_followup=is_followup,
            model="gpt-4.1-mini",
        )
    else:
        normalized_question, norm_method = question, "skipped_not_meetingsphere"
 
    # Load and format the real schema for this instance
    # For CDXP, _load_schema already filters to CDXP_ALLOWED_TABLES
    schema = _load_schema(instance_key)
    schema_block = _format_schema_block(schema)
 
    # ── POP: Proactive out-of-scope keyword interception ──────────────────────
    try:

        sql = vn.generate_sql(
            question=normalized_question,
            allow_llm_to_see_data=True,
            schema_constraint=schema_block,
        )

        if not sql:
            err_msg = _POP_DEFAULT_POLITE_MSG if instance_key == _POP_INSTANCE_KEY else "I wasn't able to understand your question well enough to search for an answer. Could you try rephrasing it?"
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": err_msg,
            }

        if sql.strip().startswith("NO_MATCH:"):
            user_msg = sql.strip().removeprefix("NO_MATCH:").strip()
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": user_msg,
            }

        # ── CDXP: autocorrect hallucinated schema prefix ──────────────────────
        # The LLM occasionally writes "CDXP.TableName" (using the database name
        # as a schema) instead of the correct "CPPA_CA.TableName". Silently fix
        # this before validation and execution so valid queries aren't rejected.
        if instance_key == _CDXP_INSTANCE_KEY:
            sql = re.sub(r'\bCDXP\.', 'CPPA_CA.', sql, flags=re.IGNORECASE)
 
        if _INTROSPECTION_MARKER in sql:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I need a moment to look that up — please try your question again.",
            }
 
        if not _is_valid_sql(sql):
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I wasn't able to find an answer for that. Try rephrasing your question.",
            }
 
        schema_error = _validate_sql_against_schema(sql, schema, instance_key=instance_key)
        if schema_error:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": schema_error,
            }
 
        # ── Execute ───────────────────────────────────────────────────────────
        df = vn.run_sql(sql)
        if df is not None:
            df = df.drop_duplicates()
            import math

            def sanitize(val):
                if val is None:
                    return None
                try:
                    import pandas as pd
                    if pd.isna(val):
                        return None
                except (TypeError, ValueError):
                    pass
                if isinstance(val, (bytes, bytearray)):
                    import base64
                    return base64.b64encode(val).decode('utf-8')
                if isinstance(val, float) and val.is_integer():
                    return int(val)
                return val
 
            results = [
                {k: sanitize(v) for k, v in record.items()}
                for record in df.to_dict(orient="records")
            ]
        else:
            results = []
 
        nl_summary = generate_nl_summary(
            question=summary_question or question,
            sql=sql,
            results=results,
            error=None,
            api_key=settings.openai_api_key,
            instance_key=instance_key,
        )
 
        return {
            "sql": sql,
            "results": results,
            "normalized_question": normalized_question,
            "normalization_method": norm_method,
            "nl_summary": nl_summary,
            "error": None,
        }
 
    except Exception as e:
        err = str(e)
        if _INTROSPECTION_MARKER in err:
            return {
                "sql": None, "results": None,
                "normalized_question": normalized_question,
                "normalization_method": norm_method,
                "nl_summary": None,
                "error": "I need a moment to look that up — please try your question again.",
            }
        return {
            "sql": None, "results": None,
            "normalized_question": normalized_question,
            "normalization_method": norm_method,
            "nl_summary": None,
            "error": _friendly_db_error(err),
        }
 
 
# ─── Training helpers ─────────────────────────────────────────────────────────
 
def debug_vanna(instance_key: str, question: str):
    vn = get_vanna(instance_key)
    df = vn.get_training_data()
    print("Total training records:", len(df) if df is not None else 0)
    if df is not None:
        print(df[['training_data_type', 'question', 'content']].to_string())
    print("\nSimilar Q&A:", vn.get_similar_question_sql(question))
    print("\nRelated DDL:", vn.get_related_ddl(question))
    print("\nRelated docs:", vn.get_related_documentation(question))
 
 
def train_ddl(instance_key: str, ddl: str) -> None:
    invalidate_schema_cache(instance_key)
    get_vanna(instance_key).train(ddl=ddl)
 
 
def train_documentation(instance_key: str, doc: str) -> None:
    get_vanna(instance_key).train(documentation=doc)
 
 
def train_qa(instance_key: str, question: str, sql: str) -> None:
    get_vanna(instance_key).train(question=question, sql=sql)
 
 
def remove_training_data(instance_key: str, training_id: str) -> bool:
    return get_vanna(instance_key).remove_training_data(id=training_id)
 
 
def get_training_data(instance_key: str) -> list[dict]:
    df = get_vanna(instance_key).get_training_data()
    return [] if df is None else df.to_dict(orient="records")
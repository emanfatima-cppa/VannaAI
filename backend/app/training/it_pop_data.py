"""app/training/it_pop_data.py – Q&A pairs and documentation for POP instance."""

IT_POP_TRAINING: dict = {
    "documentation": [
        # ── Core Domain Overview & Hierarchy ──────────────────────────────────
        """
        POP (Purchase of Power) manages Independent Power Producer
        (IPP / Vendor) data, Power Purchase Agreements (PPAs), and invoice processing lifecycle
        for power generation in CPPA.

        Data Hierarchy & Granularity:
          Plant ➔ Site ➔ Fuel ➔ Invoice Type ➔ Blocks ➔ Components

        Domain Filtering Scope & Extraction Rules:
        - Strict Column-Existence Filtering Principle: Apply default domain filters ONLY IF the corresponding column exists in the queried table. If the column is present, the filter MUST be applied. If the column is absent from the target table, omit that filter:
        - Fuel Type Filter: Extract ONLY standalone Coal fuel type (FUEL_TYPE = 'Coal') whenever target table contains FUEL_TYPE column. Do NOT include hybrid fuel types like Coal and Bagasse in any case.
        - Invoice Type Filter: Extract ONLY EPP invoice type (INV_TYPE / INVOICE_TYPE = 'EPP') whenever target table contains INV_TYPE / INVOICE_TYPE column.
        - Invoice Category Filter: Extract ONLY Monthly and Hourly invoices (INV_CATEGORY IN ('Monthly', 'Hourly')) whenever target table contains INV_CATEGORY column. If absent, omit this filter.
        - Disabled Flag Filter: Include ONLY active/non-disabled records (IS_DISABLE = 'N' or IS_DISABLE = 'No') whenever target table contains IS_DISABLE column.
        - Approval Status Filter: Apply APPROVAL_STATUS = 'Approved' filter BY DEFAULT ONLY when querying the PPA table (CPPA_POP_PPA_DATA_ALL_T). For the Verified table (CPPA_POP_VERIFIED_DATA_ALL_T), APPROVAL_STATUS is 'Approved', but do NOT auto-apply any APPROVAL_STATUS filter by default unless the user specifically mentions or asks for approved status. For the Unverified/Pending table (CPPA_NOT_VERIFIED_ALERT_T), do NOT auto-apply any approved filter — filter by status ONLY if the user explicitly asks for a specific status.
        - Deduplication & Top-N / List Limits: ALWAYS use SELECT DISTINCT when querying lists of entities (such as IPPs, PPAs, Invoices) to prevent duplicate rows from multi-line or component-level tables. When the user asks for a limited count or list (e.g., "list 5 invoices", "show top 10 IPPs", "list 5 Coal plants"), ensure SELECT DISTINCT is applied so that exactly N unique/distinct records are returned (e.g., SELECT DISTINCT ... FETCH FIRST 5 ROWS ONLY) rather than returning duplicate rows of the same entity before reaching the row limit.
        - Component Name Selection & Filter: When asked for a component name or when filtering by component name (e.g., 'VO&M', 'FCC', 'Fuel Price', 'NEO', component rate/amount/value), ALWAYS select and filter on STANDARD_COMP_NAME (or STANDARD_COMPONENT_NAME) instead of COMP_NAME whenever the target table contains the STANDARD_COMP_NAME column (e.g., CPPA_POP_VERIFIED_DATA_ALL_T). Only use COMP_NAME if the target table does not have STANDARD_COMP_NAME.
        - Invoice Due Date Priority: When asked for the due date of an invoice (e.g., "give me the due date of this invoice"), ALWAYS prioritize REVISED_FINAL_DUE_DATE if available; if it is NULL, fall back to FINAL_DUE_DATE (using NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) or COALESCE(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) AS DUE_DATE). NEVER use DEFAULT_DUE_DATE.
        - Delayed Invoices / Delay Calculation: Whenever the user asks about 'delayed' invoices, payments, or items (e.g., "Which invoice is most delayed"), ALWAYS use GL_DATE_VR (Invoice Verification Accounting Date) against the due date NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) for calculating the delay (i.e. (TRUNC(GL_DATE_VR) - TRUNC(NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE))) AS DELAY_DAYS). NEVER use SYSDATE or GL_DATE_CL for invoice delay calculation.
        - Date / Billing Month Year Expansion: Whenever the user enters a date or billing month with a 2-digit year (e.g., 'Jan-24', 'Jan 24', 'May 26'), ALWAYS expand the 2-digit year to a full 4-digit YYYY format (e.g. 'JAN-2024') in SQL filtering conditions (e.g., UPPER(BILLING_MONTH) = 'JAN-2024' OR BILLING_MONTH = 'JAN-24' OR BILLING_MONTH = 'Jan-24').
        """,

    

        # ── Table: CPPA_POP_PPA_DATA_ALL_T ───────────────────────────────────
        """
        CPPA_POP_PPA_DATA_ALL_T — Master Table for Power Purchase Agreements (PPA).
        This table contains comprehensive master data for Power Purchase Agreements (PPA) agreed between CPPA and Independent Power Producers (IPPs). 
        Extract ONLY PPA data for Coal fuel type (FUEL_TYPE = 'Coal'), EPP invoice type (INVOICE_TYPE = 'EPP'). Apply BOTH IS_DISABLE = 'N' AND APPROVAL_STATUS = 'Approved' filters.
        It holds contract terms, policy descriptions, capacity limits (Contracted & Dependable MW), agreement dates, effective periods, interest rate calculations, block structures, fuel types, tariff components (component names, types, zones, values, formulas, units), claim portal & diary/invoice flags, and audit metadata.

        Key columns:
        - PPA_NO                 : PPA contract / agreement number
        - IPP_NAME               : Name of the IPP vendor / power producer
        - IPP_SITE               : Vendor plant site 
        - IPP_ADDRESS            : Physical address of the IPP vendor / plant
        - POWER_POLICY           : Applicable power policy (Policy 2002, 2015, etc.) 
        - POWER_POLICY_DESC      : Applicable power policy (Policy 2002, 2015, etc.) description
        - CONTRACTED_CAPACITY    : Capacity identified in PPA at the time of agreement (MW)
        - DEPENDABLE_CAPACITY    : Actual capacity that the plant is producing / tested capacity (MW)
        - PPA_TERM               : PPA agreement life / total tenure (years)
        - AGREEMENT_DATE         : PPA agreement signing date
        - FINANCIAL_CLOSE_DATE   : Target date / time allowed for IPP to complete financial arrangements for installation
        - REQUIRED_COD           : Required Commercial Operation Date on which the plant must be operational
        - ACTUAL_COD             : Actual Commercial Operation Date when the plant became commercially functional and operational
        - PPA_EFFECTIVE_FROM     : PPA start date from which the agreement becomes functional and effective
        - PPA_EFFECTIVE_TO       : PPA end date until which the agreement remains functional and effective
        - INVOICE_TYPE           : Associated PPA invoice type (Filter: 'EPP')
        - IS_HOURLY              : Flag indicating invoice billing frequency (If 'Y' / 'Yes' then Hourly billing; otherwise if 'N' / 'No' then Monthly billing)
        - ADVANCE_PAYMENT        : Yes/No flag indicating whether CPPA provides advance payment/capacity to IPP
        - INT_RATE_TYPE          : Method for interest rate calculation on delayed payments (e.g., KIBOR, RIFO, 1 week, 3 months as per agreement)
        - INT_CALC_FIXED_DAYS    : Fixed number of days used for interest calculation on delayed payments
        - BLOCK_NO               : Physical dependency and capacity block identifier based on plant complex configuration (e.g., Complex: entire power plant acts as a single block; Solar: Block No per panel array like Block I, Block II; Wind: based on capacity / energy level)
        - PART_OF                : Classification and grouping hierarchy of components
        - FUEL_TYPE              : Source of energy/fuel that the plant uses to produce electricity (e.g., Coal)
        - PPA_BLOCK_EFFECTIVE_TO : PPA block deadline date / effective end date
        - COMP_TYPE              : Component type classification:
                                     * 'related': component data sourced from another form/reference (e.g. Reference Tariff, Present Rate, Avg. Exchange Rate)
                                     * 'input'  : manual input data (e.g. from PPA or Invoice)
                                     * 'formula': calculated dynamically using a formula
        - COMP_ZONE              : Source zone / origin indicating where component data comes from for related and input types (e.g., for related: 'Reference Tariff', 'Present Rate', 'Avg. Exchange Rate'; for input: 'Invoice', 'PPA')
        - COMP_NAME              : Name of the component
        - COMP_VALUE             : Respective value for the component
        - UNIT                   : Measurement unit for the component (e.g., Rs, kWh, index, factor)
        - FORMULA                : Mathematical formula used to calculate different tariff components
        - FCA_COMPONNET_NAME     : Fuel Cost Adjustment (FCA) component grouping and in which category will the component fall
        - SHOW_ON_DIARY          : Flag indicating whether the component is shown in diary / CDXP portal or not
        - SHOW_ON_INV            : Flag indicating whether the component is shown on the invoice or not
        - INCLUD_IN_CLAIM_PORTAL : Flag indicating whether the particular component will be included in the claim portal or not
        - INC_IN_TOT             : Flag indicating whether the component is included in the invoice / billing total or not
        - CREATION_DATE          : System creation timestamp / date when the invoice or record was created
        - CREATED_BY             : Person / user who created the invoice or record
        - IS_DISABLE             : Status flag indicating if PPA record/component is disabled (Filter: (UPPER(IS_DISABLE) = 'N' OR IS_DISABLE = 'N' OR IS_DISABLE = 'No'))
        - APPROVAL_STATUS        : Status flag indicating PPA approval status (Filter: (UPPER(APPROVAL_STATUS) LIKE '%APPROV%' OR APPROVAL_STATUS = 'Approved'))
        """,

        # ── Table: CPPA_NOT_VERIFIED_ALERT_T ────────────────────────────────
        """
        CPPA_NOT_VERIFIED_ALERT_T — Table for Unverified / Pending / Incomplete & Rejected Invoices.
        This table contains information about all invoices that are not fully verified yet, including rejected, pending, inprocess, and incomplete invoices.
        ALWAYS query from this table whenever the user asks about:
        - Rejected Invoices (e.g. "rejected invoices", "invoices rejected", "how many invoices were rejected", "Invoice Reject")
        - Pending / Inprocess / Incomplete Invoices (e.g. "pending invoices", "inprocess invoices", "incomplete invoices", "unverified items", "pending days", "on desk")
        - Workflow statuses ('Diary Approved', 'Diary Incomplete', 'Invoice Inprocess', 'Invoice Incomplete', 'Invoice', 'Invoice Reject').
        Extract and query ONLY for Coal fuel IPPs (join with CPPA_POP_PPA_DATA_ALL_T on IPP_NAME for FUEL_TYPE if needed), EPP invoice type (INV_TYPE = 'EPP'), and Monthly & Hourly invoices.

        Synonyms for unverified/pending/rejected invoices: rejected invoice, invoices rejected, invoice reject, not verified, unverified alert, pending invoice, inprocess invoice, incomplete invoice

        Key columns:
        - IPP_NAME               : Name of the IPP / Vendor
        - IPP_SITE               : IPP plant site 
        - INV_TYPE               : Type of invoice submitted (Filter: 'EPP')
        - DIARY_NO               : Diary tracking number 
        - INVOICE_NO             : Invoice number that comes from ERP
        - REC_INV_AMOUNT         : Total received invoice amount
        - RECEIVING_DATE         : Date invoice was received
        - INV_DUE_DATE           : Due date provided by IPP for invoice payment
        - PENDING_DAYS           : Number of days remaining until the due date.
        - APPROVAL_STATUS        : Workflow approval status of the invoice. Possible values: 'Diary Approved', 'Diary Incomplete', 'Invoice Inprocess', 'Invoice Incomplete', 'Invoice', 'Invoice Reject'. For rejected invoices, filter: (UPPER(APPROVAL_STATUS) LIKE '%REJECT%' OR APPROVAL_STATUS = 'Invoice Reject').
        - ON_DESK                : Name of the officer / personnel currently holding the invoice file on their desk (e.g., 'Mr. Asfandyar Shakeel', 'Hamdan Wazir')
        - INITIATOR / INITIATOR_EMAIL : Name and email of the person who is creating invoice.
        - MANAGER_NAME / MANAGER_EMAIL : Finance manager name and email who is verifying invoices
        - DGM_NAME / DGM_EMAIL   : Name and email of Deputy General Manager overseeing approval
        - FORM_NAME              : Workflow / approval form type indicating whether the record is related to 'Diary' or 'Invoice'
        - EVENT_STATUS           : Workflow stage / current processing status of the invoice (e.g., 'Invoice Send To Finance', 'Invoice Send to Tech Department', 'Invoice Received', 'Invoice Accepted By Finance')
        - LAST_UPDATE_DATE       : Invoice last update date
        """,

        # ── Table: CPPA_POP_VERIFIED_DATA_ALL_T ─────────────────────────────
        """
        CPPA_POP_VERIFIED_DATA_ALL_T — Table for Fully Verified & Approved Invoices.
        Primary and default table to query whenever asking about verified invoices in general, top invoices, total verified values, approved invoice totals, or complete verified invoice details. 
        Extract ONLY data for Coal fuel type (FUEL_TYPE = 'Coal'), EPP invoice type (INV_TYPE = 'EPP'), and Monthly & Hourly FORM/INVOICE. 
        Contains comprehensive information regarding verified invoices at all hierarchy levels (Plant ➔ Site ➔ Fuel ➔ Invoice Type ➔ Block ➔ Component level). Includes standard invoice components stored in LEV_COMP (e.g., 'VO&M Rate', 'FCC Rate', 'Fuel Price', 'Dependable Capacity (MW)', 'VO&M Amount', 'FCC Amount', 'NEO (kWh)', etc.).
        CRITICAL TABLE SELECTION RULE: This table contains ONLY approved/verified invoices. NEVER query this table for rejected invoices, pending invoices, or unverified workflow statuses! Whenever asked about rejected or pending invoices, ALWAYS query CPPA_NOT_VERIFIED_ALERT_T instead.

        Synonyms for verified invoices: invoice, invoices, top invoices, verified invoice, approved invoice, verified amount, billing details

        Key columns:
        - IPP_NAME               : Name of the IPP vendor / power producer
        - IPP_SITE               : Vendor plant site name
        - IS_HISTORICAL          : Indicator showing if invoice is historical ('Y' - before ERP) or non-historical (after ERP)
        - IPP_EMAIL / IPP_ADDRESS: IPP email and physical address details
        - POWER_POLICY / POWER_POLICY_DESC : Power policy name and description
        - INV_TYPE / INV_SUB_TYPE: Invoice type (Filter: 'EPP') and its sub-type
        - INV_CATEGORY           : Invoice category ('Monthly' or 'Hourly')
        - ADVANCE_PAYMENT        : Yes/No flag indicating whether CPPA provides advance payment/capacity to IPP
        - FUEL_TYPE              : Source of energy/fuel that the plant uses to produce electricity (e.g., Coal)
        - BLOCK_NO               : Physical dependency and capacity block identifier based on plant complex configuration (e.g., Complex: entire power plant acts as a single block; Solar: Block No per panel array like Block I, Block II; Wind: based on capacity / energy level)
        - COMP_TYPE              : Component type classification:
                                     * 'related': component data sourced from another form/reference (e.g. Reference Tariff, Present Rate, Avg. Exchange Rate)
                                     * 'input'  : manual input data (e.g. from PPA or Invoice)
                                     * 'formula': calculated dynamically using a formula
        - COMP_ZONE              : Source zone / origin indicating where component data comes from for related and input types (e.g., for related: 'Reference Tariff', 'Present Rate', 'Avg. Exchange Rate'; for input: 'Invoice', 'PPA')
        - COMP_NAME              : Component name in invoice/portal
        - STANDARD_COMP_NAME     : Standardized component name. ALWAYS use and filter on STANDARD_COMP_NAME instead of COMP_NAME (e.g., "VO&M Amount", "FCC Amount", "Fuel Price", "NEO (kWh)", etc.) whenever querying or filtering component names, because COMP_NAME contains raw variant values (e.g., "Amount (for VO&M)", "Variable O&M Amount").
        - COMP_VALUE             : Value for the component
        - COMP_UNIT              : Measurement unit for the component (e.g., Rs, kWh, index, factor)
        - FCA_COMPONNET_NAME     : Fuel Cost Adjustment (FCA) component grouping and category classification
        - PART_OF                : Classification and grouping hierarchy of components
        - DIARY_NO               : Internal CPPA diary tracking number
        - IPP_INV_NO             : Invoice number coming from CDXP
        - INV_RECEIVED_DATE      : Date when invoice was received (from CDXP)
        - GL_DATE_CL             : Accounting claim date for invoice claim (contains date, month, and year, e.g., 31-OCT-17)
        - GL_PERIOD_CL           : Claim accounting period in month-year format (e.g., OCT-17, recording expense in the month claimed)
        - INV_PERIOD_FRM         : Invoice effective start date (billing period from date)
        - INV_PERIOD_TO           : Invoice effective end date (billing period to date)
        - GL_DATE_VR             : Invoice verification accounting date (contains date, month, and year, e.g., 31-OCT-17)
        - GL_PERIOD_VR           : Invoice verification accounting period in month-year format (e.g., OCT-17)
        - BILLING_MONTH          : Billing month (e.g., MAY-2026) representing the billing cycle/consumption period for which the bill is generated
        - TRANSFER_TO_AP         : Indicator if verified invoice has been transferred to Accounts Payable (AP)
        - TOTAL_CLAIMED_VALUE    : Total invoice amount claimed by IPP (energy consumption, fuel costs, or other expenses)
        - TOTAL_VERIFIED_VALUE   : Main column for Total Verified Value / Approved Invoice Amount verified by CPPA
        - TOTAL_DIFFERENCE_VALUE : Difference between total claimed value and verified value (when CPPA verifies a different/lower amount)
        - BLK_CLAIMED_VALUE      : Block-wise amount claimed by IPP
        - BLK_CPPA_WORKING_VALUE : Block-wise amount calculated by CPPA
        - BLK_VERIFIED_VALUE     : Block-wise verified value (if BLK_CLAIMED_VALUE < BLK_CPPA_WORKING_VALUE then BLK_CLAIMED_VALUE, otherwise BLK_CPPA_WORKING_VALUE)
        - ADV_ALREADY_PAID_CL    : Advance payment amount claimed by IPP indicating how much advance payment has already been made (applicable when ADVANCE_PAYMENT = 'Yes')
        - INVOICE_NO             : Unique identifier for the invoice (FROM ERP)
        - ADV_ALREADY_PAID_CPPA  : Advance payment amount calculated / worked out by CPPA indicating how much advance payment has already been made (applicable when ADVANCE_PAYMENT = 'Yes')
        - CLAIMED_VALUE          : Component-level rate, value, or amount claimed by IPP
        - CPPA_WORKING           : Component-level value calculated by CPPA
        - VERIFIED_VALUE         : Component-level verified value (CPPA working value, or claimed value if claim is lower)
        - DIFF_VALUE_VF          : Difference between component claimed value and CPPA working value
        - INC_IN_TOT             : Flag indicating whether this component is included/added in the invoice total calculation
        - SHOW_ON_DIARY          : Flag indicating whether the component is shown in diary / CDXP portal or not
        - SHOW_ON_INV            : Flag indicating whether the component is shown on the invoice or not
        - AP_INVOICE_VALUE       : Accounts Payable (AP) invoice entry amount / total verified value transferred to AP
        - AP_PAYMENT_VALUE       : Actual total payment amount paid to vendor via AP
        - DIFF_CAUSE             : Cause / reason category for the differential invoice category
        - DIFF_CAUSE_DESC        : Detailed description and explanation of the difference cause for differential invoice category
        - CREATED_BY             : Person / user who created the invoice after diary entry
        - CREATION_DATE          : Timestamp / date when the invoice was created
        - LAST_UPDATED_BY        : Invoice last updated by whom
        - LAST_UPDATE_DATE       : Invoice last update date
        - AP_LAST_UPDATE_DATE    : Timestamp / date of the last action performed in Accounts Payable (AP) after the invoice is verified in POP and transferred to AP
        - PRE_POST               : Differential categorization indicator ('Pre': differential invoice type for invoices prior to ERP implementation; 'Post': differential invoice type for invoices after ERP implementation)
        - PARENT_INV_NO          : Parent invoice reference number. Used when original invoices (e.g., Invoices A, B, C for Jan, Feb, Mar) have NOT been paid yet and NEPRA revises/changes the tariff rate; any new revised/differential invoice created will reference those original unpaid invoices as its parent invoices.
        - MAIN_INV_NO            : Invoice number for miscellaneous invoice category / debit notes
        - MAIN_INV_TOTAL_AMOUNT  : Total amount of miscellaneous invoice / debit note
        - DUE_DATE_TO_BE_CALCULATED_FROM : Base reference date written on the invoice for invoice payment calculation
        - DUE_DATE_TERM          : Number of days allowed for invoice payment (e.g., 25 days)
        - DEFAULT_DUE_DATE       : Default due date calculated as DUE_DATE_TO_BE_CALCULATED_FROM + DUE_DATE_TERM days. DO NOT use this column when asked for invoice due date.
        - DUE_DATE_TOLERANCE     : Holiday / weekend adjustment days (+1 day if due date falls on Sunday to shift to Monday; -2 days if on weekend to shift to Friday)
        - FINAL_DUE_DATE         : Final payment due date for invoice (fallback if REVISED_FINAL_DUE_DATE is NULL)
        - REVISED_FINAL_DUE_DATE : Most revised / updated final due date for invoice payment. When the user asks for invoice due date, always prioritize REVISED_FINAL_DUE_DATE and fall back to FINAL_DUE_DATE (using NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) or COALESCE(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) AS DUE_DATE). NEVER use DEFAULT_DUE_DATE.
        - APPROVAL_STATUS        : Status flag indicating invoice approval status in verified table (Contains ONLY 'Approved' records. Filter: (UPPER(APPROVAL_STATUS) LIKE '%APPROV%' OR APPROVAL_STATUS = 'Approved'))
        - CANCELLATION_DATE      : Date of cancellation of diary
        - CANCELLATION_STATUS    : Status flag indicating cancellation status of invoice
        - CANCELLATION_GL_DATE   : Cancellation date of invoice
        - LETTER_MAIL_CHECK      : Yes/No flag indicating whether the invoice is approved and the verification letter is emailed to the IPP
        - DEBIT_NOTE_CATEGORY    : Category classification for debit notes (contains only miscellaneous invoice category and adjustments)
        - REF_INVOICE_NO / REF_INVOICE_NUMBER : Reference invoice number. Used when an invoice (e.g., Invoice A) is already PAID, and subsequently a new differential/adjustment invoice (e.g., Invoice B) is generated due to tariff/rate changes by NEPRA; Invoice A is referenced in Invoice B.
        - REF_BILLING_MONTH      : Billing month of the referenced paid invoice (e.g., MAY-2026) indicating the original service/consumption period of the reference invoice.
        """,
    ],
    "qa_pairs": [
        {
            "question": "For each power producer, how many of their invoices were Rejected and what fuel type do they use?",
            "sql": "SELECT n.IPP_NAME, p.FUEL_TYPE, COUNT(DISTINCT n.INVOICE_NO) AS REJECTED_INVOICE_COUNT FROM CPPA_NOT_VERIFIED_ALERT_T n JOIN CPPA_POP_PPA_DATA_ALL_T p ON UPPER(n.IPP_NAME) = UPPER(p.IPP_NAME) WHERE (UPPER(p.FUEL_TYPE) = 'COAL' OR LOWER(p.FUEL_TYPE) = 'coal' OR p.FUEL_TYPE = 'Coal') AND (UPPER(n.INV_TYPE) = 'EPP' OR LOWER(n.INV_TYPE) = 'epp' OR n.INV_TYPE = 'EPP') AND (UPPER(n.APPROVAL_STATUS) LIKE '%REJECT%' OR n.APPROVAL_STATUS = 'Invoice Reject') GROUP BY n.IPP_NAME, p.FUEL_TYPE ORDER BY n.IPP_NAME;"
        },
        {
            "question": "Show all rejected invoices for IPPs",
            "sql": "SELECT IPP_NAME, IPP_SITE, INVOICE_NO, REC_INV_AMOUNT, RECEIVING_DATE, APPROVAL_STATUS, ON_DESK FROM CPPA_NOT_VERIFIED_ALERT_T WHERE (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(APPROVAL_STATUS) LIKE '%REJECT%' OR APPROVAL_STATUS = 'Invoice Reject');"
        },
        {
            "question": "Which invoice is most delayed",
            "sql": "SELECT IPP_NAME, IPP_SITE, INVOICE_NO, BILLING_MONTH, GL_DATE_VR, NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) AS DUE_DATE, (TRUNC(GL_DATE_VR) - TRUNC(NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE))) AS DELAY_DAYS, TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly')) AND NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE) IS NOT NULL AND GL_DATE_VR IS NOT NULL ORDER BY (TRUNC(GL_DATE_VR) - TRUNC(NVL(REVISED_FINAL_DUE_DATE, FINAL_DUE_DATE))) DESC FETCH FIRST 1 ROWS ONLY;"
        },
        {
            "question": "Please tell me the total verified value of EPP Invoices of Engro",
            "sql": "SELECT SUM(TOTAL_VERIFIED_VALUE) AS TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly')) AND (UPPER(IPP_NAME) LIKE '%ENGRO%' OR LOWER(IPP_NAME) LIKE '%engro%');"
        },
        {
            "question": "Show all verified EPP invoices for Coal IPPs",
            "sql": "SELECT IPP_NAME, INVOICE_NO, BILLING_MONTH, INV_CATEGORY, TOTAL_CLAIMED_VALUE, TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly'));"
        },
        {
            "question": "Show total verified value by IPP vendor for EPP Coal invoices",
            "sql": "SELECT IPP_NAME, SUM(TOTAL_VERIFIED_VALUE) AS TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly')) GROUP BY IPP_NAME ORDER BY TOTAL_VERIFIED_VALUE DESC;"
        }
    ],
}


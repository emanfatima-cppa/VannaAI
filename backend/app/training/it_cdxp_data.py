"""app/training/it_cdxp_data.py – Q&A pairs and documentation for CDXP instance."""

IT_CDXP_TRAINING: dict = {
    "documentation": [

        # ── Core Domain Overview ──────────────────────────────────────────────
        """
        This is CDXP (CPPA Data Exchange Portal) — an Invoice Management System
        used by CPPA (Central Power Purchasing Agency) to manage power invoices
        submitted by IPPs (Independent Power Producers / suppliers).

        Invoice Types:
        - Monthly   : standard monthly power purchase invoice
        - Differential : raised when there is a revision or difference in a previously settled claim
        - Interest  : raised when payment delays trigger interest charges against CPPA

        Invoice Lifecycle:
        IPP submits invoice → CPPA Technical team reviews → CPPA Finance team reviews
        → If accepted: Services team sends it to ERP for payment
        → Payment (full or partial) is synced back to CDXP
        → If rejected: invoice is returned to supplier for resubmission
        → If claim changes after ERP acceptance: supplier creates a NEW invoice (not resubmit)

        Invoice Hierarchy:
        Supplier → Diary (Header) → Blocks → Components → Attachments

        Invoice Status Values (APPROVED_STATUS):
        - Draft      : created but not yet submitted by supplier
        - Submitted  : supplier has submitted for CPPA review
        - Received   : CPPA has formally accepted the invoice for processing
        - Returned   : CPPA has returned invoice to supplier for corrections
        - Deleted    : invoice has been deleted
        - Withdraw   : supplier has withdrawn the invoice
        """,

        # ── Table: CPPA_CA.DIARY_HEADER_INTERFACE ────────────────────────────
        """
        CPPA_CA.DIARY_HEADER_INTERFACE — Master Invoice Table (also called diary, invoice header).
        This is the top-level table. Every invoice (monthly, differential, interest) has
        one record here. It holds the overall overview: who submitted it, when, what was
        claimed, and what the current status is.

        Synonyms: invoice, diary, header, claim, bill


        IMPORTANT:
        - Use TOTAL_CLAIM for claim-related queries
        - Use VERIFIED_AMOUNT for verified/approved amount queries
        - For latest invoice: ORDER BY SUBMIT_DATE DESC
        - Always go DIARY → BLOCK → COMPONENT. Never join COMPONENT directly with DIARY.
        """,

        # ── Table: CPPA_CA.BLOCKS_HEADER_INTERFACE ───────────────────────────
        """
        CPPA_CA.BLOCKS_HEADER_INTERFACE — Block Table for Monthly Invoices.
        A block represents a fuel type within a Monthly invoice. Each monthly invoice
        can have one or more blocks, one per applicable fuel type.

        Synonyms: block, fuel block, fuel type

        This table is ONLY for Monthly invoices.
        For Differential and Interest invoices use WP_GC_INV_DIFF_PARENT.


        """,

        # ── Table: CPPA_CA.COMP_HEADER_INTERFACE ─────────────────────────────
        """
        CPPA_CA.COMP_HEADER_INTERFACE — Component Table for Monthly Invoices.
        Each block (fuel type) in a Monthly invoice is further broken down into
        chargeable components (e.g. Capacity Payment, Variable O&M, Fuel Cost).
        This table holds each component's name, value, and verification status.

        Synonyms: component, fuel component, price, charge, line item

        This table is ONLY for Monthly invoices.
        For Differential and Interest invoices use WP_GC_INTEREST_DETAIL.


        """,

        # ── Table: WP_GC_INV_DIFF_PARENT ─────────────────────────────────────
        """
        WP_GC_INV_DIFF_PARENT — Block Table for Differential and Interest Invoices.
        This table plays the same role as BLOCKS_HEADER_INTERFACE but for
        Differential and Interest invoice types. Each record is a fuel/block entry
        within a Differential or Interest invoice.

        Synonyms: differential block, interest block, diff parent, fuel block (for differential/interest)


        """,

        # ── Table: CPPA_CA.WP_GC_INTEREST_DETAIL ─────────────────────────────
        """
        CPPA_CA.WP_GC_INTEREST_DETAIL — Component Table for Differential and Interest Invoices.
        This table plays the same role as COMP_HEADER_INTERFACE but for Differential and
        Interest invoice types.
        - For Interest invoices: stores payment schedule details used to calculate interest charges.
        - For Differential invoices: stores the component-by-component breakdown of the differential claim.

        Synonyms: interest detail, differential component, interest component


        """,

        # ── Table: CPPA_CA.ATTACHMENT_HEADER ─────────────────────────────────
        """
        CPPA_CA.ATTACHMENT_HEADER — Attachments for All Invoice Types.
        Stores all file attachments uploaded against invoices — across Monthly,
        Differential, and Interest invoice types. Attachments can be structured
        (Excel, Word) or unstructured (PDF, images).

        Synonyms: attachment, file, document, upload


        """,

        # ── Table: dbo.DISPUTE_ATTACHMENTS ───────────────────────────────────
        """
        dbo.DISPUTE_ATTACHMENTS — Attachments for Invoice Disputes.
        When an invoice is returned from ERP due to a claim discrepancy and the
        supplier raises a dispute or creates a revised invoice, CPPA uploads
        dispute-related documents here. These are separate from regular invoice
        attachments in ATTACHMENT_HEADER.

        Synonyms: dispute attachment, dispute file, dispute document

        """,

        # ── Table: CPPA_CA.WP_GC_ERP_INVOICES ───────────────────────────────
        """
        CPPA_CA.WP_GC_ERP_INVOICES — ERP Invoice Sync Table.
        Stores ERP-side invoice records synced back to CDXP after payment processing.
        Once an invoice is paid (fully or partially) in ERP, the payment details are
        written here so CDXP has an up-to-date view of paid amounts and outstanding balances.

        Synonyms: ERP invoice, paid invoice, payment record, erp sync


        """,

        # ── PPA Tables ────────────────────────────────────────────────────────
        """
        PPA (Power Purchase Agreement) Tables.
        PPA tables store the master agreement and rate definitions that govern
        how invoices are structured, calculated, and validated.
        Invoice components and blocks are always traced back to PPA definitions.

        Synonyms: agreement, ppa, contract, power agreement
        """,

        # ── Table: CPPA_CA.PPA_HEADER ─────────────────────────────────────────
        """
        CPPA_CA.PPA_HEADER — Master PPA Table.
        Each record is a Power Purchase Agreement between CPPA and one IPP/supplier.
        Stores overall agreement details, contracted capacity, COD dates, and approval status.

        """,

        # ── Table: CPPA_CA.PPA_BLOCKS_FUELS ──────────────────────────────────
        """
        CPPA_CA.PPA_BLOCKS_FUELS — Fuel Types / Blocks defined in a PPA.
        Each PPA can have multiple fuel types (e.g. EPP, CPP, and others).
        Blocks in invoices reference this table for their fuel type definition.

        Synonyms: ppa block, fuel type, ppa fuel, block definition

        """,

        # ── Table: CPPA_CA.PPA_COMP_DEFS ─────────────────────────────────────
        """
        CPPA_CA.PPA_COMP_DEFS — Component Definitions for PPA Blocks.
        Defines chargeable components for each block/fuel type in a PPA.
        These definitions serve as the template for what components appear on invoices
        and at what rates (e.g. Capacity Payment, Variable O&M, Fuel Cost).

        Synonyms: component definition, ppa component, rate, ppa rate

        """,

        # ── Table: CPPA_CA.PPA_APPLICABLE_INVOICES ───────────────────────────
        """
        CPPA_CA.PPA_APPLICABLE_INVOICES — Invoice Type Configuration per PPA.
        Defines which invoice types and configurations are applicable under each PPA.
        Acts as a configuration table controlling invoice categorization and payment settings.

        Synonyms: applicable invoice, invoice config, invoice type config

        """,

        # ── Supplier Tables ───────────────────────────────────────────────────
        """
        Supplier Tables.
        Suppliers are the IPPs (Independent Power Producers) who submit invoices to CPPA.
        Synonyms: supplier, vendor, ipp, company
        """,

        # ── Table: CPPA_CA.AP_SUPPLIERS ──────────────────────────────────────
        """
        CPPA_CA.AP_SUPPLIERS — Master Supplier / Vendor Table.
        Stores all registered suppliers (IPPs) that can submit invoices to CPPA.
        VENDOR_ID is the primary key used across all invoice tables to identify the supplier.

        Synonyms: supplier, vendor, ipp, company

        """,

        # ── Table: CPPA_CA.APP_SUPPLIER_SITE_ALL ─────────────────────────────
        """
        CPPA_CA.APP_SUPPLIER_SITE_ALL — Supplier Site Table.
        Stores individual supplier sites (sub-units / plants) for each supplier.
        A single IPP may operate multiple power plants or have multiple payment sites,
        each registered as a separate supplier site. When submitting an invoice, both
        VENDOR_ID and VENDOR_SITE_ID are specified. Site options appear in dropdowns
        when a supplier logs in.

        Synonyms: supplier site, vendor site, plant site, ipp site

        """,

        # ── User Tables ───────────────────────────────────────────────────────

        # ── Table: CPPA_CA.ApiUsers ───────────────────────────────────────────
        """
        CPPA_CA.ApiUsers — User Login and Profile Table.
        Stores login credentials and profile information for all CDXP portal users.
        Includes supplier representatives (IPP users), CPPA staff, and department heads.
        Each user is linked to a PPA to control what data they can access.

        Synonyms: user, login, portal user, staff, employee

        """,

        # ── Table: dbo.WP_GC_USER_ACCESS ─────────────────────────────────────
        """
        dbo.WP_GC_USER_ACCESS — User Access Rights Table.
        Defines granular access rights for each user across the system.
        Controls which entities a user can view, create, edit, or delete.
        Also maps users to specific vendors/sites so supplier users only see their own data.

        Synonyms: user access, user rights, user permissions, access control

        """,

        # ── Key Relationships ─────────────────────────────────────────────────
        """
        Key Table Relationships for CDXP:

        Supplier to Invoice:
        - AP_SUPPLIERS → DIARY_HEADER_INTERFACE (via VENDOR_ID)
        - APP_SUPPLIER_SITE_ALL → DIARY_HEADER_INTERFACE (via VENDOR_SITE_ID)

        Invoice Hierarchy (Monthly):
        - DIARY_HEADER_INTERFACE → BLOCKS_HEADER_INTERFACE (via DIARY_HEADER_ID)
        - BLOCKS_HEADER_INTERFACE → COMP_HEADER_INTERFACE (via BLOCK_HEADER_ID)

        Invoice Hierarchy (Differential & Interest):
        - DIARY_HEADER_INTERFACE → WP_GC_INV_DIFF_PARENT (via DIARY_HEADER_ID_FK)
        - WP_GC_INV_DIFF_PARENT → WP_GC_INTEREST_DETAIL (via DIFF_PAR_ID_FK)

        Attachments:
        - DIARY_HEADER_INTERFACE → ATTACHMENT_HEADER (via DIARY_HEADER_ID)
        - WP_GC_ERP_INVOICES → DISPUTE_ATTACHMENTS (via AP_INVOICE_ID)

        PPA Linkage:
        - PPA_HEADER → PPA_BLOCKS_FUELS (via HEADER_ID_FK)
        - PPA_BLOCKS_FUELS → PPA_COMP_DEFS (via BLK_FUEL_ID_FK)
        - PPA_HEADER → PPA_APPLICABLE_INVOICES (via HEADER_ID_FK)
        - PPA_HEADER → DIARY_HEADER_INTERFACE (via PPA_HEADER_ID)

        ERP Sync:
        - DIARY_HEADER_INTERFACE → WP_GC_ERP_INVOICES (via TRANSACTION_NO / DIARY_NO)

        User Access:
        - ApiUsers → WP_GC_USER_ACCESS (via UserId)
        - ApiUsers → PPA_HEADER (via PPA_HEADER_ID_FK)
        - WP_GC_USER_ACCESS → AP_SUPPLIERS (via VENDOR_ID)

        IMPORTANT — Never join COMP_HEADER_INTERFACE directly with DIARY_HEADER_INTERFACE.
        Always go: DIARY → BLOCK → COMPONENT.
        Same rule applies for Differential/Interest:
        DIARY → WP_GC_INV_DIFF_PARENT → WP_GC_INTEREST_DETAIL.
        """,

        # ── Query Rules ───────────────────────────────────────────────────────
        """
        Query Rules for CDXP:

        • Use TOTAL_CLAIM for claim/claimed amount queries
        • Use VERIFIED_AMOUNT for verified/approved amount queries
        • For latest invoice: ORDER BY SUBMIT_DATE DESC
        • For invoice status: filter APPROVED_STATUS column in DIARY_HEADER_INTERFACE
        • Note: COMP_HEADER_INTERFACE has a typo — column is VARIFIED_AMOUNT not VERIFIED_AMOUNT
        • Note: WP_GC_INTEREST_DETAIL has a typo — column is FULE_TYPE not FUEL_TYPE
        • Always use proper JOIN paths. Never skip levels in the hierarchy.
        • For attachment queries: join ATTACHMENT_HEADER on DIARY_HEADER_ID
        • For dispute attachment queries: join DISPUTE_ATTACHMENTS on AP_INVOICE_ID
        """,
    ],
    "qa_pairs": [],
}

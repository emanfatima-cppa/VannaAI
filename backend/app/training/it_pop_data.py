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
        - Fuel Type Filter: Extract ONLY standalone Coal fuel type (FUEL_TYPE = 'Coal'). Do NOT include hybrid fuel types like Coal and Bagasse in any case.
        - Invoice Type Filter: Extract ONLY EPP invoice type (INV_TYPE / INVOICE_TYPE = 'EPP').
        - Invoice Category Filter: Extract ONLY Monthly and Hourly invoices (INV_CATEGORY IN ('Monthly', 'Hourly')) ONLY if the target table contains the INV_CATEGORY column. If the table does not have INV_CATEGORY column, omit this filter.


        """,

        # ── Table: CPPA_IPPS_INFORMATION_T ───────────────────────────────────
        """
        CPPA_IPPS_INFORMATION_T — Independent Power Producers (IPPs / Vendors / Suppliers) Master Table.
        Primary master table containing operational details, and contractual parameters of 
        Independent Power Producers (IPPs) and vendor plant sites. Extract and filter ONLY IPP info for Coal fuel type (FUEL_TYPE = 'Coal'), 
        EPP invoice type, and Monthly and Hourly form/invoice. Contains information for fuel types, 
        power policy agreements, COD dates, financial close dates, spread rates, PPA terms, elapsed tenure (past years, months, days), and remaining tenure (left years, months, days).

        Synonyms for IPP: ipp, vendor, supplier, power producer, seller, company, plant, site

        Key columns:
        - VENDOR_NAME            : Name of the IPP / power generation vendor company / supplier name / project name / plant name
        - VENDOR_SITE            : Vendor site / power plant ID 
        - VENDOR_SITE_ADDRESS    : Physical address of the vendor site
        - FUEL_TYPE / REPORT_FUEL_TYPE : Primary fuel type (Coal) 
        - POWER_POLICY           : Applicable government power policy (GENCOS, GOP Project, Energy 2015)
        - CONTRACTED_CAPACITY    : Contracted power generation capacity (MW)
        - DEPENDABLE_CAPACITY    : Tested dependable power generation capacity (MW)
        - PPA_DATE               : Power Purchase Agreement signing date
        - PPA_TERM               : Total tenure / term of the PPA agreement (years)
        - FINANCIAL_CLOSE_DATE   : Financial closing date
        - REQUIRED_COD / ACTUAL_COD : Required and actual Commercial Operation Dates (COD)
        - EFFECTIVE_FROM / EFFECTIVE_TO : Agreement effective start and end dates
        - END_OF_AGREEMENT       : Expiration date of the PPA agreement
        - PAST_YRS / PAST_MNTHS / PAST_DYS : Tenure elapsed since agreement start (Years, Months, Days)
        - LEFT_YRS / LEFT_MNTHS / LEFT_DYS : Tenure remaining until agreement expiry (Years, Months, Days)
        - SPREAD_RATE            : Applicable interest/tariff spread rate
        - MANUAL_DIARY           : Flag for manual diary entry allowance
        - LAST_UPDATE_DATE       : Timestamp of last record update
        """,

        # ── Table: CPPA_POP_PPA_DATA_ALL_T ───────────────────────────────────
        """
        CPPA_POP_PPA_DATA_ALL_T — Master Table for Power Purchase Agreements (PPA).
        This table contains comprehensive master data for Power Purchase Agreements (PPA) agreed between CPPA and Independent Power Producers (IPPs). 
        Extract ONLY PPA data for Coal fuel type (FUEL_TYPE = 'Coal'), EPP invoice type (INVOICE_TYPE = 'EPP'). It holds contract terms, policy descriptions,
        capacity limits (Contracted & Dependable MW), agreement dates, effective periods, invoice type rules, interest rate calculations, block structures, fuel types, tariff components (component names, types, values, formulas, units), and diary/invoice display flags.

        Key columns:
        - PPA_NO                 : PPA contract / agreement number
        - IPP_NAME               : Name of the IPP vendor / power producer
        - IPP_SITE               : Vendor plant site location
        - POWER_POLICY / POWER_POLICY_DESC : Applicable power policy (Policy 2002, 2015, etc.) and description
        - CONTRACTED_CAPACITY    : Contracted power generation capacity (MW)
        - DEPENDABLE_CAPACITY    : Tested dependable power generation capacity (MW)
        - PPA_TERM               : Total tenure / duration of the PPA agreement (years)
        - AGREEMENT_DATE         : PPA agreement signing date
        - FINANCIAL_CLOSE_DATE   : Financial closing date
        - REQUIRED_COD           : Required Commercial Operation Date (COD)
        - PPA_EFFECTIVE_FROM / PPA_EFFECTIVE_TO : PPA contract effective start and end dates
        - INVOICE_TYPE           : Associated PPA invoice type (Filter: 'EPP')
        - IS_HOURLY              : Flag indicating hourly invoice billing (Filter: Monthly & Hourly)
        - ADVANCE_PAYMENT        : Advance payment terms indicator
        - INT_RATE_TYPE / INT_CALC_FIXED_DAYS : Interest rate type and calculation fixed days
        - BLOCK_NO / FUEL_TYPE   : PPA block number and fuel type (Filter: 'Coal')
        - COMP_TYPE / COMP_NAME / COMP_VALUE / UNIT : Tariff component type, name, value, and measurement unit
        - FORMULA                : Tariff / component calculation formula
        - SHOW_ON_DIARY / SHOW_ON_INV : Display visibility flags for diary and invoice
        - IS_DISABLE             : Status flag indicating if PPA record/component is disabled
        """,

        # ── Table: CPPA_NOT_VERIFIED_ALERT_T ────────────────────────────────
        """
        CPPA_NOT_VERIFIED_ALERT_T — Table for Unverified/Incomplete/Inprocess & Pending Invoices.
        This table contains information about all invoices that are not verified yet. Extract and query ONLY for Coal fuel IPPs, 
        EPP invoice type (INV_TYPE = 'EPP'), and Monthly & Hourly invoices. Whenever a user asks about unverified invoices, not verified items, pending invoices, pending days, query from this table. It tracks pending invoice details, received invoice amounts, pending days, current desk/personnel location (ON_DESK), and complete approval workflow status ('Diary Approved', 'Diary Incomplete', 'Invoice Inprocess', 'Invoice Incomplete', 'Invoice', 'Invoice Reject').


        Synonyms for unverified invoices: not verified, unverified alert, pending invoice, inprocess invoice

        Key columns:
        - IPP_NAME               : Name of the IPP / Vendor
        - IPP_SITE               : IPP plant site location
        - INV_TYPE               : Type of invoice submitted (Filter: 'EPP')
        - DIARY_NO / DIARY_HEADER_ID : CPPA diary tracking number and header ID
        - INVOICE_NO             : Submitted invoice number
        - REC_INV_AMOUNT         : Total received invoice amount claimed by IPP
        - RECEIVING_DATE         : Date invoice was physically received at CPPA
        - INV_DUE_DATE           : Due date for invoice payment
        - PENDING_DAYS           : Total number of days invoice has been pending verification
        - APPROVAL_STATUS        : Approval status ('Diary Approved', 'Diary Incomplete', 'Invoice Inprocess', 'Invoice Incomplete', 'Invoice', 'Invoice Reject')
        - ON_DESK                : Name of the officer / personnel currently holding the invoice file on their desk (e.g., 'Mr. Asfandyar Shakeel', 'Hamdan Wazir')
        - FORM_NAME / EVENT_STATUS : Approval form name and workflow event status
        - INITIATOR / INITIATOR_EMAIL : Name and email of the officer who initiated processing
        - MANAGER_NAME / MANAGER_EMAIL : Name and email of the reviewing manager
        - DGM_NAME / DGM_EMAIL   : Name and email of Deputy General Manager overseeing approval
        - LAST_UPDATE_DATE       : Timestamp of last record update
        """,

        # ── Table: CPPA_POP_VERIFIED_DATA_ALL_T ─────────────────────────────
        """
        CPPA_POP_VERIFIED_DATA_ALL_T — Table for Fully Verified & Approved Invoices.
        Primary table to query whenever asking about total verified values, approved invoice totals, or complete verified invoice details. 
        Extract ONLY data for Coal fuel type (FUEL_TYPE = 'Coal'), EPP invoice type (INV_TYPE = 'EPP'), and Monthly & Hourly FORM/INVOICE. 
        Contains comprehensive information regarding all approved invoices across all hierarchy levels (Plant ➔ Site ➔ Fuel ➔ Invoice Type ➔ Block ➔ Component level). Includes standard invoice components stored in LEV_COMP (e.g., 'VO&M Rate', 'FCC Rate', 'Fuel Price', 'Dependable Capacity (MW)', 'VO&M Amount', 'FCC Amount', 'NEO (kWh)', etc.).

        Synonyms for verified invoices: verified invoice, approved invoice, verified amount

        Key columns:
        - LEV_TYPE / LEV_BLOCK_FULE / LEV_COMP : Level classification, block fuel level, and component name
        - COMP_FROM              : Source of component calculation
        - IPP_NAME               : Name of the IPP vendor
        - IPP_SITE               : Vendor plant site location
        - IPP_EMAIL / IPP_ADDRESS: IPP email and address details
        - POWER_POLICY / POWER_POLICY_DESC : Power policy code and description
        - INV_TYPE / INV_SUB_TYPE / INV_CATEGORY : Invoice type (Filter: 'EPP'), sub-type, and category
        - ADVANCE_PAYMENT        : Advance payment indicator
        - DIARY_NO               : Internal CPPA diary tracking number
        - IPP_INV_NO / INVOICE_NO: IPP invoice number / CPPA internal invoice number
        - INV_RECEIVED_DATE      : Date invoice was received at CPPA
        - INV_PERIOD_FRM / INV_PERIOD_TO : Invoice billing period start and end dates
        - BILLING_MONTH          : Billing month (e.g. MAY-2026)
        - INV_CATEGORY           : 'Monthly' or 'Hourly'
        - FINAL_DUE_DATE         : Final due date for payment
        - APPROVAL_STATUS        : Approval status (Only approved invoices)
        - TRANSFER_TO_AP         : Indicator if invoice has been transferred to Accounts Payable
        - TOTAL_CLAIMED_VALUE    : Total invoice amount claimed by IPP
        - TOTAL_VERIFIED_VALUE   : Main column for Total Verified Value / Approved Invoice Amount
        - TOTAL_DIFFERENCE_VALUE : Difference between total claimed and verified amounts
        - AP_INVOICE_VALUE       : Accounts Payable (AP) invoice entry amount
        - AP_PAYMENT_VALUE       : Actual amount paid to vendor via AP
        - PAYED_TO_VENDOR_ID / PAYED_TO_VENDOR_SITE_ID : Vendor payment details
        - PRE_POST / PARENT_INV_NO / MAIN_INV_NO / MAIN_INV_TOTAL_AMOUNT : Parent and main invoice reference and totals
        - DIARY_BLOCK_LEVEL_ID / PPA_BLOCK_ID : Block level identifiers
        
        """,
    ],
    # "qa_pairs": [
    #     {
    #         "question": "Please tell me the total verified value of EPP Invoices of Engro",
    #         "sql": "SELECT SUM(TOTAL_VERIFIED_VALUE) AS TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly')) AND (UPPER(IPP_NAME) LIKE '%ENGRO%' OR LOWER(IPP_NAME) LIKE '%engro%');"
    #     },
    #     {
    #         "question": "Show all verified EPP invoices for Coal IPPs",
    #         "sql": "SELECT IPP_NAME, INVOICE_NO, BILLING_MONTH, INV_CATEGORY, TOTAL_CLAIMED_VALUE, TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly'));"
    #     },
    #     {
    #         "question": "Show total verified value by IPP vendor for EPP Coal invoices",
    #         "sql": "SELECT IPP_NAME, SUM(TOTAL_VERIFIED_VALUE) AS TOTAL_VERIFIED_VALUE FROM CPPA_POP_VERIFIED_DATA_ALL_T WHERE (UPPER(FUEL_TYPE) = 'COAL' OR LOWER(FUEL_TYPE) = 'coal' OR FUEL_TYPE = 'Coal') AND (UPPER(INV_TYPE) = 'EPP' OR LOWER(INV_TYPE) = 'epp' OR INV_TYPE = 'EPP') AND (UPPER(INV_CATEGORY) IN ('MONTHLY', 'HOURLY') OR LOWER(INV_CATEGORY) IN ('monthly', 'hourly') OR INV_CATEGORY IN ('Monthly', 'Hourly')) GROUP BY IPP_NAME ORDER BY TOTAL_VERIFIED_VALUE DESC;"
    #     }
    # ],
}


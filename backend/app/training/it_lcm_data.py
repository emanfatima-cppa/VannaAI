"""app/training/it_lcm_data.py – Q&A pairs and documentation strictly for LCM (Legal Case Management) instance."""

IT_LCM_TRAINING: dict = {
    "documentation": [

        # ── Core Domain Overview ──────────────────────────────────────────────
        """
        LCM (Legal Case Management System) manages legal cases — a "case"
        (matter, litigation, suit) is the central record.
        • Petitioner (applicant, plaintiff) – files the case.
        • Respondent (defendant) – the party the case is filed against.
        • Cases are Domestic or International.
        • Cases move through statuses (Pending, Decided, Dismissed, etc.),
          tracked at status and sub-status level.
        """,

        # ── Case Types & Classification ─────────────────────────────────────
        """
        Case Type / Classification:
        • Case Classification – e.g. Strategic, Non-contested, Per-forma (from Lookups).
        • Financial Implications – whether money is involved in the case.
        • Forum – the court/forum hearing the case, e.g. NEPRA Appellate
          Tribunal, Islamabad High Court, London Court of International
          Arbitration (from Lookups).
        • Case Value – recorded when the case involves a monetary claim.
        • Linked Cases – other related cases can be referenced.
        • Related Lower Court Cases – reference to a prior lower-court case
          on the same matter, if any.
        """,

        # ── SETTINGS: Participant Details ───────────────────────────────────
        """
        Settings → Participant Details:
        Master list of people/entities used as Petitioners and Respondents
        across cases, with an Enable/Disable status to control availability.
        """,

        # ── SETTINGS: Schedule of Fees ──────────────────────────────────────
        """
        Settings → Schedule of Fees:
        Fee structures approved via a Board Resolution. Each record covers a
        Forum and its applicable fees (e.g. court fee, mediation fee), can
        have attachments, and goes through a workflow from created to
        Reviewed status.
        """,

        # ── SETTINGS: Advocates ──────────────────────────────────────────────
        """
        Settings → Advocates:
        Master list of advocates/lawyers available for engagement on cases
        (identified by EERP Supplier No., NTN, enrollment, place of
        practice, with an Enable/Disable status). Advocate fee details are
        maintained against each advocate and used when assigning legal
        counsel to a case.
        """,


        # ── DASHBOARD ─────────────────────────────────────────────────────────
        """
        Dashboard:
        Case-wise overview showing Case Number, Case Name, Initiation Date,
        Upcoming Hearing, Forum Name, Case Classification, Financial
        Implications, and Case Status, with an option to export to Excel.
        Also shows summary counters: Total Cases, Pending Cases, Pending for
        Review, Decided Cases, and Upcoming Hearing(s).
        """,

        # ── CASE CREATION – Overview ─────────────────────────────────────────
        """
        Case Creation Workflow:
        A new case is created in 5 steps: Step 1 – Case Details, Step 2 –
        Legal Counsel, Step 3 – Case Fee Details, Step 4 – Hearing Data,
        Step 5 – Case Status.
        """,

        # ── CASE CREATION – Step 1: Case Details ────────────────────────────
        """
        Case Creation → Step 1: Case Details.
        Captures: Case Type, Case Number, Initiation Date, Forum Name, Case
        Value, Linked Cases, Related Lower Court Cases, Case Description,
        Petitioner, Case Officer (supervises the case), Respondent, and
        Attachments.
        """,

        # ── CASE CREATION – Step 2: Legal Counsel ───────────────────────────
        """
        Case Creation → Step 2: Legal Counsel.
        Table of advocates assigned to the case — Advocate Type,
        Advocate/Firm Name, Engagement No., Remarks — plus attachments.
        """,

        # ── CASE CREATION – Step 3: Case Fee Details ────────────────────────
        """
        Case Creation → Step 3: Case Fee Details.
        Table of case fees — Case Fee Type, Engagement No., Additional Fee
        Type, Amount.
        """,

        # ── CASE CREATION – Step 4: Hearing Data ────────────────────────────
        """
        Case Creation → Step 4: Hearing Data.
        Hearing history for the case — Hearing Date, Remarks — plus
        attachments if any.
        """,

        # ── CASE CREATION – Step 5: Case Status ─────────────────────────────
        """
        Case Creation → Step 5: Case Status.
        Current status of the case — Status (e.g. Pending, Completed),
        Sub Status (e.g. Final Argument), Remarks — plus attachments if any.
        """,

        # ── EXECUTIVE VIEW ────────────────────────────────────────────────────
        """
        Executive View:
        Consolidated view for analysis across all cases — users with access
        can filter and drill into case data spanning Settings, Setup,
        Dashboard, and all 5 case-creation steps.
        """,
        # Case category ------
        """
        Case Category:
        Cases are Domestic case or International Arbitration. The data is stored in table [MtCaseHeader] in column [MtCaseHeader_CaseCategory]
        """,

        # ── Lookup Reference Table ────────────────────────────────────────
        """
        [LCM].[LuCPPA_LCM_LOOKUP_V] — master lookup table used across the
        system for reference values and their descriptions.
        • LOOKUP_TYPE / LOOKUP_TYPE_MEANING – the category of lookup, e.g.
          Advocate Type, Case Status, Case Fee Type, Case Classification,
          Case Type, Forum.
        • LOOKUP_VALUE_CODE / LOOKUP_VALUE_MEANING / LOOKUP_VALUE_DESC –
          the actual value under that category and its description.
        • Examples by type:
          - Advocate Type → Advocate, Attorney, Journal.
          - Case Fee Type → Scheduled Fee, Special Fee, Additional Fee.
          - Case Status → Pending, Decided, etc.
          - Case Sub Status → further detail like Withdrawn, Stayed,
            Against CPPA.
          - Case Type → Intra Court Appeal, Execution Petition, Criminal
            Original, Constitutional Petition.
          - Case Classification → Non-contested Matter, Reputational,
            Strategic.
          - Forum → e.g. Islamabad High Court (Domestic Cases), London
            Court of International Arbitration (International
            Arbitration), Federal Constitutional Court Pakistan (Domestic
            Cases).
        • LOOKUP_VALUE_ENABLED_FLAG shows if a value is active.
        • LOOKUP_VALUE_EFF_FROM / EFF_TO give the validity period of a
          value.
        • Note: these are sample/illustrative values only — actual data
          in the table may contain additional types and values not
          listed here.
        """,

        # ── User Setup (Header) ───────────────────────────────────────────
        """
        [LCM].[RuUserSettingHeader] — stores details of users created in
        the system.
        • Holds user's name, email, and a system-generated user code
          (UserCode) created upon adding a new user.
        • CreatedBy / CreatedDate – who created the user and when.
        • ModifiedBy / ModifiedDate – who last updated the user and when.
        • EffectiveFrom / EffectiveTo – validity period of the user
          record.
        • isDisabled – 0 = enabled, 1 = disabled.
        • IsAdmin – flags whether the user has admin rights.
        """,

        # ── User Setup (Permissions/Details) ──────────────────────────────
        """
        [LCM].[RuUserSettingDetails] — stores permission/menu assignments
        given to a user at the time of user creation (Add User process).
        • RuUserSettingHeader_UserCode – links to the user in
          RuUserSettingHeader.
        • RuRoleDefinition_Code – the permission/role granted, e.g. Edit,
          View, Review.
        • RuMenu_MenuCode – the menu/module the permission applies to,
          e.g. 'ADV_DET'(advocate details), 'SETTINGS', 'USR_DSH'(user dashboard), 'EXEC_DSH'(executive dashboard).
        • CreatedBy / CreatedDate, ModifiedBy / ModifiedDate – audit of
          who assigned/changed the setting and when.
        • isDisabled – whether this permission/menu assignment is active.
        """,

        # ── Approval Workflow ──────────────────────────────────────────────
        """
        [LCM].[MtApprovalWorkflow] — activity/approval log table.
        • RuMenu_MenuCode indicates the context of the approval:
          - 'USR-DSH' → approval related to a Case (User Dashboard).
          - 'SETTINGS' → approval related to a Board Resolution.
        • MtApprovalWorkflow_SourceId – reference id of the source record
          being approved.
        • MtApprovalWorkflow_UserCode / RuRoleDefinition_Code – the user
          and their role involved in the approval step.
        • MtApprovalWorkflow_ReviewerSequence – order of the reviewer in
          the approval chain.
        • MtApprovalWorkflow_ActionDate / ApprovalCode / Remarks – when
          the action was taken, its approval code should be these values : 'Draft', 'Pending for review', 'Pending for reviewer 1', 'Pending for reviewer 2', 'Reviewed', 'Returned for review', and any remarks.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        """,

        # ── Audit Logs ──────────────────────────────────────────────────────
        """
        [LCM].[MtAuditLogs] — stores audit/activity information for user
        actions across the system.
        • Captures which user performed an action.
        • Records the menu and sub-menu where the action occurred.
        • Captures the type/event of the action and its description.
        """,

        # ── Lawyer / Advocate Details ────────────────────────────────────────
        """
        [LCM].[RuLawyerDetails] — stores information about lawyers /
        advocates.
        • Routing rule: when the user asks for lawyer info, check this
          table; if a case number is also given, cross-check with
          [LCM].[MtCaseAdvocates] instead.
        • Key fields: LawyerName, Address, City, ContactNo, NTN,
          Enrollment, EmailAddress.
        • RuLawyerDetails_ERPSupllierNo – linked ERP supplier number.
        • isActive – 1 = active/enabled, 0 = disabled.
        • ImportDate / LastUpdateDate / LastUpdatedBy – tracks when the
          lawyer record was imported and last updated, and by whom.
        """,

        # ── Schedule of Charges (Header) ─────────────────────────────────────
        """
        [LCM].[MtScheduleOfChargesHeader] — overall/summary information
        about a schedule of charges.
        • BoardResolutionNo / BoardResolutionDate – the board resolution
          authorizing this charge schedule.
        • Status – current status of the schedule.
        • EffectiveFrom / EffectiveTo – validity period of the schedule.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • isDisabled – whether this schedule header is active.
        """,

        # ── Schedule of Charges (Details) ────────────────────────────────────
        """
        [LCM].[MtScheduleOfChargesDetails] — detailed fee information
        created during the "Add Schedule Fee" process.
        • MtScheduleOfChargesHeader_id – links to the parent schedule in
          MtScheduleOfChargesHeader.
        • ForumCode – the court/forum the fee applies to.
        • Description – description of the charge/fee line.
        • ScheduleFee – the fee amount for that forum.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – who created/
          modified the fee entry and when.
        • isDisabled – whether this fee line is active.
        """,

        # ── Participant Details ──────────────────────────────────────────────
        """
        [LCM].[RuParticipantDetails] — stores information about
        participants (parties/persons involved) and who created them.
        • Code / Name / Description – participant identity details.
        • Email, Address, ContactNo – participant contact information.
        • EffectiveFrom / EffectiveTo – validity period of the
          participant record.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • isDisabled – whether the participant record is active.
        """,

        # ── Case Header ───────────────────────────────────────────────────
        """
        [LCM].[MtCaseHeader] — core table holding the main details of a
        case.
        • CaseType, CaseNumber, ForumName – identifies the case and
          where it is being heard.
        • InitiationDate – date the case was initiated.
        • CaseCategory – 2 types: Domestic Case and International
          Arbitration.
        • CaseValue – monetary value involved in the case, if any.
        • CaseDescription – free text description of the case.
        • AdvocateOnRecord – flag indicating if an advocate on record is
          assigned.
        • Status / WorkFlowStatus – current status and workflow stage of
          the case.
        • IsDeleted – whether the case record is deleted.
        • ERPTransferCheck – whether the case has been transferred to
          ERP.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        """,

        # ── Case Classification ──────────────────────────────────────────────
        """
        [LCM].[MtCaseClassification] — stores the classification value
        assigned to a case.
        • MtCaseHeader_id – links to the case in MtCaseHeader.
        • MtCaseClassification_Value – the classification value, e.g.
          Strategic, Non-contested Matter, Reputational (from Lookups).
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – who
          created/modified the classification and when.
        • IsDeleted – whether this classification record is deleted.
        """,

        # ── Case Petitioner ───────────────────────────────────────────────────
        """
        [LCM].[MtCasePetitioner] — links petitioners to a case.
        • Routing rule: for petitioner info alone, check
          [LCM].[RuParticipantDetails]; for petitioner info tied to a
          specific case, check [LCM].[MtCasePetitioner].
        • MtCaseHeader_id – the case this petitioner is linked to.
        • RuParticipantDetails_id – links to the petitioner's details in
          RuParticipantDetails.
        • EffectiveFrom / EffectiveTo – validity period of this link.
        • Remarks – any remarks about the petitioner in this case.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • IsDeleted – whether this record is deleted.
        """,

        # ── Case Respondent ───────────────────────────────────────────────────
        """
        [LCM].[MtCaseRespondent] — links respondents to a case.
        • Routing rule: for respondent info alone, check
          [LCM].[RuParticipantDetails]; for respondent info tied to a
          specific case, check [LCM].[MtCaseRespondent].
        • MtCaseHeader_id – the case this respondent is linked to.
        • RuParticipantDetails_id – links to the respondent's details in
          RuParticipantDetails.
        • EffectiveFrom / EffectiveTo – validity period of this link.
        • Remarks – any remarks about the respondent in this case.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • IsDeleted – whether this record is deleted.
        """,

        # ── Case Officer ───────────────────────────────────────────────────────
        """
        [LCM].[MtCaseOfficer] — stores the case officer(s) supervising a
        case.
        • MtCaseHeader_id – the case this officer is linked to.
        • EMPLOYEE_NUMBER – identifies the employee assigned as case
          officer.
        • EffectiveFrom / EffectiveTo – validity period of this
          assignment.
        • Remarks – any remarks about the assignment.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – who
          created/modified the assignment and when.
        • IsDeleted – whether this record is deleted.
        """,

        # ── Case Hearing ───────────────────────────────────────────────────────
        """
        [LCM].[MtCaseHearing] — stores hearing details for a case.
        • MtCaseHeader_id – the case this hearing belongs to.
        • MtCaseHearing_Date – date of the hearing.
        • MtCaseHearing_Remarks – remarks/notes about the hearing.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • IsDeleted – whether this hearing record is deleted.
        """,

        # ── Case Fee ───────────────────────────────────────────────────────────
        """
        [LCM].[MtCaseFee] — stores fee details for a case.
        • MtCaseHeader_id – the case this fee belongs to.
        • MtCaseFee_Type – type of fee, e.g. Scheduled Fee, Special Fee,
          Additional Fee (from Lookups).
        • MtCaseAdvocates_id – links to the advocate this fee is
          associated with (in MtCaseAdvocates).
        • MtCaseFee_AdditionalFeeType – further detail when fee type is
          additional.
        • MtCaseFee_Date – date of the fee entry.
        • MtCaseFee_Amount – amount charged.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • IsDeleted – whether this fee record is deleted.
        """,

        # ── Case Advocates ────────────────────────────────────────────────────
        """
        [LCM].[MtCaseAdvocates] — stores advocates/lawyers engaged on a
        specific case.
        • Routing rule: for advocate info alone, check
          [LCM].[RuLawyerDetails]; for advocate info tied to a specific
          case, check [LCM].[MtCaseAdvocates].
        • MtCaseHeader_id – the case this advocate is engaged on.
        • MtCaseAdvocates_AdvocateType – type of advocate, e.g. Advocate,
          Attorney, Journal (from Lookups).
        • RuLawyerDetails_ERPSupllierNo – links to the lawyer's ERP
          supplier number in RuLawyerDetails.
        • EngagementNumber – engagement reference number.
        • EffectiveFrom / EffectiveTo – validity period of the
          engagement.
        • Remarks – any remarks about the engagement.
        • FirmName – the law firm name, if applicable.
        • ERPTransferCheck – whether this record has been transferred to
          ERP.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • IsDeleted – whether this record is deleted.
        """,

        # ── Attachments ────────────────────────────────────────────────────────
        """
        [LCM].[MtAttachments] — central table storing all attachments
        uploaded across the application.
        • SourceName – identifies which module the attachment belongs
          to: SoC, CaseDetails, CaseAdvocates, CaseHearing.
        • SourceID – id of the source record the attachment is linked
          to.
        • FileName / ActualFileName / FileType – file identity details.
        • Description – description of the attachment.
        • FileLink / BinaryData – where/how the file content is stored.
        • DocLibID, Field01, Field02 – additional reference/metadata
          fields.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • isDeleted – whether this attachment is deleted.
        """,

        # ── Case Status Details ──────────────────────────────────────────────
        """
        [LCM].[MtCaseStatusDetails] — stores status history for a case.
        • MtCaseHeader_Id – the case this status entry belongs to.
        • StatusTypeCode – main case status, e.g. Pending (from
          Lookups).
        • SubStatusCode – further detail, e.g. Dismissed, Withdrawn,
          Stayed (from Lookups).
        • Remarks – e.g. "Dismissed for Non-Prosecution".
        • WorkFlowStatus / WorkFlowRemarks – workflow stage and remarks
          for this status update.
        • CreatedBy/CreatedDate, ModifiedBy/ModifiedDate – audit fields.
        • isDeleted – whether this status record is deleted.
        """,

        # ── Active Schedule of Charges (business rule) ─────────────────────
        """
        Determining an active Schedule of Charges:
        • Do NOT rely on MtScheduleOfChargesHeader_Status for this.
        • Instead, check MtScheduleOfChargesHeader_EffectiveFrom and
          MtScheduleOfChargesHeader_EffectiveTo — a schedule is
          "active" only if the current date falls within this range
          (and EffectiveTo is null/blank or in the future = active;
          a past EffectiveTo = inactive).
        """,

        # ── Attachments (shared table) ─────────────────────────────────────
        """
        [LCM].[MtAttachments] — single shared table for all attachments
        across the system.
        • MtAttachments_SourceName identifies which module/entity the
          attachment belongs to: 'CaseDetails', 'SoC' (Schedule of
          Charges), 'CaseAdvocates', 'CaseHearing', 'CaseStatus'.
        • Always filter by SourceName (and the relevant SourceId) to get
          attachments for a specific module.
        """,

        # ── Forum Code Abbreviations ─────────────────────────────────────────
        """
        Use abbreviation when generating sql.
        Forum Code ↔ code mapping (used in
        MtScheduleOfChargesDetails_ForumCode and
        MtCaseHeader_ForumName) — users typically type the full name,
        map it to the code before querying:
          ARB      → Arbitration
          ATIR     → Appellate Tribunal Inland Revenue
          BHC      → Balochistan High Court
          DC       → District Court
          EM       → Expert Mediation
          FO       → Federal Ombudsman
          IHC      → Islamabad High Court
          LC       → Lower Court
          LHC      → Lahore High Court
          NEPRA    → NEPRA
          NEPRAAT  → NEPRA Appellate Tribunal
          PHC      → Peshawar High Court
          SC       → Supreme Court
          SHC      → Sindh High Court
          NIRC_LC  → NIRC / Lower Court
          LCIA     → London Court of International Arbitration
          ICC      → International Chamber of Commerce
        Note: list is illustrative; other forums (e.g. Federal
        Constitutional Court Pakistan) may exist with their own codes.
        """,

        # ── Case Type Abbreviations ──────────────────────────────────────────
        """
        Use abbreviation when generating sql.
        Case type name ↔ code mapping (used in
        MtCaseHeader_CaseType) — users typically type the full name,
        map it to the code before querying:
          CO       → Civil Original
          WP       → Writ Petition
          CAP      → Civil Appeal
          CPLA     → Petition for Leave to Appeal (Civil)
          CA       → Civil Application
          CRL_A    → Criminal Appeal
          CRL_O    → Criminal Original
          CRL_R    → Criminal Revision
          EP       → Execution Petition
          ICA      → Intra Court Appeal
          SUIT     → Suit
          CONST_P  → Constitutional Petition
          CP       → Civil Petition
        Note: list is illustrative; actual codes/values may vary.
        """,

        # ── Case Classification Abbreviations ────────────────────────────────
        """
        Use abbreviation when generating sql.
        Case classification name ↔ code mapping (used in
        MtCaseClassification_Value) — users typically type the full
        name, map it to the code before querying:
          CR    → Compliance reporting
          FI    → Financial Implications
          HRAI  → HR & Admin Issue
          NCM   → Non-contested matter
          PCA   → Per-forma cases
          REP   → Reputational
          STG   → Strategic
          TI    → Technical Issue
        """,

        # ── Advocate Type Abbreviations ──────────────────────────────────────
        """
        Use abbreviation when generating sql.
        Advocate type name ↔ code mapping (used in
        MtCaseAdvocates_AdvocateType) — users typically type the full
        name, map it to the code before querying:
          AG  → Attorney General
          PA  → Panel Advocate
          LA  → Lead Advocate
        Note: LA's expansion is inferred from naming pattern (not
        directly confirmed) — worth verifying against the lookup table.
        """,
        
        # ── Key Workflow Summary ─────────────────────────────────────────────
        """
        Key Relationships:
        - A Case has a Case Type, Forum, and Classification (from Lookups).
        - A Case can reference Linked Cases and Related Lower Court Cases.
        - A Case has one or more Legal Counsel (Advocate) assignments.
        - A Case has one or more Case Fee entries, optionally tied to the
          Schedule of Fees.
        - A Case has one or more Hearing entries.
        - A Case has one or more Case Status entries over time.
        - Advocates in Legal Counsel come from Settings → Advocates.
        - User module access is set in Setup → User Management; all
          activity is recorded in Setup → Audit Logs.
        """,
    ],
    "qa_pairs": [],
}

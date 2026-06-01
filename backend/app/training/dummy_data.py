"""app/training/dummy_data.py – placeholder Q&A pairs and documentation per instance.
Replace these with real domain knowledge later.
"""

DUMMY_TRAINING: dict[str, dict] = {

    "it_meetingsphere": {
        "documentation": [
            # ── Core Domain Overview ──────────────────────────────────────────────
            """
            This is a Meeting Management System (MeetingSphere). The core entities are:
            - Committees (MtCommitteeHeader)
            - Meetings (MtMeetingHeader)
            - Users/Members (RuUsers, MtCommitteeUsers)
            - Shared Documents (MtSharedDocumentsHeader, MtDocumentCommittee, MtDocumentMeeting)
            - Agendas (MtMeetingAgenda)
            - Minutes of Meeting (MtMeetingMOM)
            - Attachments (MtAttachment, MtSharedAttachment)
            - Meeting Profiles (RuMeetingProfile)
            - Organizations (RuOrganizations)
            """,

            # ── Table: MtCommitteeHeader ──────────────────────────────────────────
            """
            MtCommitteeHeader stores committee records.
            Columns:
            - MtCommitteeHeader_Id (decimal, PK)
            - RuMeetingProfile_Id (decimal, FK to RuMeetingProfile)
            - MtCommitteeHeader_Name (varchar) – the committee name
            - MtCommitteeHeader_Status (bit)
            - MtCommitteeHeader_Isdeleted (bit) – use = 0 to filter active records
            - MtCommitteeHeader_CreatedBy, MtCommitteeHeader_CreatedOn
            - MtCommitteeHeader_ModifiedBy, MtCommitteeHeader_ModifiedOn
            """,

            # ── Table: MtCommitteeUsers ───────────────────────────────────────────
            """
            MtCommitteeUsers stores the members assigned to each committee.
            Columns:
            - MtCommitteeUsers_Id (decimal, PK)
            - MtCommitteeHeader_Id (decimal, FK to MtCommitteeHeader)
            - RuUsers_Id (decimal, FK to RuUsers)
            - RuRoles_Code (varchar) – member's role in the committee
            - MtCommitteeUsers_EffectiveFrom (datetime)
            - MtCommitteeUsers_EffectiveTo (datetime, nullable)
            - MtCommitteeUsers_Isdeleted (bit) – use = 0 for active members
            To list members of a committee, join MtCommitteeUsers with RuUsers on RuUsers_Id,
            and join with MtCommitteeHeader on MtCommitteeHeader_Id.
            """,

            # ── Table: RuUsers ────────────────────────────────────────────────────
            """
            RuUsers stores all system users/persons.
            Columns:
            - RuUsers_Id (decimal, PK)
            - RuUsers_FirstName, RuUsers_LastName (varchar)
            - RuUsers_DomainUserName (nvarchar)
            - RuUsers_EmailAddress (nvarchar)
            - RuUsers_UserType (varchar)
            - RuOrganizations_Code (varchar, FK to RuOrganizations)
            - RuUsers_GenderCode (varchar)
            - RuUsers_IsAdmin (bit)
            - RuUsers_DesignationCode (varchar)
            - RuUsers_PrimaryContact, RuUsers_SecondaryContact (nvarchar)
            - RuUsers_IsDisabled (bit)
            - RuUsers_IsDeleted (bit) – use = 0 to filter active users
            Do NOT use the table RuUsers_backup_15_may_2025; that is a backup and should be ignored.
            """,

            # ── Table: MtMeetingHeader ────────────────────────────────────────────
            """
            MtMeetingHeader stores meeting records.
            Columns:
            - MtMeetingHeader_Id (decimal, PK)
            - MtMeetingHeader_Title (varchar) – the meeting name/title
            - MtCommitteeHeader_Id (decimal, FK to MtCommitteeHeader)
            - MtMeetingHeader_Organizer (varchar)
            - MtMeetingHeader_MeetingDate (datetime)
            - MtMeetingHeader_MeetingStartTime (nvarchar)
            - MtMeetingHeader_Description (nvarchar)
            - MtMeetingHeader_Meeting_Link (nvarchar)
            - LuMeetingSphereLookups_StatusCode (varchar) – meeting status
            - LuMeetingSphereLookups_LocationCode (varchar) – meeting location
            - MtMeetingHeader_OtherAddress (nvarchar)
            - MtMeetingHeader_Isdeleted (int) – use = 0 for active meetings
            - MtMeetingHeader_issubmitted (int)
            To get upcoming meetings, filter MtMeetingHeader_MeetingDate >= CAST(GETDATE() AS DATE).
            """,

            # ── Table: MtMeetingAgenda ────────────────────────────────────────────
            """
            MtMeetingAgenda stores agenda items for each meeting.
            Columns:
            - MtMeetingAgenda_Id (decimal, PK)
            - MtMeetingHeader_Id (decimal, FK to MtMeetingHeader)
            - MtMeetingAgenda_Title (varchar)
            - MtMeetingAgenda_Isdeleted (bit) – use = 0 for active agendas
            - MtMeetingAgenda_IsRolledback (bit)
            - MtMeetingAgenda_issubmitted (int)
            - MtMeetingAgenda_CreatedOn (datetime)
            """,

            # ── Table: MtMeetingMOM ───────────────────────────────────────────────
            """
            MtMeetingMOM stores Minutes of Meeting (MOM) items.
            Columns:
            - MtMeetingMOM_Id (decimal, PK)
            - MtMeetingMOM_Title (varchar)
            - MtMeetingHeader_Id (decimal, FK to MtMeetingHeader)
            - MtMeetingMOM_Isdeleted (bit) – use = 0 for active records
            - MtMeetingMOM_CreatedOn (datetime)
            """,

            # ── Tables: Shared Documents ──────────────────────────────────────────
            """
            Shared documents are stored across three tables:

            MtSharedDocumentsHeader – the main document record:
            - MtSharedDocumentsHeader_Id (decimal, PK)
            - MtSharedDocumentsHeader_Title (varchar)
            - MtSharedDocumentsHeader_Description (nvarchar)
            - RuMeetingProfile_Id (decimal, FK to RuMeetingProfile)
            - MtMeetingHeader_Id (decimal, nullable FK to MtMeetingHeader)
            - MtSharedDocumentsHeader_IsDeleted (bit) – use = 0 for active docs

            MtDocumentCommittee – links a shared document to a committee:
            - MtDocumentCommittee_Id (decimal, PK)
            - MtSharedDocumentsHeader_Id (decimal, FK to MtSharedDocumentsHeader)
            - MtCommitteeHeader_Id (decimal, FK to MtCommitteeHeader)
            - MtDocumentCommittee_IsDeleted (bit) – use ISNULL(MtDocumentCommittee_IsDeleted, 0) = 0

            MtDocumentMeeting – links a shared document to a meeting:
            - MtDocumentMeeting_Id (decimal, PK)
            - MtSharedDocumentsHeader_Id (decimal, FK to MtSharedDocumentsHeader)
            - MtMeetingHeader_Id (decimal, FK to MtMeetingHeader)
            - MtDocumentMeeting_IsDeleted (bit) – use ISNULL(MtDocumentMeeting_IsDeleted, 0) = 0

            To find shared documents for a committee, join MtDocumentCommittee with
            MtSharedDocumentsHeader on MtSharedDocumentsHeader_Id, then join MtCommitteeHeader
            on MtCommitteeHeader_Id.
            """,

            # ── Table: MtAttachment ───────────────────────────────────────────────
            """
            MtAttachment stores file attachments linked to various entities (agendas, MOMs, etc).
            Columns:
            - MtAttachment_Id (decimal, PK)
            - MtAttachment_Source (varchar) – the entity type (e.g. 'Agenda', 'MOM')
            - MtAttachment_SourceId (decimal) – the FK id of the source entity
            - MtAttachment_FileName (nvarchar)
            - MtAttachment_FileExtension (nvarchar)
            - MtAttachment_FileSizeBytes (bigint)
            - MtAttachment_EcmFileId (decimal)
            - MtAttachment_IsDeleted (bit) – use = 0 for active attachments
            To find attachments for an agenda, filter MtAttachment_Source = 'Agenda' (or similar)
            and join on MtAttachment_SourceId = MtMeetingAgenda_Id.
            """,

            # ── Table: MtSharedAttachment ─────────────────────────────────────────
            """
            MtSharedAttachment stores file attachments specifically for shared documents.
            Columns:
            - MtSharedAttachment_Id (decimal, PK)
            - MtSharedDocumentsHeader_Id (decimal, FK to MtSharedDocumentsHeader)
            - MtSharedAttachment_FileName (nvarchar)
            - MtSharedAttachment_FileExtension (nvarchar)
            - MtSharedAttachment_FileSizeBytes (bigint)
            - MtSharedAttachment_IsDeleted (bit) – use = 0 for active attachments
            """,

            # ── Table: RuMeetingProfile ───────────────────────────────────────────
            """
            RuMeetingProfile defines meeting profiles that group committees.
            Columns:
            - RuMeetingProfile_Id (decimal, PK)
            - RuOrganizations_Code (varchar, FK to RuOrganizations)
            - RuMeetingProfile_Name (varchar)
            - RuMeetingProfile_EffectiveFrom (datetime)
            - RuMeetingProfile_EffectiveTo (datetime, nullable)
            - RuMeetingProfile_IsDisabled (bit)
            MtCommitteeHeader links to RuMeetingProfile via RuMeetingProfile_Id.
            """,

            # ── Table: RuOrganizations ────────────────────────────────────────────
            """
            RuOrganizations stores organization records.
            Columns:
            - RuOrganizations_Id (int, PK)
            - RuOrganizations_Code (varchar) – used as FK in other tables
            - RuOrganizations_Name (varchar)
            - RuOrganizations_IsDisabled (bit)
            """,

            # ── Table: RuRoles ────────────────────────────────────────────────────
            """
            RuRoles stores roles available in the system.
            Columns:
            - RuRoles_Id (int, PK)
            - RuRoles_Code (varchar) – used as FK in MtCommitteeUsers, AspNetUsers etc.
            - RuRoles_Name (varchar)
            - RuRoles_Isdeleted (bit) – use = 0 for active roles
            - RuRoles_ShowOnScreen (bit)
            """,

            """
                IMPORTANT – these columns do NOT exist in MtMeetingHeader, never use them:
                - MtMeetingHeader_MeetingTime  → use MtMeetingHeader_MeetingStartTime instead
                - MtMeetingHeader_Venue        → use LuMeetingSphereLookups_LocationCode instead
                - MtMeetingHeader_Location     → use LuMeetingSphereLookups_LocationCode instead
                - MtMeetingHeader_Status       → use LuMeetingSphereLookups_StatusCode instead
            """,

            """
                IMPORTANT – these columns do NOT exist in MtCommitteeUsers, never use them:
                - MtCommitteeUsers_Role     → use RuRoles_Code instead
                - MtCommitteeUsers_RoleName → use RuRoles_Code instead
                - MtCommitteeUsers_Position → use RuRoles_Code instead
                The role of a committee member is stored in RuRoles_Code (varchar) on MtCommitteeUsers.
                To get the full role name, join RuRoles on RuRoles.RuRoles_Code = MtCommitteeUsers.RuRoles_Code.
            """,

            # ── Soft Delete Convention ────────────────────────────────────────────
            """
            Soft Delete Convention across all tables:
            Every table has an IsDeleted or Isdeleted column. Always filter it out in queries:
            - bit columns: WHERE ColumnName_Isdeleted = 0  (or IS NULL OR = 0 for nullable ones)
            - int columns: WHERE ColumnName_Isdeleted = 0
            - For nullable bit columns use: ISNULL(ColumnName_IsDeleted, 0) = 0
            Never return deleted records unless the user explicitly asks for deleted/historical data.
            """,

            # ── Key Relationships Summary ─────────────────────────────────────────
            """
            Key table relationships:
            - RuMeetingProfile → MtCommitteeHeader (via RuMeetingProfile_Id)
            - MtCommitteeHeader → MtMeetingHeader (via MtCommitteeHeader_Id)
            - MtCommitteeHeader → MtCommitteeUsers (via MtCommitteeHeader_Id)
            - MtCommitteeUsers → RuUsers (via RuUsers_Id)
            - MtMeetingHeader → MtMeetingAgenda (via MtMeetingHeader_Id)
            - MtMeetingHeader → MtMeetingMOM (via MtMeetingHeader_Id)
            - MtMeetingAgenda → MtAttachment (via MtAttachment_SourceId, MtAttachment_Source)
            - MtSharedDocumentsHeader → MtDocumentCommittee (via MtSharedDocumentsHeader_Id)
            - MtSharedDocumentsHeader → MtDocumentMeeting (via MtSharedDocumentsHeader_Id)
            - MtDocumentCommittee → MtCommitteeHeader (via MtCommitteeHeader_Id)
            - MtDocumentMeeting → MtMeetingHeader (via MtMeetingHeader_Id)
            - MtSharedDocumentsHeader → MtSharedAttachment (via MtSharedDocumentsHeader_Id)
            - RuOrganizations → RuUsers (via RuOrganizations_Code)
            - RuOrganizations → RuMeetingProfile (via RuOrganizations_Code)
            """,
        ],
        "qa_pairs": [
            {
                "question": "list users of a meeting",
                "sql": """
                    SELECT DISTINCT
                        u.RuUsers_Id,
                        u.RuUsers_FirstName,
                        u.RuUsers_LastName,
                        u.RuUsers_EmailAddress
                    FROM RuUsers u
                    INNER JOIN MtCommitteeUsers cu ON u.RuUsers_Id = cu.RuUsers_Id
                    INNER JOIN MtCommitteeHeader c ON cu.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
                    INNER JOIN MtMeetingHeader m ON c.MtCommitteeHeader_Id = m.MtCommitteeHeader_Id
                    WHERE m.MtMeetingHeader_Title LIKE '%meetingname%'
                    AND m.MtMeetingHeader_Isdeleted = 0
                    AND cu.MtCommitteeUsers_Isdeleted = 0
                    AND u.RuUsers_IsDeleted = 0
                """
            },
            {
            "question": "list second recent meeting",
            "sql": """
                SELECT m.MtMeetingHeader_Id,
                    m.MtMeetingHeader_Title,
                    m.MtMeetingHeader_MeetingDate,
                    m.MtMeetingHeader_MeetingStartTime,
                    m.LuMeetingSphereLookups_LocationCode,
                    m.MtMeetingHeader_OtherAddress,
                    m.MtMeetingHeader_Organizer,
                    m.LuMeetingSphereLookups_StatusCode,
                    c.MtCommitteeHeader_Name
                FROM MtMeetingHeader m
                INNER JOIN MtCommitteeHeader c ON m.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
                WHERE m.MtMeetingHeader_Isdeleted = 0
                AND m.MtMeetingHeader_Id = (
                    SELECT MtMeetingHeader_Id
                    FROM (
                        SELECT TOP 2
                            MtMeetingHeader_Id,
                            MtMeetingHeader_CreatedOn,
                            ROW_NUMBER() OVER (ORDER BY MtMeetingHeader_CreatedOn DESC) AS RowNum
                        FROM MtMeetingHeader
                        WHERE MtMeetingHeader_Isdeleted = 0
                        ORDER BY MtMeetingHeader_CreatedOn DESC
                    ) AS RecentMeetings
                    WHERE RowNum = 2
                )
            """
        },
            {
            "question": "how many agendas are created till today",
            "sql": " SELECT COUNT(*) AS TotalAgendas FROM MtMeetingAgenda WHERE MtMeetingAgenda_Isdeleted = 0 AND MtMeetingAgenda_CreatedOn <= GETDATE()"
        },
        {
            "question": "which meeting profile is used in the meeting '18 may all emails send'",
            "sql": "SELECT m.MtMeetingHeader_Id, m.MtMeetingHeader_Title, c.MtCommitteeHeader_Id, mp.RuMeetingProfile_Name FROM MtMeetingHeader m JOIN MtCommitteeHeader c ON m.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id JOIN RuMeetingProfile mp ON c.RuMeetingProfile_Id = mp.RuMeetingProfile_Id WHERE m.MtMeetingHeader_Title = '18 may all emails send';"
        },
        {
            "question": "can you name the attachment used in the agenda 'a'",
            "sql": "SELECT a.MtMeetingAgenda_Id, a.MtMeetingAgenda_Title, att.MtAttachment_FileName, att.MtAttachment_EcmFileId, att.MtAttachment_FileContent FROM MtMeetingAgenda a INNER JOIN MtAttachment att ON a.MtMeetingAgenda_Id = att.MtAttachment_SourceId WHERE a.MtMeetingAgenda_Title = 'a' AND a.MtMeetingAgenda_Isdeleted = 0 AND att.MtAttachment_IsDeleted = 0"
        },
        {
            "question": "List all users",
            "sql": "SELECT RuUsers_Id, RuUsers_FirstName, RuUsers_LastName, RuUsers_DomainUserName, RuUsers_UserType,RuOrganizations_Code, RuUsers_GenderCode, RuUsers_IsAdmin, RuUsers_DesignationCode, RuUsers_EmailAddress, RuUsers_PrimaryContact, RuUsers_SecondaryContact, RuUsers_CreatedBy, RuUsers_CreatedOn,RuUsers_ModifiedBy,RuUsers_ModifiedOn, RuUsers_IsDisabled,RuUsers_IsDeleted FROM RuUsers WHERE RuUsers_IsDeleted = 0"
        },
        {
            "question": "Show upcoming meetings",
            "sql": "SELECT MtMeetingHeader_Id, MtMeetingHeader_Title, MtMeetingHeader_MeetingDate, MtMeetingHeader_MeetingStartTime, MtMeetingHeader_Organizer, MtMeetingHeader_Description, MtMeetingHeader_Meeting_Link, LuMeetingSphereLookups_StatusCode, MtMeetingHeader_OtherAddress FROM MtMeetingHeader WHERE  MtMeetingHeader_MeetingDate >= CAST(GETDATE() AS DATE) AND MtMeetingHeader_Isdeleted = 0 ORDER BY MtMeetingHeader_MeetingDate ASC"
        },
        {
            "question": "how many shared documents are available with committee April Committee ",
            "sql": "select MtCommitteeHeader_Id from MtCommitteeHeader where MtCommitteeHeader_Name like '%April Committee%' DECLARE @CommitteeId DECIMAL(18,0) = 173 SELECT header.MtCommitteeHeader_Name, * FROM MtDocumentCommittee dc INNER JOIN MtSharedDocumentsHeader doc ON doc.MtSharedDocumentsHeader_Id = dc.MtSharedDocumentsHeader_Id LEFT JOIN MtCommitteeHeader header ON header.MtCommitteeHeader_Id = dc.MtCommitteeHeader_Id WHERE dc.MtCommitteeHeader_Id = @CommitteeId AND ISNULL(dc.MtDocumentCommittee_IsDeleted,0) = 0 AND ISNULL(doc.MtSharedDocumentsHeader_IsDeleted,0) = 0"
        }
        ],
    },

}
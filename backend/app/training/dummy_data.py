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

             # ── MEETINGS ───────────────────────────────────────────
            """Meetings are stored in the table MtMeetingHeader.  Every column in this
            table is prefixed with MtMeetingHeader_.  A meeting (also called session,
            meetup, meet up, gathering, bethak, conference) has the following key columns:
            • MtMeetingHeader_Id          – primary key / unique meeting ID
            • MtMeetingHeader_Title       – title / subject / heading / topic name
            • MtMeetingHeader_Description – description / detail / agenda summary
            • MtMeetingHeader_MeetingDate – date of the meeting (din / tareekh)
            • MtMeetingHeader_MeetingStartTime – start time / timing / waqt
            • MtMeetingHeader_Organizer   – organizer / host / created by / arranged by
            • MtMeetingHeader_Meeting_Link – meeting link / online link / video link
            • MtMeetingHeader_OtherAddress – physical address / venue
            • MtMeetingHeader_Isdeleted   – soft-delete flag (always filter = 0)
            • LuMeetingSphereLookups_StatusCode – meeting status (see Status section)
            • MtCommitteeHeader_Id        – links the meeting to its committee
            To show upcoming / future / next / aanay wali meetings filter MtMeetingHeader_MeetingDate >= CAST(GETDATE() AS DATE).
            To show past / previous / pehle wali / already happened meetings filter MtMeetingHeader_MeetingDate < CAST(GETDATE() AS DATE).
            For today's (aaj / aj) meetings filter CAST(MtMeetingHeader_MeetingDate AS DATE) = CAST(GETDATE() AS DATE).
            For this week (iss haftay / is week) use DATEPART(WEEK,...) = DATEPART(WEEK,GETDATE()).
            For this month (iss mahine / is month) use MONTH(...) = MONTH(GETDATE()).
            To search meeting by name/title use LIKE: WHERE MtMeetingHeader_Title LIKE '%keyword%'""",

            # ── MEETING STATUS ─────────────────────────────────────
            """Meeting status is stored in the column LuMeetingSphereLookups_StatusCode
            inside MtMeetingHeader.  Status synonyms: status, state, halat, situation.
            Valid status values and their meaning:
            • Draft      – draft, drafted, draft version, not published yet, incomplete
            • Published  – published, released, live, announced, finalised
            • Cancelled  – cancelled, canceled, cancel, stopped, nahin hogi
            • Completed  – completed, done, finished, ended, ho chuki, khatam
            • InProgress – in progress, ongoing, running, chal rahi, active
            When someone asks about the status of a meeting always return
            LuMeetingSphereLookups_StatusCode along with meeting title and ID.""",

             # ── AGENDAS ────────────────────────────────────────────
            """Meeting agendas are stored in MtMeetingAgenda.  Every column is prefixed
            with MtMeetingAgenda_.  An agenda (also called topic, point, discussion item,
            task, kya discuss hua, agenda item, agendaa, agnda, ageda) belongs to a meeting
            through the foreign key MtMeetingHeader_Id.  Key columns:
            • MtMeetingAgenda_Id        – primary key
            • MtMeetingHeader_Id        – foreign key linking to MtMeetingHeader
            • MtMeetingAgenda_Title     – title / name of the agenda item
            • MtMeetingAgenda_CreatedOn – creation timestamp
            • MtMeetingAgenda_Isdeleted – soft-delete flag (always filter = 0)
            To count agendas created until today:
            SELECT COUNT(*) AS TotalAgendas FROM MtMeetingAgenda
            WHERE MtMeetingAgenda_Isdeleted = 0 AND MtMeetingAgenda_CreatedOn <= GETDATE()""",

             # ── USERS / EMPLOYEES ──────────────────────────────────
            """Employees, users, staff, workers, people, and team members are all stored
            in the RuUsers table.  Key columns:
            • RuUsers_Id               – primary key
            • RuUsers_FirstName        – first name
            • RuUsers_LastName         – last name
            • RuUsers_DomainUserName   – domain / login username
            • RuUsers_EmailAddress     – email address
            • RuUsers_GenderCode       – gender stored as text: 'Female' or 'Male' (capital first letter)
            • RuUsers_IsAdmin          – 1 if admin user
            • RuUsers_IsDisabled       – 1 if account is disabled
            • RuUsers_IsDeleted        – soft-delete flag (always filter = 0)
            • RuOrganizations_Code     – the organisation this user belongs to (e.g. 'CPPA')
            • RuUsers_DesignationCode  – job designation / title
            • RuUsers_PrimaryContact   – primary phone number
            Always filter RuUsers_IsDeleted = 0 to exclude removed accounts.""",

                        # ── GENDER ─────────────────────────────────────────────
                        """Gender is stored in the column RuUsers_GenderCode as full capitalised text.
            IMPORTANT: The actual values in the database are 'Female' and 'Male' (capital F and M).
            Do NOT use 'F' or 'M' single characters. Do NOT use LOWER() comparison.
            Use exact match: WHERE RuUsers_GenderCode = 'Female'  OR  WHERE RuUsers_GenderCode = 'Male'

            Female synonyms: female, females, woman, women, girl, girls, lady, ladies,
            larki, larkiyan, aurat, auratein, khawateen, femlae, femail, grils, girs, femal, grl.

            Male synonyms: male, males, man, men, boy, boys, larka, larkay, mard, aadmi,
            mal, mle, boi, mens.

            Correct SQL to list female users:
            SELECT RuUsers_Id, RuUsers_FirstName, RuUsers_LastName, RuUsers_EmailAddress,
                    RuUsers_GenderCode, RuUsers_DesignationCode
            FROM RuUsers
            WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Female'

            Correct SQL to count female users:
            SELECT COUNT(*) AS female_count FROM RuUsers
            WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Female'

            Correct SQL to list male users:
            SELECT RuUsers_Id, RuUsers_FirstName, RuUsers_LastName, RuUsers_EmailAddress,
                    RuUsers_GenderCode, RuUsers_DesignationCode
            FROM RuUsers
            WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Male'

            Correct SQL to count male users:
            SELECT COUNT(*) AS male_count FROM RuUsers
            WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Male'""",

                        # ── COMMITTEES ─────────────────────────────────────────
                        """Committees (also called group, team, panel) are stored in
            MtCommitteeHeader.  Key columns:
            • MtCommitteeHeader_Id   – primary key
            • MtCommitteeHeader_Name – committee name / title (search with LIKE '%name%')
            • RuMeetingProfile_Id    – FK to RuMeetingProfile
            • MtCommitteeHeader_IsDeleted – soft-delete flag (filter = 0)

            Committee members, users, attendees, participants are stored in MtCommitteeUsers.
            Key columns:
            • MtCommitteeUsers_Id        – primary key
            • MtCommitteeHeader_Id       – FK to committee
            • RuUsers_Id                 – FK to RuUsers (the person)
            • MtCommitteeUsers_RoleCode  – role of the person: 'Secretary', 'Chairman', 'Member', etc.
            • MtCommitteeUsers_IsDeleted – soft-delete (filter = 0)

            To find members/users of a committee join MtCommitteeUsers with RuUsers.
            Do NOT use imaginary tables like MtMeetingUsers or MtCommitteeMembers.

            To find a specific role (e.g. secretary, chairman) in a meeting or committee:
            JOIN MtMeetingHeader m ON m.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
            JOIN MtCommitteeUsers cu ON cu.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
            JOIN RuUsers u ON u.RuUsers_Id = cu.RuUsers_Id
            WHERE cu.MtCommitteeUsers_RoleCode LIKE '%Secretary%'

            Meeting profiles are linked to committees through RuMeetingProfile via
            RuMeetingProfile_Id. Meeting profile names are in RuMeetingProfile_Name.""",

                        # ── DOCUMENTS & ATTACHMENTS ────────────────────────────
                        """Files, attachments, documents (also: docs, upload, kagaz, file, attchment,
            atachment) are stored in MtAttachment.  Key columns:
            • MtAttachment_FileName      – file name
            • MtAttachment_FileExtension – file extension
            • MtAttachment_EcmFileId     – ECM / document management ID
            • MtAttachment_Source        – type of parent record (e.g. 'MeetingAgenda', 'SharedDocument')
            • MtAttachment_SourceId      – ID of the parent record
            • MtAttachment_IsDeleted     – soft-delete (filter = 0)
            Link attachments using MtAttachment_Source and MtAttachment_SourceId.

            Shared documents (also: shared files, common documents, public documents) are
            stored in MtSharedDocumentsHeader.  To get shared documents WITH file names:
            SELECT sd.MtSharedDocumentsHeader_Id, att.MtAttachment_FileName,
                    att.MtAttachment_FileExtension, att.MtAttachment_EcmFileId
            FROM MtSharedDocumentsHeader sd
            LEFT JOIN MtAttachment att
                ON att.MtAttachment_Source = 'SharedDocument'
            AND att.MtAttachment_SourceId = sd.MtSharedDocumentsHeader_Id
            WHERE sd.MtSharedDocumentsHeader_IsDeleted = 0
                AND att.MtAttachment_IsDeleted = 0""",

                        # ── MINUTES OF MEETING ─────────────────────────────────
                        """Minutes of Meeting (MOM) — also called minutes, meeting notes, summary,
            meeting record, minits, momm, minutez, kya hua meeting mein — contain the
            official record of what was discussed and decided in a meeting.  MOMs are
            linked to their parent meeting through MtMeetingHeader_Id.""",


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

            """
            Meeting Status Convention:
            Database stores meeting status as integers.

            Status Mapping:
            0 = Cancelled
            1 = Pending
            2 = Ended
            3 = Completed
            4 = Draft

            Always convert user-friendly status names to these numeric values when
            building SQL WHERE clauses. If the user asks for completed, pending,
            draft, ended, or cancelled meetings, filter using the corresponding
            numeric status value.
            """,
            "Gendercode can be male and female only",
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
                "question": "name the male person from this meeting",
                "sql": "gjh"
            },
            {
                "question": "is there any guest whose name is Eman",
                "sql": """
                   SELECT DISTINCT
                        u.RuUsers_Id,
                        u.RuUsers_FirstName,
                        u.RuUsers_LastName,
                        u.RuUsers_EmailAddress,
                        u.RuUsers_DomainUserName
                    FROM RuUsers AS u
                    INNER JOIN MtCommitteeUsers AS cu
                        ON u.RuUsers_Id = cu.RuUsers_Id
                    WHERE u.RuUsers_IsDeleted = 0
                    AND cu.MtCommitteeUsers_Isdeleted = 0
                    AND cu.RuRoles_Code LIKE '%member%'
                    AND (u.RuUsers_FirstName LIKE '%Eman%' OR u.RuUsers_LastName LIKE '%Eman%');
                """
            },
            {
                "question" : "which meeting profiles are effective till 06-Jun-2026",
                "sql" : """
                    SELECT *
                    FROM RuMeetingProfile
                    WHERE RuMeetingProfile_EffectiveTo <= '2026-06-06'
                    AND RuMeetingProfile_IsDeleted = 0
                """
            },
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
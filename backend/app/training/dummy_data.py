# """app/training/dummy_data.py – placeholder Q&A pairs and documentation per instance.
# Replace these with real domain knowledge later.
# """

# DUMMY_TRAINING: dict[str, dict] = {

#     "it_meetingsphere": {
#         "documentation": [
#             # ── Core Domain Overview ──────────────────────────────────────────────
#             """
#             This is a Meeting Management System (MeetingSphere). The core entities are:
#             - Committees (MtCommitteeHeader)
#             - Meetings (MtMeetingHeader)
#             - Users/Members (RuUsers, MtCommitteeUsers)
#             - Shared Documents (MtSharedDocumentsHeader, MtDocumentCommittee, MtDocumentMeeting)
#             - Agendas (MtMeetingAgenda)
#             - Minutes of Meeting (MtMeetingMOM)
#             - Attachments (MtAttachment, MtSharedAttachment)
#             - Meeting Profiles (RuMeetingProfile)
#             - Organizations (RuOrganizations)
#             """,

#              # ── MEETINGS ───────────────────────────────────────────
#             """Meetings are stored in the table MtMeetingHeader.  Every column in this
#             table is prefixed with MtMeetingHeader_.  A meeting (also called session,
#             meetup, meet up, gathering, bethak, conference) has the following key columns:
#             • MtMeetingHeader_Id          – primary key / unique meeting ID
#             • MtMeetingHeader_Title       – title / subject / heading / topic name
#             • MtMeetingHeader_Description – description / detail / agenda summary
#             • MtMeetingHeader_MeetingDate – date of the meeting (din / tareekh)
#             • MtMeetingHeader_MeetingStartTime – start time / timing / waqt
#             • MtMeetingHeader_Organizer   – organizer / host / created by / arranged by
#             • MtMeetingHeader_Meeting_Link – meeting link / online link / video link
#             • MtMeetingHeader_OtherAddress – physical address / venue
#             • MtMeetingHeader_Isdeleted   – soft-delete flag (always filter = 0)
#             • LuMeetingSphereLookups_StatusCode – meeting status (see Status section)
#             • MtCommitteeHeader_Id        – links the meeting to its committee""",

#              # ── AGENDAS ────────────────────────────────────────────
#             """Meeting agendas are stored in MtMeetingAgenda.  Every column is prefixed
#             with MtMeetingAgenda_.  An agenda (also called topic, point, discussion item,
#             task, kya discuss hua, agenda item, agendaa, agnda, ageda) belongs to a meeting
#             through the foreign key MtMeetingHeader_Id.  Key columns:
#             • MtMeetingAgenda_Id        – primary key
#             • MtMeetingHeader_Id        – foreign key linking to MtMeetingHeader
#             • MtMeetingAgenda_Title     – title / name of the agenda item
#             • MtMeetingAgenda_CreatedOn – creation timestamp
#             • MtMeetingAgenda_Isdeleted – soft-delete flag (always filter = 0)""",

#              # ── USERS / EMPLOYEES ──────────────────────────────────
#             """Employees, users, staff, workers, people, and team members are all stored
#             in the RuUsers table.  Key columns:
#             • RuUsers_Id               – primary key
#             • RuUsers_FirstName        – first name
#             • RuUsers_LastName         – last name
#             • RuUsers_DomainUserName   – domain / login username
#             • RuUsers_EmailAddress     – email address
#             • RuUsers_GenderCode       – gender stored as text: 'Female' or 'Male' (capital first letter)
#             • RuUsers_IsAdmin          – 1 if admin user
#             • RuUsers_IsDisabled       – 1 if account is disabled
#             • RuUsers_IsDeleted        – soft-delete flag (always filter = 0)
#             • RuOrganizations_Code     – the organisation this user belongs to (e.g. 'CPPA')
#             • RuUsers_DesignationCode  – job designation / title
#             • RuUsers_PrimaryContact   – primary phone number
#             Always filter RuUsers_IsDeleted = 0 to exclude removed accounts.""",

#                         # ── GENDER ─────────────────────────────────────────────
#                         """Gender is stored in the column RuUsers_GenderCode as full capitalised text.
#             IMPORTANT: The actual values in the database are 'Female' and 'Male' (capital F and M).
#             Do NOT use 'F' or 'M' single characters. Do NOT use LOWER() comparison.
#             Use exact match: WHERE RuUsers_GenderCode = 'Female'  OR  WHERE RuUsers_GenderCode = 'Male'

#             Female synonyms: female, females, woman, women, girl, girls, lady, ladies,
#             larki, larkiyan, aurat, auratein, khawateen, femlae, femail, grils, girs, femal, grl.

#             Male synonyms: male, males, man, men, boy, boys, larka, larkay, mard, aadmi,
#             mal, mle, boi, mens.

#             Correct SQL to list female users:
#             SELECT RuUsers_Id, RuUsers_FirstName, RuUsers_LastName, RuUsers_EmailAddress,
#                     RuUsers_GenderCode, RuUsers_DesignationCode
#             FROM RuUsers
#             WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Female'

#             Correct SQL to count female users:
#             SELECT COUNT(*) AS female_count FROM RuUsers
#             WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Female'

#             Correct SQL to list male users:
#             SELECT RuUsers_Id, RuUsers_FirstName, RuUsers_LastName, RuUsers_EmailAddress,
#                     RuUsers_GenderCode, RuUsers_DesignationCode
#             FROM RuUsers
#             WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Male'

#             Correct SQL to count male users:
#             SELECT COUNT(*) AS male_count FROM RuUsers
#             WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'Male'""",

#                         # ── COMMITTEES ─────────────────────────────────────────
#                         """Committees (also called group, team, panel) are stored in
#             MtCommitteeHeader.  Key columns:
#             • MtCommitteeHeader_Id   – primary key
#             • MtCommitteeHeader_Name – committee name / title (search with LIKE '%name%')
#             • RuMeetingProfile_Id    – FK to RuMeetingProfile
#             • MtCommitteeHeader_IsDeleted – soft-delete flag (filter = 0)

#             Committee members, users, attendees, participants are stored in MtCommitteeUsers.
#             Key columns:
#             • MtCommitteeUsers_Id        – primary key
#             • MtCommitteeHeader_Id       – FK to committee
#             • RuUsers_Id                 – FK to RuUsers (the person)
#             • MtCommitteeUsers_RoleCode  – role of the person: 'Secretary', 'Convener', 'Member', 'participant'.
#             • MtCommitteeUsers_IsDeleted – soft-delete (filter = 0)

#             To find members/users of a committee join MtCommitteeUsers with RuUsers.
#             Do NOT use imaginary tables like MtMeetingUsers or MtCommitteeMembers.

#             Meeting profiles are linked to committees through RuMeetingProfile via
#             RuMeetingProfile_Id. Meeting profile names are in RuMeetingProfile_Name.""",

#                         # ── DOCUMENTS & ATTACHMENTS ────────────────────────────
#                         """Files, attachments, documents (also: docs, upload, kagaz, file, attchment,
#             atachment) are stored in MtAttachment.  Key columns:
#             • MtAttachment_FileName      – file name
#             • MtAttachment_FileExtension – file extension
#             • MtAttachment_EcmFileId     – ECM / document management ID
#             • MtAttachment_Source        – type of parent record (e.g. 'MeetingAgenda', 'MoM' , 'SharedDocument', 'MoM_Miscellaneous')
#             • MtAttachment_SourceId      – ID of the parent record
#             • MtAttachment_IsDeleted     – soft-delete (filter = 0)
#             Link attachments using MtAttachment_Source and MtAttachment_SourceId.

#             IMPORTANT:
#             • Meeting attachments are linked DIRECTLY to MtMeetingHeader.
#             • Use MtAttachment_SourceId = MtMeetingHeader_Id when retrieving attachments of a meeting.
#             • Do NOT assume meeting attachments are linked through MtMeetingAgenda.
#             • For queries such as:
#             - "show meeting attachments"
#             - "attachments of the latest meeting"
#             - "attachments of the second last meeting"
#             - "files attached to meeting X"
#             join MtAttachment directly with MtMeetingHeader using:
#                 MtAttachment_SourceId = MtMeetingHeader_Id
#             and MtAttachment_IsDeleted = 0.

#             Shared documents (also: shared files, common documents, public documents) are
#             stored in MtSharedDocumentsHeader.  To get shared documents WITH file names:
#             SELECT sd.MtSharedDocumentsHeader_Id, att.MtAttachment_FileName,
#                     att.MtAttachment_FileExtension, att.MtAttachment_EcmFileId
#             FROM MtSharedDocumentsHeader sd
#             LEFT JOIN MtAttachment att
#                 ON att.MtAttachment_Source = 'SharedDocument'
#             AND att.MtAttachment_SourceId = sd.MtSharedDocumentsHeader_Id
#             WHERE sd.MtSharedDocumentsHeader_IsDeleted = 0
#                 AND att.MtAttachment_IsDeleted = 0""",

#                         # ── MINUTES OF MEETING ─────────────────────────────────
#                         """Minutes of Meeting (MOM) — also called minutes, meeting notes, summary,
#             meeting record, minits, momm, minutez, kya hua meeting mein — contain the
#             official record of what was discussed and decided in a meeting.  MOMs are
#             linked to their parent meeting through MtMeetingHeader_Id.""",


#             # ── Table: MtCommitteeHeader ──────────────────────────────────────────
#             """
#             MtCommitteeHeader stores committee records.
#             Columns:
#             - MtCommitteeHeader_Id (decimal, PK)
#             - RuMeetingProfile_Id (decimal, FK to RuMeetingProfile)
#             - MtCommitteeHeader_Name (varchar) – the committee name
#             - MtCommitteeHeader_Status (bit)
#             - MtCommitteeHeader_Isdeleted (bit) – use = 0 to filter active records
#             - MtCommitteeHeader_CreatedBy, MtCommitteeHeader_CreatedOn
#             - MtCommitteeHeader_ModifiedBy, MtCommitteeHeader_ModifiedOn
#             """,

#             # ── Table: MtCommitteeUsers ───────────────────────────────────────────
#             """
#             MtCommitteeUsers stores the members assigned to each committee.
#             Columns:
#             - MtCommitteeUsers_Id (decimal, PK)
#             - MtCommitteeHeader_Id (decimal, FK to MtCommitteeHeader)
#             - RuUsers_Id (decimal, FK to RuUsers)
#             - RuRoles_Code (varchar) – member's role in the committee
#             - MtCommitteeUsers_EffectiveFrom (datetime)
#             - MtCommitteeUsers_EffectiveTo (datetime, nullable)
#             - MtCommitteeUsers_Isdeleted (bit) – use = 0 for active members
#             To list members of a committee, join MtCommitteeUsers with RuUsers on RuUsers_Id,
#             and join with MtCommitteeHeader on MtCommitteeHeader_Id.
#             """,

#             # ── Table: RuUsers ────────────────────────────────────────────────────
#             """
#             RuUsers stores all system users/persons.
#             Columns:
#             - RuUsers_Id (decimal, PK)
#             - RuUsers_FirstName, RuUsers_LastName (varchar)
#             - RuUsers_DomainUserName (nvarchar)
#             - RuUsers_EmailAddress (nvarchar)
#             - RuUsers_UserType (varchar)
#             - RuOrganizations_Code (varchar, FK to RuOrganizations)
#             - RuUsers_GenderCode (varchar)
#             - RuUsers_IsAdmin (bit)
#             - RuUsers_DesignationCode (varchar)
#             - RuUsers_PrimaryContact, RuUsers_SecondaryContact (nvarchar)
#             - RuUsers_IsDisabled (bit)
#             - RuUsers_IsDeleted (bit) – use = 0 to filter active users
#             Do NOT use the table RuUsers_backup_15_may_2025; that is a backup and should be ignored.
#             """,

#             # ── Table: MtMeetingHeader ────────────────────────────────────────────
#             """
#             MtMeetingHeader stores meeting records.
#             Columns:
#             - MtMeetingHeader_Id (decimal, PK)
#             - MtMeetingHeader_Title (varchar) – the meeting name/title
#             - MtCommitteeHeader_Id (decimal, FK to MtCommitteeHeader)
#             - MtMeetingHeader_Organizer (varchar)
#             - MtMeetingHeader_MeetingDate (datetime)
#             - MtMeetingHeader_MeetingStartTime (nvarchar)
#             - MtMeetingHeader_Description (nvarchar)
#             - MtMeetingHeader_Meeting_Link (nvarchar)
#             - LuMeetingSphereLookups_StatusCode (varchar) – meeting status
#             - LuMeetingSphereLookups_LocationCode (varchar) – meeting location
#             - MtMeetingHeader_OtherAddress (nvarchar)
#             - MtMeetingHeader_Isdeleted (int) – use = 0 for active meetings
#             - MtMeetingHeader_issubmitted (int)
#             To get upcoming meetings, filter MtMeetingHeader_MeetingDate >= CAST(GETDATE() AS DATE).
#             """,

#             # ── Table: MtMeetingAgenda ────────────────────────────────────────────
#             """
#             MtMeetingAgenda stores agenda items for each meeting.
#             Columns:
#             - MtMeetingAgenda_Id (decimal, PK)
#             - MtMeetingHeader_Id (decimal, FK to MtMeetingHeader)
#             - MtMeetingAgenda_Title (varchar)
#             - MtMeetingAgenda_Isdeleted (bit) – use = 0 for active agendas
#             - MtMeetingAgenda_IsRolledback (bit)
#             - MtMeetingAgenda_issubmitted (int)
#             - MtMeetingAgenda_CreatedOn (datetime)
#             """,

#             # ── Table: MtMeetingMOM ───────────────────────────────────────────────
#             """
#             MtMeetingMOM stores Minutes of Meeting (MOM) items.
#             Columns:
#             - MtMeetingMOM_Id (decimal, PK)
#             - MtMeetingMOM_Title (varchar)
#             - MtMeetingHeader_Id (decimal, FK to MtMeetingHeader)
#             - MtMeetingMOM_Isdeleted (bit) – use = 0 for active records
#             - MtMeetingMOM_CreatedOn (datetime)
#             """,

#             # ── Tables: Shared Documents ──────────────────────────────────────────
#             """
#             Shared documents are stored across three tables:

#             MtSharedDocumentsHeader – the main document record:
#             - MtSharedDocumentsHeader_Id (decimal, PK)
#             - MtSharedDocumentsHeader_Title (varchar)
#             - MtSharedDocumentsHeader_Description (nvarchar)
#             - RuMeetingProfile_Id (decimal, FK to RuMeetingProfile)
#             - MtMeetingHeader_Id (decimal, nullable FK to MtMeetingHeader)
#             - MtSharedDocumentsHeader_IsDeleted (bit) – use = 0 for active docs

#             MtDocumentCommittee – links a shared document to a committee:
#             - MtDocumentCommittee_Id (decimal, PK)
#             - MtSharedDocumentsHeader_Id (decimal, FK to MtSharedDocumentsHeader)
#             - MtCommitteeHeader_Id (decimal, FK to MtCommitteeHeader)
#             - MtDocumentCommittee_IsDeleted (bit) – use ISNULL(MtDocumentCommittee_IsDeleted, 0) = 0

#             MtDocumentMeeting – links a shared document to a meeting:
#             - MtDocumentMeeting_Id (decimal, PK)
#             - MtSharedDocumentsHeader_Id (decimal, FK to MtSharedDocumentsHeader)
#             - MtMeetingHeader_Id (decimal, FK to MtMeetingHeader)
#             - MtDocumentMeeting_IsDeleted (bit) – use ISNULL(MtDocumentMeeting_IsDeleted, 0) = 0

#             To find shared documents for a committee, join MtDocumentCommittee with
#             MtSharedDocumentsHeader on MtSharedDocumentsHeader_Id, then join MtCommitteeHeader
#             on MtCommitteeHeader_Id.
#             """,

#             # ── Table: MtAttachment ───────────────────────────────────────────────
#             """
#             MtAttachment stores file attachments linked to various entities (agendas, MOMs, etc).
#             Columns:
#             - MtAttachment_Id (decimal, PK)
#             - MtAttachment_Source (varchar) – the entity type (e.g. 'Agenda', 'MOM')
#             - MtAttachment_SourceId (decimal) – the FK id of the source entity
#             - MtAttachment_FileName (nvarchar)
#             - MtAttachment_FileExtension (nvarchar)
#             - MtAttachment_FileSizeBytes (bigint)
#             - MtAttachment_EcmFileId (decimal)
#             - MtAttachment_IsDeleted (bit) – use = 0 for active attachments
#             To find attachments for an agenda, filter MtAttachment_Source = 'Agenda' (or similar)
#             and join on MtAttachment_SourceId = MtMeetingAgenda_Id.
#             """,

#             # ── Table: MtSharedAttachment ─────────────────────────────────────────
#             """
#             MtSharedAttachment stores file attachments specifically for shared documents.
#             Columns:
#             - MtSharedAttachment_Id (decimal, PK)
#             - MtSharedDocumentsHeader_Id (decimal, FK to MtSharedDocumentsHeader)
#             - MtSharedAttachment_FileName (nvarchar)
#             - MtSharedAttachment_FileExtension (nvarchar)
#             - MtSharedAttachment_FileSizeBytes (bigint)
#             - MtSharedAttachment_IsDeleted (bit) – use = 0 for active attachments
#             """,

#             # ── Table: RuMeetingProfile ───────────────────────────────────────────
#             """
#             RuMeetingProfile defines meeting profiles that group committees.
#             Columns:
#             - RuMeetingProfile_Id (decimal, PK)
#             - RuOrganizations_Code (varchar, FK to RuOrganizations)
#             - RuMeetingProfile_Name (varchar)
#             - RuMeetingProfile_EffectiveFrom (datetime)
#             - RuMeetingProfile_EffectiveTo (datetime, nullable)
#             - RuMeetingProfile_IsDisabled (bit)
#             MtCommitteeHeader links to RuMeetingProfile via RuMeetingProfile_Id.
#             """,

#             # ── Table: RuOrganizations ────────────────────────────────────────────
#             """
#             RuOrganizations stores organization records.
#             Columns:
#             - RuOrganizations_Id (int, PK)
#             - RuOrganizations_Code (varchar) – used as FK in other tables
#             - RuOrganizations_Name (varchar)
#             - RuOrganizations_IsDisabled (bit)
#             """,

#             # ── Table: RuRoles ────────────────────────────────────────────────────
#             """
#             RuRoles stores roles available in the system.
#             Columns:
#             - RuRoles_Id (int, PK)
#             - RuRoles_Code (varchar) – used as FK in MtCommitteeUsers, AspNetUsers etc.
#             - RuRoles_Name (varchar)
#             - RuRoles_Isdeleted (bit) – use = 0 for active roles
#             - RuRoles_ShowOnScreen (bit)
#             """,

#             """
#                 IMPORTANT – these columns do NOT exist in MtMeetingHeader, never use them:
#                 - MtMeetingHeader_MeetingTime  → use MtMeetingHeader_MeetingStartTime instead
#                 - MtMeetingHeader_Venue        → use LuMeetingSphereLookups_LocationCode instead
#                 - MtMeetingHeader_Location     → use LuMeetingSphereLookups_LocationCode instead
#                 - MtMeetingHeader_Status       → use LuMeetingSphereLookups_StatusCode instead
#             """,

#             """
#                 IMPORTANT – these columns do NOT exist in MtCommitteeUsers, never use them:
#                 - MtCommitteeUsers_Role     → use RuRoles_Code instead
#                 - MtCommitteeUsers_RoleName → use RuRoles_Code instead
#                 - MtCommitteeUsers_Position → use RuRoles_Code instead
#                 The role of a committee member is stored in RuRoles_Code (varchar) on MtCommitteeUsers.
#                 To get the full role name, join RuRoles on RuRoles.RuRoles_Code = MtCommitteeUsers.RuRoles_Code.
#             """,

#             # ── Soft Delete Convention ────────────────────────────────────────────
#             """
#             Soft Delete Convention across all tables:
#             Every table has an IsDeleted or Isdeleted column. Always filter it out in queries:
#             - bit columns: WHERE ColumnName_Isdeleted = 0  (or IS NULL OR = 0 for nullable ones)
#             - int columns: WHERE ColumnName_Isdeleted = 0
#             - For nullable bit columns use: ISNULL(ColumnName_IsDeleted, 0) = 0
#             Never return deleted records unless the user explicitly asks for deleted/historical data.
#             """,

#             """
#             Meeting Status Convention:
#             Database stores meeting status as integers.

#             Status Mapping:
#             0 = Cancelled
#             1 = Pending
#             2 = Ended
#             3 = Completed
#             4 = Draft

#             Always convert user-friendly status names to these numeric values when
#             building SQL WHERE clauses. If the user asks for completed, pending,
#             draft, ended, or cancelled meetings, filter using the corresponding
#             numeric status value.
#             """,
#             "Gendercode can be male and female only",
#             # ── Key Relationships Summary ─────────────────────────────────────────
#             """
#             Key table relationships:
#             - RuMeetingProfile → MtCommitteeHeader (via RuMeetingProfile_Id)
#             - MtCommitteeHeader → MtMeetingHeader (via MtCommitteeHeader_Id)
#             - MtCommitteeHeader → MtCommitteeUsers (via MtCommitteeHeader_Id)
#             - MtCommitteeUsers → RuUsers (via RuUsers_Id)
#             - MtMeetingHeader → MtMeetingAgenda (via MtMeetingHeader_Id)
#             - MtMeetingHeader → MtMeetingMOM (via MtMeetingHeader_Id)
#             - MtMeetingAgenda → MtAttachment (via MtAttachment_SourceId, MtAttachment_Source)
#             - MtSharedDocumentsHeader → MtDocumentCommittee (via MtSharedDocumentsHeader_Id)
#             - MtSharedDocumentsHeader → MtDocumentMeeting (via MtSharedDocumentsHeader_Id)
#             - MtDocumentCommittee → MtCommitteeHeader (via MtCommitteeHeader_Id)
#             - MtDocumentMeeting → MtMeetingHeader (via MtMeetingHeader_Id)
#             - MtSharedDocumentsHeader → MtSharedAttachment (via MtSharedDocumentsHeader_Id)
#             - RuOrganizations → RuUsers (via RuOrganizations_Code)
#             - RuOrganizations → RuMeetingProfile (via RuOrganizations_Code)
#             """,
#         ],
#         "qa_pairs": [
#             {
#                 "question": "when was the last meeting held?",
#                 "sql": """
#                     SELECT 
#                         m.MtMeetingHeader_Id,
#                         m.MtMeetingHeader_Title,
#                         m.MtMeetingHeader_MeetingDate,
#                         m.MtMeetingHeader_MeetingStartTime,
#                         m.MtCommitteeHeader_Id
#                     FROM MtMeetingHeader AS m
#                     WHERE m.MtMeetingHeader_Isdeleted = 0
#                     AND m.MtMeetingHeader_MeetingDate = (
#                             SELECT MAX(MtMeetingHeader_MeetingDate)
#                             FROM MtMeetingHeader
#                             WHERE MtMeetingHeader_Isdeleted = 0
#                     )
#                     ORDER BY m.MtCommitteeHeader_Id, m.MtMeetingHeader_Id;
#                 """
#             },
#             {
#                 "question": "is there any guest whose name is Eman",
#                 "sql": """
#                    SELECT DISTINCT
#                         u.RuUsers_Id,
#                         u.RuUsers_FirstName,
#                         u.RuUsers_LastName,
#                         u.RuUsers_EmailAddress,
#                         u.RuUsers_DomainUserName
#                     FROM RuUsers AS u
#                     INNER JOIN MtCommitteeUsers AS cu
#                         ON u.RuUsers_Id = cu.RuUsers_Id
#                     WHERE u.RuUsers_IsDeleted = 0
#                     AND cu.MtCommitteeUsers_Isdeleted = 0
#                     AND cu.RuRoles_Code LIKE '%member%'
#                     AND (u.RuUsers_FirstName LIKE '%Eman%' OR u.RuUsers_LastName LIKE '%Eman%');
#                 """
#             },
#             {
#                 "question": "Are there any attachments linked with the meetings held on 2026-06-13 titled 'asd' and '11 june meeting with agenda items'?",
#                 "sql": """
#                     SELECT 
#                         m.MtMeetingHeader_Id,
#                         m.MtMeetingHeader_Title,
#                         m.MtMeetingHeader_MeetingDate,
#                         att.MtAttachment_Id,
#                         att.MtAttachment_Source,
#                         att.MtAttachment_SourceId,
#                         att.MtAttachment_FileName,
#                         att.MtAttachment_FileExtension,
#                         att.MtAttachment_EcmFileId,
#                         att.MtAttachment_FileSizeBytes,
#                         att.MtAttachment_CreatedOn
#                     FROM MtMeetingHeader AS m
#                     LEFT JOIN MtAttachment AS att
#                         ON att.MtAttachment_SourceId = m.MtMeetingHeader_Id
#                     AND att.MtAttachment_IsDeleted = 0
#                     WHERE m.MtMeetingHeader_Isdeleted = 0
#                     AND m.MtMeetingHeader_MeetingDate = '2026-06-13'
#                     AND (
#                             m.MtMeetingHeader_Title LIKE '%asd%'
#                             OR m.MtMeetingHeader_Title LIKE '%11 june meeting with agenda items%'
#                         );
#                 """
#             },
#             {
#                 "question" : "which meeting profiles are effective till 06-Jun-2026",
#                 "sql" : """
#                     SELECT *
#                     FROM RuMeetingProfile
#                     WHERE RuMeetingProfile_EffectiveTo <= '2026-06-06'
#                     AND RuMeetingProfile_IsDeleted = 0
#                 """
#             },
#             {
#                 "question": "list attachments of meeting with title like '4J Meeting'",
#                 "sql": """
#                     SELECT m.MtMeetingHeader_Id,
#                     m.MtMeetingHeader_Title,
#                     d.MtAttachment_SourceId,
#                     d.MtAttachment_FileName,
#                     d.MtAttachment_CreatedOn
#                 FROM MtMeetingHeader AS m
#                 INNER JOIN [MtAttachment] AS d
#                     ON m.MtMeetingHeader_Id = d.MtAttachment_SourceId
#                 WHERE m.MtMeetingHeader_Isdeleted = 0
#                 AND d.MtAttachment_IsDeleted = 0
#                 AND m.MtMeetingHeader_Title LIKE '%4J Meeting%'
#                 """
#             },
#             {
#                 "question": "name all the meetings that are scheduled in location CPPAOFFICEISLAMABAD",
#                 "sql": """    
#                     SELECT 
#                         MtMeetingHeader_Id,
#                         MtMeetingHeader_Title,
#                         MtMeetingHeader_MeetingDate,
#                         MtMeetingHeader_MeetingStartTime,
#                         MtMeetingHeader_Organizer,
#                         MtMeetingHeader_Description,
#                         MtMeetingHeader_Meeting_Link,
#                         LuMeetingSphereLookups_StatusCode,
#                         MtMeetingHeader_OtherAddress
#                     FROM MtMeetingHeader
#                     WHERE MtMeetingHeader_Isdeleted = 0
#                     AND LuMeetingSphereLookups_LocationCode = 'CPPAOFFICEISLAMABAD'
#                 """
#             },
#             {
#                 "question": "list attachments of 4J meeting",
#                 "sql": """
#                     SELECT m.MtMeetingHeader_Id,
#                     m.MtMeetingHeader_Title,
#                     d.MtAttachment_SourceId,
#                     d.MtAttachment_FileName,
#                     d.MtAttachment_CreatedOn
#                 FROM MtMeetingHeader AS m
#                 INNER JOIN [MtAttachment] AS d
#                     ON m.MtMeetingHeader_Id = d.MtAttachment_SourceId
#                 WHERE m.MtMeetingHeader_Isdeleted = 0
#                 AND d.MtAttachment_IsDeleted = 0
#                 AND m.MtMeetingHeader_Title LIKE '%4J Meeting%'
#                 """
#             },
#             {
#                 "question": "how many shared documents are available with committee Engro Power",
#                 "sql": """
#                     SELECT 
#                         c.MtCommitteeHeader_Id,
#                         c.MtCommitteeHeader_Name,
#                         sd.MtSharedDocumentsHeader_Id,
#                         sd.MtSharedDocumentsHeader_Title,
#                         att.MtAttachment_Id,
#                         att.MtAttachment_FileName,
#                         att.MtAttachment_FileExtension,
#                         att.MtAttachment_FileSizeBytes,
#                         att.MtAttachment_EcmFileId,
#                         att.MtAttachment_CreatedOn
#                     FROM MtCommitteeHeader AS c
#                     INNER JOIN MtDocumentCommittee AS dc
#                         ON dc.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
#                     INNER JOIN MtSharedDocumentsHeader AS sd
#                         ON sd.MtSharedDocumentsHeader_Id = dc.MtSharedDocumentsHeader_Id
#                     LEFT JOIN MtAttachment AS att
#                         ON att.MtAttachment_Source = 'SharedDocument'
#                     AND att.MtAttachment_SourceId = sd.MtSharedDocumentsHeader_Id
#                     WHERE c.MtCommitteeHeader_Isdeleted = 0
#                     AND ISNULL(dc.MtDocumentCommittee_IsDeleted, 0) = 0
#                     AND sd.MtSharedDocumentsHeader_IsDeleted = 0
#                     AND att.MtAttachment_IsDeleted = 0
#                     AND c.MtCommitteeHeader_Name LIKE '%Engro Power%';
#                 """
#             },
#             {
#                 "question": "list users of a meeting",
#                 "sql": """
#                     SELECT DISTINCT
#                         u.RuUsers_Id,
#                         u.RuUsers_FirstName,
#                         u.RuUsers_LastName,
#                         u.RuUsers_EmailAddress
#                     FROM RuUsers u
#                     INNER JOIN MtCommitteeUsers cu ON u.RuUsers_Id = cu.RuUsers_Id
#                     INNER JOIN MtCommitteeHeader c ON cu.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
#                     INNER JOIN MtMeetingHeader m ON c.MtCommitteeHeader_Id = m.MtCommitteeHeader_Id
#                     WHERE m.MtMeetingHeader_Title LIKE '%meetingname%'
#                     AND m.MtMeetingHeader_Isdeleted = 0
#                     AND cu.MtCommitteeUsers_Isdeleted = 0
#                     AND u.RuUsers_IsDeleted = 0
#                 """
#             },
#             {
#             "question": "list second recent meeting",
#             "sql": """
#                 SELECT m.MtMeetingHeader_Id,
#                     m.MtMeetingHeader_Title,
#                     m.MtMeetingHeader_MeetingDate,
#                     m.MtMeetingHeader_MeetingStartTime,
#                     m.LuMeetingSphereLookups_LocationCode,
#                     m.MtMeetingHeader_OtherAddress,
#                     m.MtMeetingHeader_Organizer,
#                     m.LuMeetingSphereLookups_StatusCode,
#                     c.MtCommitteeHeader_Name
#                 FROM MtMeetingHeader m
#                 INNER JOIN MtCommitteeHeader c ON m.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
#                 WHERE m.MtMeetingHeader_Isdeleted = 0
#                 AND m.MtMeetingHeader_Id = (
#                     SELECT MtMeetingHeader_Id
#                     FROM (
#                         SELECT TOP 2
#                             MtMeetingHeader_Id,
#                             MtMeetingHeader_CreatedOn,
#                             ROW_NUMBER() OVER (ORDER BY MtMeetingHeader_CreatedOn DESC) AS RowNum
#                         FROM MtMeetingHeader
#                         WHERE MtMeetingHeader_Isdeleted = 0
#                         ORDER BY MtMeetingHeader_CreatedOn DESC
#                     ) AS RecentMeetings
#                     WHERE RowNum = 2
#                 )
#             """
#         },
#             {
#             "question": "how many agendas are created till today",
#             "sql": " SELECT COUNT(*) AS TotalAgendas FROM MtMeetingAgenda WHERE MtMeetingAgenda_Isdeleted = 0 AND MtMeetingAgenda_CreatedOn <= GETDATE()"
#         },
#         {
#             "question": "which meeting profile is used in the meeting '18 may all emails send'",
#             "sql": "SELECT m.MtMeetingHeader_Id, m.MtMeetingHeader_Title, c.MtCommitteeHeader_Id, mp.RuMeetingProfile_Name FROM MtMeetingHeader m JOIN MtCommitteeHeader c ON m.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id JOIN RuMeetingProfile mp ON c.RuMeetingProfile_Id = mp.RuMeetingProfile_Id WHERE m.MtMeetingHeader_Title = '18 may all emails send';"
#         },
#         {
#             "question": "can you name the attachment used in the agenda 'a'",
#             "sql": "SELECT a.MtMeetingAgenda_Id, a.MtMeetingAgenda_Title, att.MtAttachment_FileName, att.MtAttachment_EcmFileId, att.MtAttachment_FileContent FROM MtMeetingAgenda a INNER JOIN MtAttachment att ON a.MtMeetingAgenda_Id = att.MtAttachment_SourceId WHERE a.MtMeetingAgenda_Title = 'a' AND a.MtMeetingAgenda_Isdeleted = 0 AND att.MtAttachment_IsDeleted = 0"
#         },
#         {
#             "question": "List all users",
#             "sql": "SELECT RuUsers_Id, RuUsers_FirstName, RuUsers_LastName, RuUsers_DomainUserName, RuUsers_UserType,RuOrganizations_Code, RuUsers_GenderCode, RuUsers_IsAdmin, RuUsers_DesignationCode, RuUsers_EmailAddress, RuUsers_PrimaryContact, RuUsers_SecondaryContact, RuUsers_CreatedBy, RuUsers_CreatedOn,RuUsers_ModifiedBy,RuUsers_ModifiedOn, RuUsers_IsDisabled,RuUsers_IsDeleted FROM RuUsers WHERE RuUsers_IsDeleted = 0"
#         },
#         {
#             "question": "Show upcoming meetings",
#             "sql": "SELECT MtMeetingHeader_Id, MtMeetingHeader_Title, MtMeetingHeader_MeetingDate, MtMeetingHeader_MeetingStartTime, MtMeetingHeader_Organizer, MtMeetingHeader_Description, MtMeetingHeader_Meeting_Link, LuMeetingSphereLookups_StatusCode, MtMeetingHeader_OtherAddress FROM MtMeetingHeader WHERE  MtMeetingHeader_MeetingDate >= CAST(GETDATE() AS DATE) AND MtMeetingHeader_Isdeleted = 0 ORDER BY MtMeetingHeader_MeetingDate ASC"
#         },
#         {
#             "question": "how many shared documents are available with committee April Committee ",
#             "sql": "select MtCommitteeHeader_Id from MtCommitteeHeader where MtCommitteeHeader_Name like '%April Committee%' DECLARE @CommitteeId DECIMAL(18,0) = 173 SELECT header.MtCommitteeHeader_Name, * FROM MtDocumentCommittee dc INNER JOIN MtSharedDocumentsHeader doc ON doc.MtSharedDocumentsHeader_Id = dc.MtSharedDocumentsHeader_Id LEFT JOIN MtCommitteeHeader header ON header.MtCommitteeHeader_Id = dc.MtCommitteeHeader_Id WHERE dc.MtCommitteeHeader_Id = @CommitteeId AND ISNULL(dc.MtDocumentCommittee_IsDeleted,0) = 0 AND ISNULL(doc.MtSharedDocumentsHeader_IsDeleted,0) = 0"
#         }
#         ],
#     },


#     # ========================= CDXP =========================
#     "it_cdxp": {
#         "documentation": [

#             # ── Core Domain Overview ──────────────────────────────────────────────
#             """
#             This is CDXP (CPPA Data Exchange Portal) — an Invoice Management System
#             used by CPPA (Central Power Purchasing Agency) to manage power invoices
#             submitted by IPPs (Independent Power Producers / suppliers).

#             Invoice Types:
#             - Monthly   : standard monthly power purchase invoice
#             - Differential : raised when there is a revision or difference in a previously settled claim
#             - Interest  : raised when payment delays trigger interest charges against CPPA

#             Invoice Lifecycle:
#             IPP submits invoice → CPPA Technical team reviews → CPPA Finance team reviews
#             → If accepted: Services team sends it to ERP for payment
#             → Payment (full or partial) is synced back to CDXP
#             → If rejected: invoice is returned to supplier for resubmission
#             → If claim changes after ERP acceptance: supplier creates a NEW invoice (not resubmit)

#             Invoice Hierarchy:
#             Supplier → Diary (Header) → Blocks → Components → Attachments

#             Invoice Status Values (APPROVED_STATUS):
#             - Draft      : created but not yet submitted by supplier
#             - Submitted  : supplier has submitted for CPPA review
#             - Received   : CPPA has formally accepted the invoice for processing
#             - Returned   : CPPA has returned invoice to supplier for corrections
#             - Deleted    : invoice has been deleted
#             - Withdraw   : supplier has withdrawn the invoice
#             """,

#             # ── Table: CPPA_CA.DIARY_HEADER_INTERFACE ────────────────────────────
#             """
#             CPPA_CA.DIARY_HEADER_INTERFACE — Master Invoice Table (also called diary, invoice header).
#             This is the top-level table. Every invoice (monthly, differential, interest) has
#             one record here. It holds the overall overview: who submitted it, when, what was
#             claimed, and what the current status is.

#             Synonyms: invoice, diary, header, claim, bill


#             IMPORTANT:
#             - Use TOTAL_CLAIM for claim-related queries
#             - Use VERIFIED_AMOUNT for verified/approved amount queries
#             - For latest invoice: ORDER BY SUBMIT_DATE DESC
#             - Always go DIARY → BLOCK → COMPONENT. Never join COMPONENT directly with DIARY.
#             """,

#             # ── Table: CPPA_CA.BLOCKS_HEADER_INTERFACE ───────────────────────────
#             """
#             CPPA_CA.BLOCKS_HEADER_INTERFACE — Block Table for Monthly Invoices.
#             A block represents a fuel type within a Monthly invoice. Each monthly invoice
#             can have one or more blocks, one per applicable fuel type.

#             Synonyms: block, fuel block, fuel type

#             This table is ONLY for Monthly invoices.
#             For Differential and Interest invoices use WP_GC_INV_DIFF_PARENT.


#             """,

#             # ── Table: CPPA_CA.COMP_HEADER_INTERFACE ─────────────────────────────
#             """
#             CPPA_CA.COMP_HEADER_INTERFACE — Component Table for Monthly Invoices.
#             Each block (fuel type) in a Monthly invoice is further broken down into
#             chargeable components (e.g. Capacity Payment, Variable O&M, Fuel Cost).
#             This table holds each component's name, value, and verification status.

#             Synonyms: component, fuel component, price, charge, line item

#             This table is ONLY for Monthly invoices.
#             For Differential and Interest invoices use WP_GC_INTEREST_DETAIL.


#             """,

#             # ── Table: WP_GC_INV_DIFF_PARENT ─────────────────────────────────────
#             """
#             WP_GC_INV_DIFF_PARENT — Block Table for Differential and Interest Invoices.
#             This table plays the same role as BLOCKS_HEADER_INTERFACE but for
#             Differential and Interest invoice types. Each record is a fuel/block entry
#             within a Differential or Interest invoice.

#             Synonyms: differential block, interest block, diff parent, fuel block (for differential/interest)


#             """,

#             # ── Table: CPPA_CA.WP_GC_INTEREST_DETAIL ─────────────────────────────
#             """
#             CPPA_CA.WP_GC_INTEREST_DETAIL — Component Table for Differential and Interest Invoices.
#             This table plays the same role as COMP_HEADER_INTERFACE but for Differential and
#             Interest invoice types.
#             - For Interest invoices: stores payment schedule details used to calculate interest charges.
#             - For Differential invoices: stores the component-by-component breakdown of the differential claim.

#             Synonyms: interest detail, differential component, interest component


#             """,

#             # ── Table: CPPA_CA.ATTACHMENT_HEADER ─────────────────────────────────
#             """
#             CPPA_CA.ATTACHMENT_HEADER — Attachments for All Invoice Types.
#             Stores all file attachments uploaded against invoices — across Monthly,
#             Differential, and Interest invoice types. Attachments can be structured
#             (Excel, Word) or unstructured (PDF, images).

#             Synonyms: attachment, file, document, upload


#             """,

#             # ── Table: dbo.DISPUTE_ATTACHMENTS ───────────────────────────────────
#             """
#             dbo.DISPUTE_ATTACHMENTS — Attachments for Invoice Disputes.
#             When an invoice is returned from ERP due to a claim discrepancy and the
#             supplier raises a dispute or creates a revised invoice, CPPA uploads
#             dispute-related documents here. These are separate from regular invoice
#             attachments in ATTACHMENT_HEADER.

#             Synonyms: dispute attachment, dispute file, dispute document

#             """,

#             # ── Table: CPPA_CA.WP_GC_ERP_INVOICES ───────────────────────────────
#             """
#             CPPA_CA.WP_GC_ERP_INVOICES — ERP Invoice Sync Table.
#             Stores ERP-side invoice records synced back to CDXP after payment processing.
#             Once an invoice is paid (fully or partially) in ERP, the payment details are
#             written here so CDXP has an up-to-date view of paid amounts and outstanding balances.

#             Synonyms: ERP invoice, paid invoice, payment record, erp sync


#             """,

#             # ── PPA Tables ────────────────────────────────────────────────────────
#             """
#             PPA (Power Purchase Agreement) Tables.
#             PPA tables store the master agreement and rate definitions that govern
#             how invoices are structured, calculated, and validated.
#             Invoice components and blocks are always traced back to PPA definitions.

#             Synonyms: agreement, ppa, contract, power agreement
#             """,

#             # ── Table: CPPA_CA.PPA_HEADER ─────────────────────────────────────────
#             """
#             CPPA_CA.PPA_HEADER — Master PPA Table.
#             Each record is a Power Purchase Agreement between CPPA and one IPP/supplier.
#             Stores overall agreement details, contracted capacity, COD dates, and approval status.

#             """,

#             # ── Table: CPPA_CA.PPA_BLOCKS_FUELS ──────────────────────────────────
#             """
#             CPPA_CA.PPA_BLOCKS_FUELS — Fuel Types / Blocks defined in a PPA.
#             Each PPA can have multiple fuel types (e.g. EPP, CPP, and others).
#             Blocks in invoices reference this table for their fuel type definition.

#             Synonyms: ppa block, fuel type, ppa fuel, block definition

#             """,

#             # ── Table: CPPA_CA.PPA_COMP_DEFS ─────────────────────────────────────
#             """
#             CPPA_CA.PPA_COMP_DEFS — Component Definitions for PPA Blocks.
#             Defines chargeable components for each block/fuel type in a PPA.
#             These definitions serve as the template for what components appear on invoices
#             and at what rates (e.g. Capacity Payment, Variable O&M, Fuel Cost).

#             Synonyms: component definition, ppa component, rate, ppa rate

#             """,

#             # ── Table: CPPA_CA.PPA_APPLICABLE_INVOICES ───────────────────────────
#             """
#             CPPA_CA.PPA_APPLICABLE_INVOICES — Invoice Type Configuration per PPA.
#             Defines which invoice types and configurations are applicable under each PPA.
#             Acts as a configuration table controlling invoice categorization and payment settings.

#             Synonyms: applicable invoice, invoice config, invoice type config

#             """,

#             # ── Supplier Tables ───────────────────────────────────────────────────
#             """
#             Supplier Tables.
#             Suppliers are the IPPs (Independent Power Producers) who submit invoices to CPPA.
#             Synonyms: supplier, vendor, ipp, company
#             """,

#             # ── Table: CPPA_CA.AP_SUPPLIERS ──────────────────────────────────────
#             """
#             CPPA_CA.AP_SUPPLIERS — Master Supplier / Vendor Table.
#             Stores all registered suppliers (IPPs) that can submit invoices to CPPA.
#             VENDOR_ID is the primary key used across all invoice tables to identify the supplier.

#             Synonyms: supplier, vendor, ipp, company

#             """,

#             # ── Table: CPPA_CA.APP_SUPPLIER_SITE_ALL ─────────────────────────────
#             """
#             CPPA_CA.APP_SUPPLIER_SITE_ALL — Supplier Site Table.
#             Stores individual supplier sites (sub-units / plants) for each supplier.
#             A single IPP may operate multiple power plants or have multiple payment sites,
#             each registered as a separate supplier site. When submitting an invoice, both
#             VENDOR_ID and VENDOR_SITE_ID are specified. Site options appear in dropdowns
#             when a supplier logs in.

#             Synonyms: supplier site, vendor site, plant site, ipp site

#             """,

#             # ── User Tables ───────────────────────────────────────────────────────

#             # ── Table: CPPA_CA.ApiUsers ───────────────────────────────────────────
#             """
#             CPPA_CA.ApiUsers — User Login and Profile Table.
#             Stores login credentials and profile information for all CDXP portal users.
#             Includes supplier representatives (IPP users), CPPA staff, and department heads.
#             Each user is linked to a PPA to control what data they can access.

#             Synonyms: user, login, portal user, staff, employee

#             """,

#             # ── Table: dbo.WP_GC_USER_ACCESS ─────────────────────────────────────
#             """
#             dbo.WP_GC_USER_ACCESS — User Access Rights Table.
#             Defines granular access rights for each user across the system.
#             Controls which entities a user can view, create, edit, or delete.
#             Also maps users to specific vendors/sites so supplier users only see their own data.

#             Synonyms: user access, user rights, user permissions, access control

#             """,

#             # ── Key Relationships ─────────────────────────────────────────────────
#             """
#             Key Table Relationships for CDXP:

#             Supplier to Invoice:
#             - AP_SUPPLIERS → DIARY_HEADER_INTERFACE (via VENDOR_ID)
#             - APP_SUPPLIER_SITE_ALL → DIARY_HEADER_INTERFACE (via VENDOR_SITE_ID)

#             Invoice Hierarchy (Monthly):
#             - DIARY_HEADER_INTERFACE → BLOCKS_HEADER_INTERFACE (via DIARY_HEADER_ID)
#             - BLOCKS_HEADER_INTERFACE → COMP_HEADER_INTERFACE (via BLOCK_HEADER_ID)

#             Invoice Hierarchy (Differential & Interest):
#             - DIARY_HEADER_INTERFACE → WP_GC_INV_DIFF_PARENT (via DIARY_HEADER_ID_FK)
#             - WP_GC_INV_DIFF_PARENT → WP_GC_INTEREST_DETAIL (via DIFF_PAR_ID_FK)

#             Attachments:
#             - DIARY_HEADER_INTERFACE → ATTACHMENT_HEADER (via DIARY_HEADER_ID)
#             - WP_GC_ERP_INVOICES → DISPUTE_ATTACHMENTS (via AP_INVOICE_ID)

#             PPA Linkage:
#             - PPA_HEADER → PPA_BLOCKS_FUELS (via HEADER_ID_FK)
#             - PPA_BLOCKS_FUELS → PPA_COMP_DEFS (via BLK_FUEL_ID_FK)
#             - PPA_HEADER → PPA_APPLICABLE_INVOICES (via HEADER_ID_FK)
#             - PPA_HEADER → DIARY_HEADER_INTERFACE (via PPA_HEADER_ID)

#             ERP Sync:
#             - DIARY_HEADER_INTERFACE → WP_GC_ERP_INVOICES (via TRANSACTION_NO / DIARY_NO)

#             User Access:
#             - ApiUsers → WP_GC_USER_ACCESS (via UserId)
#             - ApiUsers → PPA_HEADER (via PPA_HEADER_ID_FK)
#             - WP_GC_USER_ACCESS → AP_SUPPLIERS (via VENDOR_ID)

#             IMPORTANT — Never join COMP_HEADER_INTERFACE directly with DIARY_HEADER_INTERFACE.
#             Always go: DIARY → BLOCK → COMPONENT.
#             Same rule applies for Differential/Interest:
#             DIARY → WP_GC_INV_DIFF_PARENT → WP_GC_INTEREST_DETAIL.
#             """,

#             # ── Query Rules ───────────────────────────────────────────────────────
#             """
#             Query Rules for CDXP:

#             • Use TOTAL_CLAIM for claim/claimed amount queries
#             • Use VERIFIED_AMOUNT for verified/approved amount queries
#             • For latest invoice: ORDER BY SUBMIT_DATE DESC
#             • For invoice status: filter APPROVED_STATUS column in DIARY_HEADER_INTERFACE
#             • Note: COMP_HEADER_INTERFACE has a typo — column is VARIFIED_AMOUNT not VERIFIED_AMOUNT
#             • Note: WP_GC_INTEREST_DETAIL has a typo — column is FULE_TYPE not FUEL_TYPE
#             • Always use proper JOIN paths. Never skip levels in the hierarchy.
#             • For attachment queries: join ATTACHMENT_HEADER on DIARY_HEADER_ID
#             • For dispute attachment queries: join DISPUTE_ATTACHMENTS on AP_INVOICE_ID
#             """,
#         ],

#         # "qa_pairs": [
#         #     {
#         #         "question": "show invoices of a vendor",
#         #         "sql": """
#         #             SELECT DIARY_HEADER_ID, VENDOR_ID, TOTAL_CLAIM, VERIFIED_AMOUNT,
#         #                    APPROVED_STATUS, SUBMIT_DATE, INVOICE_PERIOD_FROM, INVOICE_PERIOD_TO
#         #             FROM CPPA_CA.DIARY_HEADER_INTERFACE
#         #             WHERE VENDOR_ID = 101
#         #             ORDER BY SUBMIT_DATE DESC
#         #         """
#         #     },
#         #     {
#         #         "question": "list blocks of an invoice",
#         #         "sql": """
#         #             SELECT BLOCK_HEADER_ID, DIARY_HEADER_ID, CLAIM_TOTAL, VERIFIED_AMOUNT,
#         #                    RATE_VALID_FROM, RATE_VALID_TO
#         #             FROM CPPA_CA.BLOCKS_HEADER_INTERFACE
#         #             WHERE DIARY_HEADER_ID = 1001
#         #         """
#         #     },
#         #     {
#         #         "question": "show components of a block",
#         #         "sql": """
#         #             SELECT COM_HEADER_ID, COMP_NAME, COMP_VALUE, VARIFIED_AMOUNT, GST_PER
#         #             FROM CPPA_CA.COMP_HEADER_INTERFACE
#         #             WHERE BLOCK_HEADER_ID = 5001
#         #         """
#         #     },
#         #     {
#         #         "question": "latest invoice",
#         #         "sql": """
#         #             SELECT TOP 1 *
#         #             FROM CPPA_CA.DIARY_HEADER_INTERFACE
#         #             ORDER BY SUBMIT_DATE DESC
#         #         """
#         #     },
#         #     {
#         #         "question": "show all submitted invoices",
#         #         "sql": """
#         #             SELECT DIARY_HEADER_ID, VENDOR_ID, TOTAL_CLAIM, VERIFIED_AMOUNT,
#         #                    APPROVED_STATUS, SUBMIT_DATE
#         #             FROM CPPA_CA.DIARY_HEADER_INTERFACE
#         #             WHERE APPROVED_STATUS = 'Submitted'
#         #             ORDER BY SUBMIT_DATE DESC
#         #         """
#         #     },
#         #     {
#         #         "question": "list attachments of an invoice",
#         #         "sql": """
#         #             SELECT a.ATTACH_HEADER_ID, a.DIARY_HEADER_ID, a.FILE_NAME,
#         #                    a.FILE_TYPE, a.ATTACHMENT_TITLE, a.CREATION_DATE
#         #             FROM CPPA_CA.ATTACHMENT_HEADER a
#         #             WHERE a.DIARY_HEADER_ID = 1001
#         #             AND (a.bisDeleted = 0 OR a.bisDeleted IS NULL)
#         #         """
#         #     },
#         #     {
#         #         "question": "show components of an invoice with all joins",
#         #         "sql": """
#         #             SELECT d.DIARY_HEADER_ID, d.TOTAL_CLAIM, d.APPROVED_STATUS,
#         #                    b.BLOCK_HEADER_ID, b.CLAIM_TOTAL,
#         #                    c.COMP_NAME, c.COMP_VALUE, c.VARIFIED_AMOUNT
#         #             FROM CPPA_CA.DIARY_HEADER_INTERFACE d
#         #             INNER JOIN CPPA_CA.BLOCKS_HEADER_INTERFACE b
#         #                 ON b.DIARY_HEADER_ID = d.DIARY_HEADER_ID
#         #             INNER JOIN CPPA_CA.COMP_HEADER_INTERFACE c
#         #                 ON c.BLOCK_HEADER_ID = b.BLOCK_HEADER_ID
#         #             WHERE d.DIARY_HEADER_ID = 1001
#         #         """
#         #     },
#         #     {
#         #         "question": "show differential invoice blocks",
#         #         "sql": """
#         #             SELECT dp.DIFF_PAR_ID_PK, dp.DIARY_HEADER_ID_FK, dp.CLAIM_AMOUNT,
#         #                    dp.CURRENT_CLAIM, dp.INVOICE_TYPE, dp.PAR_INV_PER_FRM, dp.PAR_INV_PER_TO
#         #             FROM WP_GC_INV_DIFF_PARENT dp
#         #             WHERE dp.DIARY_HEADER_ID_FK = 1001
#         #         """
#         #     },
#         #     {
#         #         "question": "show interest invoice components",
#         #         "sql": """
#         #             SELECT id.INT_DET_ID_PK, id.PAYMENT_DATE, id.NO_OF_DAYS,
#         #                    id.AMOUNT_PAID, id.INTEREST_RATE, id.INTEREST_AMOUNT
#         #             FROM CPPA_CA.WP_GC_INTEREST_DETAIL id
#         #             WHERE id.HEADER_ID_FK = 1001
#         #         """
#         #     },
#         #     {
#         #         "question": "show ERP payment details for an invoice",
#         #         "sql": """
#         #             SELECT WP_GC_ERP_INVOICES_PK, DIARY_NO, TRANSACTION_NO,
#         #                    TOTAL_CLAIMED_AMOUNT, TOTAL_VERIFIED_AMOUNT,
#         #                    PAID_AMOUNT, OUTSTANDING_BALANCE_AMOUNT, PAYMENT_STATUS
#         #             FROM CPPA_CA.WP_GC_ERP_INVOICES
#         #             WHERE TRANSACTION_NO = 'TXN001'
#         #         """
#         #     },
#         #     {
#         #         "question": "list all PPAs",
#         #         "sql": """
#         #             SELECT HEADER_ID_PK, DOCUMENT_NO, DOCUMENT_DATE,
#         #                    CONTRACTED_CAPACITY, APPROVAL_STATUS, EFFECTIVE_FROM, EFFECTIVE_TO
#         #             FROM CPPA_CA.PPA_HEADER
#         #             WHERE APPROVAL_STATUS = 'Approved'
#         #             ORDER BY DOCUMENT_DATE DESC
#         #         """
#         #     },
#         #     {
#         #         "question": "show supplier details",
#         #         "sql": """
#         #             SELECT VENDOR_ID, VENDOR_NAME, VENDOR_NAME_ALT,
#         #                    ENABLED_FLAG, START_DATE_ACTIVE, END_DATE_ACTIVE
#         #             FROM CPPA_CA.AP_SUPPLIERS
#         #             WHERE ENABLED_FLAG = 'Y'
#         #             ORDER BY VENDOR_NAME
#         #         """
#         #     }
#         # ],
#     },

# }




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
            • MtCommitteeHeader_Id        – links the meeting to its committee""",

             # ── AGENDAS ────────────────────────────────────────────
            """Meeting agendas are stored in MtMeetingAgenda.  Every column is prefixed
            with MtMeetingAgenda_.  An agenda (also called topic, point, discussion item,
            task, kya discuss hua, agenda item, agendaa, agnda, ageda) belongs to a meeting
            through the foreign key MtMeetingHeader_Id.  Key columns:
            • MtMeetingAgenda_Id        – primary key
            • MtMeetingHeader_Id        – foreign key linking to MtMeetingHeader
            • MtMeetingAgenda_Title     – title / name of the agenda item
            • MtMeetingAgenda_CreatedOn – creation timestamp
            • MtMeetingAgenda_Isdeleted – soft-delete flag (always filter = 0)""",

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
            • MtCommitteeUsers_RoleCode  – role of the person: 'Secretary', 'Convener', 'Member', 'participant'.
            • MtCommitteeUsers_IsDeleted – soft-delete (filter = 0)

            To find members/users of a committee join MtCommitteeUsers with RuUsers.
            Do NOT use imaginary tables like MtMeetingUsers or MtCommitteeMembers.

            Meeting profiles are linked to committees through RuMeetingProfile via
            RuMeetingProfile_Id. Meeting profile names are in RuMeetingProfile_Name.""",

                        # ── DOCUMENTS & ATTACHMENTS ────────────────────────────
                        """Files, attachments, documents (also: docs, upload, kagaz, file, attchment,
            atachment) are stored in MtAttachment.  Key columns:
            • MtAttachment_FileName      – file name
            • MtAttachment_FileExtension – file extension
            • MtAttachment_EcmFileId     – ECM / document management ID
            • MtAttachment_Source        – type of parent record (e.g. 'MeetingAgenda', 'MoM' , 'SharedDocument', 'MoM_Miscellaneous')
            • MtAttachment_SourceId      – ID of the parent record
            • MtAttachment_IsDeleted     – soft-delete (filter = 0)
            Link attachments using MtAttachment_Source and MtAttachment_SourceId.

            IMPORTANT:
            • Meeting attachments are linked DIRECTLY to MtMeetingHeader.
            • Use MtAttachment_SourceId = MtMeetingHeader_Id when retrieving attachments of a meeting.
            • Do NOT assume meeting attachments are linked through MtMeetingAgenda.
            • For queries such as:
            - "show meeting attachments"
            - "attachments of the latest meeting"
            - "attachments of the second last meeting"
            - "files attached to meeting X"
            join MtAttachment directly with MtMeetingHeader using:
                MtAttachment_SourceId = MtMeetingHeader_Id
            and MtAttachment_IsDeleted = 0.

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
                "question": "when was the last meeting held?",
                "sql": """
                    SELECT 
                        m.MtMeetingHeader_Id,
                        m.MtMeetingHeader_Title,
                        m.MtMeetingHeader_MeetingDate,
                        m.MtMeetingHeader_MeetingStartTime,
                        m.MtCommitteeHeader_Id
                    FROM MtMeetingHeader AS m
                    WHERE m.MtMeetingHeader_Isdeleted = 0
                    AND m.MtMeetingHeader_MeetingDate = (
                            SELECT MAX(MtMeetingHeader_MeetingDate)
                            FROM MtMeetingHeader
                            WHERE MtMeetingHeader_Isdeleted = 0
                    )
                    ORDER BY m.MtCommitteeHeader_Id, m.MtMeetingHeader_Id;
                """
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
                "question": "Are there any attachments linked with the meetings held on 2026-06-13 titled 'asd' and '11 june meeting with agenda items'?",
                "sql": """
                    SELECT 
                        m.MtMeetingHeader_Id,
                        m.MtMeetingHeader_Title,
                        m.MtMeetingHeader_MeetingDate,
                        att.MtAttachment_Id,
                        att.MtAttachment_Source,
                        att.MtAttachment_SourceId,
                        att.MtAttachment_FileName,
                        att.MtAttachment_FileExtension,
                        att.MtAttachment_EcmFileId,
                        att.MtAttachment_FileSizeBytes,
                        att.MtAttachment_CreatedOn
                    FROM MtMeetingHeader AS m
                    LEFT JOIN MtAttachment AS att
                        ON att.MtAttachment_SourceId = m.MtMeetingHeader_Id
                    AND att.MtAttachment_IsDeleted = 0
                    WHERE m.MtMeetingHeader_Isdeleted = 0
                    AND m.MtMeetingHeader_MeetingDate = '2026-06-13'
                    AND (
                            m.MtMeetingHeader_Title LIKE '%asd%'
                            OR m.MtMeetingHeader_Title LIKE '%11 june meeting with agenda items%'
                        );
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
                "question": "list attachments of meeting with title like '4J Meeting'",
                "sql": """
                    SELECT m.MtMeetingHeader_Id,
                    m.MtMeetingHeader_Title,
                    d.MtAttachment_SourceId,
                    d.MtAttachment_FileName,
                    d.MtAttachment_CreatedOn
                FROM MtMeetingHeader AS m
                INNER JOIN [MtAttachment] AS d
                    ON m.MtMeetingHeader_Id = d.MtAttachment_SourceId
                WHERE m.MtMeetingHeader_Isdeleted = 0
                AND d.MtAttachment_IsDeleted = 0
                AND m.MtMeetingHeader_Title LIKE '%4J Meeting%'
                """
            },
            {
                "question": "name all the meetings that are scheduled in location CPPAOFFICEISLAMABAD",
                "sql": """    
                    SELECT 
                        MtMeetingHeader_Id,
                        MtMeetingHeader_Title,
                        MtMeetingHeader_MeetingDate,
                        MtMeetingHeader_MeetingStartTime,
                        MtMeetingHeader_Organizer,
                        MtMeetingHeader_Description,
                        MtMeetingHeader_Meeting_Link,
                        LuMeetingSphereLookups_StatusCode,
                        MtMeetingHeader_OtherAddress
                    FROM MtMeetingHeader
                    WHERE MtMeetingHeader_Isdeleted = 0
                    AND LuMeetingSphereLookups_LocationCode = 'CPPAOFFICEISLAMABAD'
                """
            },
            {
                "question": "list attachments of 4J meeting",
                "sql": """
                    SELECT m.MtMeetingHeader_Id,
                    m.MtMeetingHeader_Title,
                    d.MtAttachment_SourceId,
                    d.MtAttachment_FileName,
                    d.MtAttachment_CreatedOn
                FROM MtMeetingHeader AS m
                INNER JOIN [MtAttachment] AS d
                    ON m.MtMeetingHeader_Id = d.MtAttachment_SourceId
                WHERE m.MtMeetingHeader_Isdeleted = 0
                AND d.MtAttachment_IsDeleted = 0
                AND m.MtMeetingHeader_Title LIKE '%4J Meeting%'
                """
            },
            {
                "question": "how many shared documents are available with committee Engro Power",
                "sql": """
                    SELECT 
                        c.MtCommitteeHeader_Id,
                        c.MtCommitteeHeader_Name,
                        sd.MtSharedDocumentsHeader_Id,
                        sd.MtSharedDocumentsHeader_Title,
                        att.MtAttachment_Id,
                        att.MtAttachment_FileName,
                        att.MtAttachment_FileExtension,
                        att.MtAttachment_FileSizeBytes,
                        att.MtAttachment_EcmFileId,
                        att.MtAttachment_CreatedOn
                    FROM MtCommitteeHeader AS c
                    INNER JOIN MtDocumentCommittee AS dc
                        ON dc.MtCommitteeHeader_Id = c.MtCommitteeHeader_Id
                    INNER JOIN MtSharedDocumentsHeader AS sd
                        ON sd.MtSharedDocumentsHeader_Id = dc.MtSharedDocumentsHeader_Id
                    LEFT JOIN MtAttachment AS att
                        ON att.MtAttachment_Source = 'SharedDocument'
                    AND att.MtAttachment_SourceId = sd.MtSharedDocumentsHeader_Id
                    WHERE c.MtCommitteeHeader_Isdeleted = 0
                    AND ISNULL(dc.MtDocumentCommittee_IsDeleted, 0) = 0
                    AND sd.MtSharedDocumentsHeader_IsDeleted = 0
                    AND att.MtAttachment_IsDeleted = 0
                    AND c.MtCommitteeHeader_Name LIKE '%Engro Power%';
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


    # ========================= CDXP =========================
    "it_cdxp": {
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

        # "qa_pairs": [
        #     {
        #         "question": "show invoices of a vendor",
        #         "sql": """
        #             SELECT DIARY_HEADER_ID, VENDOR_ID, TOTAL_CLAIM, VERIFIED_AMOUNT,
        #                    APPROVED_STATUS, SUBMIT_DATE, INVOICE_PERIOD_FROM, INVOICE_PERIOD_TO
        #             FROM CPPA_CA.DIARY_HEADER_INTERFACE
        #             WHERE VENDOR_ID = 101
        #             ORDER BY SUBMIT_DATE DESC
        #         """
        #     },
        #     {
        #         "question": "list blocks of an invoice",
        #         "sql": """
        #             SELECT BLOCK_HEADER_ID, DIARY_HEADER_ID, CLAIM_TOTAL, VERIFIED_AMOUNT,
        #                    RATE_VALID_FROM, RATE_VALID_TO
        #             FROM CPPA_CA.BLOCKS_HEADER_INTERFACE
        #             WHERE DIARY_HEADER_ID = 1001
        #         """
        #     },
        #     {
        #         "question": "show components of a block",
        #         "sql": """
        #             SELECT COM_HEADER_ID, COMP_NAME, COMP_VALUE, VARIFIED_AMOUNT, GST_PER
        #             FROM CPPA_CA.COMP_HEADER_INTERFACE
        #             WHERE BLOCK_HEADER_ID = 5001
        #         """
        #     },
        #     {
        #         "question": "latest invoice",
        #         "sql": """
        #             SELECT TOP 1 *
        #             FROM CPPA_CA.DIARY_HEADER_INTERFACE
        #             ORDER BY SUBMIT_DATE DESC
        #         """
        #     },
        #     {
        #         "question": "show all submitted invoices",
        #         "sql": """
        #             SELECT DIARY_HEADER_ID, VENDOR_ID, TOTAL_CLAIM, VERIFIED_AMOUNT,
        #                    APPROVED_STATUS, SUBMIT_DATE
        #             FROM CPPA_CA.DIARY_HEADER_INTERFACE
        #             WHERE APPROVED_STATUS = 'Submitted'
        #             ORDER BY SUBMIT_DATE DESC
        #         """
        #     },
        #     {
        #         "question": "list attachments of an invoice",
        #         "sql": """
        #             SELECT a.ATTACH_HEADER_ID, a.DIARY_HEADER_ID, a.FILE_NAME,
        #                    a.FILE_TYPE, a.ATTACHMENT_TITLE, a.CREATION_DATE
        #             FROM CPPA_CA.ATTACHMENT_HEADER a
        #             WHERE a.DIARY_HEADER_ID = 1001
        #             AND (a.bisDeleted = 0 OR a.bisDeleted IS NULL)
        #         """
        #     },
        #     {
        #         "question": "show components of an invoice with all joins",
        #         "sql": """
        #             SELECT d.DIARY_HEADER_ID, d.TOTAL_CLAIM, d.APPROVED_STATUS,
        #                    b.BLOCK_HEADER_ID, b.CLAIM_TOTAL,
        #                    c.COMP_NAME, c.COMP_VALUE, c.VARIFIED_AMOUNT
        #             FROM CPPA_CA.DIARY_HEADER_INTERFACE d
        #             INNER JOIN CPPA_CA.BLOCKS_HEADER_INTERFACE b
        #                 ON b.DIARY_HEADER_ID = d.DIARY_HEADER_ID
        #             INNER JOIN CPPA_CA.COMP_HEADER_INTERFACE c
        #                 ON c.BLOCK_HEADER_ID = b.BLOCK_HEADER_ID
        #             WHERE d.DIARY_HEADER_ID = 1001
        #         """
        #     },
        #     {
        #         "question": "show differential invoice blocks",
        #         "sql": """
        #             SELECT dp.DIFF_PAR_ID_PK, dp.DIARY_HEADER_ID_FK, dp.CLAIM_AMOUNT,
        #                    dp.CURRENT_CLAIM, dp.INVOICE_TYPE, dp.PAR_INV_PER_FRM, dp.PAR_INV_PER_TO
        #             FROM WP_GC_INV_DIFF_PARENT dp
        #             WHERE dp.DIARY_HEADER_ID_FK = 1001
        #         """
        #     },
        #     {
        #         "question": "show interest invoice components",
        #         "sql": """
        #             SELECT id.INT_DET_ID_PK, id.PAYMENT_DATE, id.NO_OF_DAYS,
        #                    id.AMOUNT_PAID, id.INTEREST_RATE, id.INTEREST_AMOUNT
        #             FROM CPPA_CA.WP_GC_INTEREST_DETAIL id
        #             WHERE id.HEADER_ID_FK = 1001
        #         """
        #     },
        #     {
        #         "question": "show ERP payment details for an invoice",
        #         "sql": """
        #             SELECT WP_GC_ERP_INVOICES_PK, DIARY_NO, TRANSACTION_NO,
        #                    TOTAL_CLAIMED_AMOUNT, TOTAL_VERIFIED_AMOUNT,
        #                    PAID_AMOUNT, OUTSTANDING_BALANCE_AMOUNT, PAYMENT_STATUS
        #             FROM CPPA_CA.WP_GC_ERP_INVOICES
        #             WHERE TRANSACTION_NO = 'TXN001'
        #         """
        #     },
        #     {
        #         "question": "list all PPAs",
        #         "sql": """
        #             SELECT HEADER_ID_PK, DOCUMENT_NO, DOCUMENT_DATE,
        #                    CONTRACTED_CAPACITY, APPROVAL_STATUS, EFFECTIVE_FROM, EFFECTIVE_TO
        #             FROM CPPA_CA.PPA_HEADER
        #             WHERE APPROVAL_STATUS = 'Approved'
        #             ORDER BY DOCUMENT_DATE DESC
        #         """
        #     },
        #     {
        #         "question": "show supplier details",
        #         "sql": """
        #             SELECT VENDOR_ID, VENDOR_NAME, VENDOR_NAME_ALT,
        #                    ENABLED_FLAG, START_DATE_ACTIVE, END_DATE_ACTIVE
        #             FROM CPPA_CA.AP_SUPPLIERS
        #             WHERE ENABLED_FLAG = 'Y'
        #             ORDER BY VENDOR_NAME
        #         """
        #     }
        # ],
    },

    # ========================= LCM =========================
        "it_lcm": {
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
            """

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
    },
}
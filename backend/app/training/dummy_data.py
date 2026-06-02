"""app/training/dummy_data.py – placeholder Q&A pairs and documentation per instance.
Replace these with real domain knowledge later.
"""

DUMMY_TRAINING: dict[str, dict] = {
    # "hr_policies": {
    #     "documentation": [
    #         "This database contains company HR policy documents, employee handbooks, and compliance guidelines.",
    #         "The Policies table stores official policy documents with fields: PolicyID, Title, Category, EffectiveDate, Content, ApprovedBy.",
    #         "The PolicyCategories table has: CategoryID, CategoryName (e.g. Leave, Conduct, Safety).",
    #     ],
    #     "qa_pairs": [
    #         {
    #             "question": "How many policies are currently active?",
    #             "sql": "SELECT COUNT(*) AS active_policy_count FROM Policies WHERE Status = 'Active'",
    #         },
    #         {
    #             "question": "List all leave-related policies",
    #             "sql": "SELECT p.Title, p.EffectiveDate FROM Policies p JOIN PolicyCategories pc ON p.CategoryID = pc.CategoryID WHERE pc.CategoryName = 'Leave'",
    #         },
    #         {
    #             "question": "Who approved the most recent policy?",
    #             "sql": "SELECT TOP 1 ApprovedBy, Title, EffectiveDate FROM Policies ORDER BY EffectiveDate DESC",
    #         },
    #     ],
    # },

    # "hr_salaries": {
    #     "documentation": [
    #         "This instance covers compensation data including salary bands, pay grades, and employee salary records.",
    #         "The SalaryBands table has: BandID, Grade, MinSalary, MaxSalary, Currency.",
    #         "The EmployeeSalaries table has: EmpID, BandID, CurrentSalary, LastReviewDate, Department.",
    #         "Sensitive data – only hr_admin role has access.",
    #     ],
    #     "qa_pairs": [
    #         {
    #             "question": "What is the average salary by department?",
    #             "sql": "SELECT Department, AVG(CurrentSalary) AS AvgSalary FROM EmployeeSalaries GROUP BY Department ORDER BY AvgSalary DESC",
    #         },
    #         {
    #             "question": "Which employees are paid above the maximum of their salary band?",
    #             "sql": """
    #                 SELECT es.EmpID, es.CurrentSalary, sb.MaxSalary, sb.Grade
    #                 FROM EmployeeSalaries es
    #                 JOIN SalaryBands sb ON es.BandID = sb.BandID
    #                 WHERE es.CurrentSalary > sb.MaxSalary
    #             """,
    #         },
    #         {
    #             "question": "Show salary band ranges for all grades",
    #             "sql": "SELECT Grade, MinSalary, MaxSalary, Currency FROM SalaryBands ORDER BY MinSalary",
    #         },
    #     ],
    # },

    "it_meetingsphere": {
        "documentation": [
            # ================= CORE SYSTEM =================
            "MeetingsPortal database contains meetings, users, committees, agendas, MOM, and documents.",
            "All tables use IsDeleted flag (0 = active, 1 = deleted).",
            "Soft-delete synonyms: deleted, removed, archived, inactive record, trash.",
            "Always filter by IsDeleted = 0 (or *Isdeleted* / *IsDeleted* columns) to exclude deleted records.",
            "For date-only comparisons in SQL Server, use CAST(column AS DATE).",
            "Use TOP N instead of LIMIT in SQL Server.",
            "GETDATE() returns current datetime in SQL Server.",

            # ================= MEETINGS =================
            "Meetings are stored in MtMeetingHeader.",
            "The main meeting table is MtMeetingHeader with columns prefixed with MtMeetingHeader_.",
            "Meeting agendas are stored in MtMeetingAgenda with columns prefixed with MtMeetingAgenda_.",
            "Join meetings and agendas using MtMeetingHeader_Id as the foreign key.",

            "Meeting synonyms: meeting, session, meetup, meet up, gathering, bethak, conference.",
            "Meeting title synonyms: title, subject, heading, topic name.",
            "Meeting description synonyms: description, detail, details, agenda summary.",
            "Meeting organizer synonyms: organizer, host, created by, creator, arranged by.",

            "Date synonyms: date, meeting date, din, tareekh.",
            "Time synonyms: time, waqt, timing, start time, end time, duration.",
            "Upcoming synonyms: upcoming, next, future, aanay wali.",
            "Past synonyms: previous, last, pehle wali, already happened.",
            "Today synonyms: today, aaj, aj.",
            "Yesterday synonyms: yesterday, kal (past).",
            "Tomorrow synonyms: tomorrow, kal (future).",
            "This week synonyms: this week, iss haftay, is week.",
            "This month synonyms: this month, iss mahine, is month.",
            "Next week synonyms: next week, aglay haftay, coming week.",
            "Next month synonyms: next month, aglay mahine, coming month.",

            "Meeting status is stored in LuMeetingSphereLookups_StatusCode column.",
            "Status synonyms: status, state, halat, situation.",
            "Common status values are: Draft, Published, Cancelled, Completed, InProgress.",
            "Draft synonyms: draft, drafted, draft version, in draft, not published yet.",
            "Published synonyms: published, release, released, live, announced.",
            "Cancelled synonyms: cancelled, canceled, cancel, stopped.",
            "Completed synonyms: completed, done, finished, ended, ho chuki.",
            "InProgress synonyms: in progress, ongoing, running, chal rahi.",

            # ================= ACTIVE / INACTIVE (0/1) STATUS FLAGS =================
            "Many modules (user management, committee management, meeting profile, meeting management) store active status as a 0/1 flag in a Status or IsActive column.",
            "Status mapping (0/1): 0 = Inactive/Disabled, 1 = Active/Enabled.",
            "Active synonyms: active, enabled, on, valid, running.",
            "Inactive synonyms: inactive, disabled, off, not active, blocked.",
            "Pending synonyms: pending, waiting, in review, not approved yet.",

            # ================= USERS / EMPLOYEES =================
            "Users/employees are stored in RuUsers (people, staff, employees, users, members).",
            "Common user synonyms: user, users, employee, employees, staff, worker, workers, people, members, persons.",
            "In this DB, organization code for a user is stored in RuOrganizations_Code (e.g. RuOrganizations_Code = 'CPPA').",

            # ================= GENDER =================
            "Gender stored in RuUsers_GenderCode: F = Female, M = Male.",

            "Female synonyms: female, females, woman, women, girl, girls, lady, ladies.",
            "Pakistani/Roman Urdu: larki, larkiyan, aurat, auratein, khawateen.",
            "Misspellings: femlae, femail, grils, girs, femal.",
            "If the user asks 'how many larki' or 'how many girls' or 'how many girs', treat it as a count of female users (RuUsers_GenderCode = 'F').",

            "Male synonyms: male, males, man, men, boy, boys.",
            "Pakistani/Roman Urdu: larka, larkay, mard, aadmi.",
            "Misspellings: mal, mle, boi, mens.",
            "If the user asks 'how many larka' or 'how many boys', treat it as a count of male users (RuUsers_GenderCode = 'M').",

            # ================= MEETING PROFILE =================
            "Meeting profile includes organization name, profile name, effective dates, creation date, status.",

            "Synonyms: profile, meeting profile, setup, configuration, meeting type.",
            "Organization synonyms: organization, org, company, department, dept.",
            "Profile name synonyms: profile name, meeting type name.",
            "Effective from synonyms: start date, from date, shuru date.",
            "Effective to synonyms: end date, to date, khatam date.",
            "Creation date synonyms: created date, banane ki date.",
            "Active/inactive synonyms: active, inactive, pending, enabled, disabled.",

            # ================= COMMITTEE =================
            "Committee contains name, roles, organization, status.",

            "Committee synonyms: committee, group, team, panel.",
            "Roles synonyms:",
            "secretary: secretary, secratry, secritary.",
            "convener: convener, convenor, head, lead.",
            "member: member, staff, user, banda.",
            "participant: participant, attendee, joiner.",
            "Pakistani: log, banda, team members.",

            # ================= AGENDA =================
            "Agenda contains meeting discussion points.",

            "Agenda synonyms: agenda, topics, points, discussion, items, tasks.",
            "Pakistani: kya discuss hua, points, topics.",
            "Agenda misspellings: agendaa, agnda, ageda.",

            # ================= MOM =================
            "Minutes of Meeting (MOM) contains meeting summary.",

            "MOM synonyms: minutes, notes, summary, meeting record.",
            "Pakistani: meeting notes, kya hua meeting mein.",
            "MOM misspellings: minits, momm, minutez.",

            # ================= DOCUMENTS =================
            "Documents include files, attachments, records.",

            "Document synonyms: document, file, attachment, record, docs, upload.",
            "Pakistani: file, kagaz, documents.",
            "Misspellings: documnt, filess, attchment, atachment.",
            "Shared documents synonyms: shared documents, shared files, common documents, public documents, attachments section.",
            "Shared documents are stored in MtSharedDocumentsHeader.",
            "Files/attachments are stored in MtAttachment. Link attachments using MtAttachment_Source and MtAttachment_SourceId.",
            "MtAttachment_Source examples include: MeetingAgenda, SharedDocument. MtAttachment_SourceId is the related record id.",

            # ================= COMMITTEE USERS / MEETING USERS =================
            "Committee users and meeting users are stored in MtCommitteeUsers.",
            "To list users for a committee or a meeting, query MtCommitteeUsers (then join RuUsers if names are needed).",
            "Do NOT use non-existing tables like MtMeetingUsers or MtCommitteeMembers.",
            "When joining multiple tables, always use aliases (m., a., att.) to avoid ambiguous column names.",
        ],
        "qa_pairs": [
            {
            "question": "how many agendas are created till today",
            "sql": " SELECT COUNT(*) AS TotalAgendas FROM MtMeetingAgenda WHERE MtMeetingAgenda_Isdeleted = 0 AND MtMeetingAgenda_CreatedOn <= GETDATE()"
        },
        {
            "question": "give details of meeting id 22",
            "sql": "SELECT MtMeetingHeader_Id, MtMeetingHeader_Title, MtMeetingHeader_MeetingDate, MtMeetingHeader_MeetingStartTime, MtMeetingHeader_Organizer, MtMeetingHeader_Description, MtMeetingHeader_Meeting_Link, LuMeetingSphereLookups_StatusCode, MtMeetingHeader_OtherAddress FROM MtMeetingHeader WHERE MtMeetingHeader_Id = 22 AND MtMeetingHeader_Isdeleted = 0"
        },
        {
            "question": "was there any agenda attached in meeting header id 262",
            "sql": "SELECT m.MtMeetingHeader_Id, m.MtMeetingHeader_Title, a.MtMeetingAgenda_Id, a.MtMeetingAgenda_Title FROM MtMeetingHeader m LEFT JOIN MtMeetingAgenda a ON m.MtMeetingHeader_Id = a.MtMeetingHeader_Id WHERE m.MtMeetingHeader_Id = 262 AND m.MtMeetingHeader_Isdeleted = 0 AND a.MtMeetingAgenda_Isdeleted = 0"
        },
        {
            "question": "list the shared documents",
            "sql": "SELECT sd.* FROM MtSharedDocumentsHeader sd WHERE sd.MtSharedDocumentsHeader_IsDeleted = 0"
        },
        {
            "question": "list the shared documents with file names",
            "sql": "SELECT sd.MtSharedDocumentsHeader_Id, att.MtAttachment_FileName, att.MtAttachment_FileExtension, att.MtAttachment_EcmFileId FROM MtSharedDocumentsHeader sd LEFT JOIN MtAttachment att ON att.MtAttachment_Source = 'SharedDocument' AND att.MtAttachment_SourceId = sd.MtSharedDocumentsHeader_Id WHERE sd.MtSharedDocumentsHeader_IsDeleted = 0 AND att.MtAttachment_IsDeleted = 0"
        },
        {
            "question": "what is the status of meeting id 258",
            "sql": "SELECT m.MtMeetingHeader_Id, m.MtMeetingHeader_Title, m.LuMeetingSphereLookups_StatusCode FROM MtMeetingHeader m WHERE m.MtMeetingHeader_Id = 258 AND m.MtMeetingHeader_Isdeleted = 0"
        },
        {
            "question": "how many females work here",
            "sql": "SELECT COUNT(*) AS female_count FROM RuUsers WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'F'"
        },
        {
            "question": "how many larki",
            "sql": "SELECT COUNT(*) AS female_count FROM RuUsers WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'F'"
        },
        {
            "question": "how many girs",
            "sql": "SELECT COUNT(*) AS female_count FROM RuUsers WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'F'"
        },
        {
            "question": "how many males work here",
            "sql": "SELECT COUNT(*) AS male_count FROM RuUsers WHERE RuUsers_IsDeleted = 0 AND RuUsers_GenderCode = 'M'"
        },
        {
            "question": "Show upcoming meetings",
            "sql": "SELECT MtMeetingHeader_Id, MtMeetingHeader_Title, MtMeetingHeader_MeetingDate, MtMeetingHeader_MeetingStartTime, MtMeetingHeader_Organizer, MtMeetingHeader_Description, MtMeetingHeader_Meeting_Link, LuMeetingSphereLookups_StatusCode, MtMeetingHeader_OtherAddress FROM MtMeetingHeader WHERE  MtMeetingHeader_MeetingDate >= CAST(GETDATE() AS DATE) AND MtMeetingHeader_Isdeleted = 0 ORDER BY MtMeetingHeader_MeetingDate ASC"
        }
        ],
    },

    # "it_rms": {
    #     "documentation": [
    #         "RMS (Resource Management System) tracks project resources, allocations, and utilisation on Azure SQL.",
    #         "Key tables: Projects (ProjectID, Name, StartDate, EndDate, Status, BudgetUSD), Resources (ResourceID, Name, Role, Department, HourlyRate), Allocations (AllocationID, ProjectID, ResourceID, AllocatedHours, StartDate, EndDate), Timesheets (TimesheetID, ResourceID, ProjectID, WeekStart, HoursLogged).",
    #     ],
    #     "qa_pairs": [
    #         {
    #             "question": "Which projects are currently over budget?",
    #             "sql": """
    #                 SELECT p.Name, p.BudgetUSD,
    #                     SUM(r.HourlyRate * t.HoursLogged) AS actual_cost
    #                 FROM Projects p
    #                 JOIN Timesheets t ON p.ProjectID = t.ProjectID
    #                 JOIN Resources r ON t.ResourceID = r.ResourceID
    #                 WHERE p.Status = 'Active'
    #                 GROUP BY p.ProjectID, p.Name, p.BudgetUSD
    #                 HAVING SUM(r.HourlyRate * t.HoursLogged) > p.BudgetUSD
    #             """,
    #         },
    #         {
    #             "question": "Show resource utilisation for the current month",
    #             "sql": """
    #                 SELECT r.Name, r.Role,
    #                     SUM(t.HoursLogged) AS hours_logged_this_month
    #                 FROM Resources r
    #                 JOIN Timesheets t ON r.ResourceID = t.ResourceID
    #                 WHERE MONTH(t.WeekStart) = MONTH(GETDATE()) AND YEAR(t.WeekStart) = YEAR(GETDATE())
    #                 GROUP BY r.ResourceID, r.Name, r.Role
    #                 ORDER BY hours_logged_this_month DESC
    #             """,
    #         },
    #         {
    #             "question": "List resources allocated to more than 2 active projects",
    #             "sql": """
    #                 SELECT r.Name, COUNT(DISTINCT a.ProjectID) AS active_projects
    #                 FROM Resources r
    #                 JOIN Allocations a ON r.ResourceID = a.ResourceID
    #                 JOIN Projects p ON a.ProjectID = p.ProjectID
    #                 WHERE p.Status = 'Active'
    #                 GROUP BY r.ResourceID, r.Name
    #                 HAVING COUNT(DISTINCT a.ProjectID) > 2
    #             """,
    #         },
    #     ],
    # },
}
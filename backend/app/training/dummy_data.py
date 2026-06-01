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
        "The MeetingsPortal database stores information about meetings, attendees, and schedules.",
        "Meetings can have multiple participants and are associated with specific dates and times.",
        "Users can create, update, and view meetings they are involved in.",
        "The main meeting table is MtMeetingHeader with columns prefixed with MtMeetingHeader_",
        "Meeting agendas are stored in MtMeetingAgenda table with columns prefixed with MtMeetingAgenda_",
        "All tables use soft deletes with an Isdeleted column (0=active, 1=deleted)",
        "Always filter by MtMeetingHeader_Isdeleted = 0 to exclude deleted records",
        "Meeting status is stored in LuMeetingSphereLookups_StatusCode column",
        "Common status values are: Draft, Published, Cancelled, Completed, InProgress",
        "For date comparisons, use CAST(column AS DATE) to compare dates only",
        "The MeetingDate column stores the full meeting date and time",
        "Use TOP N instead of LIMIT for limiting results in SQL Server",
        "GETDATE() returns current datetime in SQL Server",
        "For text search, use LIKE with % wildcards: column LIKE '%search%'",
        "Join meetings and agendas using MtMeetingHeader_Id as the foreign key"
    ],
        "qa_pairs": [
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
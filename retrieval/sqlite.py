import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
connection = sqlite3.connect("inventers.db")
cursor = connection.cursor()

# Drop tables if they already exist (for re-runs)
cursor.execute("DROP TABLE IF EXISTS CEO")
cursor.execute("DROP TABLE IF EXISTS DEPARTMENT")
cursor.execute("DROP TABLE IF EXISTS MANAGER")
cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")
cursor.execute("DROP TABLE IF EXISTS PROJECT")
cursor.execute("DROP TABLE IF EXISTS TASK")
cursor.execute("DROP TABLE IF EXISTS INTERVIEW")
cursor.execute("DROP TABLE IF EXISTS CLIENT")

# Create tables
cursor.execute("""
CREATE TABLE CEO (
    CEO_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    EMAIL VARCHAR(50)
)
""")

cursor.execute("""
CREATE TABLE DEPARTMENT (
    DEPT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(30)
)
""")

cursor.execute("""
CREATE TABLE MANAGER (
    MANAGER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    DEPT_ID INTEGER,
    EMAIL VARCHAR(50),
    FOREIGN KEY (DEPT_ID) REFERENCES DEPARTMENT(DEPT_ID)
)
""")

cursor.execute("""
CREATE TABLE EMPLOYEE (
    EMP_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    DEPT_ID INTEGER,
    MANAGER_ID INTEGER,
    ROLE VARCHAR(30),
    EMAIL VARCHAR(50),
    FOREIGN KEY (DEPT_ID) REFERENCES DEPARTMENT(DEPT_ID),
    FOREIGN KEY (MANAGER_ID) REFERENCES MANAGER(MANAGER_ID)
)
""")

cursor.execute("""
CREATE TABLE PROJECT (
    PROJECT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    DEPT_ID INTEGER,
    MANAGER_ID INTEGER,
    STATUS VARCHAR(20),
    FOREIGN KEY (DEPT_ID) REFERENCES DEPARTMENT(DEPT_ID),
    FOREIGN KEY (MANAGER_ID) REFERENCES MANAGER(MANAGER_ID)
)
""")

cursor.execute("""
CREATE TABLE TASK (
    TASK_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PROJECT_ID INTEGER,
    NAME VARCHAR(100),
    ASSIGNED_TO INTEGER,
    STATUS VARCHAR(20),
    DEADLINE DATE,
    FOREIGN KEY (PROJECT_ID) REFERENCES PROJECT(PROJECT_ID),
    FOREIGN KEY (ASSIGNED_TO) REFERENCES EMPLOYEE(EMP_ID)
)
""")

cursor.execute("""
CREATE TABLE INTERVIEW (
    INTERVIEW_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CANDIDATE_NAME VARCHAR(50),
    POSITION VARCHAR(30),
    HR_ID INTEGER,
    RESULT VARCHAR(20),
    DATE DATE,
    FOREIGN KEY (HR_ID) REFERENCES EMPLOYEE(EMP_ID)
)
""")

cursor.execute("""
CREATE TABLE CLIENT (
    CLIENT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50),
    CONTACT VARCHAR(50),
    PROJECT_ID INTEGER,
    STATUS VARCHAR(20),
    FOREIGN KEY (PROJECT_ID) REFERENCES PROJECT(PROJECT_ID)
)
""")

# Insert CEO
cursor.execute("INSERT INTO CEO (NAME, EMAIL) VALUES ('Alex Johnson', 'alex.johnson@inventers.com')")

# Insert Departments
departments = ['IT', 'Marketing', 'HR', 'Sales']
for dept in departments:
    cursor.execute("INSERT INTO DEPARTMENT (NAME) VALUES (?)", (dept,))

# Insert Managers
managers = [
    ('Priya Sharma', 1, 'priya.sharma@inventers.com'),   # IT
    ('Rahul Mehta', 2, 'rahul.mehta@inventers.com'),     # Marketing
    ('Sonal Gupta', 3, 'sonal.gupta@inventers.com'),     # HR
    ('Amit Verma', 4, 'amit.verma@inventers.com')        # Sales
]
for name, dept_id, email in managers:
    cursor.execute("INSERT INTO MANAGER (NAME, DEPT_ID, EMAIL) VALUES (?, ?, ?)", (name, dept_id, email))

# Insert Employees
employees = [
    # IT Department
    ('Anjali Rao', 1, 1, 'Backend Developer', 'anjali.rao@inventers.com'),
    ('Rohan Singh', 1, 1, 'Frontend Developer', 'rohan.singh@inventers.com'),
    ('Vikram Patel', 1, 1, 'DevOps Engineer', 'vikram.patel@inventers.com'),
    # Marketing Department
    ('Sneha Kapoor', 2, 2, 'Designer', 'sneha.kapoor@inventers.com'),
    ('Manoj Kumar', 2, 2, 'Digital Marketer', 'manoj.kumar@inventers.com'),
    ('Pooja Yadav', 2, 2, 'Content Creator', 'pooja.yadav@inventers.com'),
    # HR Department
    ('Kiran Desai', 3, 3, 'HR Executive', 'kiran.desai@inventers.com'),
    ('Ritika Jain', 3, 3, 'HR Associate', 'ritika.jain@inventers.com'),
    # Sales Department
    ('Arjun Nair', 4, 4, 'Sales Executive', 'arjun.nair@inventers.com'),
    ('Neha Sinha', 4, 4, 'Account Manager', 'neha.sinha@inventers.com')
]
for name, dept_id, manager_id, role, email in employees:
    cursor.execute("""
        INSERT INTO EMPLOYEE (NAME, DEPT_ID, MANAGER_ID, ROLE, EMAIL)
        VALUES (?, ?, ?, ?, ?)
    """, (name, dept_id, manager_id, role, email))

# Insert Projects (IT and Sales)
projects = [
    ('Website Revamp', 1, 1, 'Ongoing'),
    ('Mobile App Development', 1, 1, 'Planning'),
    ('CRM Integration', 1, 1, 'Completed'),
    ('Client Acquisition', 4, 4, 'Ongoing')
]
for name, dept_id, manager_id, status in projects:
    cursor.execute("""
        INSERT INTO PROJECT (NAME, DEPT_ID, MANAGER_ID, STATUS)
        VALUES (?, ?, ?, ?)
    """, (name, dept_id, manager_id, status))

# Insert Tasks for IT Projects
tasks = [
    # Website Revamp (Project_ID=1)
    (1, 'Design Homepage UI', 2, 'In Progress', '2025-07-20'),
    (1, 'Implement Backend APIs', 1, 'Pending', '2025-07-25'),
    (1, 'Setup CI/CD Pipeline', 3, 'Completed', '2025-07-10'),
    # Mobile App Development (Project_ID=2)
    (2, 'Design App Mockups', 2, 'Pending', '2025-08-01'),
    (2, 'Develop Authentication Module', 1, 'Pending', '2025-08-10'),
    # CRM Integration (Project_ID=3)
    (3, 'Integrate CRM with Website', 1, 'Completed', '2025-06-30'),
    # Client Acquisition (Sales Project_ID=4)
    (4, 'Prepare Client Pitch', 9, 'In Progress', '2025-07-15'),
    (4, 'Follow up with Prospects', 10, 'Pending', '2025-07-18')
]
for project_id, name, assigned_to, status, deadline in tasks:
    cursor.execute("""
        INSERT INTO TASK (PROJECT_ID, NAME, ASSIGNED_TO, STATUS, DEADLINE)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, name, assigned_to, status, deadline))

# Insert Interviews (HR)
interviews = [
    ('Ravi Kumar', 'Backend Developer', 7, 'Selected', '2025-07-01'),
    ('Meena Joshi', 'Designer', 8, 'Rejected', '2025-07-03'),
    ('Suresh Iyer', 'Sales Executive', 7, 'Selected', '2025-07-05')
]
for candidate, position, hr_id, result, date in interviews:
    cursor.execute("""
        INSERT INTO INTERVIEW (CANDIDATE_NAME, POSITION, HR_ID, RESULT, DATE)
        VALUES (?, ?, ?, ?, ?)
    """, (candidate, position, hr_id, result, date))

# Insert Clients (Sales)
clients = [
    ('ABC Corp', 'abc@client.com', 4, 'Active'),
    ('XYZ Ltd', 'xyz@client.com', 4, 'Prospect'),
    ('MegaMart', 'megamart@client.com', 3, 'Completed')
]
for name, contact, project_id, status in clients:
    cursor.execute("""
        INSERT INTO CLIENT (NAME, CONTACT, PROJECT_ID, STATUS)
        VALUES (?, ?, ?, ?)
    """, (name, contact, project_id, status))

connection.commit()
connection.close()

print("Database 'inventers.db' created and populated successfully!")

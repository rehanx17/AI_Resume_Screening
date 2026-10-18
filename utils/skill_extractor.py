
import re


# Broad IT and Computer Science skills dictionary.
# Add more skills here whenever needed.
SKILLS = [
    # Programming languages
    "Python", "Java", "JavaScript", "TypeScript",
    "C#", "C++", "C", "PHP", "Ruby", "Go",
    "Golang", "Rust", "Swift", "Kotlin", "Dart",
    "R", "Scala", "Perl", "MATLAB", "Bash",
    "PowerShell", "Assembly",

    # Web development
    "HTML", "CSS", "React", "React.js", "Angular",
    "Vue.js", "Next.js", "Node.js", "Express.js",
    "jQuery", "Bootstrap", "Tailwind CSS",
    "ASP.NET", ".NET", "Blazor", "Laravel",
    "Django", "Flask", "FastAPI", "Spring Boot",
    "Spring Framework", "Ruby on Rails",
    "REST API", "RESTful API", "GraphQL",
    "XML", "JSON", "AJAX", "WordPress",

    # Databases
    "SQL", "MySQL", "PostgreSQL", "SQLite",
    "Microsoft SQL Server", "SQL Server",
    "Oracle Database", "Oracle SQL", "PL/SQL",
    "MongoDB", "Redis", "Cassandra", "Firebase",
    "DynamoDB", "MariaDB", "Elasticsearch",
    "Database Management", "DBMS", "NoSQL",

    # Data analytics and data science
    "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Scikit-learn", "SciPy", "Power BI",
    "Microsoft Excel", "Excel", "Tableau",
    "Data Analysis", "Data Analytics", "Data Science",
    "Data Visualization", "Statistics",
    "Business Intelligence", "ETL",
    "Data Warehousing", "Apache Spark",
    "Apache Hadoop", "PySpark", "Power Query",

    # Artificial intelligence and machine learning
    "Machine Learning", "Deep Learning",
    "Artificial Intelligence", "Natural Language Processing",
    "NLP", "Computer Vision", "Generative AI",
    "Large Language Models", "LLM", "TensorFlow",
    "PyTorch", "Keras", "OpenCV", "Hugging Face",
    "Transformers", "Neural Networks", "Prompt Engineering",

    # Cloud computing and DevOps
    "AWS", "Amazon Web Services", "Microsoft Azure",
    "Google Cloud Platform", "GCP",
    "Docker", "Kubernetes", "Jenkins",
    "GitHub Actions", "CI/CD", "Terraform",
    "Ansible", "Linux", "Unix", "Nginx",
    "Apache", "Serverless", "DevOps",

    # Version control and development tools
    "Git", "GitHub", "GitLab", "Bitbucket",
    "Jira", "VS Code", "Visual Studio",
    "IntelliJ IDEA", "Eclipse", "PyCharm",
    "Postman", "Swagger", "Maven", "Gradle",
    "npm", "Yarn", "Vite", "Webpack",

    # Operating systems and networking
    "Windows", "Windows Server", "Linux Administration",
    "Networking", "Computer Networks", "TCP/IP",
    "DNS", "DHCP", "HTTP", "HTTPS",
    "OSI Model", "Network Security",
    "Operating Systems", "Shell Scripting",

    # Cybersecurity
    "Cybersecurity", "Information Security",
    "Ethical Hacking", "Penetration Testing",
    "OWASP", "Cryptography", "Encryption",
    "Firewalls", "Vulnerability Assessment",
    "SIEM", "Identity and Access Management",

    # Software engineering and testing
    "Software Development", "Software Engineering",
    "Object-Oriented Programming", "OOP",
    "Data Structures", "Algorithms",
    "Design Patterns", "Microservices",
    "Agile", "Scrum", "SDLC",
    "Software Testing", "Manual Testing",
    "Automation Testing", "Selenium",
    "Cypress", "Playwright", "JUnit",
    "Pytest", "Unit Testing", "Integration Testing",

    # Mobile development
    "Android Development", "Android Studio",
    "iOS Development", "Flutter",
    "React Native", "Kotlin Multiplatform",

    # Big data and distributed systems
    "Big Data", "Apache Kafka", "Apache Hive",
    "Apache Airflow", "HBase", "MapReduce",
    "HDFS", "Distributed Systems",

    # Computer science fundamentals
    "Computer Science", "Computer Architecture",
    "Compiler Design", "Theory of Computation",
    "Discrete Mathematics", "Object-Oriented Design",

    # Productivity and other IT skills
    "Microsoft Word", "Microsoft PowerPoint",
    "Communication", "Problem Solving",
    "Analytical Skills", "Project Management",
]


def _build_pattern(skill):
    """
    Build a case-insensitive pattern that handles punctuation
    in skills such as C#, C++, .NET and Node.js.
    """

    if skill == "C":
        # Match the C language without also matching C# or C++.
        return re.compile(
            r"(?<![A-Za-z0-9_])C(?![A-Za-z0-9_+#])",
            re.IGNORECASE,
        )

    escaped_skill = re.escape(skill)

    return re.compile(
        r"(?<![A-Za-z0-9_])"
        + escaped_skill
        + r"(?![A-Za-z0-9_])",
        re.IGNORECASE,
    )


# Compile patterns once when the module is imported.
SKILL_PATTERNS = [
    (skill, _build_pattern(skill))
    for skill in SKILLS
]


def extract_skills(text):
    """
    Extract recognized IT/CS skills from text.

    Returns a list of unique skill names.
    Matching is case-insensitive.
    """

    if not text:
        return []

    found_skills = []

    for skill, pattern in SKILL_PATTERNS:
        if pattern.search(text):
            found_skills.append(skill)

    return found_skills

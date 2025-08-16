import re
from io import BytesIO
from typing import Optional
import PyPDF2

# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(file_bytes: bytes) -> Optional[str]:
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text
            else:
                print(f"[WARN] No text found on page {i}")
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None

# ---------- TEXT CLEANING ----------
def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ---------- SIMPLE SKILL MATCHING ----------
def extract_fields(text: str) -> list:
    skills_keywords = [
        "Python", "Java", "C++", "JavaScript", "HTML", "CSS", "SQL", "NoSQL", "MongoDB", "PostgreSQL",
        "MySQL", "Django", "Flask", "React", "Angular", "Vue.js", "Node.js", "Express.js", "REST APIs", "GraphQL",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Git", "GitHub", "Bitbucket", "Agile",
        "Scrum", "Kanban", "Project Management", "JIRA", "Trello", "Confluence", "DevOps", "Machine Learning", "Deep Learning", "NLP",
        "Computer Vision", "TensorFlow", "Keras", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Data Analysis",
        "Data Visualization", "Big Data", "Hadoop", "Spark", "Hive", "Scala", "R", "MATLAB", "Statistics", "Linear Algebra",
        "Calculus", "Time Series Analysis", "Predictive Modeling", "Data Mining", "Tableau", "Power BI", "Looker", "Excel", "VBA", "Google Sheets",
        "Financial Analysis", "Accounting", "QuickBooks", "SAP", "Oracle", "CRM", "Salesforce", "HubSpot", "Marketing Automation", "Email Marketing",
        "SEO", "SEM", "Google Analytics", "Facebook Ads", "Instagram Marketing", "LinkedIn Ads", "Content Marketing", "Copywriting", "Creative Writing", "Technical Writing",
        "UX Design", "UI Design", "Adobe XD", "Figma", "Sketch", "Photoshop", "Illustrator", "InDesign", "Wireframing", "Prototyping",
        "Customer Service", "Client Relations", "Public Speaking", "Presentation Skills", "Negotiation", "Conflict Resolution", "Teamwork", "Leadership", "Time Management", "Problem Solving",
        "Critical Thinking", "Decision Making", "Analytical Thinking", "Strategic Planning", "Operations Management", "Logistics", "Supply Chain", "Inventory Management", "Procurement", "Lean Manufacturing",
        "Six Sigma", "Quality Assurance", "Testing", "Unit Testing", "Integration Testing", "Selenium", "Cypress", "Manual Testing", "Automated Testing", "Performance Testing",
        "Penetration Testing", "Cybersecurity", "Network Security", "Firewall Configuration", "Encryption", "Ethical Hacking", "Linux", "Windows Server", "Bash", "PowerShell",
        "System Administration", "Cloud Computing", "Cloud Security", "Virtualization", "VMware", "Hyper-V", "Technical Support", "Help Desk", "ITIL", "Business Analysis",
        "Requirements Gathering", "Process Improvement", "Change Management", "Risk Management", "Compliance", "Legal Research", "Contract Management", "Litigation", "Case Management", "Paralegal",
        "Medical Coding", "Medical Billing", "EMR", "EHR", "HIPAA", "Patient Scheduling", "Clinical Research", "Lab Techniques", "Pharmaceuticals", "Biotechnology",
        "Genetics", "Microbiology", "Chemistry", "Physics", "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Structural Analysis", "AutoCAD", "SolidWorks",
        "ANSYS", "3D Modeling", "3D Printing", "Product Design", "Manufacturing", "Welding", "CNC Programming", "Robotics", "Automation", "IoT",
        "Blockchain", "Smart Contracts", "Solidity", "Cryptocurrency", "Fintech", "Banking", "Investment Analysis", "Portfolio Management", "Wealth Management", "Insurance",
        "Real Estate", "Property Management", "Construction Management", "Blueprint Reading", "Cost Estimation", "Site Inspection", "Safety Compliance", "OSHA", "HVAC", "Plumbing",
        "Electrical Wiring", "Customer Acquisition", "Lead Generation", "Cold Calling", "Account Management", "B2B Sales", "B2C Sales", "Retail Sales", "Cash Handling", "POS Systems",
        "Hospitality", "Food Service", "Event Planning", "Bartending", "Housekeeping", "Front Desk", "Receptionist", "Data Entry", "Typing", "Transcription",
        "Translation", "Multilingual", "Spanish", "French", "German", "Mandarin", "Arabic", "Korean", "Japanese", "Sign Language",
        "Tutoring", "Teaching", "Curriculum Development", "Instructional Design", "Online Learning", "eLearning", "LMS", "EdTech", "Assessment Design", "Grading",
        "Coaching", "Mentoring", "Training", "Workshop Facilitation", "Public Relations", "Media Relations", "Journalism", "Video Editing", "Photography", "Filmmaking",
        "Cinematography", "Sound Design", "Audio Editing", "Music Production", "Voice Over", "Animation", "2D Animation", "3D Animation", "Motion Graphics", "Game Development",
        "Unity", "Unreal Engine", "Game Design", "Level Design", "AI Programming", "Physics Engines", "Storyboarding", "Narrative Design", "Scriptwriting", "Screenwriting",
        "eCommerce", "Dropshipping", "Shopify", "WooCommerce", "Magento", "WordPress", "Drupal", "Content Management", "Blogging", "Affiliate Marketing",
        "Crowdfunding", "Fundraising", "Grant Writing", "Nonprofit Management", "Volunteer Coordination", "Community Outreach", "Public Health", "Epidemiology", "Social Work", "Counseling",
        "Psychology", "Therapy", "Crisis Intervention", "Addiction Counseling", "Life Coaching", "Fitness Training", "Yoga", "Pilates", "Nutrition", "Diet Planning",
        "Meal Prep", "Cooking", "Baking", "Food Safety", "Sanitation", "Gardening", "Landscaping", "Carpentry", "Painting", "Interior Design",
        "Fashion Design", "Sewing", "Textile Design", "Merchandising", "Retail Buying", "Visual Merchandising", "Jewelry Design", "Makeup Artistry", "Hair Styling", "Skincare",
        "Tattooing", "Piercing", "Customer Insights", "User Research", "Human-Centered Design", "Service Design", "Business Intelligence", "ETL", "Data Warehousing", "Snowflake",
        "Airflow", "Databricks", "Kafka", "Redshift", "Google BigQuery", "Azure Synapse", "Informatica", "SSIS", "SSRS", "Data Governance",
        "Metadata Management", "Data Quality", "Data Stewardship", "Collaboration", "Adaptability", "Resilience", "Initiative", "Innovation", "Creativity", "Work Ethic"
    ]

    text_lower = text.lower()
    skills_found = []
    for skill in skills_keywords:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            skills_found.append(skill)
    return list(dict.fromkeys(skills_found))  # Remove duplicates, preserve order
### 📁 `models/user.py`

from pydantic import BaseModel, EmailStr

class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str  # 'student' or 'recruiter'
# ResuMatch - AI-Powered Resume-Job Matching Platform

🚀 **Status**: Live & Deployed  
📱 **Frontend**: [https://resumatch-frontend-hazel.vercel.app](https://resumatch-frontend-hazel.vercel.app)  
🔧 **Backend**: [https://resumatch-backend-q5qo.onrender.com](https://resumatch-backend-q5qo.onrender.com)  
🗄️ **Database**: MongoDB Atlas  

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Frontend-000000)](https://resumatch-frontend-hazel.vercel.app)
[![API Status](https://img.shields.io/badge/API%20Status-Backend-46e3b7)](https://resumatch-backend-q5qo.onrender.com/healthz)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717)](https://github.com/bipaulr/ResuMatch)  

## 🎯 Try It Now

### 🌐 Live Demo
**Frontend**: [https://resumatch-frontend-hazel.vercel.app](https://resumatch-frontend-hazel.vercel.app)

### 📋 Test Features:
1. **Student Experience**:
   - Create account → Upload resume → Get AI matches → Apply to jobs → Chat with recruiters
2. **Recruiter Experience**: 
   - Create account → Post jobs → Review applications → Chat with candidates
3. **AI Features**:
   - Resume analysis with skill extraction
   - Job matching algorithm
   - Mock interview questions

### 🔧 API Access
**Backend API**: [https://resumatch-backend-q5qo.onrender.com](https://resumatch-backend-q5qo.onrender.com)
- Health Check: [/healthz](https://resumatch-backend-q5qo.onrender.com/healthz)
- Interactive Docs: [/docs](https://resumatch-backend-q5qo.onrender.com/docs)
- OpenAPI Schema: [/openapi.json](https://resumatch-backend-q5qo.onrender.com/openapi.json)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Deployment Guide](#deployment-guide)
- [User Workflows](#user-workflows)
- [Contributing](#contributing)

## 🌟 Overview

ResuMatch is an intelligent platform that connects students and recruiters through AI-powered resume analysis and job matching. The platform uses Google Gemini AI to analyze resumes, match candidates with suitable jobs, and conduct mock interviews to help students prepare for real interviews.

### 🔗 Live Application
- **Frontend Application**: [https://resumatch-frontend-hazel.vercel.app](https://resumatch-frontend-hazel.vercel.app)
- **Backend API**: [https://resumatch-backend-q5qo.onrender.com](https://resumatch-backend-q5qo.onrender.com)
- **API Health Check**: [https://resumatch-backend-q5qo.onrender.com/healthz](https://resumatch-backend-q5qo.onrender.com/healthz)
- **API Documentation**: [https://resumatch-backend-q5qo.onrender.com/docs](https://resumatch-backend-q5qo.onrender.com/docs)

### 🚀 Quick Start
1. Visit the [live application](https://resumatch-frontend-hazel.vercel.app)
2. Sign up as a Student or Recruiter
3. Students: Upload your resume and get AI-powered job matches
4. Recruiters: Post jobs and find qualified candidates
5. Use real-time chat to communicate with each other

## ✨ Features

### For Students
- **📄 Smart Resume Analysis**: Upload PDF resumes and get AI-powered analysis with skill extraction
- **🎯 Job Matching**: Get top 3 job recommendations based on resume analysis and skills
- **💬 Real-time Chat**: Communicate with recruiters through Socket.IO powered messaging
- **🎤 Mock Interviews**: Practice with AI-generated interview questions tailored to your profile
- **📊 Application Tracking**: Track job applications and their status

### For Recruiters  
- **📝 Job Posting**: Create and manage job listings with detailed requirements
- **👥 Candidate Management**: View and manage job applicants
- **💬 Direct Communication**: Chat with potential candidates in real-time
- **🔍 Resume Screening**: AI-assisted candidate evaluation and matching

### Core Features
- **🔐 Secure Authentication**: JWT-based auth with role-based access control
- **🌓 Dark/Light Mode**: Toggle between themes for better user experience
- **📱 Responsive Design**: Works seamlessly across desktop and mobile devices
- **⚡ Real-time Updates**: Live notifications and messaging with Socket.IO

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **Socket.IO** - Real-time bidirectional communication
- **MongoDB Atlas** - Cloud database for storing user data, jobs, and messages
- **Google Gemini AI** - AI model for resume analysis and interview questions
- **JWT** - Secure authentication and authorization
- **PyPDF2** - PDF processing for resume text extraction
- **Uvicorn** - ASGI server for FastAPI

### Frontend
- **React 18** - Modern UI library with hooks and context
- **TypeScript** - Type-safe JavaScript for better development experience
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Socket.IO Client** - Real-time communication with backend
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing

### DevOps & Deployment
- **Render** - Backend hosting platform
- **Vercel** - Frontend hosting platform
- **GitHub** - Version control and CI/CD
- **Environment Variables** - Secure configuration management

## 📁 Project Structure

```
resumatch/
├── backend/                 # FastAPI Backend
│   ├── auth/               # Authentication & JWT handling
│   │   ├── auth_utils.py   # Password hashing, verification
│   │   ├── dependencies.py # Auth dependencies for routes
│   │   └── jwt_handler.py  # JWT token creation/validation
│   ├── database/           # Database connections
│   │   └── mongo.py        # MongoDB connection & collections
│   ├── models/             # Pydantic data models
│   │   ├── user.py         # User model (Student/Recruiter)
│   │   ├── job.py          # Job posting model
│   │   └── message.py      # Chat message model
│   ├── routes/             # API route handlers
│   │   ├── auth_routes.py  # Login, signup, logout
│   │   ├── student_routes.py # Resume upload, job matching
│   │   ├── recruiter_routes.py # Job posting, applicant management
│   │   ├── job_routes.py   # Job search, application
│   │   └── chat_routes.py  # Message history endpoints
│   ├── services/           # Business logic
│   │   └── chat_service.py # Chat management service
│   ├── sockets/            # Socket.IO handlers
│   │   ├── chat_server.py  # Real-time chat implementation
│   │   ├── chat_client.py  # Socket client for testing
│   │   └── chat_example.py # Usage examples
│   ├── utils/              # Utility functions
│   │   ├── password.py     # Password utilities
│   │   └── parser/         # AI & parsing utilities
│   │       ├── gemini_client.py    # Google Gemini AI integration
│   │       ├── resume_parser.py    # PDF text extraction
│   │       └── job_matcher.py      # Job matching algorithm
│   ├── scripts/            # Setup scripts
│   │   ├── setup_mongodb.py # Database initialization
│   │   └── setup_admin.py   # Admin user creation
│   ├── main.py             # FastAPI application entry point
│   ├── config.py           # Configuration settings
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── Layout.tsx          # Main app layout
│   │   │   ├── LoadingSpinner.tsx  # Loading indicator
│   │   │   ├── ErrorBoundary.tsx   # Error handling
│   │   │   └── DarkModeToggle.tsx  # Theme switcher
│   │   ├── pages/          # Page components
│   │   │   ├── LoginPage.tsx       # User authentication
│   │   │   ├── SignupPage.tsx      # User registration
│   │   │   ├── StudentDashboard.tsx # Student main page
│   │   │   ├── RecruiterDashboard.tsx # Recruiter main page
│   │   │   ├── ResumeUploadPage.tsx # Resume analysis
│   │   │   ├── JobListPage.tsx     # Job search & browsing
│   │   │   ├── JobDetailsPage.tsx  # Individual job details
│   │   │   ├── ChatPage.tsx        # Real-time messaging
│   │   │   ├── MockInterviewPage.tsx # AI interview practice
│   │   │   ├── PostJobPage.tsx     # Job creation (recruiters)
│   │   │   └── MyJobsPage.tsx      # Job management
│   │   ├── services/       # API communication
│   │   │   ├── api.ts              # Axios configuration
│   │   │   ├── authService.ts      # Authentication API
│   │   │   ├── studentService.ts   # Student-specific API
│   │   │   ├── recruiterService.ts # Recruiter-specific API
│   │   │   ├── jobService.ts       # Job-related API
│   │   │   ├── resumeService.ts    # Resume analysis API
│   │   │   └── chatService.ts      # Chat/messaging API
│   │   ├── context/        # React Context providers
│   │   │   ├── AuthContext.tsx     # Authentication state
│   │   │   ├── ThemeContext.tsx    # Dark/light mode
│   │   │   └── ChatContext.tsx     # Chat state management
│   │   ├── hooks/          # Custom React hooks
│   │   │   ├── useApi.ts           # API calling hook
│   │   │   ├── useLoading.ts       # Loading state hook
│   │   │   └── useJobs.ts          # Job data hook
│   │   ├── types/          # TypeScript type definitions
│   │   │   └── index.ts            # All type definitions
│   │   └── utils/          # Utility functions
│   │       ├── auth.ts             # Auth helper functions
│   │       └── helpers.ts          # General utilities
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   ├── vite.config.ts      # Vite configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   └── tsconfig.json       # TypeScript configuration
│
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🚀 Quick Deployment Guide

### Prerequisites
- MongoDB Atlas account (free tier available)
- Google Cloud account (for Gemini AI API)
- Render account (for backend deployment)
- Vercel account (for frontend deployment)

### 1. Clone and Setup
```bash
git clone https://github.com/bipaulr/ResuMatch.git
cd ResuMatch
```

### 2. Backend Deployment (Render)
1. Connect this repository to Render
2. Create Web Service with these settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:api --host 0.0.0.0 --port $PORT`
3. Add environment variables:
   ```
   MONGODB_URI=your_mongodb_atlas_connection_string
   JWT_SECRET=your_secure_random_secret
   GOOGLE_API_KEY=your_google_gemini_api_key
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

### 3. Frontend Deployment (Vercel)
1. Connect this repository to Vercel
2. Set root directory to `frontend`
3. Add environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend.onrender.com
   VITE_SOCKET_PATH=/ws/socket.io
   ```

### 4. Database Setup (MongoDB Atlas)
1. Create free M0 cluster
2. Create database user
3. Add network access (0.0.0.0/0 for deployment)
4. Get connection string

### 5. AI Setup (Google Gemini)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Add to backend environment variables

## 🔧 Environment Variables

### Backend (.env)
```env
# Server Configuration
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend-domain.vercel.app
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
JWT_EXPIRES_IN=86400

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/resumatch?retryWrites=true&w=majority

# AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### Frontend (.env.local)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_PATH=/ws/socket.io
```

### Production Environment Variables

**Render (Backend):**
- `ALLOWED_ORIGINS`: Your Vercel domain(s)
- `MONGODB_URI`: MongoDB Atlas connection string
- `JWT_SECRET`: Strong secret key
- `GOOGLE_API_KEY`: Google Cloud API key

**Vercel (Frontend):**
- `VITE_API_BASE_URL`: Your Render backend URL
- `VITE_SOCKET_PATH`: `/ws/socket.io`

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Student Endpoints
- `POST /student/upload-resume` - Upload and analyze resume
- `GET /student/job-matches` - Get matched jobs
- `POST /student/apply/{job_id}` - Apply to a job
- `GET /student/applications` - Get user's applications

### Recruiter Endpoints
- `POST /recruiter/jobs` - Create new job posting
- `GET /recruiter/jobs` - Get recruiter's jobs
- `GET /recruiter/jobs/{job_id}/applicants` - Get job applicants

### Job Endpoints
- `GET /jobs` - Search and filter jobs
- `GET /jobs/{job_id}` - Get job details

### Chat Endpoints
- `GET /chat/messages/{room_id}` - Get chat history
- WebSocket: `/ws/socket.io` - Real-time messaging

## 🚢 Deployment Guide

### Step 1: MongoDB Atlas Setup
1. Create free MongoDB Atlas account
2. Create a new cluster (M0 free tier)
3. Create database user with read/write permissions
4. Add IP addresses to network access (0.0.0.0/0 for development)
5. Get connection string and update `MONGODB_URI`

### Step 2: Google Cloud Setup (Gemini AI)
1. Create Google Cloud project
2. Enable Gemini API
3. Create API key
4. Update `GOOGLE_API_KEY` in environment variables

### Step 3: Backend Deployment (Render)
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set root directory to `backend`
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn main:api --host 0.0.0.0 --port $PORT`
7. Add environment variables
8. Deploy and test `/healthz` endpoint

### Step 4: Frontend Deployment (Vercel)
1. Create new project on Vercel
2. Connect GitHub repository
3. Set root directory to `frontend`
4. Set build command: `npm run build`
5. Set output directory: `dist`
6. Add environment variables
7. Deploy and test the application

### Step 5: Final Configuration
1. Update `ALLOWED_ORIGINS` in Render with your Vercel domain
2. Update `VITE_API_BASE_URL` in Vercel with your Render domain
3. Test complete workflow: signup → login → resume upload → job matching → chat

## 👥 User Workflows

### Student Journey
1. **Sign Up/Login** → Create account with student role
2. **Upload Resume** → PDF analysis with AI skill extraction
3. **View Matches** → Get top 3 recommended jobs based on skills
4. **Browse Jobs** → Search and filter available positions
5. **Apply to Jobs** → Submit applications with one click
6. **Chat with Recruiters** → Real-time communication
7. **Mock Interview** → Practice with AI-generated questions
8. **Track Applications** → Monitor application status

### Recruiter Journey
1. **Sign Up/Login** → Create account with recruiter role
2. **Post Jobs** → Create detailed job listings with requirements
3. **Manage Listings** → View and edit posted jobs
4. **Review Applicants** → See candidate profiles and resumes
5. **Chat with Candidates** → Direct communication with applicants
6. **Evaluate Candidates** → AI-assisted matching and screening

### Technical Workflow
1. **Authentication**: JWT tokens for secure API access
2. **File Upload**: PDF processing and text extraction
3. **AI Analysis**: Gemini API for skill extraction and matching
4. **Real-time Chat**: Socket.IO for instant messaging
5. **Data Persistence**: MongoDB for all user data and relationships

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🐛 Known Issues & Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure `ALLOWED_ORIGINS` includes your frontend domain
2. **Socket.IO Connection**: Check `VITE_SOCKET_PATH` matches backend mount point
3. **File Upload**: Verify PDF files are valid and readable
4. **AI Responses**: Check Google API key and quota limits

### Support
- Create an issue on GitHub for bugs
- Check API documentation at `/docs` endpoint
- Verify environment variables are correctly set

---

**Built with ❤️ by the ResuMatch Team**

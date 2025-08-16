# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

# ResuMatch Frontend

🚀 **Live Demo**: [https://resumatch-front-4nts.vercel.app](https://resumatch-front-4nts.vercel.app)

A modern React application built with Vite, TypeScript, and Tailwind CSS for the ResuMatch job matching platform.

## 🌐 Live Application
- **Frontend**: [https://resumatch-front-4nts.vercel.app](https://resumatch-front-4nts.vercel.app)
- **Backend API**: [https://resumatch-backend-q5qo.onrender.com](https://resumatch-backend-q5qo.onrender.com)
- **GitHub Repository**: [https://github.com/josephshibumathew/resumatch-front](https://github.com/josephshibumathew/resumatch-front)

## 🚀 Project Structure

```
resumatch-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main layout with navigation
│   │   └── LoadingSpinner.tsx # Loading indicators
│   ├── context/             # React Context providers
│   │   ├── AuthContext.tsx  # Authentication state management
│   │   └── ChatContext.tsx  # Real-time chat functionality
│   ├── hooks/               # Custom React hooks
│   │   ├── useLoading.ts    # Loading state management
│   │   └── useJobs.ts       # Job-related operations
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx    # User authentication
│   │   ├── SignupPage.tsx   # User registration
│   │   ├── StudentDashboard.tsx    # Student overview
│   │   ├── RecruiterDashboard.tsx  # Recruiter overview
│   │   ├── JobListPage.tsx         # Browse jobs
│   │   ├── JobDetailsPage.tsx      # Job details & application
│   │   ├── ResumeUploadPage.tsx    # Resume upload & analysis
│   │   ├── ChatPage.tsx            # Real-time messaging
│   │   └── PostJobPage.tsx         # Job posting form
│   ├── services/            # API service functions
│   │   ├── api.ts           # Axios configuration
│   │   ├── authService.ts   # Authentication APIs
│   │   ├── jobService.ts    # Job-related APIs
│   │   ├── resumeService.ts # Resume analysis APIs
│   │   └── chatService.ts   # Chat APIs
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # All type definitions
│   ├── utils/               # Utility functions
│   │   ├── auth.ts          # JWT token management
│   │   └── helpers.ts       # General helper functions
│   ├── App.tsx              # Main app component with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles with Tailwind
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
├── tsconfig.json            # TypeScript configuration
└── vite.config.ts           # Vite configuration
```

## 🛠️ Technologies Used

- **React 19** - Modern React with hooks and functional components
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Socket.IO Client** - Real-time communication
- **React Dropzone** - File upload with drag-and-drop
- **React Hot Toast** - Toast notifications
- **Lucide React** - Beautiful icons

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd resumatch-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Visit `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## 🧪 Testing Guide

### 1. Authentication Flow

**Test User Registration:**
1. Go to `http://localhost:5173/signup`
2. Fill out the form with:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test123!`
   - Role: Select either "Student" or "Recruiter"
3. Click "Create account"
4. Should redirect to dashboard on success

**Test User Login:**
1. Go to `http://localhost:5173/login`
2. Use credentials from registration
3. Should authenticate and redirect to appropriate dashboard

### 2. Role-Based Routing

**Student Features:**
- Dashboard: Resume score, job matches, applications
- Jobs: Browse and apply to job listings
- Resume Upload: Drag-and-drop PDF analysis
- Chat: Message recruiters

**Recruiter Features:**
- Dashboard: Posted jobs, applications, interviews
- Post Job: Create new job listings
- Mock Interview: AI-powered interview questions
- Chat: Message candidates

### 3. UI States Testing

**Loading States:**
- All forms show loading spinners during submission
- API calls display loading indicators
- Smooth transitions between states

**Error Handling:**
- Invalid login shows error toast
- Network errors are gracefully handled
- Form validation with helpful messages

**Responsive Design:**
- Mobile-first design
- Works on all screen sizes
- Touch-friendly interface

## 📱 Key Features Implemented

### ✅ Completed Structure
1. **Authentication System**
   - Login/Signup pages with validation
   - JWT token management
   - Role-based routing (Student/Recruiter)
   - Auto-logout on token expiry

2. **Component Architecture**
   - Reusable UI components
   - Context providers for state management
   - Custom hooks for data fetching
   - TypeScript for type safety

3. **Routing & Navigation**
   - Protected routes
   - Role-based access control
   - Responsive navigation bar
   - Smooth page transitions

4. **Design System**
   - Tailwind CSS utility classes
   - Custom component styles
   - Responsive design
   - Consistent color palette

### 🚧 Ready for Implementation
1. **Resume Upload & Analysis** (Next to build)
2. **Job Management System** (Next to build)
3. **Real-time Chat** (Next to build)
4. **Dashboard Widgets** (Next to build)

## 🔧 Next Steps

To complete the application, implement these components in order:

1. **Resume Upload Page** - Drag-and-drop PDF upload with analysis
2. **Job List & Details** - Browse and apply to jobs
3. **Post Job Form** - Recruiter job creation
4. **Chat System** - Real-time messaging
5. **Dashboard Widgets** - Statistics and data visualization

## 🐛 Troubleshooting

### Common Issues

1. **Module not found errors:**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Tailwind styles not loading:**
   - Check `tailwind.config.js` content paths
   - Verify `@tailwind` directives in `index.css`

3. **API connection errors:**
   - Ensure backend is running on port 8000
   - Check CORS configuration on backend
   - Verify API_BASE_URL in auth.ts

## 📦 Dependencies Status

### ✅ Installed & Configured
- React 19 + TypeScript
- Vite build system
- Tailwind CSS + plugins
- React Router DOM
- Axios for API calls
- Framer Motion for animations
- Socket.IO client
- React Dropzone
- React Hot Toast
- Lucide React icons

---

**Current Status**: Foundation complete, ready for feature implementation!

Built with ❤️ using React, TypeScript, and modern web technologies.

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

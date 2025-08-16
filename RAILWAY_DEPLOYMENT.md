# Railway Deployment Guide for ResuMatch

## 🚂 Quick Railway Deployment

### Prerequisites
1. GitHub account with your ResuMatch code
2. Railway account (sign up at https://railway.app)
3. MongoDB Atlas database (or use Railway's MongoDB addon)

### Step 1: Connect GitHub to Railway
1. Go to https://railway.app
2. Click "Login" and sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository: `josephshibumathew/resumatch-front` or `bipaulr/ResuMatch`

### Step 2: Configure Backend Service
1. Railway will detect your backend folder automatically
2. Set the **Root Directory** to `backend`
3. Railway will use the `railway.toml` configuration automatically

### Step 3: Set Environment Variables
In Railway dashboard, go to your service → Variables tab and add:

```bash
# Required Variables
ALLOWED_ORIGINS=https://your-app-name.up.railway.app,https://resumatch-front.vercel.app,http://localhost:5173
JWT_SECRET=your_super_secret_jwt_key_minimum_32_characters_long
JWT_EXPIRES_IN=86400
ENVIRONMENT=production
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/resumatch?retryWrites=true&w=majority
MONGODB_DB_NAME=resumatch
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### Step 4: Deploy
1. Click "Deploy" 
2. Railway will build and deploy automatically
3. Your API will be available at: `https://your-app-name.up.railway.app`

### Step 5: Update Frontend
Update your frontend's production environment variables to point to your Railway backend:

```bash
# In frontend/.env.production
VITE_API_BASE_URL=https://your-app-name.up.railway.app
VITE_WS_URL=https://your-app-name.up.railway.app
```

## 🔧 Railway Features Used

- **Automatic Build**: Uses Nixpacks to detect Python and install dependencies
- **Health Checks**: Monitors `/healthz` endpoint
- **Auto-scaling**: Scales based on demand
- **Environment Variables**: Secure variable storage
- **Custom Domains**: Can add your own domain later
- **SSL**: Automatic HTTPS certificates

## 🚀 Commands for Quick Setup

```bash
# 1. Install Railway CLI (optional)
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Link to existing project
railway link [project-id]

# 4. Deploy directly from CLI
railway up
```

## 📋 Troubleshooting

### Common Issues:
1. **Build fails**: Check requirements.txt has all dependencies
2. **App crashes**: Check environment variables are set correctly
3. **Socket.IO not working**: Ensure CORS origins include your Railway domain
4. **Database connection fails**: Verify MongoDB_URI format and credentials

### Useful Railway Commands:
```bash
railway logs                 # View application logs
railway variables           # List environment variables
railway domain              # Get your app's URL
railway service              # Service management
```

## 🌐 Post-Deployment

1. Test your API: `https://your-app.up.railway.app/healthz`
2. Test Socket.IO: `https://your-app.up.railway.app/socket.io/health`
3. Update frontend to use Railway backend URL
4. Test end-to-end functionality

## 💡 Railway vs Other Platforms

**Advantages:**
- Very simple setup and deployment
- Generous free tier
- Excellent for full-stack apps
- Built-in database options
- Great developer experience

**Perfect for:** FastAPI + Socket.IO + MongoDB applications like ResuMatch!

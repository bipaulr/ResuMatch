#!/bin/bash

# Railway CLI Commands Cheat Sheet for ResuMatch

echo "🚂 Railway CLI Commands for ResuMatch"
echo "====================================="
echo ""

echo "📋 Project Information:"
echo "railway status              # Show project status"
echo "railway logs               # View live logs"
echo "railway logs --tail        # Follow logs in real-time"
echo ""

echo "🚀 Deployment:"
echo "railway up                 # Deploy current directory"
echo "railway up --detach        # Deploy without waiting"
echo ""

echo "⚙️  Environment Variables:"
echo "railway variables          # List all variables"
echo "railway variables set KEY=value   # Set variable"
echo "railway variables delete KEY      # Delete variable"
echo ""

echo "🌐 Domains:"
echo "railway domain             # Get your app URL"
echo "railway domain add custom.com     # Add custom domain"
echo ""

echo "📊 Service Management:"
echo "railway service            # List services"
echo "railway restart            # Restart service"
echo ""

echo "🔗 Project Management:"
echo "railway link --project 321a4166-32e7-4e8e-bd06-eb13f77c3ab3"
echo "railway unlink             # Unlink project"
echo ""

echo "💡 Quick Deploy ResuMatch:"
echo "cd backend && railway up   # Deploy from backend folder"

#!/bin/bash

# Single command to sync all repositories and branches
# Run this from the resumatch-deploy directory

echo "🚀 Syncing all repositories and branches..."

# Add any uncommitted changes
git add .

# Check if there are changes to commit
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Committing changes..."
    git commit -m "Railway deployment: Update environment configuration for production deployment"
else
    echo "✅ No new changes to commit"
fi

echo "🔄 Pushing to all repositories and branches..."

# Push to your repository (main)
echo "📤 Pushing to josephshibumathew/resumatch-front main..."
git push origin main

# Push to bipaulr repository (main)  
echo "📤 Pushing to bipaulr/ResuMatch main..."
git push bipaulr main

# Switch to master and sync
echo "🔄 Syncing master branch..."
git checkout master
git merge main

# Push master to both repositories
echo "📤 Pushing to josephshibumathew/resumatch-front master..."
git push origin master

echo "📤 Pushing to bipaulr/ResuMatch master..."
git push bipaulr master

# Switch back to main
git checkout main

echo "✅ All repositories and branches synced successfully!"
echo "🚂 Ready for Railway deployment!"

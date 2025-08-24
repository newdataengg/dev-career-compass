#!/bin/bash

# DevCareerCompass Deployment Script
# This script helps you deploy your application to various platforms

echo "🚀 DevCareerCompass Deployment Script"
echo "======================================"

# Check if git repository is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes. Please commit them first."
    echo "   git add . && git commit -m 'Prepare for deployment'"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if required files exist
echo "📋 Checking required files..."
required_files=("app.py" "requirements.txt" "Dockerfile" "render.yaml")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        exit 1
    fi
done

echo ""
echo "🎯 Choose your deployment platform:"
echo "1. Render (Recommended - Free)"
echo "2. Railway (Free)"
echo "3. Heroku (Paid)"
echo "4. Local Docker test"
echo "5. Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Deploying to Render..."
        echo "1. Go to https://render.com"
        echo "2. Sign up with your GitHub account"
        echo "3. Click 'New +' and select 'Web Service'"
        echo "4. Connect your GitHub repository"
        echo "5. Configure:"
        echo "   - Name: devcareer-compass"
        echo "   - Environment: Python 3"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python app.py"
        echo "   - Plan: Free"
        echo "6. Add environment variables:"
        echo "   - FLASK_ENV=production"
        echo "   - FLASK_APP=app.py"
        echo "7. Click 'Create Web Service'"
        echo ""
        echo "Your app will be available at: https://your-app-name.onrender.com"
        ;;
    2)
        echo ""
        echo "🚀 Deploying to Railway..."
        echo "1. Go to https://railway.app"
        echo "2. Sign up with your GitHub account"
        echo "3. Click 'New Project'"
        echo "4. Select 'Deploy from GitHub repo'"
        echo "5. Choose your repository"
        echo "6. Railway will auto-detect your Flask app"
        echo "7. Deploy automatically"
        echo ""
        echo "Your app will be available at: https://your-app-name.railway.app"
        ;;
    3)
        echo ""
        echo "🚀 Deploying to Heroku..."
        echo "Installing Heroku CLI..."
        if command -v heroku &> /dev/null; then
            echo "✅ Heroku CLI already installed"
        else
            echo "Please install Heroku CLI first:"
            echo "  macOS: brew install heroku/brew/heroku"
            echo "  Windows: Download from https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        echo "Logging into Heroku..."
        heroku login
        
        echo "Creating Heroku app..."
        heroku create devcareer-compass
        
        echo "Setting buildpack..."
        heroku buildpacks:set heroku/python
        
        echo "Deploying..."
        git push heroku main
        
        echo "Opening app..."
        heroku open
        ;;
    4)
        echo ""
        echo "🐳 Testing with Docker locally..."
        echo "Building Docker image..."
        docker build -t devcareer-compass .
        
        echo "Running container..."
        docker run -p 8080:8080 devcareer-compass
        
        echo "Your app is running at: http://localhost:8080"
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment instructions completed!"
echo "📚 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo "🔧 For troubleshooting, check the logs in your platform dashboard"

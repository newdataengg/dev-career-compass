# 🔑 API Keys Setup Guide for DevCareerCompass

This guide will help you set up all the necessary API keys to collect real data from multiple platforms.

## 📋 Required API Keys

### 1. 🐙 GitHub API (Already Configured)
- **Status**: ✅ Already working
- **Current**: Using GitHub Personal Access Token
- **Location**: `.env` file as `GITHUB_TOKEN`

### 2. 💬 Stack Overflow API
- **Status**: ⚠️ Needs setup
- **Purpose**: Collect top users, questions, and answers
- **Setup Steps**:
  1. Go to [Stack Exchange API](https://api.stackexchange.com/)
  2. Register for an API key at [Stack Apps](https://stackapps.com/apps/oauth/register)
  3. Add to `.env`:
     ```
     STACK_OVERFLOW_KEY=your_stack_overflow_api_key
     ```

### 3. 🤖 Reddit API
- **Status**: ⚠️ Needs setup
- **Purpose**: Collect users from programming subreddits
- **Setup Steps**:
  1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
  2. Click "Create App" or "Create Another App"
  3. Choose "script" as the app type
  4. Add to `.env`:
     ```
     REDDIT_CLIENT_ID=your_reddit_client_id
     REDDIT_CLIENT_SECRET=your_reddit_client_secret
     REDDIT_USER_AGENT=your_reddit_user_agent
     REDDIT_USERNAME=your_reddit_username
     REDDIT_PASSWORD=your_reddit_password
     ```

### 4. 💼 LinkedIn API
- **Status**: ⚠️ Needs setup
- **Purpose**: Collect job postings and professional data
- **Setup Steps**:
  1. Go to [LinkedIn Developers](https://developer.linkedin.com/)
  2. Create a new app
  3. Request access to Marketing APIs
  4. Add to `.env`:
     ```
     LINKEDIN_CLIENT_ID=your_linkedin_client_id
     LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
     ```

### 5. 🔍 Indeed API (X-Rapid API)
- **Status**: ⚠️ Needs setup
- **Purpose**: Collect job listings and skill requirements
- **Setup Steps**:
  1. Go to [RapidAPI](https://rapidapi.com/)
  2. Sign up for a free account
  3. Subscribe to the Indeed API
  4. Add to `.env`:
     ```
     XRAPID_API_KEY=your_xrapid_api_key
     ```

## 🚀 Quick Setup Commands

### Option 1: Manual Setup
```bash
# Edit your .env file
nano .env

# Add these lines to your .env file:
STACK_OVERFLOW_KEY=your_stack_overflow_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
XRAPID_API_KEY=your_xrapid_api_key
```

### Option 2: Interactive Setup
```bash
# Run the interactive setup
python real_data_collector.py
# Choose option 6 to see current statistics
```

## 📊 Data Collection Targets

### Without API Keys (GitHub Only)
- **GitHub**: 100 developers
- **Total**: ~100 items

### With All API Keys
- **GitHub**: 100 developers
- **Stack Overflow**: 100 users
- **Reddit**: 100 users
- **LinkedIn**: 50 job postings
- **Indeed**: 50 job listings
- **Total**: 400+ items

## 🎯 Collection Strategies

### GitHub (Real API)
1. **Trending Languages**: 25 programming languages
2. **Popular Users**: High follower/repo counts
3. **Company Developers**: Major tech companies

### Stack Overflow (Real API)
1. **Top Users**: High reputation users
2. **Active Contributors**: Recent activity
3. **Tag-based Search**: Programming language tags

### Reddit (Real API)
1. **Programming Subreddits**: r/programming, r/Python, r/javascript
2. **Active Users**: High karma and recent activity
3. **Community Leaders**: Moderators and top contributors

### LinkedIn (Real API)
1. **Job Postings**: Technology sector jobs
2. **Company Data**: Tech company information
3. **Skill Requirements**: Job skill analysis

### Indeed (X-Rapid API)
1. **Job Listings**: Technology positions
2. **Salary Data**: Compensation information
3. **Skill Analysis**: Required skills extraction 
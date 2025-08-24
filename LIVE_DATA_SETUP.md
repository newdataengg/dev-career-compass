# 🚀 Live Data Setup Guide for DevCareerCompass

## 🎯 **Capstone Requirements Analysis**

Your capstone project needs **live data** to meet the rubric criteria. Here's what you need to set up:

### ✅ **Already Completed**
- ✅ Live deployment at `dev-career-compass.onrender.com`
- ✅ Flask application with RAG architecture
- ✅ Vector database (Qdrant) integration
- ✅ Multi-agent system design

### ❌ **Need to Complete**
- ❌ Live data collection with API keys
- ❌ 1000+ embeddings in vector database
- ❌ RAG integration testing (5+ queries)
- ❌ Data quality checks
- ❌ Abuse protection for RAG

## 🔑 **Step 1: Get API Keys (Free)**

### **GitHub API (Required)**
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`, `read:email`
4. Copy the token

### **Indeed API (Free via RapidAPI)**
1. Go to [RapidAPI Indeed API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/indeed12/)
2. Sign up for free account
3. Subscribe to free plan (100 requests/month)
4. Copy your API key

### **Stack Overflow API (Free)**
1. Go to [Stack Exchange API](https://api.stackexchange.com/)
2. No key required for basic usage
3. For higher limits: [Register your app](https://stackapps.com/apps/oauth/register)

### **Reddit API (Free)**
1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App"
3. Select "script" type
4. Note down: Client ID, Client Secret

## ⚙️ **Step 2: Configure Render Environment Variables**

In your Render dashboard, add these environment variables:

### **Required for Live Data**
```
GITHUB_TOKEN=ghp_your_github_token_here
XRAPID_API_KEY=your_rapidapi_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=DevCareerCompass/1.0
```

### **Optional (for enhanced features)**
```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
QDRANT_CLOUD_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

### **Production Settings**
```
FLASK_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
APP_ENV=production
```

## 📊 **Step 3: Data Collection Script**

Run this script to collect live data:

```bash
# In your local environment
source ai-cap/bin/activate
python real_data_collector.py
```

This will:
- Collect 100+ GitHub developers
- Gather 1000+ repositories
- Extract 50+ skills
- Collect job postings from Indeed
- Generate 1000+ embeddings

## 🧪 **Step 4: RAG Integration Testing**

Test your RAG system with these 5 queries:

1. **"What skills are in high demand for AI engineers?"**
2. **"Find developers working on machine learning projects"**
3. **"What are the latest trends in Python development?"**
4. **"Show me job opportunities for React developers"**
5. **"What companies are hiring DevOps engineers?"**

## 🔒 **Step 5: Abuse Protection**

Add rate limiting and abuse protection:

```python
# In your Flask app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/chat')
@limiter.limit("10 per minute")
def chat():
    # Your RAG endpoint
    pass
```

## 📈 **Step 6: Data Quality Checks**

Add these data quality checks:

### **GitHub Data Quality**
```python
def check_github_data_quality():
    # Check 1: Repository completeness
    repos_with_description = repos.filter(description.isnot(None)).count()
    completeness_rate = repos_with_description / total_repos
    
    # Check 2: Language distribution
    language_counts = repos.group_by(language).count()
    return completeness_rate, language_counts
```

### **Job Data Quality**
```python
def check_job_data_quality():
    # Check 1: Salary information completeness
    jobs_with_salary = jobs.filter(salary_min.isnot(None)).count()
    salary_completeness = jobs_with_salary / total_jobs
    
    # Check 2: Company information
    jobs_with_company = jobs.filter(company.isnot(None)).count()
    company_completeness = jobs_with_company / total_jobs
    
    return salary_completeness, company_completeness
```

## 🎯 **Step 7: Capstone Submission Checklist**

### **Criteria 1: Project Spec** ✅
- [x] System/AI Agent design diagram
- [x] Screenshots (UI, example queries)
- [x] Business problem statement

### **Criteria 2: Write Up** ✅
- [x] Purpose and expected outputs
- [x] Dataset and technology choices
- [x] Steps and challenges
- [x] Future enhancements

### **Criteria 3: Vectorizing Data** ⚠️
- [ ] 2+ data quality checks per source
- [ ] 1000+ embeddings loaded

### **Criteria 4: RAG Code** ⚠️
- [x] RAG model implementation
- [x] Graph RAG (knowledge graph)
- [ ] 1000+ embeddings
- [ ] 5+ integration test queries
- [ ] Abuse protection

### **Criteria 5: Live Deployment** ✅
- [x] Live link: `dev-career-compass.onrender.com`

## 🚀 **Quick Start Commands**

```bash
# 1. Set up environment variables in Render
# (Use the Render dashboard)

# 2. Redeploy to apply changes
# (Click "Manual Deploy" in Render)

# 3. Test live data collection
curl -X POST https://your-app.onrender.com/api/collect-data

# 4. Test RAG queries
curl -X POST https://your-app.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What skills are in high demand?"}'
```

## 📞 **Need Help?**

If you encounter issues:
1. Check Render logs for errors
2. Verify API keys are correct
3. Test locally first with your API keys
4. Check rate limits on free API plans

---

**Your DevCareerCompass will be fully functional with live data once you complete these steps! 🎉**

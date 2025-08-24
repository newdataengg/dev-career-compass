# DevCareerCompass - AI-Powered Career Intelligence Platform

> **AI Engineer Capstone Project** - Demonstrating Advanced AI Engineering Skills

## 🚀 Overview

DevCareerCompass is an advanced AI-powered career intelligence platform that demonstrates cutting-edge AI engineering skills including RAG (Retrieval-Augmented Generation), vector search, knowledge graphs, and multi-agent systems. Built for showcasing AI engineering capabilities in interviews and real-world applications.

### 🎯 **Capstone Project Highlights**
- **RAG Implementation**: Vector search + LLM integration for accurate responses
- **Vector Database**: Qdrant Cloud with 384-dimensional embeddings
- **Knowledge Graph**: NetworkX-based graph with 188 nodes, 113 edges
- **Multi-LLM Support**: OpenAI, Anthropic, and intelligent fallbacks
- **Production Ready**: Error handling, logging, performance optimization
- **Real Data Integration**: GitHub, Indeed, Stack Overflow, Reddit APIs

## 🎯 Key Features

### 🤖 Advanced AI Capabilities
- **RAG (Retrieval-Augmented Generation)**: Combines vector search with LLM for accurate, contextual responses
- **Vector Search with Qdrant**: Semantic similarity search across skills, jobs, and career paths
- **Knowledge Graph (Graph RAG)**: NetworkX-based graph representing developer-skill-repository relationships
- **Multi-LLM Support**: OpenAI, Anthropic, and fallback systems with intelligent routing
- **Prompt Engineering**: Optimized prompts for different query types and contexts

### 📊 Data Integration
- **GitHub API**: Developer profiles, repositories, and skill analysis
- **Indeed API**: Real-time job postings and market data
- **Stack Overflow**: Developer community insights and trends
- **Reddit**: Community discussions and career insights
- **Airflow DAGs**: Automated data pipeline orchestration

### 🎨 Modern UI/UX
- **Crisp, Integrated Interface**: Clean, professional design focused on career insights
- **Interactive Elements**: "Learn More" buttons with detailed career information
- **Real-time Chatbot**: AI assistant with markdown rendering and conversation history
- **Responsive Design**: Tailwind CSS for modern, mobile-friendly interface

### 📸 Application Screenshots

#### **1. Main Dashboard**
![Dashboard](screenshots/dashboard.png)
*Main dashboard showing real-time statistics and data integration from multiple sources including GitHub, Indeed, Stack Overflow, and Reddit.*

#### **2. AI Assistant Chatbot**
![Chatbot](screenshots/chatbot.png)
*RAG-powered AI assistant demonstrating vector search and LLM integration with context-aware responses and confidence scoring.*

#### **3. Career Insights**
![Career Insights](screenshots/career_insights.png)
*Interactive career insights page with AI-powered recommendations and detailed career path information accessible through 'Learn More' buttons.*

#### **4. Job Market Analysis**
![Job Market](screenshots/job_market.png)
*Real-time job market analysis with data from Indeed API showing current market trends and opportunities.*

## 🏗️ Architecture

### Core Components
```
src/
├── agents/
│   └── enhanced_chatbot.py      # Main RAG-powered chatbot
├── knowledge_graph/
│   ├── graph_builder.py         # Knowledge graph construction
│   └── graph_rag_service.py     # Graph RAG query processing
├── vector_store/
│   └── qdrant_client.py         # Vector database operations
├── llm/
│   └── llm_client.py            # Multi-LLM client with fallbacks
└── data/
    ├── github_collector.py      # GitHub data collection
    ├── indeed_collector.py      # Indeed job data
    └── database_manager.py      # SQLAlchemy ORM
```

### AI Skills Demonstrated

#### 1. **RAG (Retrieval-Augmented Generation)**
- Vector embeddings for semantic search
- Context retrieval from multiple data sources
- LLM integration for intelligent response generation
- Confidence scoring and quality assessment

#### 2. **Vector Search & Embeddings**
- 384-dimensional vector embeddings
- Qdrant vector database integration
- Semantic similarity search across skills, jobs, careers
- Real-time vector updates via Airflow

#### 3. **Knowledge Graph (Graph RAG)**
- NetworkX-based knowledge graph
- Developer-skill-repository relationships
- Multi-hop query processing
- Graph traversal for complex insights

#### 4. **Prompt Engineering**
- Context-aware prompt generation
- Query type classification
- Response quality optimization
- Multi-turn conversation handling

#### 5. **Agentic AI Concepts**
- Multi-agent system architecture
- Autonomous decision-making
- Tool use and API integration
- Planning and reasoning capabilities

#### 6. **Asynchronous Programming**
- Async/await patterns throughout
- Non-blocking I/O operations
- Concurrent data processing
- Scalable architecture

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Qdrant Vector Database
- Airflow (for data pipelines)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd dev-career-compass

# Create virtual environment
python -m venv ai-cap
source ai-cap/bin/activate  # On Windows: ai-cap\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials

# Initialize database
python -m src.data.database_manager

# Start the application
python app.py
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/devcareer

# Qdrant Vector Database
QDRANT_URL=https://your-qdrant-instance.cloud
QDRANT_API_KEY=your-api-key

# LLM APIs
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Data Sources
GITHUB_TOKEN=your-github-token
X_RAPID_API_KEY=your-rapidapi-key
```

## 📈 Data Pipeline

### Airflow DAGs
The project includes automated data pipelines for:
- **GitHub Data Collection**: Developer profiles and repositories
- **Indeed Job Postings**: Real-time job market data
- **Vector Database Updates**: Embedding generation and storage
- **Knowledge Graph Updates**: Graph construction and maintenance

### Data Sources
- **97 GitHub Developers**: Active profiles with skill analysis
- **59 Skills**: Market demand and popularity scoring
- **6 Job Postings**: Real-time Indeed data
- **188 Knowledge Graph Nodes**: Developer-skill-repository relationships

## 🎯 Usage Examples

### Chatbot Queries
```
"What skills are in high demand?"
→ Returns skills with market demand scores, job opportunities, and career paths

"What are the latest AI trends?"
→ Provides comprehensive AI trend analysis with RAG, MCP, vector databases

"Tell me about Python career opportunities"
→ Specific skill analysis with salary ranges and learning paths

"Find developers working on machine learning"
→ Knowledge graph traversal for developer discovery
```

### API Endpoints
- `POST /api/chat` - Main chatbot endpoint
- `POST /api/graph_rag` - Graph RAG queries
- `GET /api/graph_statistics` - Knowledge graph metrics

## 🔧 Configuration

### LLM Configuration
The system supports multiple LLM providers with intelligent fallbacks:
- **Primary**: OpenAI GPT-4
- **Secondary**: Anthropic Claude
- **Fallback**: Mock LLM for testing

### Vector Database
- **Qdrant Cloud**: Production-ready vector database
- **Collections**: skills, job_postings, career_paths, developers
- **Embedding Dimension**: 384
- **Similarity Metric**: Cosine

## 📊 Performance Metrics

### Response Quality
- **Confidence Scores**: 0.85-0.95 for high-quality responses
- **Response Time**: <2 seconds for most queries
- **Accuracy**: Context-aware responses based on real data

### Data Coverage
- **Skills**: 59 skills with market demand analysis
- **Developers**: 97 GitHub profiles analyzed
- **Jobs**: Real-time Indeed job postings
- **Knowledge Graph**: 188 nodes, 113 edges

## 🚀 Deployment

### 🎯 **Live Demo**
Your DevCareerCompass application is now ready for deployment! Follow the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### Quick Deployment Options

#### Option 1: Render (Recommended - Free)
1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Deploy as a Web Service
4. Get your public URL: `https://your-app-name.onrender.com`

#### Option 2: Railway (Free)
1. Go to [railway.app](https://railway.app)
2. Deploy from GitHub repository
3. Get your public URL: `https://your-app-name.railway.app`

#### Option 3: Heroku
```bash
# Install Heroku CLI
heroku login
heroku create devcareer-compass
git push heroku main
heroku open
```

### Production Setup
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT app:app

# Or with Docker
docker build -t devcareer-compass .
docker run -p 8080:8080 devcareer-compass
```

### Environment Configuration
- Set `FLASK_ENV=production`
- Configure production database
- Set up monitoring and logging
- Enable SSL/TLS

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Integration Tests
```bash
python test_integration.py
```

### Chatbot Testing
```bash
python test_chatbot_functionality.py
```

## 📚 API Documentation

### Chatbot API
```json
POST /api/chat
{
  "message": "What skills are in high demand?",
  "user_id": "user123"
}

Response:
{
  "success": true,
  "response": "Based on our analysis...",
  "confidence": 0.9
}
```

### Graph RAG API
```json
POST /api/graph_rag
{
  "query": "Find developers working on Python",
  "query_type": "developer_search"
}
```

## 🎓 Learning Outcomes

This project demonstrates mastery of:

1. **Advanced AI Engineering**: RAG, vector search, knowledge graphs
2. **System Architecture**: Scalable, async, multi-component design
3. **Data Engineering**: ETL pipelines, vector databases, real-time processing
4. **Full-Stack Development**: Flask backend, modern frontend, API design
5. **DevOps**: Docker, Airflow, production deployment
6. **AI/ML Integration**: LLM APIs, embedding generation, prompt engineering

## 📚 Capstone Submission Documents

### **Project Documentation**
- **[CAPSTONE_SUBMISSION.md](CAPSTONE_SUBMISSION.md)** - Comprehensive project documentation with technical details
- **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** - Step-by-step demo script for presentation
- **[SCREENSHOT_GUIDE.md](SCREENSHOT_GUIDE.md)** - Screenshot capture guidelines and captions
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Final project status and achievements

### **Key Technical Achievements**
- ✅ **RAG System**: Production-ready retrieval-augmented generation
- ✅ **Vector Search**: 5 active collections with semantic similarity
- ✅ **Knowledge Graph**: 188 nodes representing real relationships
- ✅ **Multi-LLM**: Intelligent routing with fallback systems
- ✅ **Async Architecture**: Non-blocking I/O throughout
- ✅ **Real Data**: 97 developers, 59 skills, 6 job postings

### **Performance Metrics**
- **Response Time**: <2 seconds for most queries
- **Confidence Scores**: 0.85-0.95 for high-quality responses
- **Data Coverage**: Multiple real-world data sources
- **Production Ready**: Error handling, logging, monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude
- Qdrant for vector database
- GitHub, Indeed, Stack Overflow, Reddit for data sources

---

**Built with ❤️ for AI Engineering Excellence** 
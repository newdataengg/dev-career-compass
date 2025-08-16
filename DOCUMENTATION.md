# 📚 DevCareerCompass Technical Documentation

## 🎯 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Models](#data-models)
3. [Vector Search Implementation](#vector-search-implementation)
4. [Graph RAG System](#graph-rag-system)
5. [API Reference](#api-reference)
6. [Configuration Guide](#configuration-guide)
7. [Development Guide](#development-guide)
8. [Deployment Guide](#deployment-guide)
9. [Troubleshooting](#troubleshooting)

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    DevCareerCompass Platform                    │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Web Application (Flask)                                     │
│  ├── Dashboard & Analytics                                      │
│  ├── AI Chatbot Interface                                       │
│  ├── Vector Search UI                                           │
│  ├── Career Path Recommendations                                │
│  └── Job Market Intelligence                                    │
├─────────────────────────────────────────────────────────────────┤
│  🧠 AI/ML Layer                                                 │
│  ├── Multi-Agent System                                         │
│  ├── LLM Integration (OpenAI/Anthropic)                         │
│  ├── Deep Learning Models                                       │
│  └── Real-time Learning System                                  │
├─────────────────────────────────────────────────────────────────┤
│  🔍 Vector Search Layer (Qdrant Cloud)                          │
│  ├── Skill Vectors (384d)                                       │
│  ├── Developer Vectors (384d)                                   │
│  ├── Repository Vectors (384d)                                  │
│  ├── Job Posting Vectors (384d)                                 │
│  └── Career Path Vectors (384d)                                 │
├─────────────────────────────────────────────────────────────────┤
│  🗄️ Data Layer                                                  │
│  ├── SQLite Database (Structured Data)                          │
│  ├── Multi-Platform Data Sources                                │
│  └── File Storage (Logs, Configs)                               │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Data Collection**: Multi-platform APIs → SQLite Database
2. **Vector Generation**: Text Data → Embeddings → Qdrant Cloud
3. **Graph Construction**: Relationships → Knowledge Graph
4. **Search Processing**: Query → Vector Search → Results
5. **AI Analysis**: Data → LLM → Insights
6. **Web Interface**: Results → Dashboard → User

## 📊 Data Models

### Database Schema

#### Developers Table
```sql
CREATE TABLE developers (
    id INTEGER PRIMARY KEY,
    github_id INTEGER UNIQUE,
    username VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    bio TEXT,
    location VARCHAR(255),
    company VARCHAR(255),
    blog VARCHAR(500),
    twitter_username VARCHAR(255),
    public_repos INTEGER DEFAULT 0,
    public_gists INTEGER DEFAULT 0,
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    data_source VARCHAR(50) DEFAULT 'github',  -- 'github', 'stackoverflow', 'reddit'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Skills Table
```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100),
    description TEXT,
    popularity_score FLOAT DEFAULT 0.0,
    market_demand_score FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Job Postings Table
```sql
CREATE TABLE job_postings (
    id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    requirements TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'USD',
    job_type VARCHAR(50),  -- 'full-time', 'part-time', 'contract', 'internship'
    experience_level VARCHAR(50),  -- 'entry', 'mid', 'senior', 'lead'
    remote_option BOOLEAN DEFAULT FALSE,
    posted_date DATETIME,
    application_url VARCHAR(500),
    data_source VARCHAR(50) NOT NULL,  -- 'linkedin', 'indeed'
    source_id VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Job Skills Table
```sql
CREATE TABLE job_skills (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    is_required BOOLEAN DEFAULT TRUE,
    importance_score FLOAT DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job_postings(id),
    FOREIGN KEY (skill_id) REFERENCES skills(id)
);
```

### Vector Collections

#### Skill Vectors Collection
```python
{
    "id": "auto_increment",
    "skill_id": "int64",
    "skill_name": "varchar(255)",
    "category": "varchar(100)",
    "vector": "float_vector(768)",
    "metadata": "json"
}
```

#### Developer Vectors Collection
```python
{
    "id": "auto_increment",
    "developer_id": "int64",
    "username": "varchar(255)",
    "vector": "float_vector(768)",
    "metadata": "json"
}
```

#### Repository Vectors Collection
```python
{
    "id": "auto_increment",
    "repository_id": "int64",
    "full_name": "varchar(500)",
    "vector": "float_vector(768)",
    "metadata": "json"
}
```

#### Career Path Vectors Collection
```python
{
    "id": "auto_increment",
    "path_id": "int64",
    "path_name": "varchar(255)",
    "vector": "float_vector(768)",
    "metadata": "json"
}
```

## 🔍 Vector Search Implementation

### Embedding Generation

```python
def generate_realistic_embeddings(text: str, dimension: int = 384) -> List[float]:
    """Generate deterministic embeddings based on text content"""
    import hashlib
    
    # Create hash of text
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Convert hash to numbers
    numbers = [int(hash_hex[i:i+2], 16) for i in range(0, len(hash_hex), 2)]
    
    # Create embedding vector
    embedding = []
    for i in range(dimension):
        if i < len(numbers):
            # Normalize to [-1, 1] range
            value = (numbers[i % len(numbers)] / 255.0) * 2 - 1
        else:
            # Fill remaining dimensions with small random values
            value = np.random.normal(0, 0.1)
        embedding.append(value)
    
    return embedding
```

### Search Operations

#### Skill Similarity Search
```python
def search_similar_skills(self, query_vector: List[float], top_k: int = 10):
    """Search for similar skills using cosine similarity"""
    results = self.client.search(
        collection_name="devcareer_skills",
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    
    return [
        {
            'skill_name': result.payload.get('name'),
            'category': result.payload.get('category'),
            'score': result.score,
            'metadata': result.payload
        }
        for result in results
    ]
```

#### Developer Similarity Search
```python
def search_similar_developers(self, query_vector: List[float], top_k: int = 10):
    """Search for similar developers using cosine similarity"""
    results = self.client.search(
        collection_name="devcareer_developers",
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    
    return [
        {
            'username': result.payload.get('username'),
            'name': result.payload.get('name'),
            'location': result.payload.get('location'),
            'score': result.score,
            'metadata': result.payload
        }
        for result in results
    ]
```

### Collection Configuration

```python
# Qdrant Cloud collection configuration
vector_params = VectorParams(
    size=384,
    distance=Distance.COSINE
)

# Create collection with optimized settings
client.create_collection(
    collection_name="devcareer_skills",
    vectors_config=vector_params,
    optimizers_config={
        "default_segment_number": 2,
        "memmap_threshold": 20000
    }
)
```

## 🌐 Graph RAG System

### Knowledge Graph Structure

```json
{
  "nodes": [
    {
      "id": "skill_python",
      "type": "skill",
      "name": "Python",
      "category": "programming_language",
      "popularity_score": 0.95,
      "market_demand_score": 0.92
    },
    {
      "id": "career_data_scientist",
      "type": "career_path",
      "name": "Data Scientist",
      "required_skills": ["Python", "R", "SQL", "Machine Learning"],
      "difficulty_level": "Intermediate",
      "estimated_duration_months": 12
    }
  ],
  "edges": [
    {
      "source": "skill_python",
      "target": "career_data_scientist",
      "relationship": "required_for",
      "weight": 0.9
    }
  ]
}
```

### Career Path Recommendations

```python
def search_similar_career_paths(self, query_vector: List[float], top_k: int = 5):
    """Search for similar career paths based on user profile"""
    collection = self.get_collection("career_path_vectors")
    
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_vector],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields=["path_id", "path_name", "metadata"]
    )
    
    return self._format_search_results(results)
```

### Skill Gap Analysis

```python
def analyze_skill_gap(self, current_skills: List[str], target_role: str):
    """Analyze skills needed for target role"""
    # Get target role requirements
    target_embedding = self.generate_embedding(target_role)
    target_paths = self.search_similar_career_paths(target_embedding, top_k=1)
    
    if target_paths:
        target_skills = target_paths[0]['metadata']['skills']
        missing_skills = [skill for skill in target_skills if skill not in current_skills]
        
        return {
            "target_role": target_role,
            "current_skills": current_skills,
            "required_skills": target_skills,
            "missing_skills": missing_skills,
            "completion_percentage": len(current_skills) / len(target_skills) * 100
        }
    
    return None
```

## 🔌 API Reference

### Core Endpoints

#### Get System Statistics
```http
GET /api/statistics
```

**Response:**
```json
{
  "developers": 47,
  "repositories": 21,
  "skills": 570,
  "commits": 0,
  "developer_skills": 882,
  "vector_collections": {
    "skill_vectors": 100,
    "developer_vectors": 47,
    "repository_vectors": 21,
    "career_path_vectors": 5
  }
}
```

#### Analyze Developer Profile
```http
POST /api/analyze
Content-Type: application/json

{
  "username": "torvalds",
  "analysis_type": "comprehensive"
}
```

**Response:**
```json
{
  "developer": {
    "username": "torvalds",
    "name": "Linus Torvalds",
    "bio": "Creator of Linux and Git",
    "followers": 150000,
    "public_repos": 5
  },
  "career_analysis": {
    "predicted_role": "Systems Architect",
    "confidence": 0.95,
    "salary_range": "$150,000 - $250,000",
    "required_skills": ["C", "Linux", "Git", "Systems Design"]
  },
  "vector_search": {
    "similar_developers": [...],
    "similar_repositories": [...],
    "recommended_skills": [...]
  }
}
```

### Vector Search Endpoints

#### Search Similar Skills
```http
POST /api/search/skills
Content-Type: application/json

{
  "query": "machine learning",
  "top_k": 5
}
```

#### Search Similar Developers
```http
POST /api/search/developers
Content-Type: application/json

{
  "query": "python developer backend",
  "top_k": 5
}
```

#### Get Career Recommendations
```http
POST /api/career/recommendations
Content-Type: application/json

{
  "user_profile": "I know Python, JavaScript, and SQL. I want to become a data scientist.",
  "top_k": 3
}
```

### AI Chatbot Endpoints

#### Send Message
```http
POST /api/chat/send
Content-Type: application/json

{
  "user_id": "user123",
  "message": "What skills do I need to become a data scientist?",
  "context": "previous_conversation_history"
}
```

#### Get Chat History
```http
GET /api/chat/history?user_id=user123&limit=10
```

## ⚙️ Configuration Guide

### Environment Variables

#### Required Configuration
```bash
# GitHub API (Required)
GITHUB_TOKEN=your_github_personal_access_token

# Database Configuration
DATABASE_URL=sqlite:///devcareer_compass.db

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

#### Optional Configuration
```bash
# LLM APIs (Optional - for enhanced AI features)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Additional Data Sources
STACK_OVERFLOW_API_KEY=your_stack_overflow_api_key
ADJUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key

# Qdrant Cloud Vector Database
QDRANT_CLOUD_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Data Collection Limits
MAX_DEVELOPERS_TO_COLLECT=100
MAX_REPOSITORIES_PER_USER=100
MAX_COMMITS_PER_REPOSITORY=1000
RATE_LIMIT_DELAY=1.0
```

### Application Settings

#### Development Configuration
```python
# Development settings
DEBUG = True
LOG_LEVEL = "DEBUG"
MOCK_LLM = True
ENABLE_MONITORING = False
```

#### Production Configuration
```python
# Production settings
DEBUG = False
LOG_LEVEL = "WARNING"
MOCK_LLM = False
ENABLE_MONITORING = True
ENABLE_RATE_LIMITING = True
```

## 🛠️ Development Guide

### Project Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd dev-career-compass
python -m venv ai-cap
source ai-cap/bin/activate  # Windows: ai-cap\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

3. **Initialize Database**
```bash
python -c "from src.database.connection import init_database; init_database()"
```

4. **Setup Qdrant Cloud** (for vector search)
```bash
python qdrant_cloud_setup.py
```

### Development Workflow

#### Running the Application
```bash
# Start web application
python app.py

# Run core application logic
python main.py

# Check system status
python status.py
```

#### Data Collection
```bash
# Enhanced data collection
python enhanced_data_collection.py

# Vector search implementation
python vector_search_implementation.py
```

#### Testing
```bash
# Run tests
python -m pytest tests/

# Check specific components
python -c "from src.vector_store.qdrant_client import QdrantVectorClient; client = QdrantVectorClient()"
```

### Code Structure

#### Core Modules
```
src/
├── database/           # Database models and connection
├── vector_store/       # Qdrant Cloud vector database client
├── agents/            # Multi-agent system
├── llm/               # LLM integration
├── embeddings/        # Vector embedding generation
├── knowledge_graph/   # Graph RAG implementation
├── insights/          # Career analysis engine
├── config/            # Configuration management
└── utils/             # Utility functions
```

#### Key Classes
- `QdrantVectorClient`: Vector database operations
- `AgentOrchestrator`: Multi-agent coordination
- `CareerAnalyzer`: Career analysis engine
- `KnowledgeGraphBuilder`: Graph construction
- `EmbeddingGenerator`: Vector generation

### Adding New Features

#### 1. New Vector Collection
```python
def create_new_collection(self, dimension: int = 384):
    """Create new vector collection"""
    collection_name = "new_vectors"
    
    vector_params = VectorParams(
        size=dimension,
        distance=Distance.COSINE
    )
    
    self.client.create_collection(
        collection_name=collection_name,
        vectors_config=vector_params,
        optimizers_config={
            "default_segment_number": 2,
            "memmap_threshold": 20000
        }
    )
    
    return collection_name
```

#### 2. New API Endpoint
```python
@app.route('/api/new_endpoint', methods=['POST'])
def new_endpoint():
    """New API endpoint"""
    data = request.get_json()
    
    # Process request
    result = process_request(data)
    
    return jsonify(result)
```

## 🚀 Deployment Guide

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=sqlite:///devcareer_compass.db
      - QDRANT_CLOUD_URL=https://your-cluster.cloud.qdrant.io
      - QDRANT_API_KEY=your-qdrant-api-key
```
      - "19530:19530"
    depends_on:
      - etcd
      - minio
```

### Production Deployment

#### Environment Variables
```bash
# Production settings
DEBUG=False
LOG_LEVEL=WARNING
ENABLE_MONITORING=True
ENABLE_RATE_LIMITING=True

# Security
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Vector Database
MILVUS_HOST=your-milvus-host
MILVUS_PORT=19530
```

#### Monitoring
```python
# Add monitoring endpoints
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow()})

@app.route('/metrics')
def metrics():
    return jsonify({
        "developers_count": get_developers_count(),
        "vector_collections": get_vector_collections_status(),
        "system_health": get_system_health()
    })
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Qdrant Cloud Connection Issues
```bash
# Check Qdrant Cloud connection
python test_qdrant_cloud.py

# Verify environment variables
python test_env.py

# Check Qdrant Cloud status
python -c "from src.vector_store.qdrant_client import QdrantVectorClient; client = QdrantVectorClient(); print(client.health_check())"
```

#### 2. Database Connection Issues
```python
# Test database connection
from src.database.connection import init_database
try:
    init_database()
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### 3. Vector Search Issues
```python
# Test vector search
from src.vector_store.qdrant_client import QdrantVectorClient
try:
    client = QdrantVectorClient()
    collections = client.list_collections()
    print(f"Available collections: {collections}")
except Exception as e:
    print(f"Vector search failed: {e}")
```

#### 4. API Endpoint Issues
```bash
# Test API endpoints
curl http://localhost:8080/api/statistics
curl http://localhost:8080/health
```

### Performance Optimization

#### 1. Vector Search Optimization
```python
# Optimize search parameters
search_params = {
    "metric_type": "COSINE",
    "params": {
        "nprobe": 10,  # Increase for better accuracy, decrease for speed
        "ef": 64       # For HNSW index
    }
}
```

#### 2. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_developers_username ON developers(username);
CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_developer_skills_dev_id ON developer_skills(developer_id);
```

#### 3. Caching
```python
# Add Redis caching for frequently accessed data
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None
```

### Logging and Debugging

#### 1. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. Custom Logging
```python
from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)

def debug_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

#### 3. Performance Monitoring
```python
import time

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

---

**For additional support, please refer to the main README.md or create an issue on GitHub.** 
# DevCareerCompass Project Structure

## 📁 Root Directory

```
dev-career-compass/
├── 📄 app.py                    # Main Flask web application
├── 📄 real_data_collector.py    # Data collection script
├── 📄 requirements.txt          # Python dependencies
├── 📄 astro.yaml               # Astro CLI configuration
├── 📄 run_astro.sh             # Astro CLI management script
├── 📄 AIRFLOW_README.md        # Airflow setup documentation
├── 📄 README.md                # Main project documentation
├── 📄 .gitignore               # Git ignore patterns
├── 📄 .dockerignore            # Docker ignore patterns
├── 📄 Dockerfile               # Docker configuration
├── 📄 env.example              # Environment variables template
├── 📄 devcareer_compass.db     # SQLite database
├── 📁 src/                     # Source code directory
├── 📁 dags/                    # Airflow DAGs
├── 📁 templates/               # Flask HTML templates
├── 📁 static/                  # Static assets (CSS, JS, images)
├── 📁 tests/                   # Test files
├── 📁 .astro/                  # Astro CLI workspace
├── 📁 ai-cap/                  # Virtual environment
├── 📁 instance/                # Flask instance folder
└── 📄 Documentation files      # Various .md files
```

## 📁 Source Code Structure (`src/`)

```
src/
├── 📁 agents/                  # AI agent implementations
│   ├── agent_orchestrator.py   # Agent coordination
│   ├── base_agent.py          # Base agent class
│   └── enhanced_chatbot.py    # AI chatbot
├── 📁 config/                  # Configuration management
│   └── settings.py            # Application settings
├── 📁 data_pipeline/          # Data collection pipeline
│   ├── data_collector.py      # Main data collector
│   ├── github_client.py       # GitHub API client
│   └── job_market_clients.py  # Job market API clients
├── 📁 database/               # Database layer
│   ├── connection.py          # Database connection
│   └── models.py              # SQLAlchemy models
├── 📁 embeddings/             # Vector embeddings
│   └── embedding_generator.py # Embedding generation
├── 📁 insights/               # Data analysis
│   └── career_analyzer.py     # Career analysis
├── 📁 knowledge_graph/        # Knowledge graph
│   └── graph_builder.py       # Graph construction
├── 📁 llm/                    # Language models
│   └── llm_client.py          # LLM integration
├── 📁 preprocessing/          # Data preprocessing
├── 📁 utils/                  # Utility functions
│   └── logger.py              # Logging utilities
└── 📁 vector_store/           # Vector database
    └── qdrant_client.py       # Qdrant integration
```

## 📁 Airflow DAGs (`dags/`)

```
dags/
└── devcareer_compass_dag.py   # Main data collection DAG
```

## 📁 Web Application

```
templates/                     # Flask HTML templates
├── base.html                  # Base template
├── dashboard.html             # Main dashboard
├── analyze.html               # Analysis page
├── analysis_results.html      # Results display
└── other templates...

static/                        # Static assets
├── css/
│   └── style.css             # Main stylesheet
├── js/
│   └── main.js               # JavaScript functionality
└── images/                    # Image assets
```

## 🗂️ Key Files

### Core Application
- **`app.py`**: Main Flask web application with all routes and API endpoints
- **`real_data_collector.py`**: Standalone data collection script
- **`requirements.txt`**: All Python dependencies

### Airflow/Astro
- **`astro.yaml`**: Astro CLI configuration for Airflow
- **`run_astro.sh`**: Script to manage Astro development environment
- **`dags/devcareer_compass_dag.py`**: Airflow DAG for automated data collection

### Configuration
- **`src/config/settings.py`**: Application settings and environment variables
- **`env.example`**: Template for environment variables
- **`.gitignore`**: Git ignore patterns

### Documentation
- **`README.md`**: Main project documentation
- **`AIRFLOW_README.md`**: Airflow setup guide
- **`API_KEYS_SETUP.md`**: API configuration guide
- **`QDRANT_CLOUD_SETUP.md`**: Vector database setup
- **`CONTRIBUTING.md`**: Contribution guidelines
- **`DOCUMENTATION.md`**: Technical documentation


### Updated Files:
- ✅ `.gitignore`: Comprehensive ignore patterns
- ✅ All source files: LinkedIn code removed
- ✅ Documentation: Updated to reflect current structure

## 🚀 Current Status

The project is now clean and organized with:
- ✅ Streamlined directory structure
- ✅ No unnecessary files
- ✅ Comprehensive `.gitignore`
- ✅ Clear documentation
- ✅ Focused on core functionality (GitHub, Stack Overflow, Reddit, Indeed)
- ✅ Ready for development and deployment 
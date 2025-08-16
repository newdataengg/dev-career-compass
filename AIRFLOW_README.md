# DevCareerCompass Airflow Data Collection Pipeline

This directory contains the Airflow setup for automating the DevCareerCompass data collection pipeline using **Astro CLI**.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop running
- Python 3.11+
- Astro CLI installed (`brew install astro`)
- API keys configured in `.env` file

### 1. Start Airflow with Astro
```bash
./run_astro.sh
```

Or manually:
```bash
astro dev start
```

This will:
- Check Docker is running
- Create necessary directories
- Build and start Airflow containers using Astro
- Initialize the database
- Load all DAGs

### 2. Access Airflow UI
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

## 📊 DAG Overview

### DAG Name: `devcareer_compass_data_collection`

**Schedule**: Daily at 2:00 AM (`0 2 * * *`)

**Tasks**:
1. **start_data_collection** - Dummy start task
2. **collect_github_data** - Collect 50 developers from GitHub
3. **collect_stackoverflow_data** - Collect 30 users from Stack Overflow
4. **collect_reddit_data** - Collect 30 users from Reddit
5. **collect_linkedin_jobs** - Collect 25 job postings from LinkedIn
6. **collect_indeed_jobs** - Collect 25 job listings from Indeed
7. **generate_summary** - Generate collection summary
8. **show_database_stats** - Display current database statistics
9. **end_data_collection** - Dummy end task

**Task Dependencies**:
```
start_data_collection
    ↓
[GitHub, StackOverflow, Reddit, LinkedIn, Indeed] (parallel)
    ↓
generate_summary
    ↓
show_database_stats
    ↓
end_data_collection
```

## 🛠️ Astro CLI Operations

### Start Airflow
```bash
astro dev start
```

### Stop Airflow
```bash
astro dev stop
```

### Restart Airflow
```bash
astro dev restart
```

### View Logs
```bash
# All services
astro dev logs

# Specific service
astro dev logs --webserver
astro dev logs --scheduler
```

### Kill All Containers
```bash
astro dev kill
```

### Trigger DAG Manually
1. Go to Airflow UI: http://localhost:8080
2. Navigate to DAGs
3. Find `devcareer_compass_data_collection`
4. Click "Trigger DAG" button

### Check DAG Status
```bash
# List DAGs
astro dev run airflow dags list

# Check DAG runs
astro dev run airflow dags list-runs
```

## 📁 File Structure

```
├── dags/
│   └── devcareer_compass_dag.py          # Main DAG definition
├── .astro/                               # Astro configuration
├── astro.yaml                           # Astro project configuration
├── airflow_settings.yaml                # Airflow settings
├── requirements.txt                     # Python dependencies
├── run_astro.sh                         # Quick start script
└── AIRFLOW_README.md                    # This file
```

## 🔧 Configuration

### Astro Configuration (`astro.yaml`)
The project is configured with:
- Airflow version: 2.8.1
- Python version: 3.11
- Local executor
- SQLite database
- Custom environment variables

### Environment Variables
The following environment variables are used:

- `AIRFLOW__CORE__EXECUTOR=LocalExecutor`
- `AIRFLOW__CORE__SQL_ALCHEMY_CONN=sqlite:///devcareer_compass.db`
- `AIRFLOW__CORE__FERNET_KEY` (auto-generated)
- `AIRFLOW__WEBSERVER__SECRET_KEY` (auto-generated)

### API Keys Required
Make sure your `.env` file contains the necessary API keys:

```env
# GitHub
GITHUB_TOKEN=your_github_token

# Stack Overflow
STACK_OVERFLOW_KEY=your_stackoverflow_key

# Reddit
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_linkedin_token

# Indeed
INDEED_PUBLISHER_ID=your_indeed_publisher_id

# Qdrant
QDRANT_CLOUD_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

## 📈 Monitoring

### Airflow Metrics
- **DAG Success Rate**: Monitor in Airflow UI
- **Task Duration**: View in DAG runs
- **Error Logs**: Check task logs in Airflow UI

### Data Collection Metrics
- **GitHub**: ~50 developers per run
- **Stack Overflow**: ~30 users per run
- **Reddit**: ~30 users per run
- **LinkedIn**: ~25 job postings per run
- **Indeed**: ~25 job listings per run

### Database Statistics
The DAG automatically shows database statistics after each run, including:
- Total developers by source
- Repository and commit counts
- Skill statistics
- Job posting counts

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using the ports
   lsof -i :8080
   lsof -i :5435
   
   # Kill existing containers
   astro dev kill
   ```

2. **DAG not appearing**
   ```bash
   # Restart Astro
   astro dev restart
   ```

3. **API rate limits**
   - Check task logs for rate limit errors
   - Consider reducing collection targets
   - Add delays between API calls

4. **Database connection issues**
   ```bash
   # Rebuild containers
   astro dev restart --no-cache
   ```

### Log Locations
- **Astro Logs**: `astro dev logs`
- **Container Logs**: `astro dev logs --webserver`
- **Application Logs**: Check task logs in Airflow UI

## 🔄 Maintenance

### Regular Tasks
1. **Monitor DAG runs** daily
2. **Check database size** weekly
3. **Review API usage** monthly
4. **Update dependencies** quarterly

### Backup
```bash
# Backup database
cp devcareer_compass.db devcareer_compass.db.backup.$(date +%Y%m%d)

# Backup logs
tar -czf airflow-logs-$(date +%Y%m%d).tar.gz logs/
```

## 🆚 Astro vs Docker Compose

### Why Astro?
- **Simplified setup**: No need to manage Docker Compose files
- **Better dependency management**: Automatic version compatibility
- **Built-in development tools**: Hot reloading, better logging
- **Production ready**: Easy deployment to Astro Cloud
- **Community support**: Official Astronomer support

### Migration from Docker Compose
We previously used plain Docker Compose but switched to Astro for:
- Better dependency resolution
- Simplified development workflow
- Production deployment capabilities

## 📞 Support

For issues with the Astro setup:
1. Check the troubleshooting section above
2. Review Astro logs: `astro dev logs`
3. Check Docker container status
4. Verify API keys and permissions
5. Visit [Astro Documentation](https://docs.astronomer.io/) 
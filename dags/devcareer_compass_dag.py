"""
DevCareerCompass Data Collection DAG
Airflow DAG for collecting developer data from multiple platforms
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default arguments for the DAG
default_args = {
    'owner': 'devcareer-compass',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# DAG definition
dag = DAG(
    'devcareer_compass_data_collection',
    default_args=default_args,
    description='Collect developer data from multiple platforms',
    schedule='0 2 * * *',  # Run daily at 2 AM
    max_active_runs=1,
    tags=['devcareer', 'data-collection', 'github', 'stackoverflow', 'reddit', 'indeed'],
)


def collect_github_data(**context):
    """Collect GitHub developer data"""
    import logging
    from real_data_collector import RealDataCollector
    
    logger = logging.getLogger(__name__)
    logger.info("Starting GitHub data collection")
    
    try:
        collector = RealDataCollector()
        collector.start_timer()
        
        # Collect 50 developers from GitHub
        loaded_count = collector.collect_github_massive(1)
        
        collector.end_timer()
        logger.info(f"GitHub collection completed. Loaded {loaded_count} developers")
        
        # Push the result to XCom for downstream tasks
        context['task_instance'].xcom_push(key='github_loaded', value=loaded_count)
        
        return loaded_count
        
    except Exception as e:
        logger.error(f"GitHub collection failed: {e}")
        # Skip loading if API is not available, return 0
        context['task_instance'].xcom_push(key='github_loaded', value=0)
        return 0


def collect_stackoverflow_data(**context):
    """Collect Stack Overflow user data"""
    import logging
    from real_data_collector import RealDataCollector
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Stack Overflow data collection")
    
    try:
        collector = RealDataCollector()
        collector.start_timer()
        
        # Collect 30 users from Stack Overflow
        loaded_count = collector.collect_stack_overflow_data(500)
        
        collector.end_timer()
        logger.info(f"Stack Overflow collection completed. Loaded {loaded_count} users")
        
        # Push the result to XCom
        context['task_instance'].xcom_push(key='stackoverflow_loaded', value=loaded_count)
        
        return loaded_count
        
    except Exception as e:
        logger.error(f"Stack Overflow collection failed: {e}")
        # Skip loading if API is not available, return 0
        context['task_instance'].xcom_push(key='stackoverflow_loaded', value=0)
        return 0


def collect_reddit_data(**context):
    """Collect Reddit user data"""
    import logging
    from real_data_collector import RealDataCollector
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Reddit data collection")
    
    try:
        collector = RealDataCollector()
        collector.start_timer()
        
        # Collect 30 users from Reddit
        loaded_count = collector.collect_reddit_data(500)
        
        collector.end_timer()
        logger.info(f"Reddit collection completed. Loaded {loaded_count} users")
        
        # Push the result to XCom
        context['task_instance'].xcom_push(key='reddit_loaded', value=loaded_count)
        
        return loaded_count
        
    except Exception as e:
        logger.error(f"Reddit collection failed: {e}")
        # Skip loading if API is not available, return 0
        context['task_instance'].xcom_push(key='reddit_loaded', value=0)
        return 0





def collect_indeed_jobs(**context):
    """Collect Indeed job data using X-Rapid API"""
    import logging
    import os
    from datetime import datetime
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Indeed data collection using X-Rapid API")
    
    try:
        # Import the job market aggregator
        import sys
        sys.path.insert(0, '/opt/airflow')
        
        from src.data_pipeline.job_market_clients import JobMarketDataAggregator
        
        # Initialize the job market aggregator
        aggregator = JobMarketDataAggregator()
        
        # Collect Indeed jobs using the proper X-Rapid API
        logger.info("Collecting Indeed jobs via X-Rapid API...")
        
        # Search for various developer roles
        job_queries = [
            'software engineer', 'data scientist', 'frontend developer',
            'backend developer', 'devops engineer', 'machine learning engineer',
            'python developer', 'javascript developer', 'java developer'
        ]
        
        total_loaded = 0
        
        for query in job_queries:
            logger.info(f"Searching Indeed for: {query}")
            
            try:
                # Add retry logic for API calls
                max_retries = 3
                retry_delay = 5  # seconds
                
                for attempt in range(max_retries):
                    try:
                        jobs = aggregator.indeed_jobs.search_jobs(query, limit=5)  # Reduced limit
                        break  # Success, exit retry loop
                    except Exception as api_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"Indeed API attempt {attempt + 1} failed for '{query}': {api_error}. Retrying in {retry_delay} seconds...")
                            import time
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(f"Indeed API failed after {max_retries} attempts for '{query}': {api_error}")
                            jobs = []
                
                if jobs:
                    # Save jobs to database
                    from src.database.connection import db_manager
                    from src.database.models import JobPosting
                    
                    with db_manager.get_session() as session:
                        for job in jobs:
                            try:
                                # Create job posting
                                db_job = JobPosting(
                                    title=job.get('title', ''),
                                    company=job.get('company', ''),
                                    location=job.get('location', ''),
                                    description=job.get('description', ''),
                                    requirements=job.get('requirements', ''),
                                    salary_min=job.get('salary_min'),
                                    salary_max=job.get('salary_max'),
                                    job_type=job.get('job_type', 'full-time'),
                                    experience_level=job.get('experience_level'),
                                    remote_option=job.get('remote_option', False),
                                    posted_date=job.get('posted_date'),
                                    application_url=job.get('url', ''),
                                    data_source='indeed',
                                    source_id=job.get('id', '')
                                )
                                
                                session.add(db_job)
                                total_loaded += 1
                                
                            except Exception as e:
                                logger.error(f"Error saving job {job.get('title', '')}: {e}")
                                continue
                        
                        session.commit()
                        logger.info(f"Saved {len(jobs)} jobs for query '{query}'")
                else:
                    logger.warning(f"No jobs found for query '{query}'")
                    
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                continue
        
        logger.info(f"Indeed collection completed. Loaded {total_loaded} job listings")
        
        # Push the result to XCom for downstream tasks
        context['task_instance'].xcom_push(key='indeed_loaded', value=total_loaded)
        
        return total_loaded
        
    except Exception as e:
        logger.error(f"Indeed collection failed: {e}")
        # Skip loading if API is not available, return 0
        context['task_instance'].xcom_push(key='indeed_loaded', value=0)
        return 0


def generate_collection_summary(**context):
    """Generate summary of all data collection results"""
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info("Generating collection summary")
    
    # Pull results from XCom
    github_loaded = context['task_instance'].xcom_pull(task_ids='collect_github_data', key='github_loaded')
    stackoverflow_loaded = context['task_instance'].xcom_pull(task_ids='collect_stackoverflow_data', key='stackoverflow_loaded')
    reddit_loaded = context['task_instance'].xcom_pull(task_ids='collect_reddit_data', key='reddit_loaded')

    indeed_loaded = context['task_instance'].xcom_pull(task_ids='collect_indeed_jobs', key='indeed_loaded')
    
    total_loaded = sum([
        github_loaded or 0,
        stackoverflow_loaded or 0,
        reddit_loaded or 0,

        indeed_loaded or 0
    ])
    
    summary = f"""
    🎉 DevCareerCompass Data Collection Summary
    ===========================================
    📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    📊 Collection Results:
    • GitHub: {github_loaded or 0} developers
    • Stack Overflow: {stackoverflow_loaded or 0} users
    • Reddit: {reddit_loaded or 0} users

    • Indeed: {indeed_loaded or 0} job listings
    • Total: {total_loaded} items
    
    ✅ Data collection pipeline completed successfully!
    """
    
    logger.info(summary)
    print(summary)
    
    # Push summary to XCom
    context['task_instance'].xcom_push(key='collection_summary', value=summary)
    context['task_instance'].xcom_push(key='total_loaded', value=total_loaded)
    
    return total_loaded


def show_database_stats(**context):
    """Show current database statistics"""
    import logging
    from real_data_collector import RealDataCollector
    
    logger = logging.getLogger(__name__)
    logger.info("Showing database statistics")
    
    try:
        collector = RealDataCollector()
        collector.show_current_stats()
        
        logger.info("Database statistics displayed successfully")
        
    except Exception as e:
        logger.error(f"Failed to show database stats: {e}")
        raise


def populate_vector_database(**context):
    """Populate Qdrant vector database with new data"""
    import logging
    import sys
    import os
    
    # Add the project root to Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    logger = logging.getLogger(__name__)
    logger.info("Starting vector database population")
    
    try:
        from populate_qdrant import populate_qdrant_collections
        
        # Run the populate script
        populate_qdrant_collections()
        
        logger.info("Vector database population completed successfully")
        context['task_instance'].xcom_push(key='vector_db_populated', value=True)
        
    except Exception as e:
        logger.error(f"Failed to populate vector database: {e}")
        context['task_instance'].xcom_push(key='vector_db_populated', value=False)
        raise


def rebuild_knowledge_graph(**context):
    """Rebuild knowledge graph with new data"""
    import logging
    import sys
    import os
    import asyncio
    
    # Add the project root to Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    logger = logging.getLogger(__name__)
    logger.info("Starting knowledge graph rebuild")
    
    try:
        from src.knowledge_graph.graph_builder import KnowledgeGraphBuilder
        from src.database.connection import DatabaseManager
        
        async def rebuild_graph():
            # Initialize components
            db_manager = DatabaseManager()
            
            # Build knowledge graph
            graph_builder = KnowledgeGraphBuilder()
            
            # Get database session using context manager
            with db_manager.get_session() as session:
                await graph_builder.build_graph_from_database(session)
                logger.info("Knowledge graph rebuilt successfully")
        
        # Run async function
        asyncio.run(rebuild_graph())
        
        context['task_instance'].xcom_push(key='knowledge_graph_rebuilt', value=True)
        
    except Exception as e:
        logger.error(f"Failed to rebuild knowledge graph: {e}")
        context['task_instance'].xcom_push(key='knowledge_graph_rebuilt', value=False)
        raise


# Task definitions
start_task = EmptyOperator(
    task_id='start_data_collection',
    dag=dag,
)

collect_github_task = PythonOperator(
    task_id='collect_github_data',
    python_callable=collect_github_data,
    dag=dag,
)

collect_stackoverflow_task = PythonOperator(
    task_id='collect_stackoverflow_data',
    python_callable=collect_stackoverflow_data,
    dag=dag,
)

collect_reddit_task = PythonOperator(
    task_id='collect_reddit_data',
    python_callable=collect_reddit_data,
    dag=dag,
)



collect_indeed_task = PythonOperator(
    task_id='collect_indeed_jobs',
    python_callable=collect_indeed_jobs,
    dag=dag,
)

summary_task = PythonOperator(
    task_id='generate_summary',
    python_callable=generate_collection_summary,
    dag=dag,
)

stats_task = PythonOperator(
    task_id='show_database_stats',
    python_callable=show_database_stats,
    dag=dag,
)

populate_db_task = PythonOperator(
    task_id='populate_vector_database',
    python_callable=populate_vector_database,
    dag=dag,
)

rebuild_graph_task = PythonOperator(
    task_id='rebuild_knowledge_graph',
    python_callable=rebuild_knowledge_graph,
    dag=dag,
)

end_task = EmptyOperator(
    task_id='end_data_collection',
    dag=dag,
)

# Task dependencies
start_task >> [
    collect_github_task,
    collect_stackoverflow_task,
    collect_reddit_task,
    collect_indeed_task
]

[
    collect_github_task,
    collect_stackoverflow_task,
    collect_reddit_task,
    collect_indeed_task
] >> summary_task >> stats_task >> populate_db_task >> rebuild_graph_task >> end_task 
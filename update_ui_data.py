#!/usr/bin/env python3
"""
Script to update UI data after Airflow data collection.
This script populates Qdrant vector database and rebuilds the knowledge graph
so that the UI reflects the latest collected data.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_vector_database():
    """Populate Qdrant vector database with new data"""
    logger.info("🔄 Starting vector database population...")
    
    try:
        from populate_qdrant import populate_qdrant_collections
        
        # Run the populate script
        populate_qdrant_collections()
        
        logger.info("✅ Vector database population completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to populate vector database: {e}")
        return False


async def rebuild_knowledge_graph():
    """Rebuild knowledge graph with new data"""
    logger.info("🔄 Starting knowledge graph rebuild...")
    
    try:
        from src.knowledge_graph.graph_builder import KnowledgeGraphBuilder
        from src.vector_store.qdrant_client import QdrantVectorClient
        from src.embeddings.embedding_generator import EmbeddingGenerator
        from src.database.connection import DatabaseManager
        
        # Initialize components
        db_manager = DatabaseManager()
        
        # Build knowledge graph
        graph_builder = KnowledgeGraphBuilder()
        
        # Get database session using context manager
        with db_manager.get_session() as session:
            await graph_builder.build_graph_from_database(session)
        logger.info("✅ Knowledge graph rebuilt successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to rebuild knowledge graph: {e}")
        return False


def show_database_stats():
    """Show current database statistics"""
    logger.info("📊 Showing database statistics...")
    
    try:
        from real_data_collector import RealDataCollector
        
        collector = RealDataCollector()
        collector.show_current_stats()
        
        logger.info("✅ Database statistics displayed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to show database stats: {e}")
        return False


async def main():
    """Main function to update UI data"""
    print("🚀 DevCareerCompass UI Data Update")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Show current database stats
    print("Step 1: Checking current database statistics...")
    if not show_database_stats():
        print("❌ Failed to show database stats. Exiting.")
        return
    
    print()
    
    # Step 2: Update vector database
    print("Step 2: Updating vector database...")
    if not update_vector_database():
        print("❌ Failed to update vector database. Exiting.")
        return
    
    print()
    
    # Step 3: Rebuild knowledge graph
    print("Step 3: Rebuilding knowledge graph...")
    if not await rebuild_knowledge_graph():
        print("❌ Failed to rebuild knowledge graph. Exiting.")
        return
    
    print()
    print("🎉 UI Data Update Completed Successfully!")
    print("=" * 50)
    print("✅ Vector database updated")
    print("✅ Knowledge graph rebuilt")
    print("✅ UI should now reflect latest data")
    print()
    print("💡 You can now refresh your browser to see the updated data in the UI.")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 
#!/usr/bin/env python3
"""
DevCareerCompass Project Status Checker
Comprehensive status report for all project components
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_database_status():
    """Check SQLite database status"""
    try:
        from src.database.connection import db_manager
        from src.database.models import Developer, Repository, Skill, Commit, DeveloperSkill
        
        with db_manager.get_session() as session:
            developers_count = session.query(Developer).count()
            repositories_count = session.query(Repository).count()
            skills_count = session.query(Skill).count()
            commits_count = session.query(Commit).count()
            developer_skills_count = session.query(DeveloperSkill).count()
            
            return {
                "status": "✅ Connected",
                "developers": developers_count,
                "repositories": repositories_count,
                "skills": skills_count,
                "commits": commits_count,
                "developer_skills": developer_skills_count
            }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e),
            "developers": 0,
            "repositories": 0,
            "skills": 0,
            "commits": 0,
            "developer_skills": 0
        }

def check_qdrant_status():
    """Check Qdrant Cloud vector database status"""
    try:
        from src.vector_store.qdrant_client import QdrantVectorClient
        
        client = QdrantVectorClient()
        collections = client.list_collections()
        
        collection_stats = {}
        total_vectors = 0
        
        for collection_name in collections:
            try:
                stats = client.get_collection_stats(collection_name)
                collection_stats[collection_name] = stats.get('vectors_count', 0)
                total_vectors += stats.get('vectors_count', 0)
            except Exception:
                collection_stats[collection_name] = 0
        
        return {
            "status": "✅ Connected",
            "collections": collection_stats,
            "total_vectors": total_vectors
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e),
            "collections": {},
            "total_vectors": 0
        }

def check_web_application():
    """Check web application status"""
    try:
        import requests
        response = requests.get("http://localhost:8080/api/statistics", timeout=5)
        if response.status_code == 200:
            return {
                "status": "✅ Running",
                "url": "http://localhost:8080",
                "response_time": f"{response.elapsed.total_seconds():.2f}s"
            }
        else:
            return {
                "status": "⚠️ Responding with errors",
                "url": "http://localhost:8080",
                "status_code": response.status_code
            }
    except requests.exceptions.ConnectionError:
        return {
            "status": "❌ Not running",
            "url": "http://localhost:8080",
            "note": "Start with: python app.py"
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e)
        }

def check_qdrant_cloud_services():
    """Check Qdrant Cloud services status"""
    try:
        from src.vector_store.qdrant_client import QdrantVectorClient
        
        client = QdrantVectorClient()
        health = client.health_check()
        
        if health:
            return {
                "status": "✅ Qdrant Cloud available",
                "url": "https://cloud.qdrant.io",
                "note": "Cloud service is operational"
            }
        else:
            return {
                "status": "❌ Qdrant Cloud unavailable",
                "url": "https://cloud.qdrant.io",
                "note": "Check credentials and network"
            }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e),
            "note": "Check QDRANT_CLOUD_SETUP.md for setup instructions"
        }

def check_environment():
    """Check environment configuration"""
    try:
        from src.config.settings import settings
        
        env_status = {
            "github_token": "✅ Set" if settings.github_token else "❌ Missing",
            "qdrant_api_key": "✅ Set" if settings.qdrant_api_key else "⚠️ Optional",
            "qdrant_cloud_url": "✅ Set" if settings.qdrant_cloud_url else "⚠️ Optional",
            "debug_mode": settings.debug,
            "log_level": settings.log_level
        }
        
        return {
            "status": "✅ Configured",
            "settings": env_status
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e)
        }

def check_file_structure():
    """Check project file structure"""
    required_files = [
        "app.py",
        "main.py",
        "requirements.txt",
        "env.example",
        "QDRANT_CLOUD_SETUP.md",
        "README.md",
        "DOCUMENTATION.md"
    ]
    
    required_dirs = [
        "src/",
        "src/database/",
        "src/vector_store/",
        "src/agents/",
        "src/llm/",
        "src/embeddings/",
        "src/knowledge_graph/",
        "src/insights/",
        "src/config/",
        "src/utils/",
        "templates/",
        "static/",
        "tests/"
    ]
    
    file_status = {}
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            file_status[file] = f"✅ {size} bytes"
        else:
            file_status[file] = "❌ Missing"
    
    dir_status = {}
    for dir_path in required_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            files_count = len([f for f in os.listdir(dir_path) if f.endswith('.py')])
            dir_status[dir_path] = f"✅ {files_count} Python files"
        else:
            dir_status[dir_path] = "❌ Missing"
    
    # Check if all files and directories exist
    all_files_exist = all("✅" in status for status in file_status.values())
    all_dirs_exist = all("✅" in status for status in dir_status.values())
    
    return {
        "status": "✅ Complete" if all_files_exist and all_dirs_exist else "❌ Incomplete",
        "files": file_status,
        "directories": dir_status
    }

def generate_status_report():
    """Generate comprehensive status report"""
    print("🎯 DevCareerCompass Project Status Report")
    print("=" * 60)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check all components
    components = {
        "🗄️ Database": check_database_status(),
        "☁️ Qdrant Cloud": check_qdrant_status(),
        "🌐 Web Application": check_web_application(),
        "☁️ Qdrant Cloud Services": check_qdrant_cloud_services(),
        "⚙️ Environment": check_environment(),
        "📁 File Structure": check_file_structure()
    }
    
    # Display component status
    for component_name, status in components.items():
        print(f"{component_name}")
        print("-" * 40)
        
        if component_name == "🗄️ Database":
            print(f"Status: {status['status']}")
            if status['status'] == "✅ Connected":
                print(f"📊 Data Statistics:")
                print(f"   • Developers: {status['developers']}")
                print(f"   • Repositories: {status['repositories']}")
                print(f"   • Skills: {status['skills']}")
                print(f"   • Commits: {status['commits']}")
                print(f"   • Developer-Skill Relationships: {status['developer_skills']}")
            else:
                print(f"Error: {status.get('error', 'Unknown error')}")
        
        elif component_name == "☁️ Qdrant Cloud":
            print(f"Status: {status['status']}")
            if status['status'] == "✅ Connected":
                print(f"📊 Vector Collections:")
                for collection, count in status['collections'].items():
                    print(f"   • {collection}: {count} vectors")
                print(f"   • Total Vectors: {status['total_vectors']}")
            else:
                print(f"Error: {status.get('error', 'Unknown error')}")
        
        elif component_name == "🌐 Web Application":
            print(f"Status: {status['status']}")
            if status['status'] == "✅ Running":
                print(f"URL: {status['url']}")
                print(f"Response Time: {status['response_time']}")
            elif status['status'] == "❌ Not running":
                print(f"URL: {status['url']}")
                print(f"Note: {status['note']}")
            else:
                print(f"Details: {status}")
        
        elif component_name == "☁️ Qdrant Cloud Services":
            print(f"Status: {status['status']}")
            if status['status'] == "✅ Qdrant Cloud available":
                print(f"URL: {status['url']}")
                print(f"Note: {status['note']}")
            else:
                print(f"Error: {status.get('error', 'Unknown error')}")
                print(f"Note: {status.get('note', 'Check setup')}")
        
        elif component_name == "⚙️ Environment":
            print(f"Status: {status['status']}")
            if status['status'] == "✅ Configured":
                print("Configuration:")
                for key, value in status['settings'].items():
                    print(f"   • {key}: {value}")
            else:
                print(f"Error: {status.get('error', 'Unknown error')}")
        
        elif component_name == "📁 File Structure":
            print(f"Status: {status['status']}")
            if status['status'] == "✅ Complete":
                print("Files:")
                for file, file_status in status['files'].items():
                    print(f"   • {file}: {file_status}")
                print("Directories:")
                for dir_path, dir_status in status['directories'].items():
                    print(f"   • {dir_path}: {dir_status}")
            else:
                print("Missing files or directories:")
                for file, file_status in status['files'].items():
                    if "❌" in file_status:
                        print(f"   • {file}: {file_status}")
                for dir_path, dir_status in status['directories'].items():
                    if "❌" in dir_status:
                        print(f"   • {dir_path}: {dir_status}")
        
        print()
    
    # Summary
    print("📋 Summary")
    print("-" * 40)
    
    # Count statuses
    total_components = len(components)
    working_components = sum(1 for status in components.values() 
                           if status.get('status', '').startswith('✅'))
    
    print(f"Total Components: {total_components}")
    print(f"Working Components: {working_components}")
    print(f"Health Score: {(working_components/total_components)*100:.1f}%")
    
    # Recommendations
    print("\n💡 Recommendations")
    print("-" * 40)
    
    if components["🌐 Web Application"]["status"] == "❌ Not running":
        print("• Start the web application: python app.py")
    
    if components["☁️ Qdrant Cloud"]["status"] != "✅ Connected":
        print("• Setup Qdrant Cloud: python qdrant_cloud_setup.py")
    
    if components["⚙️ Environment"]["status"] != "✅ Configured":
        print("• Configure environment variables in .env file")
    
    if components["🗄️ Database"]["status"] != "✅ Connected":
        print("• Initialize database: python -c 'from src.database.connection import init_database; init_database()'")
    
    print("\n🎉 Project Status Check Complete!")

if __name__ == "__main__":
    generate_status_report() 
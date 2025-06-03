#!/usr/bin/env python3
"""
Enhanced Memory System Setup with pgvectorscale integration

This script sets up the enhanced memory system with pgvectorscale for 
optimal performance in semantic search operations.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_postgresql_version():
    """Check if PostgreSQL version supports pgvectorscale (>= 13)."""
    try:
        result = subprocess.run(
            ['psql', '--version'], 
            capture_output=True, text=True, check=True
        )
        version_line = result.stdout.strip()
        logger.info(f"Found PostgreSQL: {version_line}")
        return True
    except subprocess.CalledProcessError:
        logger.error("PostgreSQL not found. Please install PostgreSQL >= 13")
        return False

def install_python_dependencies():
    """Install Python dependencies for enhanced memory system."""
    logger.info("Installing Python dependencies...")
    
    requirements = [
        "sentence-transformers>=2.0.0",
        "psycopg2-binary>=2.9.0", 
        "numpy>=1.21.0"
    ]
    
    try:
        for req in requirements:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], check=True)
        logger.info("✓ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Python dependencies: {e}")
        return False

def create_config_file():
    """Create memory system configuration file."""
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "mcp-memory.env"
    example_file = config_dir / "mcp-memory.env.example"
    
    if not config_file.exists() and example_file.exists():
        # Copy example to actual config
        import shutil
        shutil.copy2(example_file, config_file)
        logger.info(f"✓ Created config file: {config_file}")
        logger.warning("Please edit the config file with your database credentials")
        return True
    elif config_file.exists():
        logger.info(f"✓ Config file already exists: {config_file}")
        return True
    else:
        logger.error("No config template found")
        return False

def setup_database_extensions():
    """Setup database extensions for enhanced memory system."""
    logger.info("Setting up database extensions...")
    
    # Note: This requires database admin privileges
    extensions_sql = """
    -- Install pgvector (required)
    CREATE EXTENSION IF NOT EXISTS vector;
    
    -- Optional: Install pgvectorscale for enhanced performance
    -- Uncomment the following line if pgvectorscale is available:
    -- CREATE EXTENSION IF NOT EXISTS vectorscale;
    
    -- Optional: Install pgai for automatic embedding generation  
    -- Uncomment the following line if pgai is available:
    -- CREATE EXTENSION IF NOT EXISTS ai;
    """
    
    logger.info("SQL commands for database setup:")
    print("="*60)
    print(extensions_sql)
    print("="*60)
    
    logger.warning("Please run the above SQL commands as a PostgreSQL superuser")
    logger.info("For pgvectorscale installation, visit: https://github.com/timescale/pgvectorscale")
    logger.info("For pgai installation, visit: https://github.com/timescale/pgai")
    
    return True

def test_memory_system():
    """Test the enhanced memory system functionality."""
    logger.info("Testing memory system...")
    
    try:
        # Import and test basic functionality
        from tools.memory_system import MemorySystem
        
        # Initialize memory system
        memory_system = MemorySystem()
        
        # Test embedding generation
        if memory_system.embedding_model:
            embedding = memory_system._generate_embedding("test memory content")
            if embedding:
                logger.info(f"✓ Embedding generation working (dim: {len(embedding)})")
            else:
                logger.warning("⚠ Embedding generation failed")
        else:
            logger.warning("⚠ Embedding model not loaded - semantic search disabled")
        
        logger.info("✓ Memory system basic test completed")
        return True
        
    except Exception as e:
        logger.error(f"Memory system test failed: {e}")
        return False

def update_existing_embeddings():
    """Update embeddings for existing memories."""
    logger.info("Updating embeddings for existing memories...")
    
    try:
        from tools.memory_system import MemorySystem
        
        memory_system = MemorySystem()
        if memory_system.embedding_model:
            result = memory_system.update_embeddings_for_existing_memories(batch_size=20)
            if result['success']:
                logger.info(f"✓ Updated embeddings for {result['updated']} memories")
            else:
                logger.warning(f"⚠ Embedding update failed: {result.get('error', 'Unknown error')}")
        else:
            logger.warning("⚠ Cannot update embeddings - embedding model not available")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update embeddings: {e}")
        return False

def main():
    """Main setup function."""
    logger.info("🚀 Starting Enhanced Memory System Setup")
    
    # Step 1: Check prerequisites
    if not check_postgresql_version():
        return False
    
    # Step 2: Install Python dependencies
    if not install_python_dependencies():
        return False
    
    # Step 3: Create configuration
    if not create_config_file():
        return False
    
    # Step 4: Setup database extensions
    setup_database_extensions()
    
    # Step 5: Test system
    if not test_memory_system():
        logger.warning("⚠ Basic tests failed - check configuration")
    
    # Step 6: Update existing embeddings
    update_existing_embeddings()
    
    logger.info("🎉 Enhanced Memory System setup completed!")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Install pgvectorscale for optimal performance:")
    print("   https://github.com/timescale/pgvectorscale#installation")
    print("2. Consider pgai for automated embedding pipelines:")
    print("   https://github.com/timescale/pgai#installation")
    print("3. Update database credentials in config/mcp-memory.env")
    print("4. Run SQL commands shown above as PostgreSQL superuser")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

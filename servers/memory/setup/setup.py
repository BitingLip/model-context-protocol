#!/usr/bin/env python3
"""
Memory MCP Server Setup Script

This script provides a comprehensive setup for the Memory MCP Server:
1. Checks and sets up the PostgreSQL database and required extensions
2. Installs Python dependencies
3. Creates and configures the memory.env configuration file
4. Tests the memory system functionality
5. Updates embeddings for existing memories (if any)

Usage:
    python setup.py [--force] [--skip-db-create] [--skip-python-deps] [--skip-embeddings-update]
"""

import os
import sys
import logging
import subprocess
import argparse
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path to import memory modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Define constants
CONFIG_DIR = parent_dir / "config"
CONFIG_FILE = CONFIG_DIR / "memory.env"
CONFIG_EXAMPLE = CONFIG_DIR / "memory.env.example"
PROJECT_ROOT = parent_dir.parent.parent.parent


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Memory MCP Server Setup")
    parser.add_argument("--force", action="store_true", help="Force setup even if already configured")
    parser.add_argument("--skip-db-create", action="store_true", help="Skip database creation and schema setup")
    parser.add_argument("--skip-python-deps", action="store_true", help="Skip Python dependencies installation")
    parser.add_argument("--skip-embeddings-update", action="store_true", help="Skip updating embeddings for existing memories")
    return parser.parse_args()


def check_postgresql_version():
    """Check if PostgreSQL version is installed and compatible."""
    logger.info("Checking PostgreSQL installation...")
    
    try:
        result = subprocess.run(
            ['psql', '--version'], 
            capture_output=True, text=True, check=True
        )
        version_line = result.stdout.strip()
        logger.info(f"Found PostgreSQL: {version_line}")
        
        # Extract version number and check compatibility
        import re
        version_match = re.search(r'(\d+\.\d+)', version_line)
        if version_match:
            version = float(version_match.group(1))
            if version < 12:
                logger.warning(f"⚠️ PostgreSQL version {version} may have limited vector support")
                logger.warning("   Recommended: PostgreSQL 13 or newer")
            else:
                logger.info(f"✅ PostgreSQL version {version} is compatible")
        
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ PostgreSQL not found. Please install PostgreSQL >= 13")
        return False
    except FileNotFoundError:
        logger.error("❌ PostgreSQL client (psql) not found. Please install PostgreSQL >= 13")
        return False


def install_python_dependencies():
    """Install required Python dependencies."""
    logger.info("Installing Python dependencies...")
    
    requirements_file = parent_dir / "requirements.txt"
    
    if not requirements_file.exists():
        logger.error(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        logger.info("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install Python dependencies: {e}")
        return False


def create_config_file():
    """Create configuration file from example if it doesn't exist."""
    logger.info("Setting up configuration file...")
    
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created config directory: {CONFIG_DIR}")
    
    if CONFIG_FILE.exists() and not args.force:
        logger.info(f"✅ Config file already exists: {CONFIG_FILE}")
        return True
    
    if not CONFIG_EXAMPLE.exists():
        logger.error(f"❌ Config example file not found: {CONFIG_EXAMPLE}")
        
        # Create a basic example file if missing
        logger.info("Creating basic configuration example file...")
        basic_config = """# Memory System Database Configuration
# PostgreSQL Connection Settings
MEMORY_DB_HOST=localhost
MEMORY_DB_PORT=5432
MEMORY_DB_NAME=memory_system
MEMORY_DB_USER=postgres
MEMORY_DB_PASSWORD=postgres

# Optional: Embedding Model Configuration
# EMBEDDING_MODEL=all-MiniLM-L6-v2
"""
        with open(CONFIG_EXAMPLE, 'w') as f:
            f.write(basic_config)
        logger.info(f"✅ Created basic config example: {CONFIG_EXAMPLE}")
    
    # Copy example to actual config
    shutil.copy2(CONFIG_EXAMPLE, CONFIG_FILE)
    logger.info(f"✅ Created config file: {CONFIG_FILE}")
    logger.info("⚠️ Please edit the config file with your database credentials")
    
    return True


def load_config():
    """Load configuration from the memory.env file."""
    logger.info("Loading configuration...")
    
    if not CONFIG_FILE.exists():
        logger.warning(f"⚠️ Config file not found: {CONFIG_FILE}")
        return {}
    
    config = {}
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
                # Also set as environment variable for modules that use os.environ
                os.environ[key.strip()] = value.strip()
    
    return config


def setup_database(config):
    """Set up the database and required extensions."""
    logger.info("Setting up database...")
    
    if args.skip_db_create:
        logger.info("Skipping database creation (--skip-db-create flag used)")
        return True
    
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        logger.error("❌ psycopg2 module not found. Please run: pip install psycopg2-binary")
        logger.error("   This is required for database operations. Install it with:")
        logger.error("   pip install psycopg2-binary>=2.9.0")
        return False
    
    # Get database settings
    db_host = config.get('MEMORY_DB_HOST', 'localhost')
    db_port = config.get('MEMORY_DB_PORT', '5432')
    db_name = config.get('MEMORY_DB_NAME', 'memory_system')
    db_user = config.get('MEMORY_DB_USER', 'postgres')
    db_password = config.get('MEMORY_DB_PASSWORD', 'postgres')
    
    logger.info(f"Database Settings:")
    logger.info(f"  Host: {db_host}")
    logger.info(f"  Port: {db_port}")
    logger.info(f"  Database: {db_name}")
    logger.info(f"  User: {db_user}")
    logger.info(f"  Password: {'*' * len(db_password)}")
    
    # Validate database settings
    if not db_user or db_user == "your_secure_username_here":
        logger.error("❌ Invalid database username in config. Please edit memory.env")
        return False
        
    if not db_password or db_password == "your_secure_password_here":
        logger.error("❌ Invalid database password in config. Please edit memory.env")
        return False
    
    # Check if database exists and create it if needed
    connection = None
    try:
        logger.info(f"Connecting to database '{db_name}'...")
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=10  # Add timeout to prevent hanging
        )
        logger.info("✅ Connected to database successfully!")
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            logger.info(f"Database '{db_name}' does not exist. Attempting to create it...")
            try:
                # Connect to default postgres database to create new database
                conn = psycopg2.connect(
                    host=db_host,
                    port=db_port,
                    dbname="postgres",  # Connect to default postgres database
                    user=db_user,
                    password=db_password,
                    connect_timeout=10
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE {db_name}")
                cursor.close()
                conn.close()
                logger.info(f"✅ Created database '{db_name}' successfully!")
                
                # Connect to the new database
                connection = psycopg2.connect(
                    host=db_host,
                    port=db_port,
                    dbname=db_name,
                    user=db_user,
                    password=db_password,
                    connect_timeout=10
                )
                logger.info("✅ Connected to database successfully!")
            except psycopg2.OperationalError as e2:
                if "password authentication failed" in str(e2).lower():
                    logger.error(f"❌ Authentication failed: Invalid username or password")
                    logger.error("  Please check your credentials in memory.env")
                elif "could not connect to server" in str(e2).lower():
                    logger.error(f"❌ Connection failed: PostgreSQL server not running or incorrect host/port")
                    logger.error("  Please check that PostgreSQL is running and verify host/port in memory.env")
                else:
                    logger.error(f"❌ Failed to create database: {e2}")
                logger.error("  Troubleshooting tips:")
                logger.error("  1. Verify PostgreSQL is installed and running")
                logger.error("  2. Check if the user has CREATE DATABASE privileges")
                logger.error("  3. Verify network connectivity to the database server")
                return False
        elif "password authentication failed" in str(e).lower():
            logger.error(f"❌ Authentication failed: Invalid username or password")
            logger.error("  Please check your credentials in memory.env")
            return False
        elif "could not connect to server" in str(e).lower():
            logger.error(f"❌ Connection failed: PostgreSQL server not running or incorrect host/port")
            logger.error("  Please check that PostgreSQL is running and verify host/port in memory.env")
            return False
        else:
            logger.error(f"❌ Database connection error: {e}")
            return False
    
    # Check PostgreSQL version
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version_info = cursor.fetchone()[0]
        logger.info(f"PostgreSQL version: {version_info}")
        
        # Extract version number
        import re
        version_match = re.search(r'PostgreSQL (\d+\.\d+)', version_info)
        if version_match:
            version = float(version_match.group(1))
            if version < 12:
                logger.warning(f"⚠️ PostgreSQL version {version} is lower than recommended (12+)")
                logger.warning("  Vector operations may have limited performance")
    except Exception as e:
        logger.warning(f"⚠️ Could not determine PostgreSQL version: {e}")
    
    # Check and enable extensions
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Check for pgvector (required for semantic search)
        cursor.execute("SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'vector';")
        result = cursor.fetchone()
        has_vector = result[0] == 1 if result else False
        
        if has_vector:
            logger.info("✅ pgvector extension is available.")
            
            # Try to create the extension if not already created
            try:
                connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("✅ pgvector extension is enabled.")
            except Exception as e:
                if "permission denied" in str(e).lower():
                    logger.warning("⚠️ Could not create pgvector extension: Permission denied")
                    logger.warning("  Try connecting as a database superuser or run:")
                    logger.warning("  CREATE EXTENSION IF NOT EXISTS vector;")
                else:
                    logger.warning(f"⚠️ Could not create pgvector extension: {e}")
        else:
            logger.warning("⚠️ pgvector extension is not available. Semantic search will be limited.")
            logger.warning("  Installation instructions:")
            logger.warning("  1. Download from: https://github.com/pgvector/pgvector")
            logger.warning("  2. Follow installation guide for your PostgreSQL version")
            logger.warning("  3. Run: CREATE EXTENSION vector;")
            
        # Check for pgvectorscale extension (optional)
        cursor.execute("SELECT COUNT(*) FROM pg_available_extensions WHERE name = 'vectorscale';")
        result = cursor.fetchone()
        has_vectorscale = result[0] == 1 if result else False
        
        if has_vectorscale:
            logger.info("✅ pgvectorscale extension is available (performance enhancement).")
            try:
                connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vectorscale;")
                logger.info("✅ pgvectorscale extension is enabled.")
            except Exception as e:
                if "permission denied" in str(e).lower():
                    logger.info("ℹ️ Could not create pgvectorscale extension: Permission denied")
                    logger.info("  Run as database superuser: CREATE EXTENSION IF NOT EXISTS vectorscale;")
                else:
                    logger.info(f"ℹ️ Could not create pgvectorscale extension: {e}")
        else:
            logger.info("ℹ️ pgvectorscale extension is not available (optional for enhanced performance)")
            logger.info("  To install: https://github.com/timescale/pgvectorscale#installation")
    except Exception as e:
        logger.warning(f"⚠️ Could not check vector extensions availability: {e}")
    
    # Initialize database tables
    logger.info("Checking/creating required tables...")
    try:
        from tools.memory.database import DatabaseManager
        db_manager = DatabaseManager(str(PROJECT_ROOT))
        db_manager._create_tables()
        logger.info("✅ Memory system tables exist or were created successfully!")
    except ImportError as e:
        logger.error(f"❌ Failed to import memory system modules: {e}")
        logger.error("  Check that the project structure is correct and Python path includes the server directory")
        return False
    except Exception as e:
        if "permission denied" in str(e).lower():
            logger.error(f"❌ Failed to create tables: Permission denied")
            logger.error("  The database user does not have sufficient privileges.")
            logger.error("  Grant CREATE TABLE permission to the database user.")
        else:
            logger.error(f"❌ Failed to create memory system tables: {e}")
        return False
    
    # Verify tables were created
    try:
        if cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            table_count = cursor.fetchone()[0]
            logger.info(f"✅ Database contains {table_count} tables in public schema")
    except Exception as e:
        logger.warning(f"⚠️ Could not verify table creation: {e}")
    
    # Close connections
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    
    return True


def test_memory_system():
    """Test the memory system basic functionality."""
    logger.info("Testing memory system...")
    
    try:
        # Import the memory system
        from tools.memory_mcp_tool import MemoryMCPTool
        
        # Initialize memory system with project root
        memory_tool = MemoryMCPTool(str(PROJECT_ROOT))
        
        # Test database connection via basic operations
        test_result = memory_tool.store_memory(
            memory_type="setup_test",
            content="This is a test memory to verify the setup process."
        )
        
        if isinstance(test_result, dict) and test_result.get("error"):
            logger.warning(f"⚠️ Memory storage failed: {test_result.get('error')}")
            return False
        else:
            logger.info("✅ Memory storage working")
        
        # Check if embedding model is loaded
        has_embeddings = hasattr(memory_tool, 'embedding_model') and memory_tool.embedding_model is not None
        if has_embeddings:
            logger.info("✅ Embedding model loaded successfully")
        else:
            logger.warning("⚠️ Embedding model not loaded - semantic search will be limited")
        
        logger.info("✅ Memory system test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory system test failed: {e}")
        return False


def update_existing_embeddings():
    """Update embeddings for existing memories."""
    if args.skip_embeddings_update:
        logger.info("Skipping embeddings update (--skip-embeddings-update flag used)")
        return True
    
    logger.info("Updating embeddings for existing memories...")
    
    try:
        from tools.memory_mcp_tool import MemoryMCPTool
        
        memory_system = MemoryMCPTool(str(PROJECT_ROOT))
        if hasattr(memory_system, 'embedding_model') and memory_system.embedding_model is not None:
            result = memory_system.update_embeddings_for_existing_memories(batch_size=20)
            if isinstance(result, dict) and result.get('success'):
                logger.info(f"✅ Updated embeddings for {result.get('updated', 0)} memories")
            else:
                logger.warning(f"⚠️ Embedding update failed: {result.get('error', 'Unknown error')}")
        else:
            logger.warning("⚠️ Cannot update embeddings - embedding model not available")
            logger.warning("   Install sentence-transformers to enable embedding generation")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to update embeddings: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("🚀 Starting Memory MCP Server Setup")
    
    # Step 1: Check PostgreSQL installation
    if not check_postgresql_version():
        logger.error("❌ PostgreSQL check failed - please install PostgreSQL >= 12")
        return False
    
    # Step 2: Install Python dependencies (if not skipped)
    if not args.skip_python_deps:
        if not install_python_dependencies():
            logger.error("❌ Python dependencies installation failed")
            return False
    else:
        logger.info("Skipping Python dependencies installation (--skip-python-deps flag used)")
    
    # Step 3: Create configuration file if needed
    if not create_config_file():
        logger.error("❌ Configuration file setup failed")
        return False
    
    # Step 4: Load configuration
    config = load_config()
    
    # Step 5: Setup database and tables
    if not setup_database(config):
        logger.error("❌ Database setup failed")
        return False
    
    # Step 6: Test memory system
    if not test_memory_system():
        logger.warning("⚠️ Memory system test failed - check configuration")
    
    # Step 7: Update existing embeddings
    if not update_existing_embeddings():
        logger.warning("⚠️ Updating embeddings failed - check embedding model")
    
    logger.info("🎉 Memory MCP Server setup completed successfully!")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Edit database credentials in servers/memory/config/memory.env")
    print("2. For optimal performance, consider installing PostgreSQL extensions:")
    print("   - pgvector (required): https://github.com/pgvector/pgvector#installation")
    print("   - pgvectorscale (optional): https://github.com/timescale/pgvectorscale#installation")
    print("3. Start the Memory MCP Server with: python server.py")
    print("="*60)
    
    return True


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Run the main setup
    success = main()
    sys.exit(0 if success else 1)

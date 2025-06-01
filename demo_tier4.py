#!/usr/bin/env python3
"""
Demo script for the new Tier 4 Infrastructure Analysis tools in Biting Lip MCP Server.

This script demonstrates the API endpoint discovery, database schema analysis,
and log analysis capabilities.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.server import BitingLipMCPServer
except ImportError:
    # Fallback for direct execution
    from server import BitingLipMCPServer


async def demo_tier4_tools():
    """Demonstrate the Tier 4 infrastructure analysis tools."""
    print("🔧 Biting Lip MCP Server - Tier 4 Infrastructure Analysis Tools Demo")
    print("=" * 70)
    
    # Initialize server
    server = BitingLipMCPServer()
    
    print("\n🎯 Available Tier 4 Tools:")
    print("1. discover_api_endpoints - API endpoint discovery across frameworks")
    print("2. analyze_database_schemas - Database schema analysis")
    print("3. analyze_logs - Log analysis and pattern detection")
    
    # Demo 1: API Endpoint Discovery
    print("\n" + "="*50)
    print("🌐 Demo 1: API Endpoint Discovery")
    print("="*50)
    
    try:
        print("\n📍 Discovering all API endpoints...")
        result = await server.handle_call_tool("discover_api_endpoints", {})
        
        if "content" in result:
            data = json.loads(result["content"][0]["text"])
            summary = data.get("summary", {})
            
            print(f"✅ Found {summary.get('total_endpoints', 0)} total endpoints")
            print(f"📋 Frameworks detected: {', '.join(summary.get('frameworks_detected', []))}")
            print(f"📁 Files analyzed: {summary.get('files_analyzed', 0)}")
            
            # Show sample endpoints
            endpoints = data.get("endpoints", {})
            for framework, framework_data in endpoints.items():
                if framework_data.get("endpoints"):
                    print(f"\n🔹 {framework.upper()} endpoints:")
                    for endpoint in framework_data["endpoints"][:3]:  # Show first 3
                        methods = endpoint.get("methods", ["GET"])
                        path = endpoint.get("path", "unknown")
                        print(f"   {', '.join(methods)} {path}")
                    
                    if len(framework_data["endpoints"]) > 3:
                        print(f"   ... and {len(framework_data['endpoints']) - 3} more")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in API endpoint discovery: {e}")
    
    # Demo 2: Framework-specific API Discovery
    print(f"\n📍 Discovering Flask-specific endpoints...")
    try:
        result = await server.handle_call_tool("discover_api_endpoints", {"framework": "flask"})
        
        if "content" in result:
            data = json.loads(result["content"][0]["text"])
            flask_endpoints = data.get("endpoints", {}).get("flask", {}).get("endpoints", [])
            print(f"✅ Found {len(flask_endpoints)} Flask endpoints")
            
            for endpoint in flask_endpoints[:2]:  # Show first 2
                print(f"   🔸 {endpoint.get('methods', ['GET'])} {endpoint.get('path', 'unknown')}")
                if endpoint.get("function"):
                    print(f"      Function: {endpoint['function']}")
                if endpoint.get("file"):
                    print(f"      File: {endpoint['file']}")
        else:
            print(f"❌ Error: {result.get('error', 'No Flask endpoints found')}")
            
    except Exception as e:
        print(f"❌ Error in Flask-specific discovery: {e}")
    
    # Demo 3: Database Schema Analysis
    print("\n" + "="*50)
    print("🗃️  Demo 2: Database Schema Analysis")
    print("="*50)
    
    try:
        print("\n📊 Analyzing all database schemas...")
        result = await server.handle_call_tool("analyze_database_schemas", {})
        
        if "content" in result:
            data = json.loads(result["content"][0]["text"])
            summary = data.get("summary", {})
            
            print(f"✅ Found {summary.get('databases_found', 0)} database configurations")
            print(f"📋 Database types: {', '.join(summary.get('database_types', []))}")
            print(f"📊 Total tables/models: {summary.get('total_tables', 0) + summary.get('total_models', 0)}")
            print(f"📁 Schema files analyzed: {summary.get('schema_files_analyzed', 0)}")
            
            # Show details for each database type
            schemas = data.get("schemas", {})
            for db_type, schema_data in schemas.items():
                print(f"\n🔹 {db_type.upper()}:")
                
                if db_type == "sqlite":
                    databases = schema_data.get("databases", [])
                    print(f"   Database files: {len(databases)}")
                    for db in databases[:2]:  # Show first 2
                        print(f"   📁 {db.get('file', 'unknown')} ({len(db.get('tables', []))} tables)")
                
                elif db_type == "django_orm":
                    apps = schema_data.get("apps", [])
                    print(f"   Django apps: {len(apps)}")
                    for app in apps[:2]:  # Show first 2
                        print(f"   📦 {app.get('app_name', 'unknown')} ({app.get('model_count', 0)} models)")
                
                elif db_type in ["postgresql", "mysql"]:
                    configs = schema_data.get("connection_configs", [])
                    schema_files = schema_data.get("schema_files", [])
                    print(f"   Config files: {len(configs)}")
                    print(f"   Schema files: {len(schema_files)}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in database schema analysis: {e}")
    
    # Demo 4: SQLite-specific Analysis
    print(f"\n📊 Analyzing SQLite databases specifically...")
    try:
        result = await server.handle_call_tool("analyze_database_schemas", {"database_type": "sqlite"})
        
        if "content" in result:
            data = json.loads(result["content"][0]["text"])
            sqlite_data = data.get("schemas", {}).get("sqlite", {})
            
            if sqlite_data:
                databases = sqlite_data.get("databases", [])
                print(f"✅ Found {len(databases)} SQLite database files")
                
                for db in databases[:1]:  # Show first database in detail
                    print(f"\n   🔸 Database: {db.get('file', 'unknown')}")
                    print(f"      Size: {db.get('size', 0)} bytes")
                    print(f"      Tables: {len(db.get('tables', []))}")
                    
                    for table in db.get("tables", [])[:3]:  # Show first 3 tables
                        print(f"         📋 {table.get('name', 'unknown')} ({len(table.get('columns', []))} columns)")
            else:
                print("ℹ️  No SQLite databases found")
        else:
            print(f"❌ Error: {result.get('error', 'No SQLite databases found')}")
            
    except Exception as e:
        print(f"❌ Error in SQLite analysis: {e}")
    
    # Demo 5: Log Analysis
    print("\n" + "="*50)
    print("📊 Demo 3: Log Analysis")
    print("="*50)
    
    try:
        print("\n📜 Analyzing all log files...")
        result = await server.handle_call_tool("analyze_logs", {})
        
        if "content" in result:
            data = json.loads(result["content"][0]["text"])
            summary = data.get("summary", {})
            
            print(f"✅ Found {summary.get('log_files_found', 0)} log files")
            print(f"📊 Total log entries: {summary.get('total_entries', 0)}")
            print(f"❌ Error count: {summary.get('error_count', 0)}")
            print(f"⚠️  Warning count: {summary.get('warning_count', 0)}")
            
            # Show log file details
            logs = data.get("logs", {})
            for log_file, log_data in list(logs.items())[:3]:  # Show first 3 log files
                print(f"\n🔹 {log_file}:")
                print(f"   Format: {log_data.get('format', 'unknown')}")
                print(f"   Entries: {log_data.get('entry_count', 0)}")
                print(f"   Errors: {log_data.get('error_count', 0)}")
                print(f"   Size: {log_data.get('file_size', 0)} bytes")
                
                # Show error patterns
                error_patterns = log_data.get("error_patterns", [])
                if error_patterns:
                    print(f"   Top error pattern: {error_patterns[0].get('pattern', 'unknown')[:60]}...")
            
            # Show cross-log patterns
            patterns = data.get("patterns", {})
            cross_errors = patterns.get("cross_file_errors", [])
            if cross_errors:
                print(f"\n🔍 Cross-file error patterns:")
                for pattern in cross_errors[:2]:  # Show first 2
                    print(f"   🔸 Found in {len(pattern.get('files', []))} files: {pattern.get('pattern', 'unknown')[:50]}...")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in log analysis: {e}")
    
    # Demo 6: Error-specific Log Analysis
    print(f"\n📜 Analyzing error logs specifically...")
    try:
        result = await server.handle_call_tool("analyze_logs", {"log_type": "error"})
        
        if "content" in result:
            data = json.loads(result["content"][0]["text"])
            summary = data.get("summary", {})
            
            error_count = summary.get("error_count", 0)
            if error_count > 0:
                print(f"✅ Found {error_count} error entries across {summary.get('log_files_found', 0)} files")
                
                # Show top error patterns
                patterns = data.get("patterns", {})
                errors = patterns.get("errors", [])
                if errors:
                    print(f"\n   Top error patterns:")
                    for error in errors[:3]:  # Show top 3
                        print(f"   🔸 {error.get('count', 0)}x: {error.get('pattern', 'unknown')[:60]}...")
            else:
                print("ℹ️  No error logs found")
        else:
            print(f"❌ Error: {result.get('error', 'No error logs found')}")
            
    except Exception as e:
        print(f"❌ Error in error log analysis: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("🎉 Tier 4 Infrastructure Analysis Tools Demo Complete!")
    print("="*70)
    print("\nThe Biting Lip MCP Server now provides comprehensive infrastructure analysis:")
    print("📍 API endpoint discovery across multiple frameworks")
    print("🗃️  Database schema analysis for various database systems") 
    print("📊 Log analysis with pattern detection and error tracking")
    print("\nThese tools provide deep insights into your application infrastructure,")
    print("helping with debugging, optimization, and architecture understanding.")
    print(f"\n🔧 Total tools available: 21 (18 existing + 3 new Tier 4 tools)")


if __name__ == "__main__":
    asyncio.run(demo_tier4_tools())

"""
Database Schema Analysis Tool for Biting Lip MCP Server.

This tool analyzes database schemas, relationships, and patterns across different
database systems including PostgreSQL, MySQL, SQLite, MongoDB, and others.
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class DatabaseSchemaAnalysis:
    """Analyzes database schemas and structures."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
    def analyze_schemas(self, database_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze database schemas across the project.
        
        Args:
            database_type: Specific database type to analyze (sqlite, postgresql, mysql, mongodb)
            
        Returns:
            Dictionary containing schema analysis results
        """
        try:
            analysis = {
                "summary": {
                    "databases_found": 0,
                    "total_tables": 0,
                    "total_columns": 0,
                    "database_types": [],
                    "files_analyzed": 0
                },
                "schemas": {},
                "analysis_metadata": {
                    "project_root": str(self.project_root),
                    "supported_types": [
                        "sqlite", "postgresql", "mysql", "mongodb", "django_orm", "sqlalchemy"
                    ]
                }
            }
            
            # If database type specified, analyze only that type
            if database_type:
                if database_type.lower() == "sqlite":
                    analysis["schemas"]["sqlite"] = self._analyze_sqlite_databases()
                elif database_type.lower() in ["postgresql", "postgres"]:
                    analysis["schemas"]["postgresql"] = self._analyze_postgresql_schemas()
                elif database_type.lower() == "mysql":
                    analysis["schemas"]["mysql"] = self._analyze_mysql_schemas()
                elif database_type.lower() == "mongodb":
                    analysis["schemas"]["mongodb"] = self._analyze_mongodb_schemas()
                elif database_type.lower() == "django_orm":
                    analysis["schemas"]["django_orm"] = self._analyze_django_models()
                elif database_type.lower() == "sqlalchemy":
                    analysis["schemas"]["sqlalchemy"] = self._analyze_sqlalchemy_models()
            else:
                # Analyze all database types
                analysis["schemas"]["sqlite"] = self._analyze_sqlite_databases()
                analysis["schemas"]["postgresql"] = self._analyze_postgresql_schemas()
                analysis["schemas"]["mysql"] = self._analyze_mysql_schemas()
                analysis["schemas"]["mongodb"] = self._analyze_mongodb_schemas()
                analysis["schemas"]["django_orm"] = self._analyze_django_models()
                analysis["schemas"]["sqlalchemy"] = self._analyze_sqlalchemy_models()
            
            # Calculate summary statistics
            self._calculate_summary_stats(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing database schemas: {e}")
            return {"error": str(e)}
    
    def _analyze_sqlite_databases(self) -> Dict[str, Any]:
        """Analyze SQLite database files."""
        sqlite_analysis = {
            "databases": [],
            "total_tables": 0,
            "schema_files": []
        }
        
        # Find SQLite database files
        db_patterns = ["*.db", "*.sqlite", "*.sqlite3"]
        for pattern in db_patterns:
            for db_file in self.project_root.rglob(pattern):
                try:
                    db_info = self._analyze_sqlite_file(db_file)
                    if db_info:
                        sqlite_analysis["databases"].append(db_info)
                        sqlite_analysis["total_tables"] += len(db_info["tables"])
                except Exception as e:
                    logger.warning(f"Error analyzing SQLite file {db_file}: {e}")
        
        # Find SQL schema files
        sql_patterns = ["*.sql"]
        for pattern in sql_patterns:
            for sql_file in self.project_root.rglob(pattern):
                try:
                    schema_info = self._analyze_sql_schema_file(sql_file)
                    if schema_info:
                        sqlite_analysis["schema_files"].append(schema_info)
                except Exception as e:
                    logger.warning(f"Error analyzing SQL file {sql_file}: {e}")
        
        return sqlite_analysis
    
    def _analyze_sqlite_file(self, db_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single SQLite database file."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            db_info = {
                "file_path": str(db_path.relative_to(self.project_root)),
                "file_size": db_path.stat().st_size,
                "tables": []
            }
            
            for (table_name,) in tables:
                if table_name.startswith('sqlite_'):  # Skip system tables
                    continue
                    
                table_info = self._analyze_sqlite_table(cursor, table_name)
                if table_info:
                    db_info["tables"].append(table_info)
            
            conn.close()
            return db_info
            
        except Exception as e:
            logger.warning(f"Error connecting to SQLite database {db_path}: {e}")
            return None
    
    def _analyze_sqlite_table(self, cursor, table_name: str) -> Dict[str, Any]:
        """Analyze a single SQLite table."""
        table_info = {
            "name": table_name,
            "columns": [],
            "indexes": [],
            "foreign_keys": []
        }
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        for col in columns:
            column_info = {
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "default_value": col[4],
                "primary_key": bool(col[5])
            }
            table_info["columns"].append(column_info)
        
        # Get index information
        cursor.execute(f"PRAGMA index_list({table_name});")
        indexes = cursor.fetchall()
        
        for idx in indexes:
            index_info = {
                "name": idx[1],
                "unique": bool(idx[2])
            }
            table_info["indexes"].append(index_info)
        
        # Get foreign key information
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        
        for fk in foreign_keys:
            fk_info = {
                "column": fk[3],
                "references_table": fk[2],
                "references_column": fk[4]
            }
            table_info["foreign_keys"].append(fk_info)
        
        return table_info
    
    def _analyze_sql_schema_file(self, sql_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze SQL schema files for table definitions."""
        try:
            content = sql_path.read_text(encoding='utf-8')
            
            schema_info = {
                "file_path": str(sql_path.relative_to(self.project_root)),
                "tables": [],
                "views": [],
                "indexes": [],
                "constraints": []
            }
            
            # Extract CREATE TABLE statements
            table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"\w]+)\s*\((.*?)\);'
            tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
            
            for table_name, table_def in tables:
                table_name = table_name.strip('`"')
                table_info = self._parse_sql_table_definition(table_name, table_def)
                schema_info["tables"].append(table_info)
            
            # Extract CREATE VIEW statements
            view_pattern = r'CREATE\s+VIEW\s+([`"\w]+)\s+AS\s+(.*?);'
            views = re.findall(view_pattern, content, re.DOTALL | re.IGNORECASE)
            
            for view_name, view_def in views:
                view_name = view_name.strip('`"')
                schema_info["views"].append({
                    "name": view_name,
                    "definition": view_def.strip()
                })
            
            # Extract CREATE INDEX statements
            index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+([`"\w]+)\s+ON\s+([`"\w]+)\s*\((.*?)\);'
            indexes = re.findall(index_pattern, content, re.IGNORECASE)
            
            for index_name, table_name, columns in indexes:
                schema_info["indexes"].append({
                    "name": index_name.strip('`"'),
                    "table": table_name.strip('`"'),
                    "columns": [col.strip() for col in columns.split(',')]
                })
            
            return schema_info
            
        except Exception as e:
            logger.warning(f"Error analyzing SQL schema file {sql_path}: {e}")
            return None
    
    def _parse_sql_table_definition(self, table_name: str, table_def: str) -> Dict[str, Any]:
        """Parse SQL table definition."""
        table_info = {
            "name": table_name,
            "columns": [],
            "constraints": []
        }
        
        # Split table definition into lines
        lines = [line.strip() for line in table_def.split('\n') if line.strip()]
        
        for line in lines:
            line = line.rstrip(',')
            
            # Check if it's a constraint
            if any(constraint in line.upper() for constraint in ['PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK']):
                table_info["constraints"].append(line)
            else:
                # Parse column definition
                column_info = self._parse_sql_column_definition(line)
                if column_info:
                    table_info["columns"].append(column_info)
        
        return table_info
    
    def _parse_sql_column_definition(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single SQL column definition."""
        # Basic column pattern: name type [constraints]
        parts = line.split()
        if len(parts) < 2:
            return None
        
        column_name = parts[0].strip('`"')
        column_type = parts[1]
        
        column_info = {
            "name": column_name,
            "type": column_type,
            "constraints": []
        }
        
        # Look for common constraints
        line_upper = line.upper()
        if 'NOT NULL' in line_upper:
            column_info["constraints"].append("NOT NULL")
        if 'PRIMARY KEY' in line_upper:
            column_info["constraints"].append("PRIMARY KEY")
        if 'UNIQUE' in line_upper:
            column_info["constraints"].append("UNIQUE")
        if 'AUTO_INCREMENT' in line_upper or 'AUTOINCREMENT' in line_upper:
            column_info["constraints"].append("AUTO_INCREMENT")
        
        # Look for DEFAULT values
        default_match = re.search(r'DEFAULT\s+([^,\s]+)', line, re.IGNORECASE)
        if default_match:
            column_info["default"] = default_match.group(1)
        
        return column_info
    
    def _analyze_postgresql_schemas(self) -> Dict[str, Any]:
        """Analyze PostgreSQL schema files and configurations."""
        pg_analysis = {
            "schema_files": [],
            "migrations": [],
            "config_files": []
        }
        
        # Look for PostgreSQL-specific files
        pg_patterns = [
            "*.sql",
            "**/migrations/*.sql",
            "**/migrations/*.py",
            "pg_dump*.sql",
            "schema.sql"
        ]
        
        for pattern in pg_patterns:
            for file_path in self.project_root.rglob(pattern):
                if self._is_postgresql_file(file_path):
                    schema_info = self._analyze_sql_schema_file(file_path)
                    if schema_info:
                        pg_analysis["schema_files"].append(schema_info)
        
        return pg_analysis
    
    def _analyze_mysql_schemas(self) -> Dict[str, Any]:
        """Analyze MySQL schema files and configurations."""
        mysql_analysis = {
            "schema_files": [],
            "config_files": []
        }
        
        # Look for MySQL-specific files
        mysql_patterns = [
            "*.sql",
            "mysqldump*.sql",
            "schema.sql"
        ]
        
        for pattern in mysql_patterns:
            for file_path in self.project_root.rglob(pattern):
                if self._is_mysql_file(file_path):
                    schema_info = self._analyze_sql_schema_file(file_path)
                    if schema_info:
                        mysql_analysis["schema_files"].append(schema_info)
        
        return mysql_analysis
    
    def _analyze_mongodb_schemas(self) -> Dict[str, Any]:
        """Analyze MongoDB schema patterns and collections."""
        mongo_analysis = {
            "collections": [],
            "schema_files": []
        }
        
        # Look for MongoDB schema patterns in JavaScript/JSON files
        mongo_patterns = ["*.js", "*.json", "*.ts"]
        
        for pattern in mongo_patterns:
            for file_path in self.project_root.rglob(pattern):
                mongo_schemas = self._extract_mongodb_schemas(file_path)
                if mongo_schemas:
                    mongo_analysis["schema_files"].append({
                        "file_path": str(file_path.relative_to(self.project_root)),
                        "schemas": mongo_schemas
                    })
        
        return mongo_analysis
    
    def _analyze_django_models(self) -> Dict[str, Any]:
        """Analyze Django ORM models."""
        django_analysis = {
            "models": [],
            "model_files": []
        }
        
        # Look for Django models.py files
        for models_file in self.project_root.rglob("models.py"):
            models_info = self._extract_django_models(models_file)
            if models_info:
                django_analysis["model_files"].append(models_info)
        
        return django_analysis
    
    def _analyze_sqlalchemy_models(self) -> Dict[str, Any]:
        """Analyze SQLAlchemy ORM models."""
        sqlalchemy_analysis = {
            "models": [],
            "model_files": []
        }
        
        # Look for SQLAlchemy model patterns
        for py_file in self.project_root.rglob("*.py"):
            models_info = self._extract_sqlalchemy_models(py_file)
            if models_info:
                sqlalchemy_analysis["model_files"].append(models_info)
        
        return sqlalchemy_analysis
    
    def _is_postgresql_file(self, file_path: Path) -> bool:
        """Check if file contains PostgreSQL-specific syntax."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            pg_indicators = [
                'SERIAL', 'BIGSERIAL', 'UUID', 'JSONB', 'ARRAY',
                'pg_dump', 'CREATE SCHEMA', 'SET search_path'
            ]
            return any(indicator in content.upper() for indicator in pg_indicators)
        except:
            return False
    
    def _is_mysql_file(self, file_path: Path) -> bool:
        """Check if file contains MySQL-specific syntax."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            mysql_indicators = [
                'AUTO_INCREMENT', 'ENGINE=InnoDB', 'ENGINE=MyISAM',
                'CHARSET=utf8', 'mysqldump'
            ]
            return any(indicator in content for indicator in mysql_indicators)
        except:
            return False
    
    def _extract_mongodb_schemas(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract MongoDB schema patterns from files."""
        # Simplified implementation - would need more sophisticated parsing
        return []
    
    def _extract_django_models(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract Django model definitions."""
        # Simplified implementation - would need AST parsing
        return None
    
    def _extract_sqlalchemy_models(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract SQLAlchemy model definitions."""
        # Simplified implementation - would need AST parsing
        return None
    
    def _calculate_summary_stats(self, analysis: Dict[str, Any]) -> None:
        """Calculate summary statistics for the analysis."""
        summary = analysis["summary"]
        
        for db_type, db_data in analysis["schemas"].items():
            if isinstance(db_data, dict):
                if "databases" in db_data:
                    summary["databases_found"] += len(db_data["databases"])
                    for db in db_data["databases"]:
                        if "tables" in db:
                            summary["total_tables"] += len(db["tables"])
                            for table in db["tables"]:
                                if "columns" in table:
                                    summary["total_columns"] += len(table["columns"])
                
                if "schema_files" in db_data:
                    summary["files_analyzed"] += len(db_data["schema_files"])
                    for schema_file in db_data["schema_files"]:
                        if "tables" in schema_file:
                            summary["total_tables"] += len(schema_file["tables"])
                            for table in schema_file["tables"]:
                                if "columns" in table:
                                    summary["total_columns"] += len(table["columns"])
                
                if db_data:  # If there's any data for this database type
                    summary["database_types"].append(db_type)
    
    def analyze_specific_table(self, table_name: str, database_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a specific table across all databases.
        
        Args:
            table_name: Name of the table to analyze
            database_type: Optional database type filter
            
        Returns:
            Dictionary with detailed table analysis
        """
        try:
            schemas = self.analyze_schemas(database_type)
            
            table_analysis = {
                "table_name": table_name,
                "found_in": [],
                "variations": [],
                "relationships": []
            }
            
            # Search for the table across all schemas
            for db_type, db_data in schemas["schemas"].items():
                if isinstance(db_data, dict):
                    self._search_table_in_database(table_name, db_type, db_data, table_analysis)
            
            return table_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return {"error": str(e)}
    
    def _search_table_in_database(self, table_name: str, db_type: str, db_data: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Search for a specific table in database data."""
        # Search in databases
        if "databases" in db_data:
            for db in db_data["databases"]:
                if "tables" in db:
                    for table in db["tables"]:
                        if table["name"].lower() == table_name.lower():
                            analysis["found_in"].append({
                                "database_type": db_type,
                                "database": db.get("file_path", "unknown"),
                                "table_info": table
                            })
        
        # Search in schema files
        if "schema_files" in db_data:
            for schema_file in db_data["schema_files"]:
                if "tables" in schema_file:
                    for table in schema_file["tables"]:
                        if table["name"].lower() == table_name.lower():
                            analysis["found_in"].append({
                                "database_type": db_type,
                                "schema_file": schema_file["file_path"],
                                "table_info": table
                            })

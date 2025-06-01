#!/usr/bin/env python3
"""
Test PostgreSQL connection for memory system with correct credentials.
"""

import psycopg2
import os

def test_connection():
    """Test PostgreSQL connection with correct credentials."""
    try:
        print("🔗 Testing PostgreSQL connection...")
        
        # Use correct credentials
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='ai_memory',
            user='postgres',
            password='postgres'
        )
        
        print("✅ Connected successfully!")
        
        # Test basic queries
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables: {[t[0] for t in tables]}")
          # Check memories table if it exists
        if any('memories' in str(t) for t in tables):
            cursor.execute("SELECT COUNT(*) FROM memories;")
            result = cursor.fetchone()
            count = result[0] if result else 0
            print(f"💾 Memories table has {count} records")
            
            if count > 0:
                cursor.execute("""
                    SELECT id, memory_type, title, created_at 
                    FROM memories 
                    ORDER BY created_at DESC 
                    LIMIT 5;
                """)
                recent_memories = cursor.fetchall()
                print("📝 Recent memories:")
                for mem in recent_memories:
                    print(f"  - {mem[0]}: [{mem[1]}] {mem[2]} ({mem[3]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()

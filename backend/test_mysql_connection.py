#!/usr/bin/env python
"""Test MySQL connection script for debugging."""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.db_connection import parse_database_url, test_connection, ConnectionError
from app.models.database import DatabaseType


async def test_mysql_connection(url: str):
    """Test MySQL connection with detailed error reporting."""
    print("=" * 60)
    print("MySQL Connection Test")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    try:
        # Parse URL
        print("Step 1: Parsing database URL...")
        database_type, normalized_url = parse_database_url(url)
        print(f"✓ Database type: {database_type.value}")
        print(f"✓ Normalized URL: {normalized_url}")
        print()
        
        # Test connection
        print("Step 2: Testing connection...")
        await test_connection(normalized_url, database_type)
        print("✓ Connection successful!")
        print()
        print("=" * 60)
        print("SUCCESS: Database connection is working!")
        print("=" * 60)
        return True
        
    except ConnectionError as e:
        print("✗ Connection failed!")
        print()
        print("Error Details:")
        print(f"  Message: {e.message}")
        print(f"  Error Type: {e.details.get('error_type', 'Unknown')}")
        print()
        
        if "traceback" in e.details:
            print("Full Traceback:")
            for line in e.details["traceback"]:
                print(f"  {line}")
            print()
        
        print("Troubleshooting Tips:")
        print("  1. Check if MySQL server is running")
        print("  2. Verify the connection URL format:")
        print("     mysql://username:password@host:port/database")
        print("  3. Check if the database exists")
        print("  4. Verify username and password are correct")
        print("  5. Check firewall settings")
        print("  6. Ensure MySQL allows connections from this host")
        print()
        print("=" * 60)
        return False
        
    except Exception as e:
        print("✗ Unexpected error occurred!")
        print(f"  Error: {e}")
        import traceback
        print()
        print("Full Traceback:")
        traceback.print_exc()
        print()
        print("=" * 60)
        return False


if __name__ == "__main__":
    # Default test URL (can be overridden via command line)
    test_url = "mysql://root:root@localhost:3306/ccsp_quiz"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    print()
    success = asyncio.run(test_mysql_connection(test_url))
    sys.exit(0 if success else 1)


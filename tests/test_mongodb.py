#!/usr/bin/env python3
"""
MongoDB Connection Test Script

This script tests the connection to MongoDB and provides information about
the MongoDB server and available databases. It performs basic connectivity
tests and displays results in a user-friendly format.

Usage:
    python test_mongodb.py [--uri MONGODB_URI] [--timeout TIMEOUT_MS]
"""

import sys
import os
import argparse
import logging
import time
from pymongo import MongoClient
import pymongo.errors

# Add project root to path for imports if running directly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to use the project's standardized logging
try:
    from lib.logging_config import configure_logger
    logger = configure_logger("mongodb_test")
except ImportError:
    # Fallback logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("mongodb_test")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test connection to MongoDB server")
    parser.add_argument('--uri', help='MongoDB connection URI', 
                      default='mongodb://localhost:27017/')
    parser.add_argument('--timeout', help='Connection timeout in milliseconds', 
                      type=int, default=2000)
    parser.add_argument('--verbose', '-v', action='store_true', 
                      help='Enable verbose output')
    return parser.parse_args()

def test_server_status(client):
    """
    Test server status and get version information.
    
    Args:
        client (MongoClient): MongoDB client connection
        
    Returns:
        dict: Server status information
    """
    try:
        server_info = client.server_info()
        logger.info(f"MongoDB version: {server_info['version']}")
        
        # Check build environment if available
        if 'buildEnvironment' in server_info:
            build_env = server_info['buildEnvironment']
            if 'target_os' in build_env:
                logger.info(f"Server OS: {build_env['target_os']}")
                
        return server_info
    except Exception as e:
        logger.error(f"Failed to get server status: {e}")
        return None

def test_admin_commands(client):
    """
    Test basic admin commands.
    
    Args:
        client (MongoClient): MongoDB client connection
        
    Returns:
        bool: True if commands executed successfully
    """
    try:
        # Get server status
        status = client.admin.command('serverStatus')
        
        # Log some important metrics
        if status:
            logger.info(f"Connections: current={status.get('connections', {}).get('current', 'N/A')}, "
                       f"available={status.get('connections', {}).get('available', 'N/A')}")
            logger.info(f"Uptime: {status.get('uptime', 'N/A')} seconds")
        
        return True
    except Exception as e:
        logger.error(f"Failed to execute admin commands: {e}")
        return False

def get_database_info(client):
    """
    Get information about all databases.
    
    Args:
        client (MongoClient): MongoDB client connection
        
    Returns:
        dict: Database information including names and collection counts
    """
    try:
        # List available databases
        databases = client.list_database_names()
        logger.info(f"Found {len(databases)} databases")
        
        db_info = {}
        for db_name in databases:
            db = client[db_name]
            collections = db.list_collection_names()
            
            # Get document counts
            collection_info = {}
            for coll in collections:
                try:
                    count = db[coll].count_documents({})
                    collection_info[coll] = count
                except Exception as e:
                    collection_info[coll] = f"Error: {str(e)}"
            
            db_info[db_name] = {
                'collections': collections,
                'collection_count': len(collections),
                'collection_info': collection_info
            }
            
        return db_info
    except Exception as e:
        logger.error(f"Failed to get database information: {e}")
        return {}

def test_write_read(client, db_name="mongodb_test"):
    """
    Test basic write and read operations.
    
    Args:
        client (MongoClient): MongoDB client connection
        db_name (str): Database name to use for testing
        
    Returns:
        bool: True if operations were successful
    """
    try:
        # Use a test database
        db = client[db_name]
        
        # Create a test collection with a unique name
        test_collection_name = f"mongodb_test_{int(time.time())}"
        collection = db[test_collection_name]
        
        # Insert a test document
        test_doc = {"test_id": "connection_test", "timestamp": time.time()}
        insert_result = collection.insert_one(test_doc)
        
        # Read the document back
        retrieved_doc = collection.find_one({"test_id": "connection_test"})
        
        # Verify document was retrieved
        if not retrieved_doc:
            logger.error("Failed to retrieve test document")
            return False
            
        # Clean up by removing the test collection
        collection.drop()
        
        logger.info("Write/read test successful")
        return True
    except Exception as e:
        logger.error(f"Write/read test failed: {e}")
        return False

def test_mongodb_connection(uri, timeout_ms):
    """
    Test connection to MongoDB server and display server information.
    
    Args:
        uri (str): MongoDB connection URI
        timeout_ms (int): Connection timeout in milliseconds
        
    Returns:
        bool: True if connection was successful, False otherwise
    """
    logger.info(f"Testing connection to MongoDB at {uri} (timeout: {timeout_ms}ms)")
    
    try:
        # Create client with timeout
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        
        # Test connection with ismaster command (requires no auth)
        client.admin.command('ismaster')
        
        # Connection successful
        logger.info("MongoDB connection successful!")
        
        # Get server information
        server_info = test_server_status(client)
        
        # Test admin commands
        admin_status = test_admin_commands(client)
        
        # Get database information
        db_info = get_database_info(client)
        
        # Display database information
        for db_name, info in db_info.items():
            logger.info(f"\nDatabase: {db_name} ({info['collection_count']} collections)")
            
            # Show collections for each database (up to 5)
            collections = info['collections']
            for i, coll in enumerate(collections[:5], 1):
                doc_count = info['collection_info'].get(coll, "unknown")
                logger.info(f"  {i}. {coll} ({doc_count} documents)")
                
            if len(collections) > 5:
                logger.info(f"  ... and {len(collections) - 5} more collections")
        
        # Test write and read operations
        write_read_success = test_write_read(client)
        
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError as err:
        logger.error("Could not connect to MongoDB server")
        logger.error("Make sure MongoDB is installed and running on your system")
        logger.error(f"Error details: {err}")
        logger.info("Tip: Run the MongoDB launcher with: python bin/mongodb_launcher.py")
        return False
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False
        
    finally:
        # Close the connection
        if 'client' in locals():
            client.close()
            logger.debug("MongoDB connection closed")

def main():
    """Main function to run the MongoDB connection test."""
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    success = test_mongodb_connection(args.uri, args.timeout)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
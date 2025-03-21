#!/usr/bin/env python3
"""
MongoDB Connection Test Script

This script tests the connection to MongoDB and provides information about
the MongoDB server and available databases.

Usage:
    python test_mongodb.py [--uri MONGODB_URI] [--timeout TIMEOUT_MS]
"""

import sys
import argparse
import logging
from pymongo import MongoClient
import pymongo.errors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
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
    return parser.parse_args()

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
        
        # Connection successful, show server info
        server_info = client.server_info()
        logger.info("MongoDB connection successful! 🎉")
        logger.info(f"MongoDB server version: {server_info['version']}")
        
        # Show build info
        if 'buildEnvironment' in server_info:
            build_env = server_info['buildEnvironment']
            if 'target_os' in build_env:
                logger.info(f"Server OS: {build_env['target_os']}")
        
        # List available databases
        databases = client.list_database_names()
        logger.info(f"\nAvailable databases ({len(databases)}):")
        for i, db in enumerate(databases, 1):
            # Get collection count for each database
            db_obj = client[db]
            collection_count = len(db_obj.list_collection_names())
            logger.info(f"  {i}. {db} ({collection_count} collections)")
            
            # Show collections for each database (up to 5)
            collections = db_obj.list_collection_names()
            if collections:
                for j, coll in enumerate(collections[:5], 1):
                    doc_count = db_obj[coll].count_documents({})
                    logger.info(f"     {j}. {coll} ({doc_count} documents)")
                if len(collections) > 5:
                    logger.info(f"     ... and {len(collections) - 5} more collections")
                    
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError as err:
        logger.error("Error: Could not connect to MongoDB server.")
        logger.error("Make sure MongoDB is installed and running on your system.")
        logger.error(f"Error details: {err}")
        logger.info("\nTip: Run the MongoDB launcher with: python bin/mongodb_launcher.py")
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
    success = test_mongodb_connection(args.uri, args.timeout)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
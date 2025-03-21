#!/usr/bin/env python3
"""
Test Utilities Module

This module provides utility functions for test isolation and setup.
It helps ensure that tests run in isolated environments with proper database 
names and cleanup procedures.
"""

import os
import uuid
import pymongo
import functools
import logging
from contextlib import contextmanager
import importlib

# Configure logging
logger = logging.getLogger(__name__)

@contextmanager
def test_database(db_name=None):
    """
    Context manager to create an isolated test database environment.
    
    Args:
        db_name (str, optional): Name for the test database. If not provided,
                                a unique name will be generated.
    
    Yields:
        tuple: A tuple containing (database_name, connection_string)
    """
    # Use provided name or generate a unique one
    database_name = db_name or f"test_db_{uuid.uuid4().hex[:8]}"
    connection_string = "mongodb://localhost:27017/"
    
    # Import here to avoid circular imports
    from mongo_tools import db_connect
    
    # Store original function
    original_get_db = db_connect.get_db
    
    try:
        # Create a test-specific function to override the default
        @functools.wraps(db_connect.get_db)
        def test_get_db(db_name=None, connection_string="mongodb://localhost:27017/", timeout=5000):
            """Override get_db to always use the test database"""
            return original_get_db(database_name, connection_string, timeout)
        
        # Override the function
        db_connect.get_db = test_get_db
        
        # Create client and initialize test database
        client = pymongo.MongoClient(connection_string)
        try:
            # Clear any existing data
            if database_name in client.list_database_names():
                client.drop_database(database_name)
            
            # Create an empty database
            db = client[database_name]
            if "nodes" not in db.list_collection_names():
                db.create_collection("nodes")
                
            logger.info(f"Created test database: {database_name}")
        finally:
            client.close()
        
        # Force reload any modules that might have imported get_db
        # This ensures they get the new version
        modules_to_reload = [
            'mongo_tools.nodes',
            'mongo_tools.edges',
            'mongo_tools.notes',
            'mongo_tools.utility'
        ]
        
        for module_name in modules_to_reload:
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
            except ImportError:
                pass
            
        # Yield the test environment variables
        yield (database_name, connection_string)
        
    finally:
        # Restore original function
        db_connect.get_db = original_get_db
        
        # Clean up the test database
        client = pymongo.MongoClient(connection_string)
        try:
            client.drop_database(database_name)
            logger.info(f"Dropped test database: {database_name}")
        except Exception as e:
            logger.error(f"Error dropping test database: {e}")
        finally:
            client.close()

def create_test_backup_dir():
    """
    Create a temporary directory for test backups.
    
    Returns:
        str: Path to the created directory
    """
    # Create a unique backup directory name
    backup_dir = f"test_backups_{uuid.uuid4().hex[:8]}"
    
    # Create the directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.debug(f"Created test backup directory: {backup_dir}")
    
    return backup_dir

def cleanup_test_backup_dir(backup_dir):
    """
    Remove a test backup directory and its contents.
    
    Args:
        backup_dir (str): Path to the backup directory
    """
    if os.path.exists(backup_dir):
        # Remove all files
        for file in os.listdir(backup_dir):
            try:
                os.remove(os.path.join(backup_dir, file))
            except Exception as e:
                logger.warning(f"Could not remove {file}: {e}")
        
        # Remove directory
        try:
            os.rmdir(backup_dir)
            logger.debug(f"Removed test backup directory: {backup_dir}")
        except Exception as e:
            logger.warning(f"Could not remove backup directory: {e}")

@contextmanager
def isolated_test_case(db_name=None):
    """
    Convenience wrapper that sets up an isolated test environment with a
    database and backup directory.
    
    Args:
        db_name (str, optional): Name for the test database
        
    Yields:
        tuple: A tuple containing (database_name, backup_dir)
    """
    backup_dir = create_test_backup_dir()
    
    try:
        with test_database(db_name) as (db_name, conn_string):
            yield (db_name, backup_dir)
    finally:
        cleanup_test_backup_dir(backup_dir) 
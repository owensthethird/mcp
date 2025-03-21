#!/usr/bin/env python3
"""
MongoDB Connection Module

This module provides utilities for connecting to MongoDB and managing database connections.
It includes a wrapper class to ensure connections are properly closed when they're no longer needed.
"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure module logger
logger = logging.getLogger(__name__)

class DBConnection:
    """
    A wrapper class to handle MongoDB connections.
    
    This class wraps a MongoDB database connection and its client to ensure proper
    resource management and connection cleanup.
    
    Attributes:
        client (MongoClient): The MongoDB client connection
        db (Database): The MongoDB database instance
    """
    def __init__(self, client, db):
        """
        Initialize a new database connection wrapper.
        
        Args:
            client (MongoClient): MongoDB client connection
            db (Database): MongoDB database instance
        """
        self.client = client
        self.db = db
    
    def __getitem__(self, name):
        """
        Access a collection by name using dictionary-style access.
        
        Args:
            name (str): The name of the collection
            
        Returns:
            Collection: The MongoDB collection
        """
        return self.db[name]
    
    def __getattr__(self, name):
        """
        Access database attributes and methods via dot notation.
        
        Args:
            name (str): The name of the attribute or method
            
        Returns:
            Any: The requested attribute or method from the database
        """
        return getattr(self.db, name)
    
    def close(self):
        """Close the MongoDB client connection to release resources."""
        if self.client:
            try:
                self.client.close()
                logger.debug("MongoDB connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")

def get_db(db_name='test_db', connection_string='mongodb://localhost:27017/', timeout=5000):
    """
    Connect to MongoDB and return a wrapped database object.
    
    This function establishes a connection to MongoDB and returns a wrapped
    database object that includes the client for proper connection management.
    
    Args:
        db_name (str): Name of the database to connect to
        connection_string (str): MongoDB connection URI
        timeout (int): Connection timeout in milliseconds
        
    Returns:
        DBConnection: A wrapped database connection
        
    Raises:
        ConnectionFailure: If unable to connect to the database
    """
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=timeout)
        
        # Test the connection
        client.admin.command('ismaster')
        
        db = client[db_name]
        logger.debug(f"Connected to MongoDB database: {db_name}")
        return DBConnection(client, db)
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise ConnectionFailure(f"Could not connect to MongoDB: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise 
#!/usr/bin/env python3
"""
MongoDB Node Operations Module

This module provides functions for managing node documents in MongoDB.
It includes operations for creating, reading, updating, and deleting nodes.
"""

import logging
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from mongo_tools.db_connect import get_db

# Configure module logger
logger = logging.getLogger(__name__)

def add_node(node_data):
    """
    Add a new node to the database.
    
    Args:
        node_data (dict): Document representing the node to insert
        
    Returns:
        ObjectId: The ID of the inserted node
        
    Raises:
        PyMongoError: If the database operation fails
    """
    if not isinstance(node_data, dict):
        raise TypeError("node_data must be a dictionary")
        
    # Ensure required fields are present
    if "name" not in node_data:
        raise ValueError("Node data must contain a 'name' field")
    
    db = get_db()
    try:
        # Ensure connections array exists
        if "connections" not in node_data:
            node_data["connections"] = []
            
        # Ensure next_interaction_notes array exists
        if "next_interaction_notes" not in node_data:
            node_data["next_interaction_notes"] = []
            
        result = db.nodes.insert_one(node_data)
        node_id = result.inserted_id
        logger.info(f"Node '{node_data.get('name')}' inserted with ID: {node_id}")
        return node_id
    except PyMongoError as e:
        logger.error(f"Failed to add node: {e}")
        raise
    finally:
        db.close()

def get_node_by_name(name):
    """
    Get a node by its name.
    
    Args:
        name (str): Name of the node to retrieve
        
    Returns:
        dict or None: The node document or None if not found
        
    Raises:
        PyMongoError: If the database operation fails
    """
    db = get_db()
    try:
        node = db.nodes.find_one({"name": name})
        if node:
            logger.debug(f"Retrieved node: {name}")
        else:
            logger.debug(f"Node not found: {name}")
        return node
    except PyMongoError as e:
        logger.error(f"Error retrieving node '{name}': {e}")
        raise
    finally:
        db.close()

def get_node_by_id(node_id):
    """
    Get a node by its ID.
    
    Args:
        node_id (str or ObjectId): ID of the node to retrieve
        
    Returns:
        dict or None: The node document or None if not found
        
    Raises:
        PyMongoError: If the database operation fails
    """
    if isinstance(node_id, str):
        node_id = ObjectId(node_id)
        
    db = get_db()
    try:
        node = db.nodes.find_one({"_id": node_id})
        if node:
            logger.debug(f"Retrieved node by ID: {node_id}")
        else:
            logger.debug(f"Node not found with ID: {node_id}")
        return node
    except PyMongoError as e:
        logger.error(f"Error retrieving node with ID '{node_id}': {e}")
        raise
    finally:
        db.close()

def update_node(node_id, updates):
    """
    Update a node with the specified updates.
    
    Args:
        node_id (ObjectId or str): ID of the node to update
        updates (dict): Dictionary of updates to apply
        
    Returns:
        int: Number of documents modified
        
    Raises:
        PyMongoError: If the database operation fails
    """
    if isinstance(node_id, str):
        node_id = ObjectId(node_id)
    
    if not isinstance(updates, dict):
        raise TypeError("updates must be a dictionary")
        
    db = get_db()
    try:
        result = db.nodes.update_one({"_id": node_id}, {"$set": updates})
        modified_count = result.modified_count
        logger.info(f"Updated {modified_count} node(s) with ID: {node_id}")
        return modified_count
    except PyMongoError as e:
        logger.error(f"Failed to update node {node_id}: {e}")
        raise
    finally:
        db.close()

def delete_node_by_name(name):
    """
    Delete a node by its name.
    
    Args:
        name (str): Name of the node to delete
        
    Returns:
        int: Number of documents deleted
        
    Raises:
        PyMongoError: If the database operation fails
    """
    db = get_db()
    try:
        result = db.nodes.delete_one({"name": name})
        deleted_count = result.deleted_count
        logger.info(f"Deleted {deleted_count} node(s) with name: {name}")
        return deleted_count
    except PyMongoError as e:
        logger.error(f"Failed to delete node '{name}': {e}")
        raise
    finally:
        db.close()

def list_all_nodes(limit=None, sort_field=None, sort_direction=1):
    """
    List all nodes in the database.
    
    Args:
        limit (int, optional): Maximum number of nodes to return
        sort_field (str, optional): Field to sort by
        sort_direction (int, optional): Sort direction (1 for ascending, -1 for descending)
        
    Returns:
        list: List of node documents
        
    Raises:
        PyMongoError: If the database operation fails
    """
    db = get_db()
    try:
        query = db.nodes.find()
        
        if sort_field:
            query = query.sort(sort_field, sort_direction)
            
        if limit:
            query = query.limit(limit)
            
        nodes = list(query)
        logger.debug(f"Retrieved {len(nodes)} nodes from database")
        return nodes
    except PyMongoError as e:
        logger.error(f"Failed to list nodes: {e}")
        raise
    finally:
        db.close() 
#!/usr/bin/env python3
"""
MongoDB Node Operations Module

This module provides functions for managing node documents in MongoDB.
It includes operations for creating, reading, updating, and deleting nodes.
"""

import logging
import csv
import json
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

def import_nodes_from_json(file_path, update_existing=False):
    """
    Import multiple nodes from a JSON file.
    
    The JSON file should contain either:
    - A list of node objects
    - A single object with 'nodes' key containing a list of node objects
    
    Args:
        file_path (str): Path to the JSON file
        update_existing (bool): If True, update existing nodes instead of skipping
        
    Returns:
        dict: Summary of the import operation with counts of added, updated, and skipped nodes
        
    Raises:
        ValueError: If the JSON file format is invalid
        PyMongoError: If the database operation fails
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Handle different JSON formats
        if isinstance(data, list):
            nodes = data
        elif isinstance(data, dict) and 'nodes' in data:
            nodes = data['nodes']
        else:
            raise ValueError("Invalid JSON format: expected a list of nodes or an object with a 'nodes' key")
            
        if not nodes:
            logger.warning("No nodes found in the JSON file")
            return {"added": 0, "updated": 0, "skipped": 0, "failed": 0}
            
        return _import_nodes(nodes, update_existing)
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Failed to read JSON file: {e}")
        raise ValueError(f"Failed to read JSON file: {e}")

def import_nodes_from_csv(file_path, update_existing=False):
    """
    Import multiple nodes from a CSV file.
    
    The CSV file must have a header row with at least a 'name' column.
    Other columns will be added as properties of the node.
    
    Args:
        file_path (str): Path to the CSV file
        update_existing (bool): If True, update existing nodes instead of skipping
        
    Returns:
        dict: Summary of the import operation with counts of added, updated, and skipped nodes
        
    Raises:
        ValueError: If the CSV file format is invalid
        PyMongoError: If the database operation fails
    """
    try:
        nodes = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            if 'name' not in reader.fieldnames:
                raise ValueError("CSV file must have a 'name' column")
                
            for row in reader:
                # Handle type conversion for certain fields that should be numeric
                for key, value in row.items():
                    # Try to convert numeric strings to numbers
                    if value.isdigit():
                        row[key] = int(value)
                    elif value and all(c in '0123456789.' for c in value) and value.count('.') == 1:
                        try:
                            row[key] = float(value)
                        except ValueError:
                            pass  # Keep as string if conversion fails
                            
                # Create node with properties
                node = {"name": row.pop('name'), "type": row.pop('type', 'generic')}
                
                # Add remaining columns as properties
                if row:
                    node["properties"] = row
                    
                nodes.append(node)
                
        if not nodes:
            logger.warning("No nodes found in the CSV file")
            return {"added": 0, "updated": 0, "skipped": 0, "failed": 0}
            
        return _import_nodes(nodes, update_existing)
        
    except FileNotFoundError as e:
        logger.error(f"Failed to read CSV file: {e}")
        raise ValueError(f"Failed to read CSV file: {e}")

def _import_nodes(nodes, update_existing=False):
    """
    Internal helper function to import multiple nodes.
    
    Args:
        nodes (list): List of node dictionaries
        update_existing (bool): If True, update existing nodes instead of skipping
        
    Returns:
        dict: Summary of the import operation
    """
    db = get_db()
    
    summary = {
        "added": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0
    }
    
    try:
        for node in nodes:
            try:
                # Check if required field is present
                if "name" not in node:
                    logger.warning(f"Skipping node without a name: {node}")
                    summary["failed"] += 1
                    continue
                    
                # Check if node already exists
                existing = db.nodes.find_one({"name": node["name"]})
                
                if existing:
                    if update_existing:
                        # Update existing node (preserving _id and connections)
                        node_id = existing["_id"]
                        # Preserve connections and notes if not in the import data
                        if "connections" not in node:
                            node["connections"] = existing.get("connections", [])
                        if "next_interaction_notes" not in node:
                            node["next_interaction_notes"] = existing.get("next_interaction_notes", [])
                            
                        result = db.nodes.replace_one({"_id": node_id}, node)
                        if result.modified_count > 0:
                            summary["updated"] += 1
                            logger.info(f"Updated existing node: {node['name']}")
                        else:
                            summary["skipped"] += 1
                    else:
                        # Skip existing node
                        summary["skipped"] += 1
                        logger.info(f"Skipped existing node: {node['name']}")
                else:
                    # Add new node
                    # Ensure arrays exist
                    if "connections" not in node:
                        node["connections"] = []
                    if "next_interaction_notes" not in node:
                        node["next_interaction_notes"] = []
                        
                    result = db.nodes.insert_one(node)
                    summary["added"] += 1
                    logger.info(f"Added new node: {node['name']} with ID: {result.inserted_id}")
            
            except Exception as e:
                logger.error(f"Failed to import node {node.get('name', '(unknown)')}: {e}")
                summary["failed"] += 1
                
        return summary
    finally:
        db.close()

def export_nodes_to_json(file_path, query=None, include_ids=False):
    """
    Export nodes to a JSON file.
    
    Args:
        file_path (str): Path to save the JSON file
        query (dict, optional): Query to filter nodes to export
        include_ids (bool): Whether to include MongoDB ObjectIds in the export
        
    Returns:
        int: Number of nodes exported
        
    Raises:
        PyMongoError: If the database operation fails
        IOError: If the file cannot be written
    """
    if query is None:
        query = {}
        
    db = get_db()
    try:
        # Get nodes matching the query
        nodes = list(db.nodes.find(query))
        
        if not nodes:
            logger.warning("No nodes found to export")
            return 0
            
        # Process nodes for export
        export_data = []
        for node in nodes:
            if not include_ids:
                # Remove MongoDB ObjectIds which aren't JSON serializable
                node.pop('_id', None)
                
                # Process connections to remove ObjectIds
                if 'connections' in node:
                    for conn in node['connections']:
                        if 'to_node' in conn and isinstance(conn['to_node'], ObjectId):
                            # Convert ObjectId to string or remove based on preference
                            conn['to_node'] = str(conn['to_node'])
            else:
                # Convert ObjectIds to strings for JSON serialization
                if '_id' in node:
                    node['_id'] = str(node['_id'])
                
                # Process connections
                if 'connections' in node:
                    for conn in node['connections']:
                        if 'to_node' in conn and isinstance(conn['to_node'], ObjectId):
                            conn['to_node'] = str(conn['to_node'])
                            
            export_data.append(node)
            
        # Write to JSON file
        with open(file_path, 'w') as f:
            json.dump({"nodes": export_data}, f, indent=2)
            
        logger.info(f"Exported {len(nodes)} nodes to {file_path}")
        return len(nodes)
        
    except Exception as e:
        logger.error(f"Failed to export nodes to JSON: {e}")
        raise
    finally:
        db.close()

def export_nodes_to_csv(file_path, query=None, fields=None):
    """
    Export nodes to a CSV file.
    
    Only basic node properties can be exported to CSV.
    Complex fields like connections will be omitted.
    
    Args:
        file_path (str): Path to save the CSV file
        query (dict, optional): Query to filter nodes to export
        fields (list, optional): List of fields to include in the export
        
    Returns:
        int: Number of nodes exported
        
    Raises:
        PyMongoError: If the database operation fails
        IOError: If the file cannot be written
    """
    if query is None:
        query = {}
        
    db = get_db()
    try:
        # Get nodes matching the query
        nodes = list(db.nodes.find(query))
        
        if not nodes:
            logger.warning("No nodes found to export")
            return 0
            
        # Collect fields if not specified
        if not fields:
            # Start with basic fields that all nodes should have
            fields = ['name', 'type']
            
            # Collect all property fields
            property_fields = set()
            for node in nodes:
                props = node.get('properties', {})
                if isinstance(props, dict):
                    property_fields.update(props.keys())
            
            # Add flattened property fields
            for field in sorted(property_fields):
                fields.append(f"properties.{field}")
        
        # Open CSV file for writing
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header row
            writer.writerow(fields)
            
            # Write data rows
            for node in nodes:
                row = []
                for field in fields:
                    if '.' in field:
                        # Handle nested fields (e.g., properties.health)
                        parts = field.split('.')
                        value = node
                        for part in parts:
                            if isinstance(value, dict) and part in value:
                                value = value[part]
                            else:
                                value = ""
                                break
                    else:
                        # Handle top-level fields
                        value = node.get(field, "")
                        
                    row.append(value)
                    
                writer.writerow(row)
                
        logger.info(f"Exported {len(nodes)} nodes to {file_path}")
        return len(nodes)
        
    except Exception as e:
        logger.error(f"Failed to export nodes to CSV: {e}")
        raise
    finally:
        db.close() 
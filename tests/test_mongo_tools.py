#!/usr/bin/env python3
"""
MongoDB Toolset Test Suite

This module contains comprehensive tests for the mongo_tools package functionality.
It verifies database connections, node operations, edge management, interaction notes,
and utility functions.

Usage:
    python -m tests.test_mongo_tools
"""

import unittest
import os
import sys
import time
import logging
import json
import pymongo
from bson.objectid import ObjectId

# Add project root to path for imports if running directly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import our MongoDB toolset modules
from mongo_tools.db_connect import get_db, DBConnection
from mongo_tools.nodes import add_node, get_node_by_name, get_node_by_id, update_node, delete_node_by_name, list_all_nodes
from mongo_tools.edges import add_edge, get_connections, remove_edge
from mongo_tools.notes import add_interaction_note, process_and_clear_notes
from mongo_tools.utility import clear_collection, create_database_snapshot, restore_database_snapshot, get_database_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("mongo_tools_tests")

class TestMongoTools(unittest.TestCase):
    """Test suite for MongoDB tools package"""
    
    TEST_DB_NAME = "test_mongo_tools_db"
    BACKUP_DIR = "test_backups"
    
    @classmethod
    def setUpClass(cls):
        """Initialize test environment before any tests run"""
        logger.info("Initializing MongoDB Toolset Tests")
        
        # Check MongoDB connection before starting tests
        try:
            client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
            client.admin.command('ismaster')
            logger.info("MongoDB is running and accessible")
            client.close()
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            logger.error("Please ensure MongoDB is running using mongodb_launcher.py")
            raise
        
        # Create backup directory if needed
        if not os.path.exists(cls.BACKUP_DIR):
            os.makedirs(cls.BACKUP_DIR)
            logger.debug(f"Created test backup directory: {cls.BACKUP_DIR}")
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a fresh database connection
        self.db = get_db(self.TEST_DB_NAME)
        # Clear collections before each test to start clean
        self.db.nodes.delete_many({})
        logger.debug("Cleared test collections for clean test environment")
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'db') and isinstance(self.db, DBConnection):
            self.db.close()
            logger.debug("Closed test database connection")
    
    def test_1_db_connection(self):
        """Test database connection wrapper functionality"""
        # Test connection is working
        self.assertIsInstance(self.db, DBConnection)
        self.assertIsNotNone(self.db.client)
        
        # Test dictionary-style access
        test_coll = self.db['test_collection']
        self.assertEqual(test_coll.name, 'test_collection')
        
        # Test attribute access
        self.assertEqual(self.db.name, self.TEST_DB_NAME)
        
        logger.info("Database connection functionality verified")
    
    def test_2_add_and_get_node(self):
        """Test adding and retrieving a node"""
        test_node = {
            "name": "test_character",
            "type": "character",
            "properties": {
                "description": "Test character for unit tests",
                "health": 100,
                "level": 1
            }
        }
        
        # Add the node
        node_id = add_node(test_node)
        self.assertIsNotNone(node_id)
        
        # Retrieve by name
        node = get_node_by_name("test_character")
        self.assertIsNotNone(node)
        self.assertEqual(node["name"], "test_character")
        self.assertEqual(node["properties"]["description"], "Test character for unit tests")
        self.assertEqual(node["properties"]["health"], 100)
        
        # Retrieve by ID
        node_by_id = get_node_by_id(node_id)
        self.assertIsNotNone(node_by_id)
        self.assertEqual(node_by_id["_id"], node_id)
        
        logger.info("Node creation and retrieval functionality verified")
    
    def test_3_update_node(self):
        """Test updating a node"""
        # Add a node first
        test_node = {
            "name": "update_test",
            "type": "item",
            "properties": {
                "value": 10
            }
        }
        
        node_id = add_node(test_node)
        
        # Update the node
        updates = {
            "properties.value": 20,
            "properties.rarity": "common"
        }
        
        modified_count = update_node(node_id, updates)
        self.assertEqual(modified_count, 1)
        
        # Verify the update
        node = get_node_by_name("update_test")
        self.assertEqual(node["properties"]["value"], 20)
        self.assertEqual(node["properties"]["rarity"], "common")
        
        logger.info("Node update functionality verified")
    
    def test_4_delete_node(self):
        """Test deleting a node"""
        # Add a node first
        test_node = {
            "name": "to_be_deleted",
            "type": "location"
        }
        
        add_node(test_node)
        
        # Verify it exists
        node = get_node_by_name("to_be_deleted")
        self.assertIsNotNone(node)
        
        # Delete the node
        deleted_count = delete_node_by_name("to_be_deleted")
        self.assertEqual(deleted_count, 1)
        
        # Verify it's gone
        node = get_node_by_name("to_be_deleted")
        self.assertIsNone(node)
        
        # Test deleting non-existent node
        deleted_count = delete_node_by_name("non_existent_node")
        self.assertEqual(deleted_count, 0)
        
        logger.info("Node deletion functionality verified")
    
    def test_5_list_all_nodes(self):
        """Test listing nodes with various options"""
        # Add multiple nodes
        node_names = ["node_a", "node_b", "node_c"]
        
        for idx, name in enumerate(node_names):
            add_node({
                "name": name,
                "type": "test",
                "priority": idx + 1
            })
            
        # Test basic listing
        nodes = list_all_nodes()
        self.assertEqual(len(nodes), 3)
        
        # Test with limit
        limited_nodes = list_all_nodes(limit=2)
        self.assertEqual(len(limited_nodes), 2)
        
        # Test with sorting (ascending)
        sorted_nodes_asc = list_all_nodes(sort_field="name", sort_direction=1)
        self.assertEqual(sorted_nodes_asc[0]["name"], "node_a")
        
        # Test with sorting (descending)
        sorted_nodes_desc = list_all_nodes(sort_field="name", sort_direction=-1)
        self.assertEqual(sorted_nodes_desc[0]["name"], "node_c")
        
        logger.info("Node listing functionality verified")
    
    def test_6_add_and_get_edges(self):
        """Test adding and retrieving connections between nodes"""
        # Add three nodes
        node1 = {"name": "source_node", "type": "location"}
        node2 = {"name": "target_node_1", "type": "location"}
        node3 = {"name": "target_node_2", "type": "location"}
        
        source_id = add_node(node1)
        target_id1 = add_node(node2)
        target_id2 = add_node(node3)
        
        # Add multiple connections
        edge_data1 = {"type": "path", "distance": 5}
        edge_data2 = {"type": "road", "distance": 10, "difficulty": "hard"}
        
        added1 = add_edge(source_id, target_id1, edge_data1)
        added2 = add_edge(source_id, target_id2, edge_data2)
        
        self.assertTrue(added1)
        self.assertTrue(added2)
        
        # Get connections
        connections = get_connections(source_id)
        
        # Verify connections exist
        self.assertEqual(len(connections), 2)
        
        # Test connection properties
        conn_types = [conn["type"] for conn in connections]
        self.assertIn("path", conn_types)
        self.assertIn("road", conn_types)
        
        # Test removing an edge
        removed = remove_edge(source_id, target_id1)
        self.assertTrue(removed)
        
        # Verify connection was removed
        connections = get_connections(source_id)
        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]["type"], "road")
        
        logger.info("Edge management functionality verified")
    
    def test_7_interaction_notes(self):
        """Test adding and processing interaction notes"""
        # Add a node
        node = {"name": "npc_with_notes", "type": "character"}
        node_id = add_node(node)
        
        # Add interaction notes
        note1 = {
            "trigger": "conversation", 
            "effect": "Reveals secret location",
            "clear_after_use": True
        }
        
        note2 = {
            "trigger": "revisit",
            "effect": "Gives quest item",
            "clear_after_use": False
        }
        
        added1 = add_interaction_note(node_id, note1)
        added2 = add_interaction_note(node_id, note2)
        
        self.assertTrue(added1)
        self.assertTrue(added2)
        
        # Verify notes were added
        node = get_node_by_name("npc_with_notes")
        self.assertEqual(len(node["next_interaction_notes"]), 2)
        
        # Process notes
        processed = process_and_clear_notes(node_id)
        self.assertTrue(processed)
        
        # Verify only persistent note remains
        node = get_node_by_name("npc_with_notes")
        self.assertEqual(len(node["next_interaction_notes"]), 1)
        self.assertEqual(node["next_interaction_notes"][0]["trigger"], "revisit")
        
        logger.info("Interaction notes functionality verified")
    
    def test_8_database_snapshots(self):
        """Test database snapshot creation and restoration"""
        # Add some test nodes
        for i in range(3):
            add_node({"name": f"snapshot_test_{i}", "type": "item"})
        
        # Create snapshot
        snapshot_file = create_database_snapshot(self.BACKUP_DIR)
        self.assertTrue(os.path.exists(snapshot_file))
        
        # Clear database
        clear_collection('nodes')
        nodes = list_all_nodes()
        self.assertEqual(len(nodes), 0)
        
        # Restore snapshot
        restored = restore_database_snapshot(snapshot_file)
        self.assertTrue(restored)
        
        # Check if data was restored
        nodes = list_all_nodes()
        self.assertEqual(len(nodes), 3)
        
        # Check snapshot file content
        with open(snapshot_file, 'r') as f:
            data = json.load(f)
            self.assertIn('nodes', data)
            self.assertEqual(len(data['nodes']), 3)
        
        logger.info("Database snapshot functionality verified")
    
    def test_9_database_stats(self):
        """Test getting database statistics"""
        # Add some test nodes
        for i in range(3):
            add_node({"name": f"stats_test_{i}", "type": "item"})
        
        # Get stats
        stats = get_database_stats()
        
        # Verify stats object structure
        self.assertIsInstance(stats, dict)
        self.assertIn("collections", stats)
        self.assertIn("counts", stats)
        
        # Verify collections
        self.assertIn('nodes', stats["collections"])
        
        # Verify count
        self.assertEqual(stats["counts"]["nodes"], 3)
        
        logger.info("Database statistics functionality verified")
    
    def test_10_error_handling(self):
        """Test error handling for various error conditions"""
        # Test adding node with invalid data type
        with self.assertRaises(TypeError):
            add_node("not a dictionary")
        
        # Test adding node without required field
        with self.assertRaises(ValueError):
            add_node({"type": "missing_name"})
        
        # Test update with invalid node ID format
        with self.assertRaises(Exception):
            update_node("invalid_id", {"field": "value"})
        
        logger.info("Error handling functionality verified")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests"""
        # Clean up test database
        db = get_db(cls.TEST_DB_NAME)
        try:
            db.nodes.delete_many({})
            logger.debug("Cleaned up test database")
        finally:
            db.close()
        
        # Remove test backup files
        if os.path.exists(cls.BACKUP_DIR):
            for file in os.listdir(cls.BACKUP_DIR):
                try:
                    os.remove(os.path.join(cls.BACKUP_DIR, file))
                except Exception as e:
                    logger.warning(f"Could not remove backup file {file}: {e}")
                    
            try:
                os.rmdir(cls.BACKUP_DIR)
                logger.debug("Removed test backup directory")
            except Exception as e:
                logger.warning(f"Could not remove backup directory: {e}")
        
        logger.info("Test cleanup completed successfully")

if __name__ == "__main__":
    logger.info("Starting MongoDB Toolset Tests")
    unittest.main() 
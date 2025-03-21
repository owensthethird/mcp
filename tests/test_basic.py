#!/usr/bin/env python3
"""
Basic MongoDB Connection and Functionality Test

This script verifies that MongoDB is running and tests basic node operations.
Run this script to quickly verify that the MongoDB server is operational and
the mongo_tools package is working correctly.

Usage:
    python -m tests.test_basic
"""

import unittest
import sys
import os
import logging
import uuid
import json
import pymongo
from bson.objectid import ObjectId

# Add project root to path for imports if running directly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import MongoDB toolset modules
from mongo_tools.db_connect import get_db
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
logger = logging.getLogger("test_basic")

class TestBasicFunctionality(unittest.TestCase):
    """Basic test suite for MongoDB toolset"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize test environment"""
        # Generate a unique test database name for isolation
        cls.test_db_name = f"basic_test_{uuid.uuid4().hex[:8]}"
        logger.info(f"Using test database: {cls.test_db_name}")
        
        # Create a backup directory for testing
        cls.backup_dir = "test_backups"
        if not os.path.exists(cls.backup_dir):
            os.makedirs(cls.backup_dir)
        
        # Check if MongoDB is running
        try:
            client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
            client.admin.command('ismaster')
            logger.info("MongoDB is running and accessible")
            client.close()
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            logger.error("Please ensure MongoDB is running using mongodb_launcher.py")
            raise
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a fresh database connection
        self.db = get_db(self.test_db_name)
        
        # Clear any existing data
        self.db.nodes.delete_many({})
    
    def tearDown(self):
        """Clean up after each test"""
        # Close the database connection
        if hasattr(self, 'db'):
            self.db.close()
    
    def test_01_add_and_retrieve_node(self):
        """Test basic node creation and retrieval"""
        # Create a test node
        test_node = {
            "name": "test_basic_node",
            "type": "test",
            "properties": {
                "description": "A test node for basic functionality verification"
            }
        }
        
        # Add the node
        node_id = add_node(test_node)
        self.assertIsNotNone(node_id)
        logger.info(f"Created node with ID: {node_id}")
        
        # Retrieve the node by name
        node = get_node_by_name("test_basic_node")
        self.assertIsNotNone(node)
        self.assertEqual(node["name"], "test_basic_node")
        self.assertEqual(node["type"], "test")
        logger.info("Successfully retrieved node by name")
        
        # Retrieve the node by ID
        node_by_id = get_node_by_id(node_id)
        self.assertIsNotNone(node_by_id)
        self.assertEqual(node_by_id["_id"], node_id)
        logger.info("Successfully retrieved node by ID")
        
        # Delete the node
        deleted = delete_node_by_name("test_basic_node")
        self.assertEqual(deleted, 1)
        logger.info("Successfully deleted node")
        
        # Verify it's gone
        node = get_node_by_name("test_basic_node")
        self.assertIsNone(node)
    
    def test_02_update_node(self):
        """Test updating a node's properties"""
        # Create a test node
        test_node = {
            "name": "update_test_node",
            "type": "character",
            "properties": {
                "health": 100,
                "level": 1
            }
        }
        
        # Add the node
        node_id = add_node(test_node)
        
        # Update the node
        updates = {
            "properties.health": 80,
            "properties.level": 2,
            "properties.status": "injured"
        }
        
        modified = update_node(node_id, updates)
        self.assertEqual(modified, 1)
        
        # Verify the updates
        node = get_node_by_name("update_test_node")
        self.assertEqual(node["properties"]["health"], 80)
        self.assertEqual(node["properties"]["level"], 2)
        self.assertEqual(node["properties"]["status"], "injured")
        
        logger.info("Successfully updated node properties")
    
    def test_03_list_nodes(self):
        """Test listing nodes with sorting and limiting"""
        # Add multiple test nodes
        nodes = [
            {"name": "list_test_1", "type": "item", "priority": 3},
            {"name": "list_test_2", "type": "item", "priority": 1},
            {"name": "list_test_3", "type": "item", "priority": 2}
        ]
        
        for node in nodes:
            add_node(node)
        
        # Test listing all nodes
        all_nodes = list_all_nodes()
        self.assertEqual(len(all_nodes), 3)
        
        # Test limiting results
        limited = list_all_nodes(limit=2)
        self.assertEqual(len(limited), 2)
        
        # Test sorting by priority (ascending)
        sorted_asc = list_all_nodes(sort_field="priority", sort_direction=1)
        self.assertEqual(sorted_asc[0]["priority"], 1)
        self.assertEqual(sorted_asc[0]["name"], "list_test_2")
        
        # Test sorting by priority (descending)
        sorted_desc = list_all_nodes(sort_field="priority", sort_direction=-1)
        self.assertEqual(sorted_desc[0]["priority"], 3)
        self.assertEqual(sorted_desc[0]["name"], "list_test_1")
        
        logger.info("Successfully tested node listing with sorting and limiting")
    
    def test_04_edge_operations(self):
        """Test adding and removing connections between nodes"""
        # Create source and target nodes
        source = {"name": "source_node", "type": "location"}
        target = {"name": "target_node", "type": "location"}
        
        source_id = add_node(source)
        target_id = add_node(target)
        
        # Add an edge with data
        edge_data = {"type": "path", "distance": 5, "difficulty": "medium"}
        added = add_edge(source_id, target_id, edge_data)
        self.assertTrue(added)
        
        # Get connections from source
        connections = get_connections(source_id)
        self.assertEqual(len(connections), 1)
        
        # Verify connection data
        conn = connections[0]
        self.assertEqual(conn.get("type"), "path")
        self.assertEqual(conn.get("distance"), 5)
        self.assertEqual(conn.get("difficulty"), "medium")
        
        # Remove the edge
        removed = remove_edge(source_id, target_id)
        self.assertTrue(removed)
        
        # Verify connection is gone
        connections = get_connections(source_id)
        self.assertEqual(len(connections), 0)
        
        logger.info("Successfully tested edge operations")
    
    def test_05_interaction_notes(self):
        """Test adding and processing interaction notes"""
        # Create a character node
        character = {"name": "npc_character", "type": "character"}
        char_id = add_node(character)
        
        # Add two interaction notes
        note1 = {
            "trigger": "first_meeting",
            "effect": "Gives quest information",
            "clear_after_use": True
        }
        
        note2 = {
            "trigger": "repeated_visit",
            "effect": "Provides hint",
            "clear_after_use": False
        }
        
        added1 = add_interaction_note(char_id, note1)
        added2 = add_interaction_note(char_id, note2)
        
        self.assertTrue(added1)
        self.assertTrue(added2)
        
        # Check notes were added
        character = get_node_by_name("npc_character")
        self.assertEqual(len(character["next_interaction_notes"]), 2)
        
        # Process notes (should clear the one-time note)
        processed = process_and_clear_notes(char_id)
        self.assertTrue(processed)
        
        # Verify one-time note was cleared
        character = get_node_by_name("npc_character")
        self.assertEqual(len(character["next_interaction_notes"]), 1)
        self.assertEqual(character["next_interaction_notes"][0]["trigger"], "repeated_visit")
        
        logger.info("Successfully tested interaction notes")
    
    def test_06_database_snapshot(self):
        """Test creating and restoring database snapshots"""
        # Add some test data
        for i in range(3):
            add_node({
                "name": f"snapshot_test_{i}",
                "type": "test",
                "value": i * 10
            })
        
        # Create a snapshot
        snapshot_file = create_database_snapshot(self.backup_dir)
        self.assertTrue(os.path.exists(snapshot_file))
        
        # Clear the database
        clear_collection("nodes", self.test_db_name)
        
        # Verify data is gone
        nodes = list_all_nodes()
        self.assertEqual(len(nodes), 0)
        
        # Restore from snapshot
        restored = restore_database_snapshot(snapshot_file)
        self.assertTrue(restored)
        
        # Verify data was restored
        nodes = list_all_nodes()
        self.assertEqual(len(nodes), 3)
        
        # Check content of a restored node
        node = get_node_by_name("snapshot_test_1")
        self.assertEqual(node["value"], 10)
        
        logger.info("Successfully tested database snapshot functionality")
    
    def test_07_database_stats(self):
        """Test retrieving database statistics"""
        # Clear database first
        clear_collection("nodes", self.test_db_name)
        
        # Add test nodes
        for i in range(5):
            add_node({
                "name": f"stats_test_{i}",
                "type": "test" if i % 2 == 0 else "item"
            })
        
        # Get database stats
        stats = get_database_stats()
        
        # Check stats structure
        self.assertIn("collections", stats)
        self.assertIn("counts", stats)
        
        # Check node count
        self.assertEqual(stats["counts"]["nodes"], 5)
        
        logger.info("Successfully tested database statistics")
    
    def test_08_error_handling(self):
        """Test error handling in various operations"""
        # Test adding a node with invalid data type
        with self.assertRaises(TypeError):
            add_node("not a dictionary")
        
        # Test adding a node without a name
        with self.assertRaises(ValueError):
            add_node({"type": "missing_name"})
        
        # Test invalid ObjectId format
        with self.assertRaises(Exception):
            get_node_by_id("not-an-object-id")
        
        logger.info("Successfully tested error handling")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Drop the test database
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        try:
            client.drop_database(cls.test_db_name)
            logger.info(f"Dropped test database: {cls.test_db_name}")
        except Exception as e:
            logger.error(f"Error dropping test database: {e}")
        finally:
            client.close()
        
        # Remove test backup files
        if os.path.exists(cls.backup_dir):
            for file in os.listdir(cls.backup_dir):
                if file.startswith("mongodb_snapshot_") and file.endswith(".json"):
                    try:
                        os.remove(os.path.join(cls.backup_dir, file))
                    except Exception as e:
                        logger.warning(f"Could not remove {file}: {e}")
            
            try:
                os.rmdir(cls.backup_dir)
            except Exception as e:
                logger.warning(f"Could not remove backup directory: {e}")

if __name__ == "__main__":
    logger.info("Starting basic MongoDB functionality tests")
    unittest.main() 
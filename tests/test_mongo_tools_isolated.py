#!/usr/bin/env python3
"""
MongoDB Tools Test Suite (Isolated Version)

This module contains tests for the MongoDB toolset, each running in an isolated
database environment to ensure proper test independence.
"""

import unittest
import sys
import os
import logging
import uuid
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path to import mongo_tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test utilities
from tests.test_utils import isolated_test_case
from mongo_tools import nodes, edges, notes, utility

# Import MongoDB toolset modules
from mongo_tools.nodes import add_node, get_node_by_name, get_node_by_id, update_node, delete_node_by_name, list_all_nodes
from mongo_tools.edges import add_edge, get_connections, remove_edge
from mongo_tools.notes import add_interaction_note, process_and_clear_notes
from mongo_tools.utility import create_snapshot, restore_snapshot, get_database_stats


class TestMongoDB(unittest.TestCase):
    """Test MongoDB connection and operations in isolated environments."""
    
    def test_connection(self):
        """Test connection to the MongoDB database."""
        with isolated_test_case("test_connection") as (db_name, _):
            # Generate a random test node name to avoid conflicts
            node_name = f"test_connection_{uuid.uuid4().hex[:8]}"
            
            # Try creating a test node
            node_data = {
                "name": node_name,
                "type": "TestConnection",
                "properties": {"test": True}
            }
            
            node_id = add_node(node_data)
            self.assertIsNotNone(node_id, "Node ID should not be None")
            
            # Retrieve the node
            node = get_node_by_name(node_name)
            self.assertIsNotNone(node, "Node should exist")
            self.assertEqual(node["name"], node_name)
            self.assertEqual(node["type"], "TestConnection")
            
            # Clean up the test node
            deleted = delete_node_by_name(node_name)
            self.assertEqual(deleted, 1, "Node should be deleted")


class TestNodeOperations(unittest.TestCase):
    """Test MongoDB node operations with proper isolation."""
    
    def test_add_and_get_node(self):
        """Test adding and retrieving nodes."""
        with isolated_test_case() as (db_name, _):
            # Generate unique test node names
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            
            # Test adding nodes
            node1_data = {
                "name": f"{test_prefix}node1",
                "type": "Location",
                "properties": {"description": "A test location"}
            }
            
            node2_data = {
                "name": f"{test_prefix}node2",
                "type": "Character",
                "properties": {"level": 5, "class": "Wizard"}
            }
            
            # Add nodes
            node1_id = add_node(node1_data)
            node2_id = add_node(node2_data)
            
            self.assertIsNotNone(node1_id, "Node 1 ID should not be None")
            self.assertIsNotNone(node2_id, "Node 2 ID should not be None")
            
            # Retrieve nodes by name
            node1 = get_node_by_name(f"{test_prefix}node1")
            node2 = get_node_by_name(f"{test_prefix}node2")
            
            self.assertIsNotNone(node1, "Node 1 should exist")
            self.assertIsNotNone(node2, "Node 2 should exist")
            
            self.assertEqual(node1["type"], "Location")
            self.assertEqual(node2["properties"]["level"], 5)
            
            # Retrieve nodes by ID
            node1_by_id = get_node_by_id(node1_id)
            node2_by_id = get_node_by_id(node2_id)
            
            self.assertIsNotNone(node1_by_id, "Node 1 should be retrievable by ID")
            self.assertIsNotNone(node2_by_id, "Node 2 should be retrievable by ID")
            
            self.assertEqual(node1_by_id["name"], f"{test_prefix}node1")
            self.assertEqual(node2_by_id["name"], f"{test_prefix}node2")
    
    def test_update_node(self):
        """Test updating node properties."""
        with isolated_test_case() as (db_name, _):
            # Create a test node
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            node_data = {
                "name": f"{test_prefix}update_test",
                "type": "Character",
                "properties": {"health": 100, "mana": 50}
            }
            
            node_id = add_node(node_data)
            self.assertIsNotNone(node_id, "Node ID should not be None")
            
            # Verify node was created correctly
            node = get_node_by_id(node_id)
            self.assertEqual(node["properties"]["health"], 100)
            self.assertEqual(node["properties"]["mana"], 50)
            
            # Update properties
            updated = update_node(node_id, {
                "properties.health": 80,
                "properties.mana": 60,
                "properties.experience": 200
            })
            
            self.assertTrue(updated > 0, "Update should modify at least one document")
            
            # Verify updates
            updated_node = get_node_by_id(node_id)
            self.assertEqual(updated_node["properties"]["health"], 80)
            self.assertEqual(updated_node["properties"]["mana"], 60)
            self.assertEqual(updated_node["properties"]["experience"], 200)
    
    def test_delete_node(self):
        """Test deleting nodes."""
        with isolated_test_case() as (db_name, _):
            # Create test nodes
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            
            # Node to be deleted
            delete_node_data = {
                "name": f"{test_prefix}to_be_deleted",
                "type": "TestNode"
            }
            
            node_id = add_node(delete_node_data)
            self.assertIsNotNone(node_id, "Node ID should not be None")
            
            # Verify node exists
            node = get_node_by_name(f"{test_prefix}to_be_deleted")
            self.assertIsNotNone(node, "Node should exist before deletion")
            
            # Delete the node
            deleted_count = delete_node_by_name(f"{test_prefix}to_be_deleted")
            self.assertEqual(deleted_count, 1, "One node should be deleted")
            
            # Verify node is gone
            node_after = get_node_by_name(f"{test_prefix}to_be_deleted")
            self.assertIsNone(node_after, "Node should not exist after deletion")
            
            # Test deleting non-existent node
            deleted_count = delete_node_by_name("non_existent_node")
            self.assertEqual(deleted_count, 0, "No nodes should be deleted for non-existent name")
    
    def test_list_all_nodes(self):
        """Test listing all nodes."""
        with isolated_test_case() as (db_name, _):
            # Verify database is empty
            initial_nodes = list_all_nodes()
            initial_count = len(initial_nodes)
            self.assertEqual(initial_count, 0, "Database should be empty initially")
            
            # Create test nodes
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            test_nodes = [
                {"name": f"{test_prefix}node1", "type": "TestType1"},
                {"name": f"{test_prefix}node2", "type": "TestType2"},
                {"name": f"{test_prefix}node3", "type": "TestType3"}
            ]
            
            for node_data in test_nodes:
                node_id = add_node(node_data)
                self.assertIsNotNone(node_id, "Node ID should not be None")
            
            # List all nodes
            all_nodes = list_all_nodes()
            self.assertEqual(len(all_nodes), 3, "Should have exactly 3 nodes")
            
            # List with limit
            limited_nodes = list_all_nodes(limit=2)
            self.assertEqual(len(limited_nodes), 2, "Should have exactly 2 nodes with limit")
            
            # List with sorting
            sorted_nodes = list_all_nodes(sort_field="name", sort_direction=1)
            self.assertEqual(len(sorted_nodes), 3, "Should have all 3 nodes when sorted")
            
            # Verify sorting
            self.assertEqual(sorted_nodes[0]["name"], f"{test_prefix}node1")
            self.assertEqual(sorted_nodes[1]["name"], f"{test_prefix}node2")
            self.assertEqual(sorted_nodes[2]["name"], f"{test_prefix}node3")


class TestEdgeOperations(unittest.TestCase):
    """Test MongoDB edge operations with proper isolation."""
    
    def test_edge_operations(self):
        """Test adding, retrieving, and removing edges."""
        with isolated_test_case() as (db_name, _):
            # Create test nodes
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            source_data = {
                "name": f"{test_prefix}source",
                "type": "Location"
            }
            
            target1_data = {
                "name": f"{test_prefix}target1",
                "type": "Character"
            }
            
            target2_data = {
                "name": f"{test_prefix}target2",
                "type": "Item"
            }
            
            # Add nodes
            source_id = add_node(source_data)
            target1_id = add_node(target1_data)
            target2_id = add_node(target2_data)
            
            # Add edges
            edge1_props = {"type": "contains", "visible": True}
            edge2_props = {"type": "has_item", "count": 3}
            
            added1 = add_edge(source_id, target1_id, edge1_props)
            added2 = add_edge(source_id, target2_id, edge2_props)
            
            self.assertTrue(added1, "Edge 1 should be added successfully")
            self.assertTrue(added2, "Edge 2 should be added successfully")
            
            # Get connections
            connections = get_connections(source_id)
            self.assertEqual(len(connections), 2, "Source should have 2 connections")
            
            # Verify edge properties
            edge1 = next(conn for conn in connections if conn["to_node"] == target1_id)
            edge2 = next(conn for conn in connections if conn["to_node"] == target2_id)
            
            self.assertEqual(edge1["type"], "contains")
            self.assertTrue(edge1["visible"])
            
            self.assertEqual(edge2["type"], "has_item")
            self.assertEqual(edge2["count"], 3)
            
            # Remove edge
            removed = remove_edge(source_id, target1_id)
            self.assertTrue(removed, "Edge should be removed successfully")
            
            # Check remaining connections
            remaining = get_connections(source_id)
            self.assertEqual(len(remaining), 1, "Source should have 1 connection remaining")
            self.assertEqual(remaining[0]["to_node"], target2_id)


class TestInteractionNotes(unittest.TestCase):
    """Test interaction notes functionality with proper isolation."""
    
    def test_interaction_notes(self):
        """Test adding and processing interaction notes."""
        with isolated_test_case() as (db_name, _):
            # Create test node
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            node_data = {
                "name": f"{test_prefix}character",
                "type": "Character",
                "properties": {"level": 5}
            }
            
            node_id = add_node(node_data)
            self.assertIsNotNone(node_id, "Node ID should not be None")
            
            # Add interaction notes
            notes = [
                "Completed quest A",
                "Found hidden treasure",
                "Defeated enemy boss"
            ]
            
            for note in notes:
                added = add_interaction_note(node_id, note)
                self.assertTrue(added, f"Note '{note}' should be added successfully")
            
            # Check notes were added
            node = get_node_by_id(node_id)
            self.assertEqual(len(node["next_interaction_notes"]), 3, "Node should have 3 notes")
            
            # Process and clear notes
            processed = process_and_clear_notes(node_id)
            self.assertTrue(processed, "Notes should be processed successfully")
            
            # Check notes were moved and cleared
            updated_node = get_node_by_id(node_id)
            self.assertEqual(len(updated_node["next_interaction_notes"]), 0, "Node should have 0 notes after processing")


class TestDatabaseOperations(unittest.TestCase):
    """Test database-wide operations with proper isolation."""
    
    def test_database_snapshot(self):
        """Test creating and restoring database snapshots."""
        with isolated_test_case() as (db_name, backup_dir):
            # Add test data
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            for i in range(3):
                node_data = {
                    "name": f"{test_prefix}node{i}",
                    "type": "TestSnapshot",
                    "properties": {"index": i}
                }
                add_node(node_data)
            
            # Verify data was added
            nodes_before = list_all_nodes()
            self.assertEqual(len(nodes_before), 3, "Should have 3 nodes before snapshot")
            
            # Create snapshot
            snapshot_file = create_snapshot(backup_dir)
            self.assertTrue(os.path.exists(snapshot_file), "Snapshot file should exist")
            
            # Clean database
            for node in nodes_before:
                delete_node_by_name(node["name"])
            
            # Verify database is empty
            empty_check = list_all_nodes()
            self.assertEqual(len(empty_check), 0, "Database should be empty after clearing")
            
            # Restore from snapshot
            restored = restore_snapshot(snapshot_file)
            self.assertTrue(restored, "Snapshot should be restored successfully")
            
            # Verify data was restored
            nodes_after = list_all_nodes()
            self.assertEqual(len(nodes_after), 3, "Should have 3 nodes after restore")
            
            # Verify node data
            for i in range(3):
                node = get_node_by_name(f"{test_prefix}node{i}")
                self.assertIsNotNone(node, f"Node {i} should exist after restore")
                self.assertEqual(node["properties"]["index"], i, f"Node {i} should have correct index")
    
    def test_database_stats(self):
        """Test database statistics functions."""
        with isolated_test_case() as (db_name, _):
            # Add test data
            test_prefix = f"test_{uuid.uuid4().hex[:6]}_"
            node_types = ["Character", "Location", "Item"]
            
            for i, node_type in enumerate(node_types):
                node_data = {
                    "name": f"{test_prefix}{node_type.lower()}",
                    "type": node_type
                }
                add_node(node_data)
            
            # Get database stats
            stats = get_database_stats()
            
            # Verify collections are present
            self.assertIn("nodes", stats["collections"], "Nodes collection should exist")
            
            # Verify node count
            self.assertEqual(stats["counts"]["nodes"], 3, "Should have 3 nodes in the database")


if __name__ == "__main__":
    unittest.main() 
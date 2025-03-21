#!/usr/bin/env python3
"""
Isolated MongoDB Tests

This module contains test cases that run in isolated database environments.
Each test uses its own database to prevent interference between tests.
"""

import unittest
import sys
import os
import logging
import shutil
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
from mongo_tools import nodes, edges, utility


class IsolatedNodeTests(unittest.TestCase):
    """Test node operations in an isolated environment."""
    
    def test_node_operations(self):
        """Test adding, retrieving, and updating nodes in isolation."""
        with isolated_test_case() as (db_name, _):
            logger.info(f"Running node operations test in database: {db_name}")
            
            # Verify database is empty
            all_nodes = nodes.list_all_nodes()
            self.assertEqual(len(all_nodes), 0, "Database should be empty at start")
            
            # Add test nodes
            test_nodes = [
                {"name": "Test Node 1", "type": "Person", "properties": {"age": 30}},
                {"name": "Test Node 2", "type": "Organization", "properties": {"employees": 100}},
                {"name": "Test Node 3", "type": "Location", "properties": {"city": "TestCity"}}
            ]
            
            node_ids = []
            for node_data in test_nodes:
                node_id = nodes.add_node(node_data)
                self.assertIsNotNone(node_id, "Node ID should not be None")
                node_ids.append(node_id)
                
            # List nodes and verify count
            all_nodes = nodes.list_all_nodes()
            self.assertEqual(len(all_nodes), 3, f"Expected 3 nodes, got {len(all_nodes)}")
            
            # Get a specific node
            node = nodes.get_node_by_id(node_ids[0])
            self.assertEqual(node["name"], "Test Node 1", "Node name should match")
            
            # Update a node
            updated = nodes.update_node(node_ids[0], {"properties.age": 31, "name": "Updated Test Node"})
            self.assertTrue(updated > 0, "Update should modify at least one document")
            
            # Verify the update
            updated_node = nodes.get_node_by_id(node_ids[0])
            self.assertEqual(updated_node["name"], "Updated Test Node", "Node name should be updated")
            self.assertEqual(updated_node["properties"]["age"], 31, "Node age should be updated")
            
            logger.info("Node operations test completed successfully")


class IsolatedEdgeTests(unittest.TestCase):
    """Test edge operations in an isolated environment."""
    
    def test_edge_operations(self):
        """Test adding and removing edges between nodes in isolation."""
        with isolated_test_case() as (db_name, _):
            logger.info(f"Running edge operations test in database: {db_name}")
            
            # Create source and target nodes
            source_data = {"name": "Source Node", "type": "Person", "properties": {"role": "source"}}
            target_data = {"name": "Target Node", "type": "Person", "properties": {"role": "target"}}
            
            source_id = nodes.add_node(source_data)
            target_id = nodes.add_node(target_data)
            
            self.assertIsNotNone(source_id, "Source node ID should not be None")
            self.assertIsNotNone(target_id, "Target node ID should not be None")
            
            # Add an edge
            edge_properties = {"relation": "knows", "since": 2020}
            edge_added = edges.add_edge(source_id, target_id, edge_properties)
            self.assertTrue(edge_added, "Edge should be added successfully")
            
            # Check connections
            connections = edges.get_connections(source_id)
            self.assertEqual(len(connections), 1, "Source should have one connection")
            self.assertEqual(connections[0]["to_node"], target_id, "Connection target should match")
            
            # Remove the edge
            edge_removed = edges.remove_edge(source_id, target_id)
            self.assertTrue(edge_removed, "Edge should be removed successfully")
            
            # Verify edge is gone
            connections = edges.get_connections(source_id)
            self.assertEqual(len(connections), 0, "Source should have no connections after removal")
            
            logger.info("Edge operations test completed successfully")


class IsolatedSnapshotTests(unittest.TestCase):
    """Test snapshot operations in an isolated environment."""
    
    def test_snapshot_operations(self):
        """Test creating and restoring database snapshots in isolation."""
        with isolated_test_case() as (db_name, backup_dir):
            logger.info(f"Running snapshot operations test in database: {db_name}")
            
            # Add test data
            for i in range(3):
                node_data = {
                    "name": f"Test Node {i}",
                    "type": "TestType",
                    "properties": {"test_property": i}
                }
                node_id = nodes.add_node(node_data)
                self.assertIsNotNone(node_id, f"Node {i} should be created successfully")
            
            # Verify data
            all_nodes = nodes.list_all_nodes()
            initial_count = len(all_nodes)
            self.assertEqual(initial_count, 3, f"Expected 3 nodes, got {initial_count}")
            
            # Create a snapshot
            snapshot_file = utility.create_snapshot(backup_dir)
            self.assertTrue(os.path.exists(snapshot_file), "Snapshot file should exist")
            
            # Clear the database
            for node in all_nodes:
                delete_count = nodes.delete_node_by_name(node["name"])
                self.assertEqual(delete_count, 1, f"Should delete exactly one node named {node['name']}")
                
            # Verify database is empty
            empty_nodes = nodes.list_all_nodes()
            self.assertEqual(len(empty_nodes), 0, "Database should be empty after clearing")
            
            # Restore from snapshot
            restored = utility.restore_snapshot(snapshot_file)
            self.assertTrue(restored, "Restore should return True")
            
            # Verify data is restored
            restored_nodes = nodes.list_all_nodes()
            self.assertEqual(len(restored_nodes), initial_count, 
                             f"Expected {initial_count} nodes after restore, got {len(restored_nodes)}")
            
            logger.info("Snapshot operations test completed successfully")


if __name__ == "__main__":
    unittest.main() 
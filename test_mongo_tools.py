import unittest
import os
import time
import pymongo
from bson.objectid import ObjectId

# Import our MongoDB toolset modules
from mongo_tools.db_connect import get_db
from mongo_tools.nodes import add_node, get_node_by_name, update_node, delete_node_by_name, list_all_nodes
from mongo_tools.edges import add_edge, get_connections, remove_edge
from mongo_tools.notes import add_interaction_note, process_and_clear_notes
from mongo_tools.utility import clear_collection, create_database_snapshot, restore_database_snapshot, get_database_stats

class TestMongoTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Check MongoDB connection before starting tests
        print("\n🧪 Running MongoDB Toolset Tests")
        print("\n🔍 Checking MongoDB connection...")
        try:
            client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
            client.admin.command('ismaster')
            print("✅ MongoDB is running and accessible")
            client.close()
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            print("Please ensure MongoDB is running using mongodb_launcher.py")
            raise
        
        # Create backup directory if needed
        if not os.path.exists('test_backups'):
            os.makedirs('test_backups')
    
    def setUp(self):
        # Clear nodes collection before each test to start clean
        clear_collection('nodes')
    
    def test_1_add_and_get_node(self):
        """Test adding and retrieving a node"""
        test_node = {
            "name": "test_character",
            "type": "character",
            "properties": {
                "description": "Test character for unit tests"
            },
            "next_interaction_notes": [],
            "connections": []
        }
        
        # Add the node
        node_id = add_node(test_node)
        self.assertIsNotNone(node_id)
        
        # Retrieve the node
        node = get_node_by_name("test_character")
        self.assertIsNotNone(node)
        self.assertEqual(node["name"], "test_character")
        self.assertEqual(node["properties"]["description"], "Test character for unit tests")
        print("✅ Test 1: Successfully added and retrieved node")
    
    def test_2_update_node(self):
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
        
        update_node(node_id, updates)
        
        # Verify the update
        node = get_node_by_name("update_test")
        self.assertEqual(node["properties"]["value"], 20)
        self.assertEqual(node["properties"]["rarity"], "common")
        print("✅ Test 2: Successfully updated node properties")
    
    def test_3_delete_node(self):
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
        delete_node_by_name("to_be_deleted")
        
        # Verify it's gone
        node = get_node_by_name("to_be_deleted")
        self.assertIsNone(node)
        print("✅ Test 3: Successfully deleted node")
    
    def test_4_add_and_get_edges(self):
        """Test adding and retrieving connections between nodes"""
        # Add two nodes
        node1 = {"name": "source_node", "type": "location"}
        node2 = {"name": "target_node", "type": "location"}
        
        source_id = add_node(node1)
        target_id = add_node(node2)
        
        # Add a connection
        edge_data = {"type": "path", "distance": 5}
        added = add_edge(source_id, target_id, edge_data)
        
        self.assertTrue(added)
        
        # Get connections
        connections = get_connections(source_id)
        
        # Verify connection exists
        self.assertEqual(len(connections), 1)
        self.assertEqual(connections[0]["type"], "path")
        self.assertEqual(connections[0]["distance"], 5)
        print("✅ Test 4: Successfully added and retrieved edge")
    
    def test_5_interaction_notes(self):
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
        
        add_interaction_note(node_id, note1)
        add_interaction_note(node_id, note2)
        
        # Verify notes were added
        node = get_node_by_name("npc_with_notes")
        self.assertEqual(len(node["next_interaction_notes"]), 2)
        
        # Process notes
        process_and_clear_notes(node_id)
        
        # Verify only persistent note remains
        node = get_node_by_name("npc_with_notes")
        self.assertEqual(len(node["next_interaction_notes"]), 1)
        self.assertEqual(node["next_interaction_notes"][0]["trigger"], "revisit")
        print("✅ Test 5: Successfully managed interaction notes")
    
    def test_6_database_stats(self):
        """Test getting database statistics"""
        # Add some test nodes
        for i in range(3):
            add_node({"name": f"stats_test_{i}", "type": "item"})
        
        # Get stats
        stats = get_database_stats()
        
        # Verify stats
        self.assertIn('nodes', stats["collections"])
        self.assertEqual(stats["counts"]["nodes"], 3)
        print("✅ Test 6: Successfully retrieved database statistics")
    
    @classmethod
    def tearDownClass(cls):
        # Clean up data after all tests
        db = get_db()
        db.nodes.delete_many({})
        # Close the client connection to avoid ResourceWarning
        db.client.close()
        
        # Remove test backup files if any
        if os.path.exists('test_backups'):
            for file in os.listdir('test_backups'):
                try:
                    os.remove(os.path.join('test_backups', file))
                except:
                    pass
            try:
                os.rmdir('test_backups')
            except:
                pass
        
        print("\n🧹 Test cleanup completed")

if __name__ == "__main__":
    print("🧪 Running MongoDB Toolset Tests")
    unittest.main() 
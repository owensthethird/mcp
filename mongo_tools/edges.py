from mongo_tools.db_connect import get_db
from bson.objectid import ObjectId

def add_edge(from_node_id, to_node_id, edge_data=None):
    """Add a connection/edge between two nodes"""
    if edge_data is None:
        edge_data = {}
        
    # Ensure we have ObjectIds
    if isinstance(from_node_id, str):
        from_node_id = ObjectId(from_node_id)
    if isinstance(to_node_id, str):
        to_node_id = ObjectId(to_node_id)
    
    db = get_db()
    try:
        edge_info = {
            "to_node": to_node_id,
            **edge_data
        }
        
        result = db.nodes.update_one(
            {"_id": from_node_id},
            {"$push": {"connections": edge_info}}
        )
        
        print(f"✅ Added edge from {from_node_id} to {to_node_id}")
        return result.modified_count > 0
    finally:
        db.client.close()

def get_connections(node_id):
    """Get all connections from a node"""
    if isinstance(node_id, str):
        node_id = ObjectId(node_id)
        
    db = get_db()
    try:
        node = db.nodes.find_one({"_id": node_id})
        
        if node and "connections" in node:
            return node["connections"]
        return []
    finally:
        db.client.close()

def remove_edge(from_node_id, to_node_id):
    """Remove a connection between nodes"""
    if isinstance(from_node_id, str):
        from_node_id = ObjectId(from_node_id)
    if isinstance(to_node_id, str):
        to_node_id = ObjectId(to_node_id)
    
    db = get_db()
    try:
        result = db.nodes.update_one(
            {"_id": from_node_id},
            {"$pull": {"connections": {"to_node": to_node_id}}}
        )
        
        print(f"🗑️ Removed edge from {from_node_id} to {to_node_id}")
        return result.modified_count > 0 
    finally:
        db.client.close() 
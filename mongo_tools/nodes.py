from mongo_tools.db_connect import get_db

def add_node(node_data):
    """Add a new node to the database"""
    db = get_db()
    try:
        result = db.nodes.insert_one(node_data)
        print(f"✅ Node inserted with ID: {result.inserted_id}")
        return result.inserted_id
    finally:
        db.client.close()

def get_node_by_name(name):
    """Get a node by its name"""
    db = get_db()
    try:
        return db.nodes.find_one({"name": name})
    finally:
        db.client.close()

def update_node(node_id, updates):
    """Update a node with the specified updates"""
    db = get_db()
    try:
        result = db.nodes.update_one({"_id": node_id}, {"$set": updates})
        print(f"🔄 Updated {result.modified_count} document(s)")
        return result.modified_count
    finally:
        db.client.close()

def delete_node_by_name(name):
    """Delete a node by its name"""
    db = get_db()
    try:
        result = db.nodes.delete_one({"name": name})
        print(f"🗑️ Deleted {result.deleted_count} document(s)")
        return result.deleted_count
    finally:
        db.client.close()

def list_all_nodes():
    """List all nodes in the database"""
    db = get_db()
    try:
        return list(db.nodes.find())
    finally:
        db.client.close() 
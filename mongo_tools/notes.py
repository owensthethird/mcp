from mongo_tools.db_connect import get_db

def add_interaction_note(node_id, note):
    """Add an interaction note to a node"""
    db = get_db()
    try:
        result = db.nodes.update_one(
            {"_id": node_id},
            {"$push": {"next_interaction_notes": note}}
        )
        print(f"📝 Added interaction note to node {node_id}")
        return result.modified_count > 0
    finally:
        db.client.close()

def process_and_clear_notes(node_id):
    """Process notes and clear those marked for deletion"""
    db = get_db()
    try:
        node = db.nodes.find_one({"_id": node_id})
        
        if not node or "next_interaction_notes" not in node:
            print(f"⚠️ No interaction notes found for node {node_id}")
            return False
        
        notes = node.get("next_interaction_notes", [])
        remaining = []

        for note in notes:
            print(f"Triggered Note: {note.get('effect', 'No effect specified')}")
            if not note.get("clear_after_use", False):
                remaining.append(note)

        db.nodes.update_one(
            {"_id": node_id},
            {"$set": {"next_interaction_notes": remaining}}
        )
        
        return True
    finally:
        db.client.close() 
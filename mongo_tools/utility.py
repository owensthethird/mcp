from mongo_tools.db_connect import get_db
import json
from bson import json_util
import os
import datetime

def clear_collection(collection_name, db_name='test_db'):
    """Remove all documents from a collection"""
    db = get_db(db_name)
    try:
        collection = db[collection_name]
        result = collection.delete_many({})
        print(f"🧹 Cleared {result.deleted_count} documents from {collection_name}")
        return result.deleted_count
    finally:
        db.client.close()

def create_database_snapshot(directory='backups'):
    """Create a JSON snapshot of the entire database"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    db = get_db()
    try:
        snapshot = {}
        
        for collection_name in db.list_collection_names():
            snapshot[collection_name] = list(db[collection_name].find())
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/mongodb_snapshot_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(snapshot, f, default=json_util.default, indent=2)
        
        print(f"📸 Database snapshot saved to {filename}")
        return filename
    finally:
        db.client.close()

def restore_database_snapshot(filename):
    """Restore database from a snapshot file"""
    if not os.path.exists(filename):
        print(f"❌ Snapshot file not found: {filename}")
        return False
    
    with open(filename, 'r') as f:
        snapshot = json.load(f)
    
    db = get_db()
    try:
        for collection_name, documents in snapshot.items():
            # Clear existing collection
            db[collection_name].delete_many({})
            
            # Insert documents if any exist
            if documents:
                parsed_docs = json_util.loads(json_util.dumps(documents))
                db[collection_name].insert_many(parsed_docs)
                
        print(f"🔄 Database restored from snapshot: {filename}")
        return True
    finally:
        db.client.close()

def get_database_stats():
    """Get statistics about the database"""
    db = get_db()
    try:
        stats = {
            "collections": db.list_collection_names(),
            "counts": {}
        }
        
        for collection in stats["collections"]:
            stats["counts"][collection] = db[collection].count_documents({})
        
        return stats
    finally:
        db.client.close() 
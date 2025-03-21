from pymongo import MongoClient

class DBConnection:
    """A wrapper class to handle MongoDB connections"""
    def __init__(self, client, db):
        self.client = client
        self.db = db
    
    def __getitem__(self, name):
        return self.db[name]
    
    def __getattr__(self, name):
        return getattr(self.db, name)
    
    def close(self):
        """Close the MongoDB client connection"""
        if self.client:
            self.client.close()

def get_db(db_name='test_db'):
    """
    Connect to MongoDB and return a wrapped database object that includes
    the client for proper connection management
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    return DBConnection(client, db) 
#!/usr/bin/env python3
import pymongo
from pymongo import MongoClient

# Try to connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    
    print("MongoDB connection successful!")
    print("MongoDB server version:", client.server_info()['version'])
    
    # List databases
    print("\nAvailable databases:")
    for db in client.list_database_names():
        print(f"- {db}")
        
except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Error: Could not connect to MongoDB server.")
    print("Make sure MongoDB is installed and running on your system.")
    print(f"Error details: {err}")
    
except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    # Close the connection
    if 'client' in locals():
        client.close() 
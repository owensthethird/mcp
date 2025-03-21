#!/usr/bin/env python3
import subprocess
import os
import sys
import time

# Path to mongod.exe (will try to find it in standard locations)
DEFAULT_MONGOD_PATHS = [
    r"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe",
    r"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe",
    r"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe",
]

# Path to your config file relative to this script
CONFIG_PATH = os.path.abspath("mongod.cfg")

def find_mongod_executable():
    """Attempt to find the mongod executable in standard locations"""
    for path in DEFAULT_MONGOD_PATHS:
        if os.path.exists(path):
            print(f"✅ Found MongoDB at: {path}")
            return path
    
    # If none of the default paths work, check if mongod is in PATH
    try:
        subprocess.run(["mongod", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        print("✅ Found MongoDB in system PATH")
        return "mongod"
    except FileNotFoundError:
        return None

def ensure_data_directory():
    """Make sure the mongo_data directory exists"""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mongo_data")
    if not os.path.exists(data_dir):
        print(f"📁 Creating data directory: {data_dir}")
        os.makedirs(data_dir)
    return data_dir

def launch_mongodb():
    print("🔍 Checking MongoDB configuration...")
    
    # Check if mongod.cfg exists
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Error: Config file not found at {CONFIG_PATH}")
        print("Creating a default config file...")
        with open(CONFIG_PATH, "w") as f:
            f.write("# mongod.cfg\nstorage:\n  dbPath: ./mongo_data\nnet:\n  bindIp: 127.0.0.1\n  port: 27017\n")
        print(f"✅ Created default config file at {CONFIG_PATH}")
    
    # Find mongod executable
    mongod_path = find_mongod_executable()
    if not mongod_path:
        print("❌ Error: MongoDB executable not found.")
        print("Please install MongoDB Server from: https://www.mongodb.com/try/download/community")
        return
    
    # Ensure data directory exists
    data_dir = ensure_data_directory()
    
    print(f"🚀 Launching MongoDB with config: {CONFIG_PATH}")
    print(f"📂 Data directory: {data_dir}")
    
    try:
        # Launch MongoDB with more verbose output
        process = subprocess.Popen(
            [mongod_path, "--config", CONFIG_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to check if process starts successfully
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            # Process exited already, get error message
            _, stderr = process.communicate()
            print(f"❌ Error: MongoDB failed to start.\nError details: {stderr}")
            return
        
        print("✅ MongoDB is now running. Leave this window open while you use the database.")
        print("🛑 Press Ctrl+C to stop MongoDB.")
        
        # Collect and display output
        while True:
            output_line = process.stdout.readline()
            if output_line:
                print(f"MongoDB: {output_line.strip()}")
            
            # Check if process still running
            if process.poll() is not None:
                break
                
    except KeyboardInterrupt:
        print("\n⏹️ Shutting down MongoDB...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ MongoDB has been stopped.")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    launch_mongodb()

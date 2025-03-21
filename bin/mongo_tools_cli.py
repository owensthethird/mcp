#!/usr/bin/env python3
"""
MongoDB Tools Command Line Interface

This script provides a command-line interface to common MongoDB operations
provided by the mongo_tools package.

Usage:
    python mongo_tools_cli.py <command> [options]

Commands:
    node              Node operations (add, get, update, delete, list, import, export)
    edge              Edge operations (add, get, remove)
    snapshot          Database snapshot operations (create, restore)
    stats             Show database statistics
    clear             Clear collections
    drop              Drop entire database (use with extreme caution)
"""

import os
import sys
import argparse
import logging
import json
from bson import json_util, ObjectId

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import mongo_tools modules
try:
    from mongo_tools.db_connect import get_db
    from mongo_tools.nodes import add_node, get_node_by_name, get_node_by_id, update_node, delete_node_by_name, list_all_nodes
    from mongo_tools.nodes import import_nodes_from_json, import_nodes_from_csv, export_nodes_to_json, export_nodes_to_csv
    from mongo_tools.edges import add_edge, get_connections, remove_edge
    from mongo_tools.utility import clear_collection, create_database_snapshot, restore_database_snapshot, get_database_stats, drop_database
    from lib.logging_config import configure_logger
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Configure logging
logger = configure_logger("mongo_tools_cli")

class MongoToolsCLI:
    """Command line interface for MongoDB tools"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="MongoDB Tools CLI",
            usage="""mongo_tools_cli.py <command> [<args>]

Commands:
  node        Node operations (add, get, update, delete, list, import, export)
  edge        Edge operations (add, get, remove)
  snapshot    Database snapshot operations (create, restore)
  stats       Show database statistics
  clear       Clear collections
  drop        Drop entire database (use with extreme caution)
"""
        )
        self.parser.add_argument('command', help='Command to run')
        self.parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
        
        # Parse initial arguments
        args = self.parser.parse_args(sys.argv[1:2])
        
        # Configure logging level based on verbose flag
        if hasattr(args, 'verbose') and args.verbose:
            logger.setLevel(logging.DEBUG)
        
        # Check if the command exists as a method
        if not hasattr(self, args.command):
            print(f"Unrecognized command: {args.command}")
            self.parser.print_help()
            sys.exit(1)
            
        # Call the appropriate command
        getattr(self, args.command)()
    
    def node(self):
        """Handle node-related commands"""
        parser = argparse.ArgumentParser(description='Node operations')
        subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')
        subparsers.required = True
        
        # Add node
        add_parser = subparsers.add_parser('add', help='Add a new node')
        add_parser.add_argument('--file', '-f', help='JSON file containing node data')
        add_parser.add_argument('--name', '-n', help='Node name')
        add_parser.add_argument('--type', '-t', help='Node type')
        
        # Get node
        get_parser = subparsers.add_parser('get', help='Get a node')
        get_parser.add_argument('--name', '-n', required=True, help='Node name')
        
        # Update node
        update_parser = subparsers.add_parser('update', help='Update a node')
        update_parser.add_argument('--name', '-n', required=True, help='Node name')
        update_parser.add_argument('--file', '-f', help='JSON file containing updates')
        update_parser.add_argument('--set', '-s', action='append', help='Updates in key=value format')
        
        # Delete node
        delete_parser = subparsers.add_parser('delete', help='Delete a node')
        delete_parser.add_argument('--name', '-n', required=True, help='Node name')
        
        # List nodes
        list_parser = subparsers.add_parser('list', help='List all nodes')
        list_parser.add_argument('--limit', '-l', type=int, help='Maximum number of nodes to return')
        list_parser.add_argument('--sort', '-s', help='Field to sort by')
        
        # Import nodes
        import_parser = subparsers.add_parser('import', help='Import multiple nodes from a file')
        import_parser.add_argument('--file', '-f', required=True, help='File containing node data (JSON or CSV)')
        import_parser.add_argument('--format', choices=['json', 'csv', 'auto'], default='auto',
                                   help='Format of the input file (default: auto-detect from extension)')
        import_parser.add_argument('--update', '-u', action='store_true', 
                                  help='Update existing nodes instead of skipping them')
        
        # Export nodes
        export_parser = subparsers.add_parser('export', help='Export nodes to a file')
        export_parser.add_argument('--file', '-f', required=True, help='Output file path (JSON or CSV)')
        export_parser.add_argument('--format', choices=['json', 'csv', 'auto'], default='auto',
                                  help='Format of the output file (default: auto-detect from extension)')
        export_parser.add_argument('--query', '-q', help='JSON query to filter nodes for export')
        export_parser.add_argument('--include-ids', action='store_true', 
                                  help='Include MongoDB ObjectIds in the exported data (JSON only)')
        export_parser.add_argument('--fields', help='Comma-separated list of fields to include (CSV only)')
        
        args = parser.parse_args(sys.argv[2:])
        
        if args.operation == 'add':
            if args.file:
                try:
                    with open(args.file, 'r') as f:
                        node_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    logger.error(f"Error reading node data file: {e}")
                    sys.exit(1)
            else:
                if not args.name:
                    logger.error("Node name is required")
                    sys.exit(1)
                node_data = {
                    "name": args.name,
                    "type": args.type or "generic"
                }
            
            try:
                node_id = add_node(node_data)
                print(f"Node added successfully with ID: {node_id}")
            except Exception as e:
                logger.error(f"Error adding node: {e}")
                sys.exit(1)
                
        elif args.operation == 'get':
            try:
                node = get_node_by_name(args.name)
                if node:
                    print(json.dumps(json.loads(json_util.dumps(node)), indent=2))
                else:
                    print(f"Node '{args.name}' not found")
            except Exception as e:
                logger.error(f"Error getting node: {e}")
                sys.exit(1)
                
        elif args.operation == 'update':
            try:
                # Get the node to update
                node = get_node_by_name(args.name)
                if not node:
                    print(f"Node '{args.name}' not found")
                    sys.exit(1)
                    
                # Get updates from file or command-line arguments
                updates = {}
                if args.file:
                    try:
                        with open(args.file, 'r') as f:
                            updates = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        logger.error(f"Error reading updates file: {e}")
                        sys.exit(1)
                elif args.set:
                    for update in args.set:
                        if '=' in update:
                            key, value = update.split('=', 1)
                            try:
                                # Try to parse the value as JSON
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                # If not valid JSON, treat as string
                                pass
                            updates[key] = value
                
                if not updates:
                    logger.error("No updates provided")
                    sys.exit(1)
                    
                modified = update_node(node['_id'], updates)
                print(f"Updated {modified} node(s)")
                
            except Exception as e:
                logger.error(f"Error updating node: {e}")
                sys.exit(1)
                
        elif args.operation == 'delete':
            try:
                deleted = delete_node_by_name(args.name)
                if deleted:
                    print(f"Node '{args.name}' deleted successfully")
                else:
                    print(f"Node '{args.name}' not found")
            except Exception as e:
                logger.error(f"Error deleting node: {e}")
                sys.exit(1)
                
        elif args.operation == 'list':
            try:
                nodes = list_all_nodes(
                    limit=args.limit,
                    sort_field=args.sort if args.sort else None
                )
                
                if not nodes:
                    print("No nodes found")
                    return
                    
                print(f"Found {len(nodes)} nodes:")
                for node in nodes:
                    print(f"- {node['name']} (Type: {node.get('type', 'unknown')})")
                    
                print("\nUse 'node get --name NODE_NAME' to view node details")
                
            except Exception as e:
                logger.error(f"Error listing nodes: {e}")
                sys.exit(1)
        
        elif args.operation == 'import':
            try:
                # Determine file format from extension if auto
                file_path = args.file
                file_format = args.format
                
                if file_format == 'auto':
                    if file_path.lower().endswith('.json'):
                        file_format = 'json'
                    elif file_path.lower().endswith('.csv'):
                        file_format = 'csv'
                    else:
                        print(f"Unable to detect format from file extension: {file_path}")
                        print("Please specify --format json or --format csv")
                        sys.exit(1)
                
                print(f"Importing nodes from {file_path} (format: {file_format})...")
                
                if file_format == 'json':
                    try:
                        summary = import_nodes_from_json(file_path, args.update)
                    except ValueError as e:
                        print(f"Error: {e}")
                        sys.exit(1)
                elif file_format == 'csv':
                    try:
                        summary = import_nodes_from_csv(file_path, args.update)
                    except ValueError as e:
                        print(f"Error: {e}")
                        sys.exit(1)
                
                # Print summary
                print("\n📊 Import Summary:")
                print(f"✅ Added: {summary['added']} new nodes")
                print(f"🔄 Updated: {summary['updated']} existing nodes")
                print(f"⏭️ Skipped: {summary['skipped']} existing nodes")
                print(f"❌ Failed: {summary['failed']} nodes")
                print(f"Total: {sum(summary.values())} nodes processed")
                
            except Exception as e:
                logger.error(f"Error importing nodes: {e}")
                sys.exit(1)
        
        elif args.operation == 'export':
            try:
                # Determine file format from extension if auto
                file_path = args.file
                file_format = args.format
                
                if file_format == 'auto':
                    if file_path.lower().endswith('.json'):
                        file_format = 'json'
                    elif file_path.lower().endswith('.csv'):
                        file_format = 'csv'
                    else:
                        print(f"Unable to detect format from file extension: {file_path}")
                        print("Please specify --format json or --format csv")
                        sys.exit(1)
                
                # Parse query if provided
                query = None
                if args.query:
                    try:
                        query = json.loads(args.query)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing query: {e}")
                        print("Query must be valid JSON. Example: '{\"type\": \"character\"}'")
                        sys.exit(1)
                
                print(f"Exporting nodes to {file_path} (format: {file_format})...")
                
                if file_format == 'json':
                    try:
                        count = export_nodes_to_json(file_path, query, args.include_ids)
                        print(f"✅ Exported {count} nodes to {file_path}")
                    except Exception as e:
                        print(f"Error exporting to JSON: {e}")
                        sys.exit(1)
                elif file_format == 'csv':
                    try:
                        # Parse fields if provided
                        fields = None
                        if args.fields:
                            fields = [f.strip() for f in args.fields.split(',')]
                            
                        count = export_nodes_to_csv(file_path, query, fields)
                        print(f"✅ Exported {count} nodes to {file_path}")
                    except Exception as e:
                        print(f"Error exporting to CSV: {e}")
                        sys.exit(1)
                
            except Exception as e:
                logger.error(f"Error exporting nodes: {e}")
                sys.exit(1)
    
    def edge(self):
        """Handle edge-related commands"""
        parser = argparse.ArgumentParser(description='Edge operations')
        subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')
        subparsers.required = True
        
        # Add edge
        add_parser = subparsers.add_parser('add', help='Add a new edge between nodes')
        add_parser.add_argument('--from', '-f', dest='from_node', required=True, help='Source node name')
        add_parser.add_argument('--to', '-t', required=True, help='Target node name')
        add_parser.add_argument('--data', '-d', help='JSON string with edge data')
        add_parser.add_argument('--file', help='JSON file containing edge data')
        
        # Get connections
        get_parser = subparsers.add_parser('get', help='Get all connections from a node')
        get_parser.add_argument('--name', '-n', required=True, help='Node name')
        
        # Remove edge
        remove_parser = subparsers.add_parser('remove', help='Remove an edge between nodes')
        remove_parser.add_argument('--from', '-f', dest='from_node', required=True, help='Source node name')
        remove_parser.add_argument('--to', '-t', required=True, help='Target node name')
        
        args = parser.parse_args(sys.argv[2:])
        
        if args.operation == 'add':
            try:
                # Get source and target nodes
                source_node = get_node_by_name(args.from_node)
                target_node = get_node_by_name(args.to)
                
                if not source_node:
                    print(f"Source node '{args.from_node}' not found")
                    sys.exit(1)
                    
                if not target_node:
                    print(f"Target node '{args.to}' not found")
                    sys.exit(1)
                
                # Get edge data
                edge_data = None
                if args.data:
                    try:
                        edge_data = json.loads(args.data)
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON in edge data")
                        sys.exit(1)
                elif args.file:
                    try:
                        with open(args.file, 'r') as f:
                            edge_data = json.load(f)
                    except (json.JSONDecodeError, FileNotFoundError) as e:
                        logger.error(f"Error reading edge data file: {e}")
                        sys.exit(1)
                
                success = add_edge(source_node['_id'], target_node['_id'], edge_data)
                if success:
                    print(f"Edge added from '{args.from_node}' to '{args.to}'")
                else:
                    print("Failed to add edge")
                    
            except Exception as e:
                logger.error(f"Error adding edge: {e}")
                sys.exit(1)
                
        elif args.operation == 'get':
            try:
                node = get_node_by_name(args.name)
                if not node:
                    print(f"Node '{args.name}' not found")
                    sys.exit(1)
                    
                connections = get_connections(node['_id'])
                if not connections:
                    print(f"No connections found for node '{args.name}'")
                    return
                    
                print(f"Connections from '{args.name}':")
                for i, conn in enumerate(connections, 1):
                    target = conn.get('target_name', 'Unknown')
                    conn_type = conn.get('type', 'connection')
                    print(f"{i}. To: {target} (Type: {conn_type})")
                    
                    # Print additional edge properties
                    for key, value in conn.items():
                        if key not in ['target_id', 'target_name', 'type']:
                            print(f"   - {key}: {value}")
                            
            except Exception as e:
                logger.error(f"Error getting connections: {e}")
                sys.exit(1)
                
        elif args.operation == 'remove':
            try:
                source_node = get_node_by_name(args.from_node)
                target_node = get_node_by_name(args.to)
                
                if not source_node:
                    print(f"Source node '{args.from_node}' not found")
                    sys.exit(1)
                    
                if not target_node:
                    print(f"Target node '{args.to}' not found")
                    sys.exit(1)
                    
                success = remove_edge(source_node['_id'], target_node['_id'])
                if success:
                    print(f"Edge removed from '{args.from_node}' to '{args.to}'")
                else:
                    print("Edge not found or could not be removed")
                    
            except Exception as e:
                logger.error(f"Error removing edge: {e}")
                sys.exit(1)
    
    def snapshot(self):
        """Handle database snapshot commands"""
        parser = argparse.ArgumentParser(description='Database snapshot operations')
        subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')
        subparsers.required = True
        
        # Create snapshot
        create_parser = subparsers.add_parser('create', help='Create a database snapshot')
        create_parser.add_argument('--dir', '-d', help='Directory to save snapshot')
        
        # Restore snapshot
        restore_parser = subparsers.add_parser('restore', help='Restore a database from snapshot')
        restore_parser.add_argument('--file', '-f', required=True, help='Snapshot file path')
        
        args = parser.parse_args(sys.argv[2:])
        
        if args.operation == 'create':
            try:
                directory = args.dir if args.dir else 'backups'
                snapshot_file = create_database_snapshot(directory)
                print(f"Database snapshot created: {snapshot_file}")
            except Exception as e:
                logger.error(f"Error creating snapshot: {e}")
                sys.exit(1)
                
        elif args.operation == 'restore':
            try:
                if not os.path.exists(args.file):
                    print(f"Snapshot file not found: {args.file}")
                    sys.exit(1)
                    
                print(f"Restoring database from {args.file}...")
                success = restore_database_snapshot(args.file)
                
                if success:
                    print("Database restored successfully")
                else:
                    print("Failed to restore database")
                    
            except Exception as e:
                logger.error(f"Error restoring database: {e}")
                sys.exit(1)
    
    def stats(self):
        """Display database statistics"""
        try:
            stats = get_database_stats()
            
            print("\n=== MongoDB Database Statistics ===\n")
            
            print("Collections:")
            for i, collection in enumerate(stats['collections'], 1):
                count = stats['counts'].get(collection, 0)
                print(f"{i}. {collection}: {count} documents")
                
            print("\nTotal document count:", sum(stats['counts'].values()))
            
        except Exception as e:
            logger.error(f"Error getting database statistics: {e}")
            sys.exit(1)
    
    def clear(self):
        """Clear database collections"""
        parser = argparse.ArgumentParser(description='Clear database collections')
        parser.add_argument('--collection', '-c', required=True, 
                          help='Collection name to clear (use "all" for all collections)')
        parser.add_argument('--force', '-f', action='store_true',
                          help='Force operation without confirmation')
        
        args = parser.parse_args(sys.argv[2:])
        
        try:
            if args.collection.lower() == 'all':
                if not args.force:
                    confirm = input("Are you sure you want to clear ALL collections? This cannot be undone! (y/N): ")
                    if confirm.lower() != 'y':
                        print("Operation cancelled")
                        return
                
                db = get_db()
                try:
                    collections = db.list_collection_names()
                    cleared_total = 0
                    
                    for collection in collections:
                        cleared = clear_collection(collection)
                        cleared_total += cleared
                        print(f"Cleared {cleared} documents from '{collection}'")
                        
                    print(f"\nCleared {cleared_total} documents from {len(collections)} collections")
                finally:
                    db.close()
            else:
                if not args.force:
                    confirm = input(f"Are you sure you want to clear collection '{args.collection}'? This cannot be undone! (y/N): ")
                    if confirm.lower() != 'y':
                        print("Operation cancelled")
                        return
                
                cleared = clear_collection(args.collection)
                print(f"Cleared {cleared} documents from '{args.collection}'")
                
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            sys.exit(1)

    def drop(self):
        """Drop an entire database"""
        parser = argparse.ArgumentParser(description='Drop entire database')
        parser.add_argument('--db', '-d', default='test_db',
                           help='Database name to drop (default: test_db)')
        parser.add_argument('--force', '-f', action='store_true',
                           help='Force operation without confirmation')
        parser.add_argument('--confirm', '-c', help='Type the database name again to confirm deletion')
        
        args = parser.parse_args(sys.argv[2:])
        
        try:
            # Multiple safety checks
            if not args.force:
                print("⚠️  WARNING: THIS OPERATION WILL PERMANENTLY DELETE ALL DATA IN THE DATABASE!")
                print(f"⚠️  Database to drop: {args.db}")
                
                if args.confirm != args.db:
                    confirm = input(f"To confirm, please type the database name '{args.db}' exactly: ")
                    if confirm != args.db:
                        print("Database names do not match. Operation cancelled.")
                        return
                
                confirm = input(f"Final confirmation - Are you ABSOLUTELY SURE you want to DROP the entire '{args.db}' database? This CANNOT be undone! (yes/NO): ")
                if confirm.lower() != 'yes':
                    print("Operation cancelled")
                    return
            
            # Create a snapshot before dropping (for safety)
            print(f"Creating backup snapshot before dropping database '{args.db}'...")
            snapshot_file = create_database_snapshot()
            print(f"Backup saved to {snapshot_file}")
            
            # Drop the database
            success = drop_database(args.db)
            
            if success:
                print(f"Database '{args.db}' has been completely dropped.")
                print(f"If this was a mistake, you can restore from the backup: {snapshot_file}")
                print("Use: mongo_tools_cli.py snapshot restore --file BACKUP_FILE")
            else:
                print(f"Failed to drop database '{args.db}'.")
                
        except Exception as e:
            logger.error(f"Error dropping database: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    try:
        MongoToolsCLI()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)

if __name__ == '__main__':
    main() 
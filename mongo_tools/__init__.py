"""
MongoDB Tools Package

A collection of tools for interacting with MongoDB databases.
This package provides utilities for database connections, node operations,
edge management, and more.

Usage:
    from mongo_tools.db_connect import get_db
    from mongo_tools.nodes import add_node, get_node_by_name
"""

import os
import sys
import logging

# Add the project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging for the package
try:
    from lib.logging_config import configure_logger
    logger = configure_logger('mongo_tools')
    logger.debug("mongo_tools package initialized with logging")
except ImportError:
    # Fallback logging configuration if central logging is not available
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('mongo_tools')
    logger.info("mongo_tools package initialized with basic logging (lib.logging_config not found)")

# Package version
__version__ = '0.1.0'

# MongoDB tools package
# This package contains utilities for working with MongoDB in our application 
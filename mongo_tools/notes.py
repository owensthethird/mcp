from mongo_tools.db_connect import get_db
import logging

# Configure module logger
logger = logging.getLogger(__name__)

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
    """
    Process notes and clear them from the node's next_interaction_notes array.
    
    Notes can be either strings or dictionaries. Dictionary notes may have
    additional metadata like 'effect' and 'clear_after_use'.
    
    Args:
        node_id: The ID of the node to process notes for
        
    Returns:
        bool: True if notes were processed, False otherwise
    """
    db = get_db()
    try:
        node = db.nodes.find_one({"_id": node_id})
        
        if not node or "next_interaction_notes" not in node:
            logger.warning(f"No interaction notes found for node {node_id}")
            return False
        
        notes = node.get("next_interaction_notes", [])
        remaining = []

        for note in notes:
            if isinstance(note, str):
                # Simple string notes
                logger.info(f"Processed note: {note}")
            else:
                # Dictionary notes with metadata
                effect = note.get('effect', 'No effect specified')
                logger.info(f"Processed note with effect: {effect}")
                
                # Keep notes that shouldn't be cleared
                if not note.get("clear_after_use", False):
                    remaining.append(note)

        # Update the node, clearing all string notes and any dict notes marked for deletion
        db.nodes.update_one(
            {"_id": node_id},
            {"$set": {"next_interaction_notes": remaining}}
        )
        
        logger.info(f"Processed and cleared notes for node {node_id}")
        return True
    except Exception as e:
        logger.error(f"Error processing notes for node {node_id}: {e}")
        raise
    finally:
        db.client.close() 
from auth import get_db_connection
import logging

logger = logging.getLogger(__name__)

def save_conversation_and_messages(user_id, prompt, response, conversation_id=None):
    """
    Save messages to an existing conversation or create a new one.
    Returns the conversation_id used.
    """
    connection = get_db_connection()
    if not connection:
        logger.warning("Database connection failed")
        return None

    try:
        cursor = connection.cursor()

        if conversation_id:
            # Verify conversation exists and belongs to the user
            cursor.execute("SELECT conversation_id FROM conversations WHERE conversation_id = %s AND user_id = %s", (conversation_id, user_id))
            if not cursor.fetchone():
                logger.warning("Conversation ID does not match user, creating new.")
                conversation_id = None

        if not conversation_id:
            cursor.execute(
                """
                INSERT INTO conversations (user_id, status)
                VALUES (%s, 'active') RETURNING conversation_id
                """,
                (user_id,)
            )
            conversation_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender, message_text)
            VALUES (%s, 'user', %s)
            """,
            (conversation_id, prompt)
        )

        cursor.execute(
            """
            INSERT INTO messages (conversation_id, sender, message_text)
            VALUES (%s, 'bot', %s)
            """,
            (conversation_id, response)
        )

        connection.commit()
        return conversation_id
    except Exception as e:
        connection.rollback()
        logger.error(f"Database error while saving conversation: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def get_conversations_by_user(user_id):
    """
    Retrieve all conversations and messages for a given user_id.
    Returns a list of conversation dictionaries.
    """
    connection = get_db_connection()
    if not connection:
        logger.warning("Database connection failed")
        return []

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT c.conversation_id, c.status, m.message_id, m.sender, m.message_text
            FROM conversations c
            LEFT JOIN messages m ON c.conversation_id = m.conversation_id
            WHERE c.user_id = %s
            ORDER BY c.conversation_id DESC, m.message_id ASC
            """,
            (user_id,)
        )
        results = cursor.fetchall()
        conversations = {}
        for row in results:
            conv_id, status, msg_id, sender, msg_text = row
            if conv_id not in conversations:
                conversations[conv_id] = {'id': conv_id, 'status': status, 'messages': []}
            if msg_id:
                conversations[conv_id]['messages'].append({
                    'id': msg_id,
                    'sender': sender,
                    'text': msg_text
                })
        return list(conversations.values())
    except Exception as e:
        logger.error(f"Database error while retrieving conversations: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

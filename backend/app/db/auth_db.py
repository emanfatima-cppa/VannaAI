import psycopg2
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

def get_connection():
    """Create a raw connection to the PostgreSQL database."""
    from app.core.config import get_settings
    settings = get_settings()
    conn_str = settings.postgres_connection_string
    if conn_str.startswith("postgresql+psycopg2://"):
        conn_str = conn_str.replace("postgresql+psycopg2://", "postgresql://", 1)
    return psycopg2.connect(conn_str)

def init_db():
    """Create the windows_users table if it does not exist and ensure last_logout column exists."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS windows_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                domain VARCHAR(100),
                roles VARCHAR(200) DEFAULT 'it_viewer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_logout TIMESTAMP
            );
            ALTER TABLE windows_users ADD COLUMN IF NOT EXISTS last_logout TIMESTAMP;

            CREATE TABLE IF NOT EXISTS user_query_history (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                instance_key VARCHAR(100) NOT NULL,
                question TEXT NOT NULL,
                sql TEXT,
                status VARCHAR(50) DEFAULT 'success',
                error TEXT,
                nl_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_user_query_history_user ON user_query_history(LOWER(username));

            CREATE TABLE IF NOT EXISTS shared_chat_sessions (
                share_id VARCHAR(50) PRIMARY KEY,
                owner_username VARCHAR(100) NOT NULL,
                instance_key VARCHAR(100) NOT NULL,
                title VARCHAR(255),
                messages_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logger.info("PostgreSQL auth database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL auth database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def get_db_user(username: str) -> Optional[dict]:
    """Retrieve a user from the windows_users table by username."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Case insensitive match for safety
        cursor.execute(
            "SELECT username, domain, roles FROM windows_users WHERE LOWER(username) = LOWER(%s)",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            # Parse comma-separated roles into a list
            roles = [r.strip() for r in row[2].split(",") if r.strip()] if row[2] else ["it_viewer"]
            return {
                "username": row[0],
                "domain": row[1],
                "roles": roles
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching user '{username}' from PostgreSQL: {e}")
        return None
    finally:
        if conn:
            conn.close()

def upsert_db_user(username: str, domain: Optional[str] = None, roles: Optional[list[str]] = None) -> Optional[dict]:
    """
    Insert a user into the windows_users table if they don't exist.
    If they exist, update their last login timestamp, domain, and roles if provided.
    Returns the user dict on success.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Convert roles list to comma-separated string if provided
        roles_str = ",".join(roles) if roles else None
        
        # Check if exists
        cursor.execute(
            "SELECT username, domain, roles FROM windows_users WHERE LOWER(username) = LOWER(%s)",
            (username,)
        )
        row = cursor.fetchone()
        
        now = datetime.now()
        if row:
            # Update last login, domain, and roles if provided
            if roles_str:
                cursor.execute(
                    "UPDATE windows_users SET last_login = %s, domain = %s, roles = %s WHERE LOWER(username) = LOWER(%s)",
                    (now, domain or row[1] or ".", roles_str, username)
                )
            else:
                cursor.execute(
                    "UPDATE windows_users SET last_login = %s, domain = %s WHERE LOWER(username) = LOWER(%s)",
                    (now, domain or row[1] or ".", username)
                )
            conn.commit()
            
            # Fetch the updated record
            cursor.execute(
                "SELECT username, domain, roles FROM windows_users WHERE LOWER(username) = LOWER(%s)",
                (username,)
            )
            updated_row = cursor.fetchone()
            db_roles = [r.strip() for r in updated_row[2].split(",") if r.strip()] if updated_row[2] else ["it_viewer"]
            return {
                "username": updated_row[0],
                "domain": updated_row[1],
                "roles": db_roles
            }
        else:
            # Insert new user
            if not roles_str:
                # Default role resolution if roles not passed
                default_roles = "it_viewer"
                if "admin" in username.lower():
                    default_roles = "it_admin"
                roles_str = default_roles
                
            cursor.execute(
                """
                INSERT INTO windows_users (username, domain, roles, created_at, last_login)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING username, domain, roles
                """,
                (username, domain or ".", roles_str, now, now)
            )
            new_row = cursor.fetchone()
            conn.commit()
            if new_row:
                db_roles = [r.strip() for r in new_row[2].split(",") if r.strip()] if new_row[2] else ["it_viewer"]
                return {
                    "username": new_row[0],
                    "domain": new_row[1],
                    "roles": db_roles
                }
            return None
    except Exception as e:
        logger.error(f"Error upserting user '{username}' in PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def record_user_logout(username: str) -> bool:
    """Update last_logout timestamp for the specified user."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute(
            "UPDATE windows_users SET last_logout = %s WHERE LOWER(username) = LOWER(%s)",
            (now, username)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error recording logout for user '{username}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def record_query_history(
    username: str,
    instance_key: str,
    question: str,
    sql: Optional[str] = None,
    status: str = "success",
    error: Optional[str] = None,
    nl_summary: Optional[str] = None,
) -> bool:
    """Record a user question and response in user_query_history table."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_query_history (username, instance_key, question, sql, status, error, nl_summary, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (username, instance_key, question, sql, status, error, nl_summary, datetime.now())
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error recording query history for user '{username}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_user_query_history(username: str, limit: int = 100, instance_key: Optional[str] = None) -> list[dict]:
    """Retrieve history of queries asked by a specific user from user_query_history."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if instance_key:
            cursor.execute(
                """
                SELECT id, username, instance_key, question, sql, status, error, nl_summary, created_at
                FROM user_query_history
                WHERE LOWER(username) = LOWER(%s) AND instance_key = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (username, instance_key, limit)
            )
        else:
            cursor.execute(
                """
                SELECT id, username, instance_key, question, sql, status, error, nl_summary, created_at
                FROM user_query_history
                WHERE LOWER(username) = LOWER(%s)
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (username, limit)
            )
        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "username": row[1],
                "instance_key": row[2],
                "question": row[3],
                "sql": row[4],
                "status": row[5],
                "error": row[6],
                "nl_summary": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
            })
        return history
    except Exception as e:
        logger.error(f"Error retrieving query history for user '{username}': {e}")
        return []
    finally:
        if conn:
            conn.close()

def clear_user_query_history(username: str, instance_key: Optional[str] = None) -> bool:
    """Clear query history for a user from user_query_history."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if instance_key:
            cursor.execute(
                "DELETE FROM user_query_history WHERE LOWER(username) = LOWER(%s) AND instance_key = %s",
                (username, instance_key)
            )
        else:
            cursor.execute(
                "DELETE FROM user_query_history WHERE LOWER(username) = LOWER(%s)",
                (username,)
            )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error clearing query history for user '{username}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def create_shared_session(
    share_id: str,
    owner_username: str,
    instance_key: str,
    title: str,
    messages_json: str,
) -> bool:
    """Insert a new shared chat snapshot into shared_chat_sessions."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO shared_chat_sessions (share_id, owner_username, instance_key, title, messages_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (share_id, owner_username, instance_key, title, messages_json),
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving shared chat session '{share_id}': {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_shared_session(share_id: str) -> Optional[dict]:
    """Retrieve a shared chat snapshot by share_id."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT share_id, owner_username, instance_key, title, messages_json, created_at
            FROM shared_chat_sessions
            WHERE share_id = %s
            """,
            (share_id,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "share_id": row[0],
                "owner_username": row[1],
                "instance_key": row[2],
                "title": row[3],
                "messages_json": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching shared chat session '{share_id}': {e}")
        return None
    finally:
        if conn:
            conn.close()
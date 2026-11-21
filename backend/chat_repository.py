from __future__ import annotations

from .database import create_connection_pool


class ChatRepository:
    def get_or_create_session(self, session_token: str, ip_address: str | None) -> int:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM chat_sessions WHERE session_token = %s",
                    (session_token,),
                )
                row = cursor.fetchone()
                if row:
                    return int(row[0])

                cursor.execute(
                    "INSERT INTO chat_sessions (session_token, ip_address) VALUES (%s, %s)",
                    (session_token, ip_address),
                )
                connection.commit()
                return int(cursor.lastrowid)

    def add_message(
        self,
        session_token: str,
        session_id: int,
        sender_type: str,
        message: str,
    ) -> int:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chat_messages (session_id, sender_type, message)
                    VALUES (%s, %s, %s)
                    """,
                    (session_id, sender_type, message),
                )
                connection.commit()
                return int(cursor.lastrowid)

    def get_history(self, session_token: str, limit: int = 50) -> list[dict[str, object]]:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT cm.id, cm.sender_type, cm.message, cm.timestamp
                    FROM chat_sessions cs
                    JOIN chat_messages cm ON cm.session_id = cs.id
                    WHERE cs.session_token = %s
                    ORDER BY cm.timestamp DESC, cm.id DESC
                    LIMIT %s
                    """,
                    (session_token, limit),
                )
                rows = list(cursor.fetchall())
        rows.reverse()
        return rows

    def get_last_messages(
        self,
        session_token: str,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT cm.sender_type, cm.message
                    FROM chat_sessions cs
                    JOIN chat_messages cm ON cm.session_id = cs.id
                    WHERE cs.session_token = %s
                    ORDER BY cm.timestamp DESC, cm.id DESC
                    LIMIT %s
                    """,
                    (session_token, limit),
                )
                rows = list(cursor.fetchall())
        rows.reverse()
        return rows

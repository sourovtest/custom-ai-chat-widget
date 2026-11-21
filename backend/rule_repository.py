from __future__ import annotations

import json

from .database import create_connection_pool


class RuleRepository:
    def list_rules(self) -> list[dict[str, object]]:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id, rule_name, trigger_event, action_type,
                           static_message, assigned_role, trigger_config,
                           priority, is_active, execution_frequency,
                           created_at, updated_at
                    FROM chatbot_rules
                    ORDER BY priority ASC, id ASC
                    """
                )
                return [self._serialize(row) for row in cursor.fetchall()]

    def get_rule(self, rule_id: int) -> dict[str, object] | None:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT id, rule_name, trigger_event, action_type,
                           static_message, assigned_role, trigger_config,
                           priority, is_active, execution_frequency,
                           created_at, updated_at
                    FROM chatbot_rules
                    WHERE id = %s
                    """,
                    (rule_id,),
                )
                row = cursor.fetchone()
                return self._serialize(row) if row else None

    def create_rule(self, data: dict[str, object]) -> dict[str, object]:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chatbot_rules (
                        rule_name, trigger_event, action_type, static_message,
                        assigned_role, trigger_config, priority, is_active,
                        execution_frequency
                    ) VALUES (%s, %s, %s, %s, %s, CAST(%s AS JSON), %s, %s, %s)
                    """,
                    (
                        data["rule_name"],
                        data["trigger_event"],
                        data["action_type"],
                        data["static_message"],
                        data["assigned_role"],
                        json.dumps(data["trigger_config"], ensure_ascii=False),
                        data["priority"],
                        data["is_active"],
                        data["execution_frequency"],
                    ),
                )
                connection.commit()
                rule_id = int(cursor.lastrowid)
        return self.get_rule(rule_id) or {}

    def update_rule(
        self,
        rule_id: int,
        data: dict[str, object],
    ) -> dict[str, object] | None:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE chatbot_rules
                    SET rule_name = %s,
                        trigger_event = %s,
                        action_type = %s,
                        static_message = %s,
                        assigned_role = %s,
                        trigger_config = CAST(%s AS JSON),
                        priority = %s,
                        is_active = %s,
                        execution_frequency = %s
                    WHERE id = %s
                    """,
                    (
                        data["rule_name"],
                        data["trigger_event"],
                        data["action_type"],
                        data["static_message"],
                        data["assigned_role"],
                        json.dumps(data["trigger_config"], ensure_ascii=False),
                        data["priority"],
                        data["is_active"],
                        data["execution_frequency"],
                        rule_id,
                    ),
                )
                connection.commit()
                if cursor.rowcount == 0:
                    return None
        return self.get_rule(rule_id)

    def delete_rule(self, rule_id: int) -> bool:
        with create_connection_pool().get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM chatbot_rules WHERE id = %s",
                    (rule_id,),
                )
                connection.commit()
                return cursor.rowcount > 0

    def _serialize(self, row: dict[str, object]) -> dict[str, object]:
        trigger_config = row.get("trigger_config")
        if isinstance(trigger_config, str):
            try:
                trigger_config = json.loads(trigger_config)
            except json.JSONDecodeError:
                trigger_config = {}
        return {
            **row,
            "trigger_config": trigger_config if isinstance(trigger_config, dict) else {},
            "is_active": bool(row.get("is_active")),
            "created_at": self._serialize_datetime(row.get("created_at")),
            "updated_at": self._serialize_datetime(row.get("updated_at")),
        }

    @staticmethod
    def _serialize_datetime(value: object) -> str | None:
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value) if value is not None else None

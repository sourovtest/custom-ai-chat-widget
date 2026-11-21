from mysql.connector.pooling import MySQLConnectionPool

from .config import settings

_pool: MySQLConnectionPool | None = None

def create_connection_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is not None:
        return _pool

    if not settings.mysql_user or not settings.mysql_database:
        raise RuntimeError(
            "Set MYSQL_USER and MYSQL_DATABASE before opening database connections."
        )

    _pool = MySQLConnectionPool(
        pool_name="bongora_chatbot",
        pool_size=5,
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        connection_timeout=5,
    )
    return _pool

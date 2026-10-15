
from database import get_db_connection


def initialize_database():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)

        conn.commit()

    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()

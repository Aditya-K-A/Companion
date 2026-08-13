import sqlite3
from app.config import settings

class Database:

    def __init__(self):
        settings.sqlite_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            settings.sqlite_path,
            check_same_thread=False
        )

        self._create_tables()

    def _create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                user_id TEXT PRIMARY KEY,
                advice_score REAL DEFAULT 0,
                venting_score REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mood_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                emotion TEXT NOT NULL,
                intensity REAL DEFAULT 0.0,
                confidence REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.commit()

    # --------------------------------------------------
    # MEMORY
    # --------------------------------------------------

    # def add_memory(
    #     self,
    #     user_id: str,
    #     memory_type: str,
    #     content: str,
    #     confidence: float = 1.0
    # ):
    #     cursor = self.connection.cursor()

    #     cursor.execute(
    #         """
    #         INSERT INTO memories
    #         (user_id, memory_type, content, confidence)
    #         VALUES (?, ?, ?, ?)
    #         """,
    #         (
    #             user_id,
    #             memory_type,
    #             content,
    #             confidence
    #         )
    #     )

    #     self.connection.commit()

    def add_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        confidence: float = 1.0
    ):
        cursor = self.connection.cursor()

        # Prevent exact duplicate memories
        cursor.execute(
            """
            SELECT id
            FROM memories
            WHERE user_id = ?
            AND memory_type = ?
            AND LOWER(TRIM(content)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (
                user_id,
                memory_type,
                content
            )
        )

        if cursor.fetchone():
            return False

        cursor.execute(
            """
            INSERT INTO memories
            (user_id, memory_type, content, confidence)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                memory_type,
                content,
                confidence
            )
        )

        self.connection.commit()

        return True

    def get_memories(self, user_id: str):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT memory_type, content, confidence
            FROM memories
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        return cursor.fetchall()

    # --------------------------------------------------
    # PREFERENCE
    # --------------------------------------------------

    def get_preference(self, user_id: str):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT advice_score, venting_score
            FROM preferences
            WHERE user_id = ?
            """,
            (user_id,)
        )

        return cursor.fetchone()

    def update_preference(
        self,
        user_id: str,
        advice_delta: float = 0,
        venting_delta: float = 0
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO preferences
            (user_id, advice_score, venting_score)
            VALUES (?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                advice_score = advice_score + excluded.advice_score,
                venting_score = venting_score + excluded.venting_score,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                advice_delta,
                venting_delta
            )
        )

        self.connection.commit()

    # --------------------------------------------------
    # MOOD
    # --------------------------------------------------

    def add_mood_event(
        self,
        user_id: str,
        emotion: str,
        intensity: float,
        confidence: float
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO mood_events
            (user_id, emotion, intensity, confidence)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                emotion,
                intensity,
                confidence
            )
        )

        self.connection.commit()

    def get_recent_moods(
        self,
        user_id: str,
        limit: int = 8
    ):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT emotion, intensity, confidence, created_at
            FROM mood_events
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        )

        return cursor.fetchall()
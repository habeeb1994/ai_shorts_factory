import sqlite3
import hashlib
import random

class TrendAgent:
    def __init__(self, db_path="assets/factory_history.db"):
        self.db_path = db_path
        self._bootstrap_db()
        
        # Niche-specific seed topics (Wealth & AI)
        self.niches = [
            "Passive income with ChatGPT",
            "AI tools for entrepreneurs",
            "The future of work in 2026",
            "How to scale a business with automation",
            "NVIDIA and the AI stock boom",
            "Replacing manual labor with agents"
        ]

    def _bootstrap_db(self):
        """Creates the tracking table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS history (topic_hash TEXT PRIMARY KEY, topic_name TEXT)")
        conn.commit()
        conn.close()

    def is_repeated(self, topic):
        """Checks if the topic has already been produced."""
        topic_hash = hashlib.md5(topic.lower().strip().encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT 1 FROM history WHERE topic_hash = ?", (topic_hash,))
        exists = cursor.fetchone()
        conn.close()
        return exists is not None

    def log_topic(self, topic):
        """Saves a topic to the database so it won't be repeated."""
        topic_hash = hashlib.md5(topic.lower().strip().encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR IGNORE INTO history (topic_hash, topic_name) VALUES (?, ?)", (topic_hash, topic))
        conn.commit()
        conn.close()

    def get_trending_topic(self):
        """
        In a full build, this would scrape Google Trends or YouTube.
        For now, it rotates through high-performing niche seeds and ensures no repeats.
        """
        random.shuffle(self.niches)
        for topic in self.niches:
            if not self.is_repeated(topic):
                return topic
        
        return "New AI Wealth Strategy " + str(random.randint(100, 999))
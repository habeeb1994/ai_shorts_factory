import sqlite3
import hashlib
import random
import requests
import xml.etree.ElementTree as ET
import urllib.parse
from contextlib import closing

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
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute("CREATE TABLE IF NOT EXISTS history (topic_hash TEXT PRIMARY KEY, topic_name TEXT)")

    def is_repeated(self, topic):
        """Checks if the topic has already been produced."""
        topic_hash = hashlib.md5(topic.lower().strip().encode()).hexdigest()
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute("SELECT 1 FROM history WHERE topic_hash = ?", (topic_hash,))
            exists = cursor.fetchone()
        return exists is not None

    def log_topic(self, topic):
        """Saves a topic to the database so it won't be repeated."""
        topic_hash = hashlib.md5(topic.lower().strip().encode()).hexdigest()
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute("INSERT OR IGNORE INTO history (topic_hash, topic_name) VALUES (?, ?)", (topic_hash, topic))

    def get_all_topics(self):
        """Retrieves all topics from the database."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute("SELECT topic_name FROM history")
            topics = [row[0] for row in cursor.fetchall()]
        return topics

    def delete_topics(self, topics):
        """Deletes multiple topics from the database by their names."""
        hashes = [(hashlib.md5(topic.lower().strip().encode()).hexdigest(),) for topic in topics]
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.executemany("DELETE FROM history WHERE topic_hash = ?", hashes)

    def get_trending_topic(self, query="Artificial Intelligence OR ChatGPT OR Passive Income", time_filter="2d"):
        """
        Fetches trending topics from Google News RSS based on niche keywords.
        Ensures topics are not repeated using the SQLite database.
        """
        try:
            # Format query for URL and append time filter for recency
            formatted_query = urllib.parse.quote_plus(query)
            if time_filter:
                formatted_query += f"+when:{time_filter}"
                
            # Use Google News RSS to find live trending news in our niche
            rss_url = f"https://news.google.com/rss/search?q={formatted_query}&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()
            
            # Parse XML RSS feed
            root = ET.fromstring(response.content)
            
            # Extract news titles and links
            trending_topics = []
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                if title is not None and title.text:
                    # Clean up the title (remove publisher suffix usually separated by " - ")
                    clean_title = title.text.split(" - ")[0].strip()
                    source_link = link.text if link is not None else None
                    trending_topics.append((clean_title, source_link))
                    
            random.shuffle(trending_topics)
            
            for topic, source_link in trending_topics:
                if not self.is_repeated(topic):
                    return topic, source_link
                    
        except Exception as e:
            print(f"⚠️ Could not fetch live trends ({e}). Falling back to seed topics.")

        # Fallback to seed niches
        random.shuffle(self.niches)
        for topic in self.niches:
            if not self.is_repeated(topic):
                return topic, None
        
        return "New AI Wealth Strategy " + str(random.randint(100, 999)), None
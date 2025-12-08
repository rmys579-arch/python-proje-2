from dataclasses import dataclass
from abc import ABC, abstractmethod
from pymongo import MongoClient, errors
import re
import logging
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "jobs")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "ads")

# -------------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------------------------------------------
# 1. Dataclass (High Score)
# -------------------------------------------------------
@dataclass
class JobPosting:
    """Represents a single cleaned job posting."""
    job_title: str
    company_name: str
    summary_description: str
    ad_link: str


# -------------------------------------------------------
# 2. Abstract Database Interface
# -------------------------------------------------------
class IDatabase(ABC):
    @abstractmethod
    def save_postings(self, postings: list[dict]):
        """Save multiple postings into the database."""
        pass


# -------------------------------------------------------
# 3. Cleaner Classes (Inheritance)
# -------------------------------------------------------
class BaseCleaner:
    def clean(self, text: str) -> str:
        return text.strip() if text else ""


class HTMLCleaner(BaseCleaner):
    """Removes HTML tags."""

    def clean(self, text: str) -> str:
        base = super().clean(text)
        return re.sub(r"<.*?>", "", base)


class EmojiCleaner(BaseCleaner):
    """Removes emojis and unusual symbols."""

    def clean(self, text: str) -> str:
        base = super().clean(text)
        return re.sub(r"[^\w\s,.!?-ğüşöçıİĞÜŞÖÇ]", "", base)


class StopwordCleaner(BaseCleaner):
    """Removes extremely common meaningless words."""

    STOPWORDS = {"and", "or", "the", "a", "to", "for", "with"}

    def clean(self, text: str) -> str:
        base = super().clean(text)
        words = [w for w in base.split() if w.lower() not in self.STOPWORDS]
        return " ".join(words)


# -------------------------------------------------------
# 4. MongoDB Manager (Enhanced Version)
# -------------------------------------------------------
class MongoDBManager(IDatabase):
    """Handles all DB logic with robustness."""

    def __init__(self, uri=None, db=None, collection=None):
        # Use environment variables if parameters are not provided
        self.uri = uri or MONGODB_URI
        self.db_name = db or MONGODB_DB
        self.collection_name = collection or MONGODB_COLLECTION
        
        logging.info(f"Connecting to MongoDB: {self.uri}/{self.db_name}/{self.collection_name}")

        # cleaners
        self.html_cleaner = HTMLCleaner()
        self.emoji_cleaner = EmojiCleaner()
        self.stopword_cleaner = StopwordCleaner()

        self.collection = self._connect_with_retry()

    # ----------------------- DB CONNECTION ----------------------- #
    def _connect_with_retry(self):
        """Retry DB connection 3 times for robustness."""
        for attempt in range(3):
            try:
                client = MongoClient(self.uri, serverSelectionTimeoutMS=1000)
                client.server_info()
                logging.info("Connected to MongoDB successfully.")
                return client[self.db_name][self.collection_name]
            except errors.ServerSelectionTimeoutError:
                logging.warning(f"MongoDB connection failed. Retrying ({attempt + 1}/3)...")
                time.sleep(1)

        logging.error("Could not connect to MongoDB after 3 attempts.")
        raise ConnectionError("MongoDB is unreachable.")

    # ----------------------- CLEAN POSTING ----------------------- #
    def _clean_posting(self, posting: dict) -> JobPosting:
        """Cleans and returns JobPosting object using multiple cleaners."""
        return JobPosting(
            job_title=self.stopword_cleaner.clean(
                self.html_cleaner.clean(posting.get("job_title", ""))
            ),
            company_name=self.html_cleaner.clean(posting.get("company_name", "")),
            summary_description=self.emoji_cleaner.clean(posting.get("summary_description", "")),
            ad_link=posting.get("ad_link", "")
        )

    # ----------------------- CHECK DUPLICATE ----------------------- #
    def _exists(self, url: str) -> bool:
        return self.collection.count_documents({"ad_link": url}, limit=1) > 0

    # ----------------------- SAVE POSTINGS ----------------------- #
    def save_postings(self, postings: list[dict]):
        """
        Cleans and inserts unique job postings into MongoDB.
        Returns the list of newly added documents.
        """
        cleaned_docs = []

        for p in postings:
            job = self._clean_posting(p)

            if not self._exists(job.ad_link):
                cleaned_docs.append(job.__dict__)
            else:
                logging.info(f"Duplicate skipped: {job.ad_link}")

        if cleaned_docs:
            self.collection.insert_many(cleaned_docs)
            logging.info(f"Inserted {len(cleaned_docs)} new job postings.")

        return cleaned_docs
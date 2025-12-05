import matplotlib.pyplot as plt
from database import MongoDBManager, HTMLCleaner, EmojiCleaner, StopwordCleaner
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
class MongoDBManagerWithCleaning(MongoDBManager):
    """Extends MongoDBManager to include data cleaning before saving."""

    def __init__(self, uri="mongodb://localhost:27017", db="jobs", collection="ads"):
        super().__init__(uri, db, collection)
        self.html_cleaner = HTMLCleaner()
        self.emoji_cleaner = EmojiCleaner()
        self.stopword_cleaner = StopwordCleaner()

    def clean_posting(self, posting: dict) -> dict:
        """Cleans the fields of a job posting."""
        posting['job_title'] = self.stopword_cleaner.clean(
            self.emoji_cleaner.clean(
                self.html_cleaner.clean(posting.get('job_title', ''))
            )
        )
        posting['company_name'] = self.stopword_cleaner.clean(
            self.emoji_cleaner.clean(
                self.html_cleaner.clean(posting.get('company_name', ''))
            )
        )
        posting['summary_description'] = self.stopword_cleaner.clean(
            self.emoji_cleaner.clean(
                self.html_cleaner.clean(posting.get('summary_description', ''))
            )
        )
        return posting

    def save_postings(self, postings: list[dict]):
        """Cleans and saves multiple postings into the database."""
        cleaned_postings = [self.clean_posting(posting) for posting in postings]
        super().save_postings(cleaned_postings)

def plot_skill_distribution(skill_counts: dict):
    """Plots a bar chart of skill distribution."""
    skills = list(skill_counts.keys())
    counts = list(skill_counts.values())

    plt.figure(figsize=(10, 6))
    plt.bar(skills, counts, color='skyblue')
    plt.xlabel('Skills')
    plt.ylabel('Counts')
    plt.title('Skill Distribution in Job Postings')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


import matplotlib.pyplot as plt
from database import MongoDBManager, HTMLCleaner, EmojiCleaner, StopwordCleaner, IDatabase, MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION
import re
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class MongoDBManagerWithCleaning(MongoDBManager):
    """Extends MongoDBManager to include data cleaning before saving."""

    def __init__(self, uri=None, db=None, collection=None):
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


def print_postings(postings: list[dict], title: str = "Job Postings"):
    """Prints postings in a readable format."""
    print(f"\n{'='*80}")
    print(f"{title.upper()}")
    print(f"{'='*80}\n")
    
    for i, posting in enumerate(postings, 1):
        print(f" Posting #{i}")
        print(f"   Job Title: {posting.get('job_title', 'N/A')}")
        print(f"   Company: {posting.get('company_name', 'N/A')}")
        print(f"   Description: {posting.get('summary_description', 'N/A')[:100]}...")
        print(f"   Link: {posting.get('ad_link', 'N/A')}")
        print(f"   {'-'*76}\n")


def main():
    """Main entry point for the application."""
    logging.info("Starting Job Scraper Application...")
    logging.info(f"MongoDB Config - URI: {MONGODB_URI}, DB: {MONGODB_DB}, Collection: {MONGODB_COLLECTION}")
    
    # Initialize the database manager with cleaning (try MongoDB, fallback to in-memory)
    try:
        db_manager = MongoDBManagerWithCleaning()
    except Exception as e:
        logging.warning(f"MongoDB unavailable, using in-memory DB fallback: {e}")

        class InMemoryDBManager:
            """Simple in-memory DB replacement used when MongoDB is unreachable."""

            def __init__(self):
                self.html_cleaner = HTMLCleaner()
                self.emoji_cleaner = EmojiCleaner()
                self.stopword_cleaner = StopwordCleaner()
                self._store: list[dict] = []

            def clean_posting(self, posting: dict) -> dict:
                p = posting.copy()
                p['job_title'] = self.stopword_cleaner.clean(
                    self.emoji_cleaner.clean(
                        self.html_cleaner.clean(p.get('job_title', ''))
                    )
                )
                p['company_name'] = self.stopword_cleaner.clean(
                    self.emoji_cleaner.clean(
                        self.html_cleaner.clean(p.get('company_name', ''))
                    )
                )
                p['summary_description'] = self.stopword_cleaner.clean(
                    self.emoji_cleaner.clean(
                        self.html_cleaner.clean(p.get('summary_description', ''))
                    )
                )
                return p

            def save_postings(self, postings: list[dict]):
                cleaned = [self.clean_posting(p) for p in postings]
                existing = {p.get('ad_link') for p in self._store}
                new = [p for p in cleaned if p.get('ad_link') not in existing]
                self._store.extend(new)
                logging.info(f"(InMemory) Inserted {len(new)} postings.")
                return new

            def find_all_postings(self):
                return list(self._store)

        db_manager = InMemoryDBManager()
    
    # Sample job postings for demonstration
    sample_postings = [
        {
            'job_title': '<p>Python Developer 🔥</p>',
            'company_name': 'Tech Corp &amp; Co.',
            'summary_description': 'Looking for and experienced Python and developer with skills in web development',
            'ad_link': 'https://example.com/job/1'
        },
        {
            'job_title': 'Senior Java Developer',
            'company_name': 'Innovation Labs 🚀',
            'summary_description': 'Java expert wanted for backend development with Spring Boot experience',
            'ad_link': 'https://example.com/job/2'
        },
        {
            'job_title': 'Full Stack Developer',
            'company_name': 'Digital Solutions',
            'summary_description': 'Full stack developer needed with React and Node.js expertise',
            'ad_link': 'https://example.com/job/3'
        }
    ]
    
    print_postings(sample_postings, "Original Postings")
    
    # Clean and save postings
    try:
        db_manager.save_postings(sample_postings)
        logging.info(f"Successfully saved {len(sample_postings)} postings to database.")
    except Exception as e:
        logging.error(f"Error saving postings: {e}")
        print(f"\n⚠️  Could not connect to MongoDB: {e}")
        print("   Displaying cleaned data in memory instead:\n")
        
        # Display cleaned postings even if DB connection fails
        cleaned_postings = [db_manager.clean_posting(p) for p in sample_postings]
        print_postings(cleaned_postings, "Cleaned Postings (In Memory)")
        return
    
    # Retrieve and display postings
    try:
        postings = db_manager.find_all_postings()
        if postings:
            print_postings(postings, "Cleaned Postings from Database")
            logging.info(f"Retrieved {len(postings)} postings from database.")
        else:
            logging.warning("No postings found in database.")
    except Exception as e:
        logging.error(f"Error retrieving postings: {e}")
        postings = []
    
    logging.info("Job Scraper Application finished.")
    
    # A simple counting logic to plot the graph
    if not postings:
        postings = []
    
    all_text = " ".join([p.get('summary_description', '') + " " + p.get('job_title', '') for p in postings])
    
    # Sample skill set
    # If data exists, draw the graph
    target_skills = ["Python", "Java", "React", "Node.js", "Spring"]
    skill_counts = {skill: all_text.count(skill) for skill in target_skills}
    
    if any(skill_counts.values()):
        logging.info("Grafik oluşturuluyor...")
        plot_skill_distribution(skill_counts)

    logging.info("Job Scraper Application finished.")


if __name__ == "__main__":
    main()

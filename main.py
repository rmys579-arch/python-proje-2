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


def print_postings(postings: list[dict], title: str = "Job Postings"):
    """Prints postings in a readable format."""
    print(f"\n{'='*80}")
    print(f"{title.upper()}")
    print(f"{'='*80}\n")
    
    for i, posting in enumerate(postings, 1):
        print(f"📋 Posting #{i}")
        print(f"   Job Title: {posting.get('job_title', 'N/A')}")
        print(f"   Company: {posting.get('company_name', 'N/A')}")
        desc = posting.get('summary_description', 'N/A')
        if len(desc) > 100:
            desc = desc[:100] + "..."
        print(f"   Description: {desc}")
        print(f"   Link: {posting.get('ad_link', 'N/A')}")
        print(f"   {'-'*76}\n")


def create_sample_cleaner():
    """Creates a simple cleaner instance without database connection."""
    cleaner = type('SimpleCleaner', (), {
        'html_cleaner': HTMLCleaner(),
        'emoji_cleaner': EmojiCleaner(),
        'stopword_cleaner': StopwordCleaner(),
        'clean_posting': MongoDBManagerWithCleaning.clean_posting
    })()
    return cleaner


def main():
    """Main entry point for the application."""
    logging.info("Starting Job Scraper Application...")
    
    # Sample job postings for demonstration
    sample_postings = [
        {
            'job_title': '<p>Python Developer 🔥</p>',
            'company_name': 'Tech Corp &amp; Co.',
            'summary_description': 'Looking for an experienced Python developer with skills in web development and REST APIs',
            'ad_link': 'https://example.com/job/1'
        },
        {
            'job_title': 'Senior Java Developer',
            'company_name': 'Innovation Labs 🚀',
            'summary_description': 'Java expert wanted for backend development with Spring Boot experience and microservices',
            'ad_link': 'https://example.com/job/2'
        },
        {
            'job_title': 'Full Stack Developer',
            'company_name': 'Digital Solutions',
            'summary_description': 'Full stack developer needed with React and Node.js expertise for frontend and backend',
            'ad_link': 'https://example.com/job/3'
        }
    ]
    
    print_postings(sample_postings, "Original Postings (Uncleaned)")
    
    # Try to connect to database
    db_manager = None
    database_connected = False
    
    try:
        print("🔌 Attempting to connect to MongoDB...")
        db_manager = MongoDBManagerWithCleaning(
            uri="mongodb://localhost:27017",
            db="jobs",
            collection="ads"
        )
        database_connected = True
        
    except Exception as e:
        logging.warning(f"MongoDB not available: {type(e).__name__}")
        print(f"\n⚠️  Could not connect to MongoDB - running in offline mode")
        print(f"   Error: {e}\n")
    
    if database_connected and db_manager:
        try:
            # Clean and save postings
            db_manager.save_postings(sample_postings)
            logging.info(f"Successfully saved {len(sample_postings)} postings to database.")
            
            # Retrieve and display postings
            postings = db_manager.find_all_postings()
            if postings:
                print_postings(postings, "Cleaned Postings from Database")
                logging.info(f"Retrieved {len(postings)} postings from database.")
            else:
                logging.warning("No postings found in database.")
        except Exception as e:
            logging.error(f"Error during database operations: {e}")
    else:
        # Offline mode: display cleaned postings in memory
        print("💾 Processing data in memory (offline mode)...\n")
        cleaner = create_sample_cleaner()
        cleaned_postings = [cleaner.clean_posting(p.copy()) for p in sample_postings]
        print_postings(cleaned_postings, "Cleaned Postings (In Memory - No Database)")
    
    logging.info("✅ Job Scraper Application finished successfully.")


if __name__ == "__main__":
    main()

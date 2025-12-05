from dataclasses import dataclass
from abc import ABC, abstractmethod
from pymongo import MongoClient
import re
import logging

# -------------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------------------------------------------
# 1. Dataclass: Skill Keyword
# -------------------------------------------------------
@dataclass
class SkillKeyword:
    name: str
    synonyms: list[str]
    category: str  # "technical" or "soft"


# -------------------------------------------------------
# 2. Abstract Analyzer Interface
# -------------------------------------------------------
class ISkillAnalyzer(ABC):
    @abstractmethod
    def count_skills(self) -> dict:
        pass


# -------------------------------------------------------
# 3. Cleaner System (Inheritance)
# -------------------------------------------------------
class BaseCleaner:
    def clean(self, text: str) -> str:
        return text.lower().strip()


class SymbolCleaner(BaseCleaner):
    """Removes non-important symbols."""

    def clean(self, text: str) -> str:
        base = super().clean(text)
        return re.sub(r"[^a-zA-Z0-9ğüşöçıİĞÜŞÖÇ\s-]", " ", base)


# -------------------------------------------------------
# 4. Analyzer Class (FULL VERSION)
# -------------------------------------------------------
class Analyzer(ISkillAnalyzer):
    """Pulls job postings from MongoDB and performs keyword analysis."""

    def __init__(self, uri="mongodb://localhost:27017", db="jobs", collection="ads"):
        self.client = MongoClient(uri)
        self.collection = self.client[db][collection]
        self.cleaner = SymbolCleaner()

        # Extended keywords
        self.keywords: list[SkillKeyword] = [
            SkillKeyword("python", ["python3", "py"], "technical"),
            SkillKeyword("sql", ["postgres", "mysql"], "technical"),
            SkillKeyword("javascript", ["js", "node"], "technical"),
            SkillKeyword("docker", ["containers"], "technical"),
            SkillKeyword("communication", ["teamwork", "iletişim"], "soft"),
            SkillKeyword("problem solving", ["critical thinking"], "soft"),
        ]

    # ----------------------- TEXT COMBINATION ----------------------- #
    def _combine_text(self, job: dict) -> str:
        """Merge all text fields into a single searchable block."""
        full_text = (
            f"{job.get('job_title', '')} "
            f"{job.get('company_name', '')} "
            f"{job.get('summary_description', '')}"
        )
        return self.cleaner.clean(full_text)

    # ----------------------- REGEX MATCH ----------------------- #
    def _match_keyword(self, text: str, keyword: str) -> bool:
        """Regex match with word boundary for precise detection."""
        pattern = rf"\b{re.escape(keyword)}\b"
        return re.search(pattern, text) is not None

    # ----------------------- SKILL COUNT ----------------------- #
    def count_skills(self) -> dict:
        """
        Returns dictionary:
        {
            'python': 12,
            'sql': 5,
            'category_counts': {'technical': 15, 'soft': 7}
        }
        """
        results = {k.name: 0 for k in self.keywords}
        category_results = {"technical": 0, "soft": 0}

        postings = self.collection.find()

        for job in postings:
            text = self._combine_text(job)

            for kw in self.keywords:
                matched = False

                # Main keyword
                if self._match_keyword(text, kw.name):
                    matched = True

                # Synonyms
                if any(self._match_keyword(text, syn) for syn in kw.synonyms):
                    matched = True

                if matched:
                    results[kw.name] += 1
                    category_results[kw.category] += 1

        results["category_counts"] = category_results
        return results
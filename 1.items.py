# With this file we define the structure of the data we will retrieve.
# The site will be kariyer.net and we will get the job title, company name, short description and job link information for the sought-after Python developer.
import scrapy #We import this library to retrieve the desired data from the #website.

class JobAdItem(scrapy.Item):
    """
    This is my Item definition. It's the data structure I use to deliver the data I've extracted to the next person (the Data Architect). It's like a structured Python dictionary.
    """
    job_title = scrapy.Field()          # Will hold the title of the job posting.
    company_name = scrapy.Field()       # Will keep the name of the company that published the ad.
    summary_description = scrapy.Field()# Will keep a brief summary of the job description.
    ad_link = scrapy.Field()            # Link to check for duplicate postings.# 1. Project Setup Variables
SEARCH_KEYWORD = "Python-Developer" 
# I'm setting the search keyword here. We chose Python Developer to start.
# I'm creating the starting URL for Kariyer.net. The bot will start from this page.
START_URL = f"https://www.kariyer.net/is-ilanlari/{SEARCH_KEYWORD}-is-ilanlari"

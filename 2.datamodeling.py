
import scrapy
# Scrapy wants the data in a separate file
# # We import the Item class that I defined in the 'items.py' file.
from items import JobAdItem 

START_URL = 'https://www.kariyer.net/is-ilanlari'

class KariyerSpider(scrapy.Spider):
    # This is the name of our bot. I'll use this name to run the bot.
    name = 'my_first_kariyer_scraper'
    # List of URLs that Scrapy should start from. A single starting URL is sufficient.
    start_urls = [START_URL]
    # Main Function 2: What to Do When a Page Loads?
    # This 'parse' method is called when Scrapy successfully downloads a page.
    # The 'response' object contains the entire HTML content of the page. 
   
    def parse(self, response):
        
       # First, I need to tell the bot where all the job postings on the page are located.
       # I'm using a CSS Selector to find all the main containers (divs) that hold the posting details.
       # NOTE: We need to make sure this selector is correct for Kariyer.net's current design!
        JOB_CARD_SELECTOR = 'div.list-items > div' 
        
        for job_card in response.css(JOB_CARD_SELECTOR):
            
            # Her bir ilan için, verilerini depolamak üzere yeni bir 'JobAdItem' oluşturuyorum.
            item = JobAdItem()
            # Now I loop over each job posting element I find on the page, one by one.
            # Data Extraction Section
            # 1. Finding the Job Title and Link
            # The title and link are usually found together within an <a> tag.
            
            title_element = job_card.css('div.job-card-head > a')
            # I take the text inside the <a> tag as the title. (I make error handling easier with default=""
            item['job_title'] = title_element.css('::text').get(default='').strip()
            # I am pulling the 'href' attribute to get the unique link.
            link = title_element.attrib.get('href', '')
            item['ad_link'] = response.urljoin(link) # response.urljoin, linki tam (mutlak) URL yapar.
            # 2. Finding the Company Name
            # The company name is usually in a paragraph (<p>) tag near the title.
            
            company_text = job_card.css('div.job-card-head > p::text').get(default='')
            item['company_name'] = company_text.strip()
            # 3. Finding the Summary Description
            # I'm capturing the short description text that appears on the ad card.
            
            description_text = job_card.css('div.job-card-body > div.job-card-desc::text').get(default='')
            item['summary_description'] = description_text.strip()
            # I 'yield' the collected Item. This sends the clean data to Scrapy's
            # output pipeline (which is the data the second person will receive).
            
            yield item
            # 3. Pagination Logic: Finding the Next Page
            # After processing all the ads, I need to find the link to the next page.
            # I'm using CSS Selector to find the 'Next' button/link.
        NEXT_PAGE_SELECTOR = 'div.pagination a.next::attr(href)' 
        next_page_url = response.css(NEXT_PAGE_SELECTOR).get()
                # If the link actually exists, it means we haven't reached the last page!

        if next_page_url is not None:
            # I'm telling Scrapy to visit this new URL.
            # I'm also asking it to call this 'parse' method for the new page.
            # This will automatically continue the bot until it finds the last link.
            yield response.follow(next_page_url, callback=self.parse)
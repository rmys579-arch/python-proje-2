Job Posting and Talent Analysis Bot This project is a data engineering project that automatically scans ads from the job search site kariyer.net, cleans the data and stores it in the database and analyzes and visualizes the most sought-after competencies in the sector (Python, SQL, Communication, etc.).
🚀 About the Project It can be difficult to understand which talents are more valuable in the technology world. Thanks to this project, instead of reading hundreds of ads manually;
We automatically collect lans (Data Scraping).

We clean and configure the data (Data Cleaning).

We prove with data which hard skills and soft skills are more popular (Data Analysis).
✨ Key Features Automatic Data Acquisition: Pulls data from dynamic websites with Selenium.

Smart Database Management: Blocks Duplicate ads with link control, only saves new ads.

Advanced Data Cleaning: Cleans up HTML tags, unnecessary spaces, and broken characters.

Category Talent Analysis: Counts the talents we determine in the advertisement texts separately.

Visual Reporting: Pours results into understandable charts using Matplotlib

🛠️ Installation and Running To run the project on your computer, follow the steps below:

1.Download the Project:

Git clone https://github.com/kullaniciadi/is-ilani-analizi.git cd is-ilani-analizi

2.Install Required Libraries:

Pip install -r requirements.txt (If you do not have a requirements.txt file manually: pip install selenium matplotlib)

3.WebDriver Setting:

Download the chromedrive suitable for the version of Chrome on your computer and throw it in the project folder.

4.Run:

Python main.py 📂 Project Architecture (Modules) The project is divided into 3 main modules according to the Separation of Concerns principle:

Plaintext ├── scraper.py # [Module 1] The bot that pulls raw data from the web (Data Collection). ├── database.py # [Module 2] Data cleaning, deduplication and SQLite operations. ├── main.py # [Module 3] Analysis logic, visualization and main stream. ├── is_ilanlari.db # [Out] Database where data is stored permanently. └── README.md # Project documentation. 📊 Case Scenario When the program runs, a flow similar to this occurs on the console:
Plaintext

The bot is starting... 
[SCRAPER] 50 ads were successfully withdrawn.
[DATABASE] Cleaning is being done... 
[DATABASE] Report: 15 new ads added to the database. (35 ads already existed, skipped.) 
[ANALYSIS] Processing data... 
[RESULT] Top searched skill: Python (28 Ads)
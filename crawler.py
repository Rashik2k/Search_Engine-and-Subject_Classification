from urllib.parse import urljoin
import time
import json
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from selenium_setup import setup_selenium


class Crawler:
    """
    A web crawler to scrape publication data from a university portal.
    """

    def __init__(self, base_url, crawl_delay=2, data_file="publications.json"):
        """
        Initialize the crawler with base URL, crawl delay, and data storage file.

        :param base_url: The base URL of the website to be crawled.
        :param crawl_delay: Time delay (in seconds) between requests to prevent overwhelming the server.
        :param data_file: Name of the file where crawled data will be stored.
        """
        self.base_url = base_url  # Store the base URL of the website
        self.crawl_delay = crawl_delay  # Set the delay between requests
        self.data_file = data_file  # Define the output file for storing scraped data
        self.publications = []  # List to store scraped publication data
        self.robot_parser = RobotFileParser()  # Initialize a robots.txt parser

    def _check_robots_txt(self):
        """
        Check the website's robots.txt file to determine crawling permissions and crawl delay.
        """
        driver = setup_selenium()
        
        # Open the robots.txt file
        driver.get(urljoin(self.base_url, "/robots.txt"))

        # Wait for any potential Cloudflare challenge or page load
        time.sleep(10) 
        
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        robots_txt_content = soup.get_text()

        # Process each line of robots.txt
        for line in robots_txt_content.splitlines():
            line = line.strip()
            if line.lower().startswith("crawl-delay:"):
                crawl_delay = int(line[len("crawl-delay:"):].strip())

        # Update the crawl delay if specified in robots.txt
        if crawl_delay is not None:
            self.crawl_delay = max(self.crawl_delay, crawl_delay)

        print(f"Crawl delay set to: {self.crawl_delay} seconds")


    def crawl_publications(self):
        """
        Crawl the website to extract publication data for authors.
        """
        print("Starting crawl...")
        self._check_robots_txt()  # Ensure that crawling is allowed

        driver = setup_selenium()  # Initialize Selenium WebDriver

        author_info = []  # List to store author details
        page = 0  # Start from the first page
        page_limit = 2  # Define the number of pages to scrape

        # Loop through multiple pages to gather author information
        while page < page_limit:
            driver.get(f"https://pureportal.coventry.ac.uk/en/organisations/fbl-school-of-economics-finance-and-accounting/persons/?page={page}")
            time.sleep(10)  # Wait for page to load

            # Parse the page content
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Extract author names and profile links
            for author in soup.find_all("h3", class_="title"):
                author_name = author.get_text(strip=True)
                author_link = author.find("a", class_="link person")["href"]
                author_info.append({"name": author_name, "link": urljoin("https://pureportal.coventry.ac.uk", author_link)})
            
            page += 1  # Move to the next page

        # Loop through each author's page to extract their publications
        for author in author_info:
            author_url = author['link'] + "/publications"  # Construct publication URL
            driver.get(author_url)
    
            time.sleep(10)  # Allow page to load

            soup = BeautifulSoup(driver.page_source, "html.parser")
    
            # Loop through each publication entry
            for pub_item in soup.find_all("li", class_="list-result-item"):
                pub_title = pub_item.find("h3", class_="title").get_text(strip=True)  # Extract publication title
                
                # Extract authors (a publication may have multiple authors)
                authors = []
                author_details = pub_item.find_all("a", class_="link person")
                for author in author_details:
                    author_name = author.get_text(strip=True)
                    author_profile = author['href']
                    authors.append({'name': author_name, 'link': author_profile})
                
                # Extract publication year
                pub_year = None
                year_element = pub_item.find("div", class_="search-result-group")
                if year_element:
                    pub_year = year_element.get_text(strip=True)

                # If no publication year is found, assume no publications and move to the next author
                if pub_year is None:
                    continue
                
                # Extract journal name and volume if available
                journal_info = pub_item.find("span", class_="journal")
                journal_name = journal_info.get_text(strip=True) if journal_info else None
                volume_info = pub_item.find("span", class_="volume")
                volume = volume_info.get_text(strip=True) if volume_info else None
                
                # Extract publication link
                pub_link = pub_item.find("a", class_="link")["href"]
                
                # Create a dictionary for the publication data
                publication_data = {
                    "title": pub_title,
                    "authors": authors,
                    "publication_year": pub_year,
                    "journal": journal_name,
                    "volume": volume,
                    "link": urljoin("https://pureportal.coventry.ac.uk", pub_link),
                }

                # Store the extracted publication data
                self.publications.append(publication_data)
                
        # Save the collected data to a file
        self.save_data()

    def save_data(self):
        """
        Save the scraped publication data to a JSON file.
        """
        with open(self.data_file, "w") as f:
            json.dump(self.publications, f, indent=4)  # Save data in a structured JSON format
        print(f"Crawled {len(self.publications)} publications. Data saved to {self.data_file}.")

    def load_data(self):
        """
        Load existing publication data from the JSON file.
        """
        try:
            with open(self.data_file, "r") as f:
                self.publications = json.load(f)  # Load data from file
        except FileNotFoundError:
            print("No existing data found. Please run the crawler first.")  # Notify user if data is missing

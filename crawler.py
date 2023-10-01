import configparser
import requests
import xml.etree.ElementTree as ET
import asyncio
import logging
import random

class Crawler:
    # Initialize the Crawler
    def __init__(self):
        # Read configuration from config.ini
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Initialize variables based on the configuration
        self.sitemap_url = self.config.get('Sitemap', 'url')
        self.crawling_rate = int(self.config.get('Crawler', 'crawling_rate'))
        self.desktop_agents = self.config.get('UserAgents', 'desktop_agents').split('|')
        self.mobile_agents = self.config.get('UserAgents', 'mobile_agents').split('|')
        
        # Initialize index for user agents and read the mode from the config
        self.user_agent_index = 0
        self.user_agent_mode = int(self.config.get('Crawler', 'user_agent_mode').split(';')[0].strip())
        self.user_agent_type = self.config.get('Crawler', 'user_agent').split(';')[0].strip()
        
        # Choose user agents based on the type
        if self.user_agent_type == "desktop":
            self.all_user_agents = self.desktop_agents
        elif self.user_agent_type == "mobile":
            self.all_user_agents = self.mobile_agents
        else:  # "desktop and mobile"
            self.all_user_agents = self.desktop_agents + self.mobile_agents

    # Main function to start the crawler
    def start(self):
        try:
            # Start the recursive crawl with the initial sitemap URL
            self.crawl_sitemaps_recursively(self.sitemap_url)
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")

    # Function to crawl sitemaps recursively
    def crawl_sitemaps_recursively(self, sitemap_url):
        # Read the sitemap
        sitemap_xml = self.read_sitemap(sitemap_url)
        
        # Check if it's a sitemap index (contains other sitemaps)
        if self.is_sitemap_index(sitemap_xml):
            # Get the list of sitemaps
            sitemaps = self.get_sitemaps(sitemap_xml)
            # Crawl each contained sitemap
            for sitemap in sitemaps:
                self.crawl_sitemaps_recursively(sitemap)
        else:
            # It's a regular sitemap, crawl it
            self.crawl_sitemap(sitemap_url)

    # Function to read a sitemap from a URL
    def read_sitemap(self, url):
        response = requests.get(url)
        return response.content

    # Check if the XML content is a sitemap index
    def is_sitemap_index(self, sitemap_xml):
        root = ET.fromstring(sitemap_xml)
        return root.tag.endswith('sitemapindex')

    # Extract sitemap URLs from a sitemap index
    def get_sitemaps(self, sitemap_xml):
        return self.get_urls_from_sitemap(sitemap_xml)

    # Function to crawl a single sitemap
    def crawl_sitemap(self, sitemap_url):
        # Read the sitemap
        sitemap_xml = self.read_sitemap(sitemap_url)
        # Extract URLs from the sitemap
        urls = self.get_urls_from_sitemap(sitemap_xml)
        # Create an async event loop
        loop = asyncio.get_event_loop()
        # Create tasks to crawl each URL
        tasks = [self.crawl_url(url) for url in urls]
        # Run the tasks
        loop.run_until_complete(asyncio.gather(*tasks))

    # Asynchronous function to crawl a single URL
    async def crawl_url(self, url):
        try:
            headers = {'User-Agent': self.get_random_user_agent()}
            await asyncio.sleep(1 / self.crawling_rate)
            response = requests.get(url, headers=headers, allow_redirects=False)
            logging.info(f"Crawled URL: {url}, Status Code: {response.status_code}")
        except requests.exceptions.TooManyRedirects:
            logging.error(f"Too many redirects for URL: {url}")


    # Extract URLs from a sitemap
    def get_urls_from_sitemap(self, sitemap_xml):
        root = ET.fromstring(sitemap_xml)
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = []
        for child in root:
            try:
                loc_element = child.find('sitemap:loc', namespaces=namespace)
                if loc_element is not None:
                    urls.append(loc_element.text)
            except Exception as e:
                logging.error(f"Error occurred while parsing sitemap: {str(e)}")
        return urls

    # Get a user agent based on the mode
    def get_random_user_agent(self):
        if self.user_agent_mode == 1:
            # Sequential mode
            user_agent = self.all_user_agents[self.user_agent_index]
            
            # Increment the index for the next call
            self.user_agent_index = (self.user_agent_index + 1) % len(self.all_user_agents)
        else:
            # Random mode
            user_agent = random.choice(self.all_user_agents)
        
        return user_agent

    # Get a user agent based on the mode
    def get_random_user_agent(self):
        if self.user_agent_mode == 1:
            # Sequential mode
            user_agent = self.all_user_agents[self.user_agent_index]
            
            # Increment the index for the next call
            self.user_agent_index = (self.user_agent_index + 1) % len(self.all_user_agents)
        else:
            # Random mode
            user_agent = random.choice(self.all_user_agents)
        
        return user_agent

# Initialize and start the Crawler
if __name__ == "__main__":
    crawler = Crawler()
    crawler.start()

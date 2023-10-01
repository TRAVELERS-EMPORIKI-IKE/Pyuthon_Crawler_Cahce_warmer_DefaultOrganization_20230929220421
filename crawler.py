'''
This file contains the Crawler class responsible for crawling the sitemaps and warming up the website cache.
'''
import configparser
import requests
import xml.etree.ElementTree as ET
import asyncio
import logging
import random
class Crawler:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.sitemap_url = self.config.get('Sitemap', 'url')
        self.crawling_rate = int(self.config.get('Crawler', 'crawling_rate'))
        self.desktop_agents = self.config.get('UserAgents', 'desktop_agents').split('|')
        self.mobile_agents = self.config.get('UserAgents', 'mobile_agents').split('|')

    def start(self):
        while True:
            try:
                # Read the sitemap XML
                sitemap_xml = self.read_sitemap(self.sitemap_url)
                # Check if it is a sitemap index file
                if self.is_sitemap_index(sitemap_xml):
                    # Get the sitemaps within the sitemap index
                    sitemaps = self.get_sitemaps(sitemap_xml)
                    # Crawl each sitemap
                    for sitemap in sitemaps:
                        self.crawl_sitemap(sitemap)
                else:
                    # Crawl the single sitemap
                    self.crawl_sitemap(self.sitemap_url)
            except Exception as e:
                logging.error(f"Error occurred: {str(e)}")
    def read_sitemap(self, url):
        response = requests.get(url)
        return response.content
    def is_sitemap_index(self, sitemap_xml):
        root = ET.fromstring(sitemap_xml)
        return root.tag == 'sitemapindex'
    def get_sitemaps(self, sitemap_xml):
        root = ET.fromstring(sitemap_xml)
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        sitemaps = []
        for child in root:
            try:
                loc_element = child.find('sitemap:loc', namespaces=namespace)
                if loc_element is not None:
                    sitemaps.append(loc_element.text)
                else:
                    logging.warning(f"No 'loc' element found in {ET.tostring(child).decode()}")
            except Exception as e:
                logging.error(f"Error occurred while parsing sitemap: {str(e)}")
        return sitemaps
    def crawl_sitemap(self, sitemap_url):
        sitemap_xml = self.read_sitemap(sitemap_url)
        urls = self.get_urls_from_sitemap(sitemap_xml)
        # Asynchronously crawl the URLs
        loop = asyncio.get_event_loop()
        tasks = [self.crawl_url(url) for url in urls]
        loop.run_until_complete(asyncio.gather(*tasks))
    async def crawl_url(self, url):
        # Simulate crawling by making a request to the URL
        headers = {'User-Agent': self.get_random_user_agent()}
        await asyncio.sleep(1 / self.crawling_rate)
        response = requests.get(url, headers=headers)
        logging.info(f"Crawled URL: {url}, Status Code: {response.status_code}")
        print(f"Crawled URL: {url}, Status Code: {response.status_code}")
    def get_urls_from_sitemap(self, sitemap_xml):
        root = ET.fromstring(sitemap_xml)
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = []
        for child in root:
            try:
                loc_element = child.find('sitemap:loc', namespaces=namespace)
                if loc_element is not None:
                    urls.append(loc_element.text)
                else:
                    logging.warning(f"No 'loc' element found in {ET.tostring(child).decode()}")
            except Exception as e:
                logging.error(f"Error occurred while parsing sitemap: {str(e)}")
        return urls
    def get_random_user_agent(self):
        # Choose a random user agent from the available agents
        user_agents = self.desktop_agents + self.mobile_agents
        return random.choice(user_agents)
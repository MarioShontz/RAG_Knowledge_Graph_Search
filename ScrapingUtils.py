import configparser
from urllib.parse import urlparse, urljoin

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector


class ScrapingUtils:
    class FsuSpider(scrapy.Spider):
        name = "fsu_spider"
        def __init__(self, start_url, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.start_urls = [start_url]

        def parse(self, response):
            # Extract all links, metadata, and text
            links = response.css('a::attr(href)').getall()
            metadata = response.xpath('//meta').getall()
            text = response.xpath("//body//text()").getall()

            # Placeholder for user-defined logic with scraped data
            self.logic_on_scrape(response.url, links, metadata, text)

            # For crawling all pages within the domain
            for link in links:
                absolute_url = urljoin(response.url, link)
                yield response.follow(absolute_url, callback=self.parse)

        def logic_on_scrape(self, url, links, metadata, text):
            # User-defined logic goes here
            pass

    def scrape_single_page(self, webpage_url):
        process = CrawlerProcess()
        process.crawl(self.FsuSpider, start_url=webpage_url)
        process.start()

    def scrape_domain(self, website_url):
        self.scrape_single_page(website_url)

    def scrape_sitemap(self, homepage_url):
        # This method would require additional logic to fetch and parse sitemap.xml,
        # and then use Scrapy requests to scrape each URL found in the sitemap.
        pass

    def scrape_with_fallback(self, homepage_url):
        # This method should attempt to scrape using sitemap first,
        # and if that fails, fallback to crawling the domain starting from the homepage.
        pass

    def read_and_filter_sites(filename):
        valid_sites = set()
        with open(filename, 'r') as site_list:
            for line in site_list:
                # Strip leading and trailing whitespace and ignore comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Remove all whitespace from the line
                line = ''.join(line.split())
                
                # Check if the line has a valid scheme (http or https)
                if urlparse(line).scheme:
                    valid_sites.add(line)

        return valid_sites

if __name__ == "__main__":
    # read config file and get domains filename
    config = configparser.ConfigParser()
    config.read('config.ini')
    domains = config['TESTING']['domain_list_file']

    utils = ScrapingUtils()
    #get list of domains
    sites = utils.read_and_filter_sites(domains)
    
    #Run scraper on each site
    utils.scrape_domain(domains)

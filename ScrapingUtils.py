import os
import configparser
from urllib.parse import urlparse, urljoin
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signals import spider_closed
from scrapy.utils.project import get_project_settings
import json

class ScrapingUtils:
    def __init__(self, config):
        self.config = config

    def create_spider_class(self):
        class Spider(scrapy.Spider):
            name = "spider"

            def __init__(self, start_url, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.start_urls = [start_url]  # Expect a single start URL
                self.data = {}  # Initialize data structure for accumulated data

            def parse(self, response):
                # Extract all links, metadata, and text
                links = response.css('a::attr(href)').getall()
                metadata = response.xpath('//meta').getall()
                text = response.xpath("//body//text()").getall()

                print(f"response url: {response.url}")
                # Accumulate scraped data
                self.data[response.url] = {
                    "links": links,
                    "metadata": metadata,
                    "text": text
                }

                # For crawling all pages within the domain
                for link in links:
                    absolute_url = response.urljoin(link)
                    if urlparse(absolute_url).netloc == urlparse(self.start_urls[0]).netloc:
                        print(f"following link: {absolute_url}")
                        yield response.follow(absolute_url, self.parse)
                    else:
                        print(f"skipping link: {absolute_url}, not within {self.start_urls[0]}")

            def closed(self, reason):
                # Write accumulated data to a JSON file upon spider closure
                with open("output.json", "w") as outfile:
                    json.dump(self.data, outfile, indent=4)
                print(reason)

            @classmethod
            def from_crawler(cls, crawler, *args, **kwargs):
                spider = super(Spider, cls).from_crawler(crawler, *args, **kwargs)
                crawler.signals.connect(spider.closed, signal=spider_closed)
                return spider

        return Spider

if __name__ == "__main__":
    # Simplified command line argument handling for clarity
    LEVEL = "--test"  # Placeholder for actual command line argument handling

    # Read config file and get settings
    config = configparser.ConfigParser()
    config.read('config.ini')
    config_level = "TESTING" if LEVEL == "--test" else "PRODUCTION"
    config = config[config_level]

    # Create Spider class and start crawling
    SU = ScrapingUtils(config)
    SpiderClass = SU.create_spider_class()

    # Set up crawling process with SpiderClass for a single domain
    process = CrawlerProcess(get_project_settings())
    process.crawl(SpiderClass, start_url="https://www.fsu.edu")
    process.start()

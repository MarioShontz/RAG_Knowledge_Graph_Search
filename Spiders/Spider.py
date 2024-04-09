from sys import argv
import configparser
import pathlib
from urllib.parse import urlparse
import json

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signals import spider_closed


class Spider(scrapy.Spider):
    name = "Spider"
    start_afresh = False

    def __init__(self, start_url):
        self.start_urls = [start_url]  # Expect a single start URL
        self.error_message = "Page scraping returned no content"
        self.outfile = f"{self.name}_output.json"
        if self.start_afresh:
            self.data = {}
        else:
            try:
                with open(self.outfile, "r") as infile:
                    self.data = json.load(infile)
            except FileNotFoundError:
                print(f"File {self.outfile} not found. Cannot progress without existing data. To start fresh, set replace_content to True.")
            except Exception as e:
                raise(f"An unexpected error occurred: {e}")

    def parse(self, response):
        # Save data mini example
        if response.url not in self.data:
            self.data[response.url] = {}
        self.data[response.url].update(
            {
                "title": response.css("title::text").get(),
            }
        )

        # Extract all links, metadata, and text
        links = response.css("a::attr(href)").getall()
        for link in links:
            absolute_url = response.urljoin(link)
            if urlparse(absolute_url).netloc == urlparse(self.start_urls[0]).netloc:
                yield response.follow(absolute_url, self.parse)

    def closed(self, reason):
        # Write accumulated data to a JSON file upon spider closure
        with open(self.outfile, "w") as outfile:
            json.dump(self.data, outfile, indent=4)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Spider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.closed, signal=spider_closed)
        return spider

    def run(self):
        if len(argv) < 2:
            LEVEL = "TESTING"
        elif argv[1] in ["--test", "--prod"]:
            LEVEL = "TESTING" if argv[1] == "--test" else "PRODUCTION"
        else:
            raise ValueError("Invalid argument. Use --test or --prod.")

        filepath = pathlib.Path(__file__).parent.resolve()
        # Read config file and get settings
        config = configparser.ConfigParser()
        config.read(f"{filepath}/config.ini")
        config = config[LEVEL]

        # Create Spider class and start crawling
        SpiderClass = self.__class__

        # Set up crawling process with SpiderClass for a single domain
        process = CrawlerProcess()
        process.crawl(SpiderClass, start_url=self.start_urls[0])
        process.start()


if __name__ == "__main__":
    spider = Spider("https://www.fsu.edu")
    spider.run()

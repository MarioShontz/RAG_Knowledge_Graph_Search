from sys import argv
import configparser
import requests
import pathlib
from urllib.parse import urlparse
import json
import time
import re

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signals import spider_closed


class Spider(scrapy.Spider):
    name = "Spider"
    start_afresh = False
    deny_patterns = [
        # File extensions (case-insensitive, match at the end)
        re.compile(r".*\.pdf\??.*$", re.IGNORECASE),
        re.compile(r".*\.docx\??.*$", re.IGNORECASE),
        re.compile(r".*\.xlsx\??.*$", re.IGNORECASE),
        re.compile(r".*\.pptx\??.*$", re.IGNORECASE),
        re.compile(r".*\.jpg\??.*$", re.IGNORECASE),
        re.compile(r".*\.jpeg\??.*$", re.IGNORECASE),
        re.compile(r".*\.png\??.*$", re.IGNORECASE),
        re.compile(r".*\.gif\??.*$", re.IGNORECASE),
        re.compile(r".*\.svg\??.*$", re.IGNORECASE),
        re.compile(r".*\.ico\??.*$", re.IGNORECASE),
        re.compile(r".*\.css\??.*$", re.IGNORECASE),
        re.compile(r".*\.js\??.*$", re.IGNORECASE),
        re.compile(r".*\.zip\??.*$", re.IGNORECASE),
        re.compile(r".*\.xml\??.*$", re.IGNORECASE),
        re.compile(r".*\.json\??.*$", re.IGNORECASE),
        re.compile(r".*\.rss\??.*$", re.IGNORECASE),
        re.compile(r".*\.atom\??.*$", re.IGNORECASE),
        re.compile(r".*\.rdf\??.*$", re.IGNORECASE),
        re.compile(r".*\.do\??.*$", re.IGNORECASE),
        re.compile(r".*\.db\??.*$", re.IGNORECASE),
        re.compile(
            r"\?\w\.html\??.*", re.IGNORECASE
        ),  # matches directory search pages matching ?[letter].html
        re.compile(
            r".*mailto:.*", re.IGNORECASE
        ),  # Matches links starting with "mailto:" (case-insensitive)
        re.compile(
            r".*tel:.*", re.IGNORECASE
        ),  # Matches links starting with "tel:" (case-insensitive)
    ]

    # Rule = Rule(LinkExtractor(deny=deny_patterns))
    def __init__(self, start_url):
        self.start_urls = [start_url]  # Expect a single start URL
        self.domain = urlparse(self.start_urls[0]).netloc
        self.scheme = urlparse(self.start_urls[0]).scheme
        self.error_message = "Page scraping returned no content"
        self.outfile = f"{self.name}_output.json"
        if self.start_afresh:
            self.data = {}
        else:
            try:
                with open(self.outfile, "r") as infile:
                    self.data = json.load(infile)
            except FileNotFoundError:
                print(
                    f"File {self.outfile} not found. Cannot progress without existing data. To start fresh, set replace_content to True."
                )
            except Exception:
                raise

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

    def test_url_validity(self,url)->bool:
        try:
            r = requests.get(url)
            r.raise_for_status()
            return True
        except:
            return False

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
        start_time = time.time()
        process.start()
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        return self.data


if __name__ == "__main__":
    spider = Spider("https://www.fsu.edu")
    spider.run()

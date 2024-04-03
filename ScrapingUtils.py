import os
from sys import argv
import configparser
from urllib.parse import urlparse, urljoin

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector


class ScrapingUtils:
    def __init__(self,config):
        self.config = config

    def create_spider_class(self):
        class Spider(scrapy.Spider):
            name = "spider"

            allowed_domains = start_urls = self.get_domains() # need to fix this to only allow one domain at a time (keeping website information modular)
            sibling_or_parent_domain_depth = self.config["sibling_or_parent_domain_depth"]
            out_of_domain_depth = self.config["out_of_domain_depth"]
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def scrape_webpage(self,url):
                process = CrawlerProcess()
                process.crawl(Spider, start_url=url)
                process.start()

            def scrape_domains(self):
                for start_url in self.start_urls:
                    self.scrape_webpage(start_url)

            def parse(self, response):
                # Extract all links, metadata, and text
                links = response.css('a::attr(href)').getall()
                metadata = response.xpath('//meta').getall()
                text = response.xpath("//body//text()").getall()
                all_elements = response.xpath(
        "//*[not(contains(@style, 'display: none')) and not(ancestor::*[contains(@style, 'display: none')])]"
    )
                # handle scraped data
                self.logic_on_scrape(response.url, links, metadata, text)
                # self.logic_on_scrape(all_elements)

                # For crawling all pages within the domain
                for link in links:
                    absolute_url = urljoin(response.url, link)
                    yield response.follow(absolute_url, callback=self.parse)

            def logic_on_scrape(self, url, links, metadata, text):
                # User-defined logic goes here
                output = {"url": url, "links": links, "metadata": metadata, "text": text}
                with open("output.json", "a") as f:
                    pass
                        
            
            # def logic_on_scrape(self, body):
            #     with open("output.txt", "a") as f:
            #         for element in body:
            #             f.write(element.get() + "\n")
            
        return Spider
    
    def get_domains(self):
        domains = []
        domains_file = self.config["domains_file"]
        # Open the file for reading
        with open(domains_file, 'r') as domains_list:
            # Iterate over each line in the file
            for line in domains_list:
                # Strip whitespace and newline characters, then add the domain to the list
                line = line.strip()
                # add if not blank or a comment
                if len(line) > 0 and not line.startswith("#"):
                    # Ensure the line has a scheme
                    if not line.startswith(('http://', 'https://')):
                        line = 'http://' + line
                    domains.append(line)
        return domains


if __name__ == "__main__":
    if len(argv) < 2:
        LEVEL = "--test"
    elif len(argv) == 2:
        LEVEL = str(argv[1]) #--test or --prod
    else:
        raise Exception("Invalid number of arguments. Please provide only one argument (--test or --prod)")
    assert LEVEL in ["--test", "--prod"], "Invalid level. Please use --test or --prod"
    config_level = "TESTING" if LEVEL == "--test" else "PRODUCTION"

    # read config file and get domains filename
    config = configparser.ConfigParser()
    config.read('config.ini')
    config = config[config_level]

    SU = ScrapingUtils(config)
    SpiderClass = SU.create_spider_class()

    FSUSpider=SpiderClass()
    FSUSpider.scrape_webpage("fsu.edu")
    # FSUSpider.scrape_domains()
    # utils = ScrapingUtils()
    # #get list of domains
    # sites = utils.read_and_filter_sites(domains)

import configparser
from urllib.parse import urlparse
import json
from sys import argv
import pathlib

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signals import spider_closed

from bs4 import BeautifulSoup as soup

import subprocess
import tempfile
# import spacy
# import openai
# from transformers import MarkupLMProcessor

class Spider(scrapy.Spider):
    name = "spider"

    def __init__(self, start_url):
        self.start_urls = [start_url]  # Expect a single start URL
        self.data = {}  # Initialize data structure for accumulated data
        # self.nlp = spacy.load('en_core_web_sm')  # Load language model
        #load open ai language model
        # self.llm = openai.load("text-davinci-003")

    def parse(self, response):
        # Extract all links, metadata, and text
        links = response.css("a::attr(href)").getall()

        # text = soup(response.text, "html.parser")
        main_content_text = response.xpath('//body//p//text()').extract()
        main_content_text = soup(" ".join(main_content_text), "html.parser").get_text()
        with tempfile.NamedTemporaryFile(suffix='.html') as temp_file:
            temp_file.write(main_content_text.encode())
            temp_file.flush() 
            # Assuming 'converter.js' is in the same directory as your spider 
            result = subprocess.run(['node', 'HTMLtoMarkdownNodeJS/converter.js', temp_file.name], 
                        stdout=subprocess.PIPE, text=True, encoding='utf-8') 

            main_content_markdown = result.stdout.strip()

            self.data[response.url] = {
                "links": links, 
                "text": main_content_text,
                "markdown": main_content_markdown 
            }

        # def get_element_score(element):
        #     score = 0  
        #     text = element.get_text() 

        #     # Basic scoring using tag weights
        #     tag_weights = {'h1': 5, 'h2': 4, "article": 3, "p": 2, 
        #                     "section": 3,"main": 5,"li": 2,"blockquote": 2,
        #                     "default": 1,}
        #     score += tag_weights.get(element.name, 1) * len(text) 
        #     return score 


        # #initialize variables to store highest scoring element and its score
        # highest_scoring_element = None
        # highest_score = 0

        #  # Pick out the most content-rich element according to heuristics in get_element_score
        # for element in soup(response.text, "html.parser"):  # Removed unnecessary 'text' variable
        #     score = get_element_score(element)
        #     if score > highest_score:
        #         highest_scoring_element = element
        #         highest_score = score

        # if highest_scoring_element:
        #     main_content_text = highest_scoring_element.get_text()  # Get text from the element

        #     with tempfile.NamedTemporaryFile(suffix='.html') as temp_file:
        #         temp_file.write(main_content_text.encode())
        #         temp_file.flush() 
        #         # Assuming 'converter.js' is in the same directory as your spider 
        #         result = subprocess.run(['node', 'HTMLtoMarkdownNodeJS/converter.js', temp_file.name], 
        #                  stdout=subprocess.PIPE, text=True, encoding='utf-8') 

        #         main_content_markdown = result.stdout.strip()

        #         self.data[response.url] = {
        #             "links": links, 
        #             "text": main_content_text,
        #             "markdown": main_content_markdown 
        #         }
        #     # print(f"{highest_scoring_element=}")
        #     # main_content_text = highest_scoring_element.get_text()

        #     # self.data[response.url] = {
        #     #     "links": links, 
        #     #     "text": main_content_text,
        #     # }
        # else:
        #     print(f"No content found on {response.url}")
        
        # For crawling all pages within the domain
        for link in links:
            absolute_url = response.urljoin(link)
            if (
                urlparse(absolute_url).netloc
                == urlparse(self.start_urls[0]).netloc
            ):
                yield response.follow(absolute_url, self.parse)

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

if __name__ == "__main__":
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
    SpiderClass = Spider

    # Set up crawling process with SpiderClass for a single domain
    process = CrawlerProcess()
    process.crawl(SpiderClass, start_url="https://www.fsu.edu")
    process.start()

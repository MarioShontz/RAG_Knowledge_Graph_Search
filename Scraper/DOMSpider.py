import configparser
import json
from sys import argv
from urllib.parse import urlparse
import pathlib
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.signals import spider_closed

from bs4 import BeautifulSoup as soup

import subprocess
import tempfile
import openai

from Spider import Spider

class DOMSpider(Spider):
    name = "domspider"
    settings = {
        'FETCH': True,
    }
    def __init__(self, start_url):
        super().__init__(start_url)
    def remove_unwanted_tags(self,body_soup):
        for tag in body_soup.find_all(["script", "svg",'noscript','iframe','nav']):
            tag.decompose()  # Removes the tag and its children

    def modify_image_tags(self,body_soup):
        for img in body_soup.find_all("img"):
            alt_text = img.get("alt", "")  # Get alt text, empty string if absent
            img.replace_with(alt_text)  # Replace image tag with alt text

    def extract_text(self,html_snippet):
        text = soup(html_snippet, 'html.parser')
        return text.get_text().strip()  # Strip leading/trailing whitespace

    def parse(self, response):
        # Save data mini example
        if response.url not in self.data:
            self.data[response.url] = {}
        self.data[response.url].update({
            "title": response.css("title::text").get(),
        })
        
        # Extract all links, metadata, and text
        links = response.css('a::attr(href)').getall()
        for link in links:
            absolute_url = response.urljoin(link)
            if (
                urlparse(absolute_url).netloc
                == urlparse(self.start_urls[0]).netloc
            ):
                yield response.follow(absolute_url, self.parse)

if __name__ == "__main__":
    spider = DOMSpider("https://www.fsu.edu")
    spider.run()
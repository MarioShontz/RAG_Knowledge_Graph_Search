from urllib.parse import urlparse
# import json
import subprocess
import html
# from sys import argv
# import pathlib
# import configparser

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule


from Spider import Spider

class GFMDSpider(Spider):
    name = "GFMDSpider"
    start_afresh = False
    rules = ( 
        Rule(
            LinkExtractor(
                allow=(''),
                deny=(
                    '\\*.js',
                    '\\*.ico',
                    '\\?\\w\\.html'
                    '\\*\\.pdf',
                    '\\*\\.jpg',
                    '\\*\\.png',
                    '\\*\\.gif',
                    '\\*\\.css',
                    '\\*\\.js',
                    '\\*\\.svg',
                    '\\*\\.jpeg',
                    '\\*\\.zip',
                    '\\*\\.ppt',
                    '\\*\\.pptx',
                    '\\*\\.xls',
                    '\\*\\.xlsx',
                    '\\*\\.doc',
                    '\\*\\.docx',
                    '\\*\\.txt',
                    '\\*\\.xml',
                    '\\*\\.json',
                    '\\*\\.rss',
                    '\\*\\.atom',
                    '\\*\\.rdf',
                    '\\*\\.xml',
                    '\\*\\.do',
                    '\\*\\.db',
                    '\\*redirect',
                ),
            ),
        )
    )
    def __init__(self, start_url):
        super().__init__(start_url=start_url)

    def unmangle_utf8(self, text):
        decoded_text = html.unescape(text)
        replace_dict = {
            "\u00e2\u20ac\u2122": "'",  # Replace with apostrophe
            "\u00e2\u20ac\u201d": "—", # Replace with em dash
            "\u00c3\u00bak\u00c3\u00ae": "ú",  # Replace with ú
            "\u00c3\u00b3" : "ó",  # Replace with ó
            "\u00c3\u00ae" : "î",  # Replace with î
            "\u00c2\u00a0" : "", # delete all non-breaking spaces
            "\u000b" : "", # delete all vertical tabs
            "\u00e2\u20ac\u2039" : "",
            "\u00c3\u00af" : "ï",
            " \\[\u2026\\]" : "", 
            "\u00e2\u20ac\u201c" : "—",       
        }
        for key, value in replace_dict.items():
            decoded_text = decoded_text.replace(key, value)
        return decoded_text
        
    def run_website_to_md_js(self, url):
        # Path to your JavaScript file (adjust as needed)
        js_file_path = './WebsiteToMD/run.js'  

        # Construct the command to execute your JavaScript file with Node.js
        command = ['node', js_file_path, url]

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            # test if result NoneType object
            if result.stdout is None:
                return self.error_message
            # String cleanup
            output = result.stdout.strip()  # Remove leading/trailing whitespace
            
            #here's a patchy way to remove the Promise { <pending> } string that is returned by the JS file
            if output.startswith("Promise { <pending> }\n"):
                output = output[len("Promise { <pending> }\n"):]  # Slice off the unwanted part
            output = self.unmangle_utf8(output)

            # print(output)
            return output

        except subprocess.CalledProcessError as e:
            return self.error_message
        
    def parse(self, response):
        links = response.css('a::attr(href)').getall()
        
        if response.url not in self.data:
            markdown_content = str(self.run_website_to_md_js(response.url))
            self.data[response.url] = {}
            self.data[response.url].update({
                "links": links,
                "content": markdown_content,
            })
        elif response.url in self.data:
            if self.data[response.url]["content"] == self.error_message:
                markdown_content = str(self.run_website_to_md_js(response.url))
                self.data[response.url].update({
                    "content": markdown_content,
                })
            if "links" not in self.data[response.url]:
                self.data[response.url].update({
                    "links": links,
                })
        for link in links:
                absolute_url = response.urljoin(link)
                # check if link is within domain of start_url
                if (
                    urlparse(absolute_url).netloc 
                    == urlparse(self.start_urls[0]).netloc
                ):
                    yield response.follow(absolute_url, self.parse)
if __name__ == "__main__":
    spider = GFMDSpider("https://www.fsu.edu")
    spider.run()
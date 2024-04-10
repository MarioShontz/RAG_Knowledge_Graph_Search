from urllib.parse import urlparse
import subprocess
import html
import re

from Spider import Spider

class HTMLtoMarkdownSpider(Spider):
    name = "HTMLtoMarkdownSpider"
    start_afresh = True #takes precedence over update and retry settings below
    
    update_links = True
    update_content = False
    retry_failed_content = True

    def __init__(self, start_url):
        super().__init__(start_url=start_url)
        self.start_page_links = []

    def unmangle_utf8(self, text: str):
        decoded_text = html.unescape(text)
        # replace_dict = {
        #     "\u00e2\u20ac\u2122": "\'",  # Replace with apostrophe
        #     "\u00e2\u20ac\u201d": "—", # Replace with em dash
        #     "\u00c3\u00bak\u00c3\u00ae": "ú",  # Replace with ú
        #     "\u00c3\u00b3" : "ó",  # Replace with ó
        #     "\u00c3\u00ae" : "î",  # Replace with î
        #     "\u00c2\u00a0" : "", # delete all non-breaking spaces
        #     "\u000b" : "", # delete all vertical tabs
        #     "\u00e2\u20ac\u2039" : "",
        #     "\u00c3\u00af" : "ï",
        #     " \\[\u2026\\]" : "",
        #     "\u00e2\u20ac\u201c" : "—",
        #     '\u2014',: "—",
        #     '\u2019' : "\'",
        #     '\u201c' : '\"',
        #     '\u201d' : '\"',
        # }
        # for key, value in replace_dict.items():
        #     decoded_text = decoded_text.replace(key, value)
        return decoded_text

    def run_website_to_md_js(self, url: str) -> str:
        # Path to your JavaScript file (adjust as needed)
        js_file_path = "./WebsiteToMD/run.js"

        # Construct the command to execute your JavaScript file with Node.js
        command = ["node", js_file_path, url]

        try:
            result = subprocess.run(
                command, capture_output=True, encoding="utf-8", text=True, check=True
            )
            if result.stdout is None:
                return self.error_message
            # String cleanup
            output = str(result.stdout).strip()  # Remove leading/trailing whitespace
            if url == self.start_urls[0]:
                print(output)

            # here's a patchy way to remove the Promise { <pending> } string that is returned by the JS file
            if output.startswith("Promise { <pending> }\n"):
                output = output[
                    len("Promise { <pending> }\n") :
                ]  # Slice off the unwanted part
            output = self.unmangle_utf8(output)

            if url == self.start_urls[0]:
                print(output)
            return output

        except:
            return self.error_message

    def parse(self, response):
        links: list = response.css("a::attr(href)").getall()

        # filter for fsu.edu domains and valid links
        actual_links = []
        for link in links:
            if link.startswith("/"):
                link = f"{self.scheme}://{self.domain}{link}"
            if (
                (urlparse(link).netloc == self.domain)
                and not any(re.search(pattern, link) for pattern in self.deny_patterns)
                and link not in actual_links
                and link not in self.start_page_links
                and link != response.url
                and self.test_url_validity(link)
            ):
                actual_links.append(link)
        if response.url == self.start_urls[0]:
            self.start_page_links = actual_links
        if self.start_afresh or response.url not in self.data:
            markdown_content = str(self.run_website_to_md_js(response.url))
            self.data[response.url] = {}
            self.data[response.url].update(
                {
                    "links": actual_links,
                    "content": markdown_content,
                }
            )
        elif response.url in self.data:
            if self.update_content or (
                self.retry_failed_content
                and self.data[response.url]["content"] == self.error_message
            ):
                markdown_content = self.run_website_to_md_js(response.url)
                self.data[response.url].update(
                    {
                        "content": markdown_content,
                    }
                )
            if self.update_links or "links" not in self.data[response.url]:
                self.data[response.url].update(
                    {
                        "links": actual_links,
                    }
                )
        for link in actual_links:
            yield response.follow(link, self.parse)


if __name__ == "__main__":
    spider = HTMLtoMarkdownSpider("https://www.fsu.edu")
    spider.run()

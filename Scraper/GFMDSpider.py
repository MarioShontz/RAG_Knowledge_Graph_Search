from urllib.parse import urlparse

from Spider import Spider

class GFMDSpider(Spider):
    name = "GFMDSpider"

    def parse(self, response):
        # Save data mini example
        if response.url not in self.data:
            self.data[response.url] = {}
        self.data[response.url].update({
            "title": response.css("title::text").get(),
        })
        


        # Extract all links, metadata, and text
        links = response.css('a::attr(href)').getall()
        # follow links within domain
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
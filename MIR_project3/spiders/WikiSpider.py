import re

import scrapy
from bs4 import BeautifulSoup


class WikiSpider(scrapy.Spider):
    name = 'wiki_spider'
    start_urls = ['https://fa.wikipedia.org/wiki/%D8%B3%D8%B9%D8%AF%DB%8C']

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        yield {
            'my_title': soup.select('h1.firstHeading')[0].get_text()
        }

        counter = 0
        tags = soup.select('div#mw-content-text')[0].find_all('a')

        next_page = tags.pop(0).get('href')
        while '#' in next_page or ':' in next_page or next_page in response.url or 'wikisource' in next_page :
            if tags:
                next_page = tags.pop(0).get('href')

        if next_page:
            if counter < 20:
                counter += 1
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parse
                )

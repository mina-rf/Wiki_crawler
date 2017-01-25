import re

import scrapy
from bs4 import BeautifulSoup


class WikiSpider(scrapy.Spider):
    name = 'wiki_spider'
    start_urls = ['https://fa.wikipedia.org/wiki/%D8%B3%D8%B9%D8%AF%DB%8C']
    allowed_domains = ['fa.wikipedia.org']

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')

        wiki_item = WikiItem()
        wiki_item['title'] = soup.select('h1.firstHeading')[0].get_text()
        wiki_item['preface'] = soup.select_one('div#mw-content-text').find_all('p')[2].get_text()
        # for i, p in enumerate(soup.select_one('div#mw-content-text').find_all('p')):
        #     print(i, ':', p)
        wiki_item['page'] = response.url
        wiki_item['links'] = []
        yield {
            'wiki_item': wiki_item
        }

        counter = 0
        tags = soup.select('div#mw-content-text')[0].find_all('a')
        while len(tags) != 0:
            next_page = tags.pop().get('href')
            while '#' in next_page or ':' in next_page or next_page in response.url or 'wikisource' in next_page:
                if tags:
                    next_page = tags.pop().get('href')

            if next_page:
                if counter < 10:
                    counter += 1
                    yield scrapy.Request(
                        response.urljoin(next_page),
                        callback=self.parse
                    )
                else:
                    break


class WikiItem(scrapy.Item):
    title = scrapy.Field()
    preface = scrapy.Field()
    body = scrapy.Field()
    page = scrapy.Field()
    links = scrapy.Field()

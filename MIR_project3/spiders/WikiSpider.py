import re
import urllib

import scrapy

from bs4 import BeautifulSoup

from MIR_project3.items import WikiItem


class WikiSpider(scrapy.Spider):
    name = 'wiki_spider'
    start_urls = ['https://fa.wikipedia.org/wiki/%D8%B3%D8%B9%D8%AF%DB%8C']
    allowed_domains = ['fa.wikipedia.org']

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        main_content = soup.select_one('div#mw-content-text')

        wiki_item = WikiItem()
        wiki_item['title'] = soup.select('h1.firstHeading')[0].get_text()
        wiki_item['preface'] = main_content.find_all('p', recursive=False)[0].get_text()
        wiki_item['page'] = urllib.parse.unquote(response.url)
        [s.extract() for s in main_content(['style', 'script', '[document]', 'head', 'title'])]
        wiki_item['body'] = main_content.get_text()
        wiki_item['links'] = []

        anchors = [urllib.parse.unquote(a['href']) for a in main_content.find_all('a')]
        refs = [response.urljoin(a) for a in anchors]
        wiki_item['links'].extend(refs)
        yield wiki_item

        valid_refs = [a for a in anchors if not bool(re.search('\d|#|:|wikisource', a))][:10]
        # print('valid', valid_refs)
        # print('anch', anchors[:10])
        while valid_refs:
            next_page = valid_refs.pop()
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

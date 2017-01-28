import re
import urllib

import scrapy
from bs4 import BeautifulSoup
from scrapy.exceptions import CloseSpider
from tqdm import tqdm

from MIR_project3.items import WikiItem


class WikiSpider(scrapy.Spider):
    name = 'wiki_spider'
    start_urls = ['https://fa.wikipedia.org/wiki/%D8%B3%D8%B9%D8%AF%DB%8C']
    allowed_domains = ['fa.wikipedia.org']
    count = 0
    COUNT_MAX = 20
    out_degree = 10

    def __init__(self, start_urls, out_degree, COUNT_MAX):
        self.out_degree = out_degree
        self.start_urls = start_urls
        self.COUNT_MAX = COUNT_MAX
        self.bar = tqdm(total=self.COUNT_MAX)
        # print(self.out_degree)
        # n = int(input())
        # logging.getLogger('scrapy').propagate = False
        # logger = logging.getLogger('scrapy')
        # logger.setLevel(logging.INFO)
        # print('a')
        # pass

    def parse(self, response):
        self.count += 1
        self.bar.update(1)
        if self.count >= self.COUNT_MAX and self.crawler.stats.get_stats()['item_scraped_count'] >= self.COUNT_MAX:
            self.bar.close()
            raise CloseSpider(reason="crawled all n urls")
            # if signals.item_passed:
            # self.count += 1
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
        valid_refs = [a for a in anchors if not bool(re.search('\d|#|:|wikisource', a))][:self.out_degree]
        # print('valid', valid_refs)
        # print('anch', anchors[:10])
        while valid_refs:
            next_page = valid_refs.pop()

            # if self.count < self.COUNT_MAX:
            # self.count += 1
            # self.bar.update(1)
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

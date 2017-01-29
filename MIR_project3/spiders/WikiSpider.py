import re
import urllib

import scrapy
from bs4 import BeautifulSoup
from scrapy.exceptions import CloseSpider
from tqdm import tqdm

from MIR_project3.items import WikiItem


def extract_infobox(info_box):
    if info_box:
        abstract = {}
        rows = info_box.find_all('tr')
        for row in rows:
            table_header = row.find('th')
            table_data = row.find_all('td')
            if table_header:
                if table_data:
                    if table_data[0].select_one('a') and table_data[0].select_one('a').select_one('img'):
                        abstract[table_header.get_text()] = table_data[0].select_one('a').select_one('img')['src']
                    else:
                        abstract[table_header.get_text()] = table_data[0].get_text()
                else:
                    abstract['title'] = table_header.get_text()
            else:
                if len(table_data) > 1:
                    abstract[table_data[0].get_text()] = table_data[1].get_text()
                elif table_data[0].select_one('a') and table_data[0].select_one('a').select_one('img'):
                    abstract['image_url'] = table_data[0].select_one('a').select_one('img')['src']
                    abstract['image_description'] = table_data[0].get_text()
        # for k, v in abstract.items():
        #     print(k, ':', v)
        return abstract
    return {}


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

    def parse(self, response):

        if self.count < self.COUNT_MAX:
            self.count += 1
            self.bar.update(1)
        elif self.crawler.stats.get_stats()['item_scraped_count'] >= self.COUNT_MAX:
            self.bar.close()
            raise CloseSpider(reason="finished items to be crawled")

        soup = BeautifulSoup(response.body, 'html.parser')
        main_content = soup.select_one('div#mw-content-text')

        wiki_item = WikiItem()
        wiki_item['title'] = soup.select('h1.firstHeading')[0].get_text()
        if main_content.find_all('p', recursive=False):
            wiki_item['preface'] = main_content.find_all('p', recursive=False)[0].get_text()
        wiki_item['page'] = urllib.parse.unquote(response.url)
        [s.extract() for s in main_content(['style', 'script', '[document]', 'head', 'title'])]
        wiki_item['body'] = main_content.get_text()
        wiki_item['links'] = []
        wiki_item['abstract'] = extract_infobox(soup.select_one('table.infobox'))
        wiki_item['page_rank'] = 0
        wiki_item['cluster_id'] = 0

        anchors = [urllib.parse.unquote(a['href']) for a in main_content.find_all('a')]
        refs = [response.urljoin(a) for a in anchors]
        wiki_item['links'].extend(refs)

        yield wiki_item
        valid_refs = [a for a in anchors if not bool(re.search('\d|#|:|wikisource', a))][:self.out_degree]

        while valid_refs:
            next_page = valid_refs.pop()
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

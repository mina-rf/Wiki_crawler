from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

from MIR_project3.spiders import WikiSpider
from search import search


# logging.getLogger('scrapy').propagate = False


# logging.getLogger('scrapy').setLevel('INFO')

cluster_label = { 0 : 'همه'}

def init():
    parts = ['بخش اول',
             'بخش دوم',
             'بخش سوم',
             'بخش چهارم',
             'بخش پنجم',
             'خروج'
             ]
    part_func = {1: part1, 2: part2, 3: part3, 4: part4, 5: part5}

    while True:
        print('لطفا بخش مورد نظر خود را انتخاب نمایید')
        print_list(parts)
        part = int(input())

        if part == 6:
            break
        else:
            part_func[part]()


def part1():
    print('لطفا start_urlهای مورد نظر خود را وارد نمایید و برای اتمام enter بزنید')
    start_urls = []
    while True:
        start_url = input()
        if start_url == '':
            break
        start_urls.append(start_url)
    print('لطفا تعداد لینک‌های خروجی هر صفحه را وارد نمایید')
    out_deg = int(input())
    print('لطفا تعداد صفحاتی که باید دریافت شوند را وارد نمایید')
    n = int(input())
    setting = get_project_settings()
    setting.set('CLOSESPIDER_ITEMCOUNT', n)
    process = CrawlerProcess(setting)
    process.crawl(WikiSpider.WikiSpider, start_urls=start_urls, out_degree=out_deg, COUNT_MAX=n)
    process.start()


def part2():
    pass


def part3():
    pass


def part4():
    print('لطفا آلفا مورد نظر برای محاسبه معیار page rank  را وارد کنید.')
    alpha = float(input())

    pass


def part5():
    print('لطفا وزن مربوط به عنوان را وارد کنید')
    title_w = int(input())
    print('لطفا وزن مربوط به خلاصه را وارد کنید.')
    preface_w = int(input())
    print('لطفا وزن مربوط به متن را وارد کنید.')
    body_w = int(input())
    print('لطفا در صورت تمایل به جستجو در بین خوشه مشخص شماره خوشه را وارد نمایید و در غیر این صورت عدد -۱ را وارد نمایید')
    for i , label in cluster_label.items():
        print( i , ':' , label)
    cluster_id = int(input())
    print(' آیا تمایل به استفاده از معیار page rank دارید؟ ۱- بله ۲-خیر')
    page_rank = True if int(input())==1 else False
    print('لطفا کلیدواژه مربوط به عنوان را وارد کنید.')
    title = input()
    print('لطفا کلیدواژه مربوط به خلاصه را وارد کنید.')
    preface = input()
    print('لطفا کلیدواژه مربوط به متن را وارد کنید.')
    body = input()
    search('wiki-index',title_w,preface_w,body_w,cluster_id,page_rank,title,preface,body)
    print('در صورت تمایل به دیدن محتوای صفحه آیدی آن را وارد کنید')
    doc_id = input()
    while doc_id!='':
        es = Elasticsearch()
        res = es.get(index="wiki-index", doc_type='doc', id=doc_id)['_source']
        print(res['page'])
        print(res['preface'])
        print('در صورت تمایل به دیدن محتوای صفحه آیدی آن را وارد کنید')
        doc_id = input()

    pass


def print_options(options):
    for k, v in options.items():
        print(v, '- ', k)


def print_list(m_list, en=False):
    if not m_list:
        print('سندی یافت نشد')
    for i, l in enumerate(m_list):
        if en:
            print((i + 1), '-', l)
        else:
            print(l, '-', (i + 1))


if __name__ == '__main__':
    init()

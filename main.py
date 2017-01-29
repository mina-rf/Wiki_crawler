import matplotlib.pyplot as plt
import networkx as nx
from elasticsearch import Elasticsearch
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from MIR_project3.spiders import WikiSpider
from cluster_labeling import print_clusters
from elastic_indexing import make_index, delete_index, get_docs_list
from k_means_lib import cluster
from page_rank import compute_and_update_pr, build_matrix
from search import search

cluster_label = {0: 'همه'}


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
    # TODO: check the twisted.internet.error.ReactorNotRestartable
    # runner = CrawlerRunner()
    #
    # d = runner.crawl(WikiSpider.WikiSpider, start_urls=start_urls, out_degree=out_deg, COUNT_MAX=n)
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()  # the script will block here until the crawling is finished
    # reactor.stop()
    print('آیا مایل هستید ماتریس مجاورت صفحات را ببینید؟ ۰ نه ۱ بله')
    if int(input()):
        draw_matrix()


def draw_matrix():
    docs = get_docs_list('files')
    _, matrix = build_matrix(docs, meta=False)
    G = nx.from_scipy_sparse_matrix(matrix)
    nx.draw_networkx(G, pos=nx.circular_layout(G))
    plt.show()


def part2():
    options = ['ساخت نمایه', 'پاک کردن نمایه', 'بازگشت']
    while True:
        print_list(options)
        option = int(input())
        if option == 1:
            print('لطفا نام پوشه‌ای که می‌خواهید روی آن نمایه را بسازید وارد نمایید')
            directory = input()
            make_index(directory)
        elif option == 2:
            print('لطفا نام نمایه‌ای که می‌خواهید پاک کنید را وارد نمایید')
            index_name = input()
            delete_index(index_name)
        else:
            break


def part3():
    print('لطفا حداکثر تعداد خوشه‌ها را وارد نمایید')
    L = int(input())
    cluster(L)


def part4():
    print('لطفا آلفا مورد نظر برای محاسبه معیار page rank  را وارد کنید.')
    alpha = float(input())
    compute_and_update_pr(alpha, 'wiki-index', 5)
    pass


def part5():
    print('لطفا وزن مربوط به عنوان را وارد کنید')
    title_w = int(input())
    print('لطفا وزن مربوط به خلاصه را وارد کنید.')
    preface_w = int(input())
    print('لطفا وزن مربوط به متن را وارد کنید.')
    body_w = int(input())
    print(
        'لطفا در صورت تمایل به جستجو در بین خوشه مشخص شماره خوشه را وارد نمایید و در غیر این صورت عدد -۱ را وارد نمایید')
    # for i , label in cluster_label.items():
    #     print( i , ':' , label)
    print_clusters()
    cluster_id = int(input())
    print(' آیا تمایل به استفاده از معیار page rank دارید؟ ۱- بله ۲-خیر')
    page_rank = True if int(input()) == 1 else False
    print('لطفا کلیدواژه مربوط به عنوان را وارد کنید.')
    title = input()
    print('لطفا کلیدواژه مربوط به خلاصه را وارد کنید.')
    preface = input()
    print('لطفا کلیدواژه مربوط به متن را وارد کنید.')
    body = input()
    search('wiki-index', title_w, preface_w, body_w, cluster_id, page_rank, title, preface, body)
    print('در صورت تمایل به دیدن محتوای صفحه آیدی آن را وارد کنید')
    doc_id = input()
    while doc_id != '':
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

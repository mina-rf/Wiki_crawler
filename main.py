from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders import WikiSpider


# logging.getLogger('scrapy').propagate = False


# logging.getLogger('scrapy').setLevel('INFO')


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
    pass


def part5():
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

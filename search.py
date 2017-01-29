from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import operator


def search(index, title_w, preface_w, body_w, cluster_id, page_rank, title, preface, body):
    client = Elasticsearch()
    s = Search(using=client, index=index) \
        .query(
        Q('match', title={'query': title, 'boost': title_w})
        |
        Q('match', preface={'query': preface, 'boost': preface_w})
        |
        Q('match', body={'query': body, 'boost': body_w})

    )

    if cluster_id != -1:
        s = Search(using=client, index=index) \
            .query(
            Q('match', cluster_id={'query': cluster_id})
            &
            (
                Q('match', title={'query': title, 'boost': title_w})
                |
                Q('match', preface={'query': preface, 'boost': preface_w})
                |
                Q('match', body={'query': body, 'boost': body_w})
            )

        )

    response = s.execute()

    if page_rank:
        pr_res = [hit for hit in response]
        try:
            max_score = max([hit.meta.score for hit in response])
            max_pr = max([hit.page_rank for hit in response])
        except:
            max_score = 1
            max_pr =1
        pr_scores = [hit.meta.score * 0.5 / max_score + 0.5 * hit.page_rank /max_pr for hit in response]
        response = [x for (y, x) in sorted(zip(pr_scores, pr_res), reverse=True)]

    for hit in response:
        print('id : ', hit.meta.id, ', title :', hit.title, hit.page_rank)

# search('wiki-index', 3, 2, 1, 2, False, "سعدی", 'شیراز', 'ا')
# Q('multi-match' , query = preface , fields=['preface'] , boost=preface_w)
# Q('multi-match' , query = body , fields=['body'] , boost=body_w)

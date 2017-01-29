from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


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

    response = s.scan()

    if page_rank:
        response = sorted(response, key=lambda x: x['page_rank'], reverse=True)

    for hit in response:
        print('id : ' , hit.meta.id, 'title :' , hit.title)


# search('wiki-index', 3, 2, 1, 2, False, "سعدی", 'شیراز', 'ا')
# Q('multi-match' , query = preface , fields=['preface'] , boost=preface_w)
# Q('multi-match' , query = body , fields=['body'] , boost=body_w)

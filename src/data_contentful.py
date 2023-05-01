import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone, timedelta

from pprint import pprint

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

API_BASE_URL = 'https://api.contentful.com'
CMA_TOKEN = os.getenv('CONTENTFUL_CMA_TOKEN')
SPACE_ID = os.getenv('CONTENTFUL_SPACE_ID')
ENVIRONMENT_ID = os.getenv('CONTENTFUL_ENVIRONMENT_ID')

# sample_articles = [
#     {'title': '북극성 지표, 어떻게(How)?', 'slug': 'about-north-star-metric', 'author_id': '371RhJKtAnp5aA8kdaQMNH', 'private': False, 'published_at': '2023-04-01T08:10:39.483Z', 'date': '2023-04-04T00:00+09:00'}, 
#     {'title': 'MACD 방법으로 시계열 데이터에서 변곡점 찾아보기', 'slug': 'find-inflection-point-with-macd', 'author_id': '7yk4llUZalWtEpmtwzDp5k', 'private': False, 'published_at': '2023-04-01T04:41:15.978Z', 'date': '2023-04-01T00:00+09:00'}, 
#     {'title': '경쟁사의 Log를 직접 볼 수 있다면? - 블록체인 Dune', 'slug': 'log-dune-wip', 'author_id': '4F228o8FrZYEvwT8U9ZD3h', 'private': False, 'published_at': '2023-03-26T11:10:17.769Z', 'date': '2023-04-02T00:00+09:00'}, 
#     {'title': '얕은 분석과 깊은 분석의 차이점', 'slug': 'What-is-deep-analysis', 'author_id': '5WRi9m1YguzzfMxSQT651e', 'private': False, 'published_at': '2023-03-25T05:43:12.189Z', 'date': '2023-03-25T00:00+09:00'}
# ]

def get_contentful_articles() -> list:
    """
    Ouput: [{
        "title": str,
        "slug": str,
        "author_id": str,
        "private: bool,
        "publisted_at": str,
        "date": str
    }]
    """
    req_url = API_BASE_URL + f'/spaces/{SPACE_ID}/environments/{ENVIRONMENT_ID}/public/entries?content_type=article'
    response = requests.get(req_url, headers={'Authorization': f'Bearer {CMA_TOKEN}'})
    if response.status_code == 200:
        result = response.json()
        articles = [{
            'title': article['fields']['title']['en-US'],
            'slug': article['fields']['slug']['en-US'],
            'author_id': article['fields']['author']['en-US']['sys']['id'],
            'private': article['fields'].get('private', {'en-US': False})['en-US'],
            'published_at': article['sys']['publishedAt'],
            'date': article['fields']['date']['en-US']
        } for article in result['items']]
        return articles
    else:
        # TODO: 요청 실패시 예외처리
        return []

# sample_authors = [
#     {'name': '박준하', 'slug': 'goldlant', 'author-id': '371RhJKtAnp5aA8kdaQMNH'}, 
#     {'name': '주정민', 'slug': 'jmin', 'author-id': '5rHNDnoqnwkIJyQSEikADA'}, 
#     {'name': '오연주', 'slug': 'yeonjuoh', 'author-id': '7yk4llUZalWtEpmtwzDp5k'}, 
#     {'name': '방태모', 'slug': 'taemobang', 'author-id': '4VK1xMT4iw9ustp6D8AW5P'}, 
#     {'name': '권남택', 'slug': 'namtaek', 'author-id': '6gHoqLPPbdiyxIQ0MTZNa8'}, 
#     {'name': '김민겸', 'slug': 'minkim', 'author-id': '4F228o8FrZYEvwT8U9ZD3h'}, 
#     {'name': '누리', 'slug': 'nuli', 'author-id': '58lKCEp8UM5xTzRrugtjm1'}, 
#     {'name': '이웅원', 'slug': 'dnddnjs11', 'author-id': '5WRi9m1YguzzfMxSQT651e'}, 
#     {'name': '이창현', 'slug': 'changhyun.lee', 'author-id': '30ylK3Wl9yg2YdyNlM9L9S'}, 
#     {'name': '홍선아', 'slug': 'soosunnaa', 'author-id': 'er9x59t9LsxaOcwxhjtft'}, 
#     {'name': '이인영', 'slug': 'nathan', 'author-id': '21xsO5PvrYaKjyLIa4DfMI'}, 
#     {'name': '윤정환', 'slug': 'alfred', 'author-id': '5UQFyzl5YwK852RxeOKwdF'}, 
#     {'name': '정원혁', 'slug': 'marvin', 'author-id': '6iHzmbpCFuZsWrjd4WVjq0'}, 
#     {'name': '이민호', 'slug': 'miika', 'author-id': '62y55ciisRKFSHp83U3G6u'}
# ]

def get_contentful_authors() -> list:
    """
    Ouput: [{
        "name": str,
        "slug": str,
        "author_id": str
    }]
    """
    req_url = API_BASE_URL + f'/spaces/{SPACE_ID}/environments/{ENVIRONMENT_ID}/public/entries?content_type=author'
    response = requests.get(req_url, headers={'Authorization': f'Bearer {CMA_TOKEN}'})
    if response.status_code == 200:
        result = response.json()
        authors = [{
            'name': author['fields']['name']['en-US'],
            'slug': author['fields'].get('slug', {}).get('en-US', None),
            'author_id': author['sys']['id']
        } for author in result['items']]
        return authors
    else:
        # TODO: 요청 실패시 예외처리
        return []


def filter_articles_by_duedate(articles: list, due_start_date: str, due_end_date:str) -> list:
    """
    - 포스팅에 표기되는 게시글 날짜가 due_start_date <= target <= due_end_date 에 포함되어야 한다.
    - 정책으로 due_start_date 는 이전 배포일+1 이 되는 것이 좋다. (첫배포시에는 배포 2주 전쯤)
    """
    start_dt = datetime.strptime(due_start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(due_end_date, '%Y-%m-%d')
    
    # Set Timezone (Naive -> Aware)
    kst_tz = timezone(timedelta(hours=9), 'KST')
    start_dt = start_dt.replace(tzinfo=kst_tz)
    end_dt = end_dt.replace(tzinfo=kst_tz)

    result = []
    for article in articles:
        # published_dt: 2023-03-25T05:43:12.189Z -> 2023-03-25 14:43:12.189000+09:00
        # published_dt = datetime.strptime(article['published_at'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=kst_tz) + timedelta(hours=9)
        article_dt = datetime.strptime(article['date'], '%Y-%m-%dT%H:%M%z')
        if start_dt <= article_dt <= end_dt:
            result.append(article)
    return result

def filter_articles_by_privateness(articles: list) -> list:
    return list(filter(lambda a: a['private'] == False, articles))

def get_target_articles(due_start_date: str, due_end_date: str) -> list:
    articles = get_contentful_articles()
    articles = filter_articles_by_privateness(articles)
    articles = filter_articles_by_duedate(articles, due_start_date, due_end_date)
    return articles

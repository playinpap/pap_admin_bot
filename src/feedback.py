import random
from pprint import pprint
from data_contentful import get_contentful_articles, filter_articles_by_duedate
from data_sheet import get_gspread_service_account, get_worksheet


def get_feedback_candidates(authors: list, articles: list, seed: str = 'abc') -> list:
    random.seed(seed)
    result = []
    for author in authors:
        target_articles = list(filter(lambda a: a['author_id'] != author['author_id'], articles))
        feedback_articles = random.sample(target_articles, k=2)
        feedback_result = {
            'author': author,
            'feedbacks': feedback_articles
        }
        result.append(feedback_result)
    return result

def run_feedback(start_dt: str, end_dt: str) -> list:
    '''
    example
    ---
    feedbacks = run_feedback('2023-03-20', '2023-04-06')
    '''
    google_svc_account = get_gspread_service_account()
    publishers = get_worksheet(google_svc_account, 'PAP 시즌 2 퍼블리셔 제출 현황', 'season3_publisher')

    articles = get_contentful_articles()
    articles = filter_articles_by_duedate(articles, start_dt, end_dt)

    feedbacks = get_feedback_candidates(publishers, articles)
    feedbacks_result = [{
        'name': f['author']['name'],
        'member_id': f['author']['member_id'],
        'feedback1': f'https://playinpap.github.io/{f["feedbacks"][0]["slug"]}',
        'feedback2': f'https://playinpap.github.io/{f["feedbacks"][1]["slug"]}'
    } for f in feedbacks]
    
    return feedbacks_result

def prettify_feedback_msg(feedbacks: list) -> list:
    msgs = ['\n'.join(['- ' + feedback["name"], '\t- ' + feedback["feedback1"], '\t- ' + feedback["feedback2"]]) for feedback in feedbacks]
    for msg in msgs:
        print(msg)

if __name__ == '__main__':
    START_DT = '2023-03-20'
    END_DT = '2023-04-06'
    feedbacks = run_feedback(START_DT, END_DT)
    prettify_feedback_msg(feedbacks)

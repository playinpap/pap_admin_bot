from data_contentful import get_contentful_articles, filter_articles_by_duedate
from data_sheet import get_gspread_service_account, get_worksheet, insert_worksheet

from pathlib import Path
from dotenv import load_dotenv
from pprint import pprint
from datetime import datetime


def upload_posts(post_group: int, due_start_date: str, due_end_date: str):
    current_time = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
    google_svc_account = get_gspread_service_account()
    
    articles = get_contentful_articles()
    articles = filter_articles_by_duedate(articles, due_start_date, due_end_date)
    articles = [[str(post_group), a['author_id'], a['title'], a['slug'], a['date'], current_time] for a in articles]

    for article in articles:
        insert_worksheet(google_svc_account, 'PAP 시즌 2 퍼블리셔 제출 현황', 'season3_posts', article)
    print('[Done]')

if __name__ == '__main__':
    # TODO : CLI에서 직접 실행할 경우 커맨드라인으로 명령어 받아서 커스텀으로 돌릴 수 있게 하기
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    POST_GROUP = 1 # 업로드 주차마다 1씩 올려야 함
    upload_posts(POST_GROUP, '2023-03-20', '2023-04-06')

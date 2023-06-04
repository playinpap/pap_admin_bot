from data_slack import get_slack_client, get_slack_client, get_replies_from_ts
from data_sheet import get_gspread_service_account, insert_worksheet

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime


def run_feedback_checker(slack_token: str, channel_id: str, thread_ts: str, post_group: int):
    current_time = (datetime.today()).strftime('%Y-%m-%d %H:%M:%S')
    
    client = get_slack_client(slack_token)
    replies = get_replies_from_ts(client, channel_id, thread_ts)
    
    feedbacks = [
        [str(post_group), r['user'], r['time'], current_time]
        for r in replies 
        if 'feedback' in r['reactions']
    ]

    google_svc_account = get_gspread_service_account()
    insert_worksheet(google_svc_account, 'PAP 시즌 2 퍼블리셔 제출 현황', 'season3_feedbacks', feedbacks)
    
    print('[Done]')


if __name__ == '__main__':
    # poetry run python src/feedback_check.py
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    # POST_GROUP=1  https://playinpap.slack.com/archives/C04SJDDSYHG/p1680698243235909  =>  1680698243.235909
    # POST_GROUP=2  https://playinpap.slack.com/archives/C04SJDDSYHG/p1683156600730909  =>  1683156600.730909
    # POST_GROUP=3  https://playinpap.slack.com/archives/C04SJDDSYHG/p1685376305481739  =>  1685376305.481739

    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    CHANNEL_ID = 'C04SJDDSYHG'
    THREAD_TS = '1685376305.481739'
    POST_GROUP = 3 # 업로드 주차마다 1씩 올려야 함

    run_feedback_checker(SLACK_BOT_TOKEN, CHANNEL_ID, THREAD_TS, POST_GROUP)

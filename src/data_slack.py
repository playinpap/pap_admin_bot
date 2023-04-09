import os
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk import WebClient
from typing import List, Dict
from datetime import datetime

from pprint import pprint

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
# SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

def timestamp_to_date(timestamp: float) -> str:
    """
    Slack의 timestamp 값을 %Y-%m-%d %H:%M:%S 포맷의 문자열로 반환합니다.
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_slack_client(token:str) -> WebClient:
    return WebClient(token=token)

def get_channel_members(client: WebClient, channel_id: str) -> list:
    # #season3-team-publishers: C04SJDDSYHG
    return client.conversations_members(channel=channel_id)['members']

def get_member_name(client:WebClient, member_id:str) -> Dict[str, str]:
    user_info = client.users_info(user=member_id)
    
    display_name = user_info['user']['profile']['display_name']
    real_name = user_info['user']['real_name']
    name = display_name if display_name != '' else real_name
    
    return {
        'member_id': member_id,
        'name': name
    }

client = get_slack_client(SLACK_BOT_TOKEN)
# member_ids = get_channel_members(client, 'C04SJDDSYHG')
# print([get_member_name(client, x) for x in member_ids])

sample_members = [
    {"member_id": "U0397UJ27FG", "name": "주정민"}, 
    {"member_id": "U0397UJ7MK8", "name": "정원혁"}, 
    {"member_id": "U039BMT9DU5", "name": "오연주"}, 
    {"member_id": "U039EJ6FUJW", "name": "이강훈"}, 
    {"member_id": "U039T6YQW6M", "name": "박종익"}, 
    {"member_id": "U03S0PYHP32", "name": "홍선아"}, 
    {"member_id": "U04K82RFBAS", "name": "김소정"}, 
    {"member_id": "U04SCG3PQNB", "name": "진형민"}, 
    {"member_id": "U04SP9YMVC6", "name": "이웅원"}, 
    {"member_id": "U04SS8PFL0N", "name": "방태모"}
]

# Private 채널은 Group:read 권한이 필요한데, 현재 봇에 해당 권한이 없음
def get_message_from_conversation(client: WebClient, channel_id:str) -> dict:
    api_response = client.conversations_history(channel=channel_id, limit=3)
    return api_response.data['messages']

# https://playinpap.slack.com/archives/C04SJDDSYHG/p1680324093763889
# p1680324093763889 여기서 앞에 p 제거후 뒤쪽 숫자 6자리 앞에 . 을 붙이면 ts값이 되는 듯
# p1680324093763889 => 1680324093.763889
# pprint(get_message_from_conversation(client, 'C04SJDDSYHG'))

def get_replies_from_ts(client: WebClient, channel_id:str, ts: str) -> dict:
    """
    - 특정 스레드에서 답장을 누가 달았는지, 어떤 이모지가 달려있는지 체크
    - ts와 thread_ts가 같을 경우 스레드 본문이기 때문에 제거
    - 댓글 작성자가 직접 붙인 이모지에만 반응
    
    output:
        [{'reactions': [], 'user': 'U04T7SZ0U1J'},
        {'reactions': [], 'user': 'U04T7SZ0U1J'},
        {'reactions': ['melting_face'], 'user': 'U02C4SP56H2'},
        {'reactions': [], 'user': 'U04T7SZ0U1J'}]
    """
    api_response = client.conversations_replies(channel=channel_id, ts=ts)
    if api_response.get('subtype') == 'bot_message':
        return []
    replies = list(filter(lambda m: m['ts'] != m['thread_ts'], api_response['messages']))
    
    def extract_reactions_from_reply(reply: dict) -> list:
        reactions = reply.get('reactions', [])
        reactions_from_replier = list(filter(lambda r: reply['user'] in r['users'], reactions))
        emojis_from_replier = [reply['name'] for reply in reactions_from_replier]
        return emojis_from_replier
    result = [{
        'user': reply['user'],
        'reactions': extract_reactions_from_reply(reply),
        'time': timestamp_to_date(float(reply['ts']))
        } for reply in replies]
    return result

# pprint(get_replies_from_ts(client, 'C04SJDDSYHG', '1680698243.235909'))

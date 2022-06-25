import os
import datetime
import re
from tracemalloc import start
from pytz import timezone
import time
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
import slack_sdk 


# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)


class SlackClient:
    def __init__(self):
        self.client = slack_sdk.WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
        self.bot_member_id = 'B038XBVR57V'

    def get_channel_id(self, channel_name):
        channel_infos = self.client.conversations_list()
        channel_id_name_map = ({channel_info['name']: channel_info['id'] for channel_info in channel_infos['channels']})
        return channel_id_name_map.get(channel_name)

    def get_channel_member_ids(self, channel_id):
        return self.client.conversations_members(channel=channel_id)['members']

    def get_channel_member_name(self, member_id):
        display_name = self.client.users_info(user=member_id)['user']['profile']['display_name']
        real_name = self.client.users_info(user=member_id)['user']['real_name']
        return display_name if display_name != '' else real_name

    def get_channel_messages(self, channel_id, start_date, end_date):
        start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        start_time = datetime.datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)
        start_time = start_time - datetime.timedelta(hours=9)
        start_time = time.mktime(start_time.timetuple())
        end_time = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_time = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59, 59)
        end_time = end_time - datetime.timedelta(hours=9)
        end_time = time.mktime(end_time.timetuple())
        response = self.client.conversations_history(channel=channel_id, oldest=start_time, latest=end_time)
        return response.data['messages']

    def get_emoji_used_member_ids(self, channel_id, start_date, end_date, emoji_name):
        messages = self.get_channel_messages(channel_id=channel_id, start_date=start_date, end_date=end_date)
        messages = [message for message in messages if ('client_msg_id' in message) and ('reactions' in message)]
        member_ids = []
        for message in messages:
            emojis = set([reaction['name'] for reaction in message['reactions']])
            if emoji_name in emojis:
                member_ids.append(message['user'])
        return list(set(member_ids))

    def get_submit_links(self, channel_id, start_date, end_date):
        messages = self.get_channel_messages(channel_id=channel_id, start_date=start_date, end_date=end_date)
        messages = [message for message in messages if ('client_msg_id' in message) and ('reactions' in message)]
        submit_links = {}
        for message in messages:
            emojis = set([reaction['name'] for reaction in message['reactions']])
            if 'submit' in emojis:
                response = self.client.chat_getPermalink(channel=channel_id, message_ts=message['ts'])
                submit_links[message['user']] = response.data['permalink']
        return submit_links

    def get_notice_message(self, channel_id, start_date, end_date):
        messages = self.get_channel_messages(
            channel_id=channel_id, start_date=start_date, end_date=end_date)
        bot_messages = [message for message in messages
            if ('bot_id' in message) and (message['bot_id'] == self.bot_member_id)]
        if len(bot_messages) <= 0:
            raise Exception(f'PAP 피드백봇을 찾을 수 없습니다.(기간: {start_date}-{end_date})')
        return bot_messages[-1]

    def get_feedback_assignments_data(self, notice_message):
        feedback_assignments = []
        lines = notice_message['text'].split('\n')
        lines = [line for line in lines if '•' in line]
        for line in lines:
            mentions = re.findall('\<@(.*?)\>', line)
            reviewers = mentions[:-1]
            reviewee = mentions[-1]
            for reviewer in reviewers:
                feedback_assignments.append({
                    'reviewer': reviewer,
                    'reviewee': reviewee,
                    'feedback_done': 'N'
                })
        return pd.DataFrame(feedback_assignments)

    def get_replies(self, channel_id, thread_timestamp):
        response = self.client.conversations_replies(
            channel=channel_id, ts=thread_timestamp)
        return [message for message in response.data['messages'] if message.get('subtype') != 'bot_message']

    def get_feedbacks(self, channel_id, thread_timestamp):
        response = self.client.conversations_replies(
            channel=channel_id, ts=thread_timestamp)
        replies = [message for message in response.data['messages'] if message.get('subtype') != 'bot_message']
        feedbacks = []
        for reply in replies:
            if 'reactions' not in reply:
                continue
            emojis = set([reaction['name'] for reaction in reply['reactions']])
            if 'feedback' in emojis:
                feedbacks.append(reply)
        return feedbacks

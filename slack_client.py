import os
import datetime
import time
from pathlib import Path

from dotenv import load_dotenv
import slack_sdk 


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class SlackClient:
    def __init__(self):
        self.client = slack_sdk.WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))

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
        start_time = time.mktime(datetime.datetime.strptime(start_date, '%Y-%m-%d').timetuple())
        end_time = time.mktime(datetime.datetime.strptime(end_date, '%Y-%m-%d').timetuple())
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

import requests
from bs4 import BeautifulSoup
import pandas as pd
# from datetime import datetime, timedelta


class CrawlingClient:
    def __init__(self,url):
        self.url = url
        # self.client = slack_sdk.WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
 

    def get_authors_page (self):
        # 작가 페이지: https://playinpap.github.io/authors
        req  = requests.get(self.url + "authors")
        html = req.text
        soup = BeautifulSoup(html, "html.parser") # BeautifulSoup으로 htlml소스를 python 객체로 변환

        # 페이지 소스 복사
        authors_page = soup.select('div.css-ucm7br > h2 > a')
        
        return authors_page
    
    def get_posts (self, authors_page):
        author_names = []
        posts = []
        post_dates = []
        subject = []

        for block in authors_page:
            # author 이름
            name = block.text
            # author별 페이지
            req = requests.get(self.url + block.attrs['href'])
            html = req.text
            soup = BeautifulSoup(html, "html.parser")
            posts_page = soup.select('div > article > a')
            posts_date = soup.select('div.css-1woe70d')

            #author별 포스트 
            for post,date in zip(posts_page, posts_date):
                post_dates.append(date.text)
                posts.append(self.url[:-1] + post.attrs['href'])
                subject.append(post.attrs['aria-label'])
                author_names.append(name)

        result = list(zip(post_dates, author_names, posts, subject))
        return result
    
    def get_lastweek_df (self, result, last_week, today):
        # raw_df 만들기
        df_raw = pd.DataFrame(result, columns = ['글 작성 날짜','성명','URL','글제목'])
        # 날짜 형식 변경
        df_raw['업데이트 날짜'] = today.strftime("%Y.%m.%d")
        df_raw['글 작성 날짜'] = df_raw['글 작성 날짜'].apply(lambda x: x.replace('-','.'))
        # 형식 맞추기
        df_total    = df_raw.iloc[:,[4,0,1,2,3]].sort_values(by = ['글 작성 날짜','성명'], ascending = [False,True])
        df_lastweek = df_total[(last_week <= pd.to_datetime(df_total['글 작성 날짜'])) & (pd.to_datetime(df_total['글 작성 날짜']) <= today)]
        return df_total, df_lastweek

        


    # def get_raw_data (self,)
    # def get_channel_id(self, channel_name):
    #     channel_infos = self.client.conversations_list()
    #     channel_id_name_map = ({channel_info['name']: channel_info['id'] for channel_info in channel_infos['channels']})
    #     return channel_id_name_map.get(channel_name)

    # def get_channel_member_ids(self, channel_id):
    #     return self.client.conversations_members(channel=channel_id)['members']

    # def get_channel_member_name(self, member_id):
    #     display_name = self.client.users_info(user=member_id)['user']['profile']['display_name']
    #     real_name = self.client.users_info(user=member_id)['user']['real_name']
    #     return display_name if display_name != '' else real_name

    # def get_channel_messages(self, channel_id, start_date, end_date):
    #     start_time = time.mktime(datetime.datetime.strptime(start_date, '%Y-%m-%d').timetuple())
    #     end_time = time.mktime(datetime.datetime.strptime(end_date, '%Y-%m-%d').timetuple())
    #     response = self.client.conversations_history(channel=channel_id, oldest=start_time, latest=end_time)
    #     return response.data['messages']

    # def get_emoji_used_member_ids(self, channel_id, start_date, end_date, emoji_name):
    #     messages = self.get_channel_messages(channel_id=channel_id, start_date=start_date, end_date=end_date)
    #     messages = [message for message in messages if ('client_msg_id' in message) and ('reactions' in message)]
    #     member_ids = []
    #     for message in messages:
    #         emojis = set([reaction['name'] for reaction in message['reactions']])
    #         if emoji_name in emojis:
    #             member_ids.append(message['user'])
    #     return list(set(member_ids))

    # def get_submit_links(self, channel_id, start_date, end_date):
    #     messages = self.get_channel_messages(channel_id=channel_id, start_date=start_date, end_date=end_date)
    #     messages = [message for message in messages if ('client_msg_id' in message) and ('reactions' in message)]
    #     submit_links = {}
    #     for message in messages:
    #         emojis = set([reaction['name'] for reaction in message['reactions']])
    #         if 'submit' in emojis:
    #             response = self.client.chat_getPermalink(channel=channel_id, message_ts=message['ts'])
    #             submit_links[message['user']] = response.data['permalink']
    #     return submit_links

import pandas as pd

from slack_client import SlackClient
from google_sheet_client import GoogelSheetClient
from utils import get_submission_dates


slack_client = SlackClient()
publisher_channel_id = slack_client.get_channel_id(channel_name='season2-team-publishers')
member_ids = slack_client.get_channel_member_ids(channel_id=publisher_channel_id)
exempt_list = [
    # 제외할 멤버
    'U02BXMB8GA2', 
    'U02CATHPX7D', 
    'U02JX5ME67N', 
    'U02JX5MF90C', 
    'U02CALV5458', 
    'U02BLC9Q495', 
    'U02C4SP56H2', 
    'U02CB8YQXQ9', 
    # PAP 정산봇
    'U03AW2YHCRY', 
]
member_ids = [member_id for member_id in member_ids if member_id not in exempt_list]
member_names = [slack_client.get_channel_member_name(member_id=member_id) for member_id in member_ids]

dataframes = []
submission_dates = get_submission_dates(start_date='2022-04-01', end_date='2022-09-30', submission_date=15)
for submission_date in submission_dates:
    dataframes.append(pd.DataFrame({
        'slackID': member_ids,
        '성명': member_names,
        '제출기한': [submission_date] * len(member_names),
        '제출여부': [None] * len(member_names),
        '패스사용여부': [None] * len(member_names),
    }))
df = pd.concat(dataframes)
google_sheet_client = GoogelSheetClient()
worksheet = google_sheet_client.get_worksheet()
worksheet.update([df.columns.values.tolist()] + df.values.tolist())
print('complete!')

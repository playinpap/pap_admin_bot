import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

from slack_client import SlackClient
from google_sheet_client import GoogelSheetClient


submission_date = 15
due_date = (datetime.datetime.now().date().replace(day=submission_date))
beginning_date = (due_date - relativedelta(months = 1) + relativedelta(days = 1))
due_date = due_date.strftime('%Y-%m-%d')
beginning_date = beginning_date.strftime('%Y-%m-%d')

slack_client = SlackClient()
publisher_channel_id = slack_client.get_channel_id(channel_name='season2-team-publishers')
submit_member_ids = slack_client.get_emoji_used_member_ids(
    channel_id=publisher_channel_id, start_date=beginning_date, end_date=due_date, emoji_name='submit')
pass_member_ids = slack_client.get_emoji_used_member_ids(
    channel_id=publisher_channel_id, start_date=beginning_date, end_date=due_date, emoji_name='pass')

google_sheet_client = GoogelSheetClient()
worksheet = google_sheet_client.get_worksheet('제출현황')
data = pd.DataFrame(worksheet.get_all_records())
data.loc[(data['slackID'].isin(submit_member_ids)) & (data['제출기한'] == due_date), '제출여부'] = 'Y'
data.loc[(~data['slackID'].isin(submit_member_ids)) & (data['제출기한'] == due_date), '제출여부'] = 'N'
data.loc[(data['slackID'].isin(pass_member_ids)) & (data['제출기한'] == due_date), '패스사용여부'] = 'Y'
data.loc[(~data['slackID'].isin(pass_member_ids)) & (data['제출기한'] == due_date), '패스사용여부'] = 'N'
worksheet.update([data.columns.values.tolist()] + data.values.tolist())
print('complete!')
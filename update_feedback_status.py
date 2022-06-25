import re
import datetime
import pandas as pd
from collections import defaultdict

from slack_client import SlackClient
from google_sheet_client import GoogelSheetClient


current_time = datetime.datetime.now().date()
last_week_start_date = current_time - datetime.timedelta(current_time.weekday()) - datetime.timedelta(days=7)
last_week_end_date = last_week_start_date + datetime.timedelta(days=6)
last_week_start_date = last_week_start_date.strftime('%Y-%m-%d')
last_week_end_date = last_week_end_date.strftime('%Y-%m-%d')

slack_client = SlackClient()
publisher_channel_id = slack_client.get_channel_id(channel_name='season2-team-publishers')
notice_message = slack_client.get_notice_message(
    channel_id=publisher_channel_id, start_date=last_week_start_date, end_date=last_week_end_date)
feedback_assignments_data = slack_client.get_feedback_assignments_data(notice_message)
feedbacks = slack_client.get_feedbacks(channel_id=publisher_channel_id, thread_timestamp=notice_message['ts'])
for feedback in feedbacks:
    reviewer = feedback['user']
    reviewee = re.search('\<@(.*?)\>', feedback['text']).group().replace('<@', '').replace('>', '')
    feedback_assignments_data.loc[
        (feedback_assignments_data['reviewer'] == reviewer) &
        (feedback_assignments_data['reviewee'] == reviewee), 'feedback_done'] = 'Y'

google_sheet_client = GoogelSheetClient()
worksheet = google_sheet_client.get_worksheet('제출현황')
data = pd.DataFrame(worksheet.get_all_records())
raw_data_columns = [column for column in data.columns if column != '차감예치금']
data = data[raw_data_columns]

this_due_date = data[data['제출여부'] != ''].iloc[-1]['제출기한']
for _, row in feedback_assignments_data.iterrows():
    reviewer = slack_client.get_channel_member_name(row['reviewer'])
    reviewee = slack_client.get_channel_member_name(row['reviewee'])
    reviewee1 = data.loc[(data['제출기한'] == this_due_date) & (data['성명'] == reviewer), '피드백대상자1'].iloc[0]
    reviewee2 = data.loc[(data['제출기한'] == this_due_date) & (data['성명'] == reviewer), '피드백대상자2'].iloc[0]
    if reviewee1 == reviewee:
        data.loc[(data['제출기한'] == this_due_date) & (data['성명'] == reviewer), '피드백여부1'] = row['feedback_done']
    if reviewee2 == reviewee:
        data.loc[(data['제출기한'] == this_due_date) & (data['성명'] == reviewer), '피드백여부2'] = row['feedback_done']

worksheet.update([raw_data_columns] + data.values.tolist())
print('complete!')
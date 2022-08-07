import re
import datetime
import pandas as pd
from collections import defaultdict

from slack_client import SlackClient
from google_sheet_client import GoogelSheetClient
from tabulate import tabulate


# 기간 설정
current_time = datetime.datetime.now().date()
last_week_start_date = current_time - datetime.timedelta(current_time.weekday()) - datetime.timedelta(days=7)
last_week_end_date = last_week_start_date + datetime.timedelta(days=6)

submission_date = 15
submission_month = last_week_start_date.month - 1 \
    if last_week_start_date.day < submission_date else last_week_start_date.month
this_due_date = datetime.datetime(last_week_start_date.year, submission_month, submission_date)

last_week_start_date = last_week_start_date.strftime('%Y-%m-%d')
last_week_end_date = last_week_end_date.strftime('%Y-%m-%d')
this_due_date = this_due_date.strftime('%Y-%m-%d')

# 피드백 현황 가져오기  
slack_client = SlackClient()
publisher_channel_id = slack_client.get_channel_id(channel_name='season2-team-publishers')
notice_message = slack_client.get_notice_message(
    channel_id=publisher_channel_id, start_date=last_week_start_date, end_date=last_week_end_date)
feedback_assignments_data = slack_client.get_feedback_assignments_data(notice_message)
feedbacks = slack_client.get_feedbacks(channel_id=publisher_channel_id, thread_timestamp=notice_message['ts'])
for feedback in feedbacks:
    reviewer = feedback['user']
    matched = re.search('\<@(.*?)\>', feedback['text'])
    if not matched:
        print(f'피드백 작성자: {slack_client.get_channel_member_name(reviewer)}님 - 멘션이 포함되지 않은 피드백입니다.')
        continue
    reviewee = matched.group().replace('<@', '').replace('>', '')
    feedback_assignments_data.loc[
        (feedback_assignments_data['reviewer'] == reviewer) &
        (feedback_assignments_data['reviewee'] == reviewee), 'feedback_done'] = 'Y'

# 피드백 현황 확인
feedback_assignments_data['reviewer_name'] = feedback_assignments_data['reviewer'].map(lambda x: slack_client.get_channel_member_name(x))
feedback_assignments_data['reviewee_name'] = feedback_assignments_data['reviewee'].map(lambda x: slack_client.get_channel_member_name(x))
print('피드백 현황)')
print(tabulate(feedback_assignments_data[['reviewer_name', 'reviewee_name', 'feedback_done']], headers='keys', tablefmt='psql'))

# 시트 데이터 업데이트     
google_sheet_client = GoogelSheetClient()
worksheet = google_sheet_client.get_worksheet('제출현황')
data = pd.DataFrame(worksheet.get_all_records())
raw_data_columns = [column for column in data.columns if column != '차감예치금']
data = data[raw_data_columns]

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
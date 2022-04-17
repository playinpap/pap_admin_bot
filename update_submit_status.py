import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter

from slack_client import SlackClient
from google_sheet_client import GoogelSheetClient


# 기간 설정
submission_date = 15
due_date = (datetime.datetime.now().date().replace(day=submission_date))
beginning_date = (due_date - relativedelta(months = 1) + relativedelta(days = 1))
due_date = due_date.strftime('%Y-%m-%d')
beginning_date = beginning_date.strftime('%Y-%m-%d')

# 슬랙 제출, 패스 이모지 데이터 조회
slack_client = SlackClient()
publisher_channel_id = slack_client.get_channel_id(channel_name='season2-team-publishers')
submit_member_ids = slack_client.get_emoji_used_member_ids(
    channel_id=publisher_channel_id, start_date=beginning_date, end_date=due_date, emoji_name='submit')
pass_member_ids = slack_client.get_emoji_used_member_ids(
    channel_id=publisher_channel_id, start_date=beginning_date, end_date=due_date, emoji_name='pass')

# 구글 스프레드 시트 제출현황 업데이트
google_sheet_client = GoogelSheetClient()
worksheet = google_sheet_client.get_worksheet('제출현황')
data = pd.DataFrame(worksheet.get_all_records())
raw_data_columns = [column for column in data.columns if column != '차감예치금']
data = data[raw_data_columns]

data.loc[(data['slackID'].isin(submit_member_ids)) & (data['제출기한'] == due_date), '제출여부'] = 'Y'
data.loc[(~data['slackID'].isin(submit_member_ids)) & (data['제출기한'] == due_date), '제출여부'] = 'N'
data.loc[(data['slackID'].isin(pass_member_ids)) & (data['제출기한'] == due_date), '패스사용여부'] = 'Y'
data.loc[(~data['slackID'].isin(pass_member_ids)) & (data['제출기한'] == due_date), '패스사용여부'] = 'N'

# 피드백대상자 배정
reviewers = data.loc[(data['패스사용여부'] != 'Y') & (data['제출기한'] == due_date), 'slackID'].tolist()
assign_count_map = {member_id: 0 for member_id in submit_member_ids}
assign_count_map = Counter(assign_count_map)

feedback_start_date = '2022-06-15'
if datetime.datetime.strptime(feedback_start_date, '%Y-%m-%d') <= datetime.datetime.strptime(due_date, '%Y-%m-%d'):
    review_assignments = []
    for reviewer in reviewers:
        assign_counts = assign_count_map.most_common()
        reviewees = [assign_count[0] for assign_count in assign_counts if assign_count[0] != reviewer]
        first_reviewee = reviewees[-1]
        second_reviewee = reviewees[-2]
        assign_count_map.update({first_reviewee: 1})
        assign_count_map.update({second_reviewee: 1})
        review_assignments.append({
            "slackID": reviewer,
            "피드백대상자1": slack_client.get_channel_member_name(member_id=first_reviewee),
            "피드백대상자2": slack_client.get_channel_member_name(member_id=second_reviewee),
        })
    review_assignments_data = pd.DataFrame(review_assignments)
    review_assignments_data = review_assignments_data.set_index('slackID')

    data.loc[data['제출기한'] == due_date, '피드백대상자1'] = \
        data['slackID'].map(review_assignments_data['피드백대상자1']).fillna('-')
    data.loc[data['제출기한'] == due_date, '피드백대상자2'] = \
        data['slackID'].map(review_assignments_data['피드백대상자2']).fillna('-')

worksheet.update([raw_data_columns] + data.values.tolist())
print('complete!')
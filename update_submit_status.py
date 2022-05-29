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

google_sheet_client = GoogelSheetClient()
publisher_info_sheet = google_sheet_client.get_worksheet('publisher_info')
publisher_info_data = pd.DataFrame(publisher_info_sheet.get_all_records())
pass_available_members = publisher_info_data.loc[publisher_info_data['잔여패스수'] > 0, 'slackID'].tolist()
pass_member_ids = [pass_member_id for pass_member_id in pass_member_ids if pass_member_id in pass_available_members]

# 구글 스프레드 시트 제출현황 업데이트
worksheet = google_sheet_client.get_worksheet('제출현황')
data = pd.DataFrame(worksheet.get_all_records())
raw_data_columns = [column for column in data.columns if column != '차감예치금']
data = data[raw_data_columns]

data.loc[(data['slackID'].isin(submit_member_ids)) & (data['제출기한'] == due_date), '제출여부'] = 'Y'
data.loc[(~data['slackID'].isin(submit_member_ids)) & (data['제출기한'] == due_date), '제출여부'] = 'N'
data.loc[(data['slackID'].isin(pass_member_ids)) & (data['제출기한'] == due_date), '패스사용여부'] = 'Y'
data.loc[(~data['slackID'].isin(pass_member_ids)) & (data['제출기한'] == due_date), '패스사용여부'] = 'N'

# 피드백대상자 배정
feedback_start_date = '2022-06-15'
if datetime.datetime.strptime(feedback_start_date, '%Y-%m-%d') <= datetime.datetime.strptime(due_date, '%Y-%m-%d'):
    reviewers = data.loc[(data['패스사용여부'] != 'Y') & (data['제출기한'] == due_date), 'slackID'].tolist()
    assign_counter = {member_id: 0 for member_id in submit_member_ids}
    assign_counter = Counter(assign_counter)

    review_assignments = []
    for reviewer in reviewers:
        assign_count_by_reviewee = assign_counter.most_common()
        reviewees = [reviewee for reviewee, assign_count in assign_count_by_reviewee if reviewee != reviewer]
        lowest_assign_count_member = reviewees[-1]
        second_lowest_assign_count_member = reviewees[-2]
        assign_counter.update({lowest_assign_count_member: 1})
        assign_counter.update({second_lowest_assign_count_member: 1})
        review_assignments.append({
            "slackID": reviewer,
            "피드백대상자1": slack_client.get_channel_member_name(member_id=lowest_assign_count_member),
            "피드백대상자2": slack_client.get_channel_member_name(member_id=second_lowest_assign_count_member),
        })
    review_assignments_data = pd.DataFrame(review_assignments).set_index('slackID')

    data.loc[data['제출기한'] == due_date, '피드백대상자1'] = \
        data['slackID'].map(review_assignments_data['피드백대상자1']).fillna('-')
    data.loc[data['제출기한'] == due_date, '피드백대상자2'] = \
        data['slackID'].map(review_assignments_data['피드백대상자2']).fillna('-')

    # 멤버별 리뷰 수 및 리뷰 못 받는 멤버 유무 체크
    review_count_by_reviewee1 = data[data['제출기한'] == due_date].groupby('피드백대상자1')['성명'].count() \
        .reset_index().rename(columns={'피드백대상자1': '피드백대상자'})
    review_count_by_reviewee2 = data[data['제출기한'] == due_date].groupby('피드백대상자2')['성명'].count() \
        .reset_index().rename(columns={'피드백대상자2': '피드백대상자'})
    review_count_by_reviewee = pd.concat([review_count_by_reviewee1, review_count_by_reviewee2])
    review_count_by_reviewee = review_count_by_reviewee.groupby('피드백대상자', as_index=False)['성명'].sum() \
        .rename(columns={'성명': '인원수'})
    print(review_count_by_reviewee)
    submit_members = set([slack_client.get_channel_member_name(member_id) for member_id in submit_member_ids])
    reviewees = set(review_count_by_reviewee['피드백대상자'].tolist())
    print('리뷰 못 받는 멤버 유무 체크', submit_members - reviewees)

worksheet.update([raw_data_columns] + data.values.tolist())
print('complete!')
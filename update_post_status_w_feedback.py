import pandas as pd
from datetime import datetime, timedelta
from google_sheet_client import GoogelSheetClient
from crawling_client import CrawlingClient
import utils

google_sheet_client = GoogelSheetClient()

# 날짜 설정-----------------------------------
date_sheet = google_sheet_client.get_worksheet('배포날짜')
today = (datetime.today()).strftime('%Y-%m-%d')
# today = datetime(2022,6,21).strftime('%Y-%m-%d')
sdate, edate, submit_date = utils.get_posting_dates(date_sheet, today)
submit_date = submit_date.strftime('%Y-%m-%d')

print(" 제출일: {}, 집계일: {} ~ {}".format(submit_date,sdate, edate))

# 피드백 대상자 확인 ----------------------------
sheet_submit   = google_sheet_client.get_worksheet('제출현황')
df_feedback    = pd.DataFrame(sheet_submit.get_all_records())[['성명','제출기한','피드백대상자1', '피드백대상자2']]
df_feedback    = df_feedback[df_feedback['제출기한']== submit_date]

# 크롤링--------------------------------------
crawling_client = CrawlingClient("https://playinpap.github.io/")
authors_page    = crawling_client.get_authors_page()
crawling_result = crawling_client.get_posts(authors_page)

df_total, df_thisweek     = crawling_client.get_lastweek_df(crawling_result, last_week = sdate, today = edate)
# df_thisweek = df_total.head(5)

# 구글시트 저장----------------------------------
sheet_slackID     = google_sheet_client.get_worksheet("publisher_info")
df_slackid        = pd.DataFrame(sheet_slackID.get_all_records())[['성명','slackID']]
df_thisweek_final = pd.merge(df_thisweek, df_slackid, left_on = '성명', right_on = '성명', how = 'inner')

df_feedback_slackid1 = pd.merge(df_feedback, df_slackid, left_on = "피드백대상자1", right_on="성명", how="inner")
df_feedback_slackid2 = pd.merge(df_feedback_slackid1, df_slackid, left_on = "피드백대상자2", right_on="성명", how="inner")
df_feedback_slackid  = df_feedback_slackid2.drop(['성명_y', '성명'],axis=1)

df_thisweek_feedback = pd.merge(df_thisweek_final, df_feedback_slackid, left_on="성명", right_on="성명_x", how="inner")
df_thisweek_feedback_final = df_thisweek_feedback.drop(["성명_x", "제출기한"],axis=1)

if sdate != pd.to_datetime('1899-01-01'): # 집계일이면 데이터 업데이트
    sheet_posting = google_sheet_client.get_worksheet('블로그게시현황')
    sheet_posting.clear()         # 기존 데이터 삭제
    
    sheet_posting.update([df_thisweek_feedback_final.columns.values.tolist()] + df_thisweek_feedback_final.values.tolist())
    print("crawling posts complete!")
else: #집계일이 아니면 skip
    print('skip crawling!')
    


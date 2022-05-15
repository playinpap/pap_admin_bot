import pandas as pd
from datetime import datetime, timedelta
from google_sheet_client import GoogelSheetClient
from crawling_client import CrawlingClient
import utils

google_sheet_client = GoogelSheetClient()

# 날짜 설정-----------------------------------
sheet = google_sheet_client.get_worksheet('시트6')
today = (datetime.today()).strftime('%Y-%m-%d')
# today = datetime(2022,4,18).strftime('%Y-%m-%d')
sdate, edate = utils.get_posting_dates(sheet, today)
print("집계일: {} ~ {}".format(sdate, edate))

# 크롤링--------------------------------------
crawling_client = CrawlingClient("https://playinpap.github.io/")
authors_page    = crawling_client.get_authors_page()
crawling_result = crawling_client.get_posts(authors_page)

df_total, df_thisweek     = crawling_client.get_lastweek_df(crawling_result, last_week = sdate, today = edate)

# 구글시트 저장----------------------------------
sheet_slackID     = google_sheet_client.get_worksheet("publisher_info")
df_slackid        = pd.DataFrame(sheet_slackID.get_all_records())[['성명','slackID']]
df_thisweek_final = pd.merge(df_thisweek, df_slackid, left_on = '성명', right_on = '성명', how = 'inner')

if sdate != pd.to_datetime('1899-01-01'): # 집계일이면 데이터 업데이트
    sheet_posting = google_sheet_client.get_worksheet('블로그게시현황')
    sheet_posting.clear()         # 기존 데이터 삭제
    sheet_posting.update([df_thisweek_final.columns.values.tolist()] + df_thisweek_final.values.tolist())
    print("crawling posts complete!")
else: #집계일이 아니면 skip
    print('skip crawling!')
    

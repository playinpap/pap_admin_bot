import pandas as pd
from datetime import datetime, timedelta
from google_sheet_client import GoogelSheetClient
from crawling_client import CrawlingClient

today = datetime(2021,12,31)
today     = datetime.today()
last_week = (today - timedelta(days = 7))
print("집계일: {} ~ {}".format(last_week.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")))

# 크롤링--------------------------------------
crawling_client = CrawlingClient("https://playinpap.github.io/")
authors_page    = crawling_client.get_authors_page()
crawling_result = crawling_client.get_posts(authors_page)
df_total, df_thisweek     = crawling_client.get_lastweek_df(crawling_result, last_week = last_week, today = today)

## 구글시트 저장----------------------------------
google_sheet_client = GoogelSheetClient()
sheet_slackID     = google_sheet_client.get_worksheet("publisher_info")
df_slackid        = pd.DataFrame(sheet_slackID.get_all_records())[['성명','slackID']]
df_thisweek_final = pd.merge(df_thisweek, df_slackid, left_on = '성명', right_on = '성명', how = 'inner')

sheet_posting = google_sheet_client.get_worksheet('블로그게시현황')
sheet_posting.delete_rows(1,100)          # 기존 데이터 삭제
sheet_posting.update([df_thisweek_final.columns.values.tolist()] + df_thisweek_final.values.tolist())
print("crawling posts complete!")

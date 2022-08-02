#------------------------------------------
# 수정 사항
# 2022-08-22 피드백 대상자 1,2에 NaN이 있어서 오류 ->inner join으로 수정
#------------------------------------------
import numpy as np
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

# 테이블 형식에 맞게 바꾸기 ------------------------
sheet_slackID     = google_sheet_client.get_worksheet("publisher_info")
df_slackid        = pd.DataFrame(sheet_slackID.get_all_records())[['성명','slackID']]

# 저자와 피드백 대상자 1, 2 inner 조인 -> cumcount()로 저자별 리뷰어 수를 세고
df_long = (pd.concat([
    pd.merge(df_thisweek, df_feedback, left_on = '성명', right_on='피드백대상자1',how='inner')
    ,pd.merge(df_thisweek, df_feedback, left_on = '성명', right_on='피드백대상자2',how='inner')
    ],axis=0)
    .sort_values("성명_x").drop(['피드백대상자1','피드백대상자2','제출기한'],axis=1)
)

df_long['idx'] = df_long.groupby('성명_x').cumcount()

# long -> wide로 변경
df_wide = df_long.pivot(index='성명_x',columns='idx', values='성명_y').reset_index()

# 저자 & 리뷰어들의 slackid 조인
for i in range(df_wide.shape[1]):
    df_temp = pd.merge(df_wide, df_slackid, left_on = df_wide.columns[i], right_on = '성명', how = 'left')
    df_wide = df_temp

# 조인 후 중복 컬럼 제외하기 author 성명, author slackid, slackid 1, slackid 2, ...
authors = pd.DataFrame(df_wide.iloc[:,0])
df_wide2 = pd.concat([authors, df_wide.loc[:,~df_wide.T.duplicated()].filter(regex=("slack.*"))], axis=1)
df_wide2.columns =  ['col' + str(x) for x in np.arange(0,len(df_wide2.columns))]

# 최종 테이블
df_thisweek_feedback_final = (
    pd.merge(
        df_thisweek  # 저자 정보
        , df_wide2   # 저자 + 리뷰어 1 ~ n
        , left_on = '성명', right_on = 'col0', how="inner")
    .drop('col0', axis=1)
    .replace(np.nan, '', regex=True)
)

# 데이터 업데이트------------------------------------
if sdate != pd.to_datetime('1899-01-01'): # 집계일이면 데이터 업데이트
    sheet_posting = google_sheet_client.get_worksheet('블로그게시현황')
    sheet_posting.clear()         # 기존 데이터 삭제
    
    sheet_posting.update([df_thisweek_feedback_final.columns.values.tolist()] + df_thisweek_feedback_final.values.tolist())
    print("crawling posts complete!")
else: #집계일이 아니면 skip
    print('skip crawling!')


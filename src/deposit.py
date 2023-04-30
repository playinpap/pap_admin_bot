import duckdb
import json
from data_sheet import get_gspread_service_account, get_worksheet


def get_sheets(spreadsheet: str, worksheet: str, account_getter: callable = get_gspread_service_account):
    google_svc_account = account_getter()
    return get_worksheet(google_svc_account, spreadsheet, worksheet)

def merge_deposits(publishers, posts, feedbacks):
    # DuckDB 에서 쉽게 읽을 수 있도록 json 파일로 변환
    with open('/tmp/publishers.json', 'w') as outfile:
        json.dump(publishers, outfile)
    with open('/tmp/posts.json', 'w') as outfile:
        json.dump(posts, outfile)
    with open('/tmp/feedbacks.json', 'w') as outfile:
        json.dump(feedbacks, outfile)

    # DuckDB로 테이블 Join
    conn = duckdb.connect()
    results = conn.execute("""
        SELECT 
            a.name, 
            COALESCE(b.post_cnt_1, 0) AS post_cnt_1, 
            COALESCE(c.feedback_cnt_1, 0) AS feedback_cnt_1,
            COALESCE(b.post_cnt_2, 0) AS post_cnt_2, 
            COALESCE(c.feedback_cnt_2, 0) AS feedback_cnt_2,
            COALESCE(b.post_cnt_3, 0) AS post_cnt_3, 
            COALESCE(c.feedback_cnt_3, 0) AS feedback_cnt_3,
        FROM '/tmp/publishers.json' AS a
        LEFT JOIN (
            SELECT author_id, 
                COUNT(1) FILTER (WHERE post_group = 1) AS post_cnt_1,
                COUNT(1) FILTER (WHERE post_group = 2) AS post_cnt_2,
                COUNT(1) FILTER (WHERE post_group = 3) AS post_cnt_3
            FROM '/tmp/posts.json'
            GROUP BY author_id
        ) AS b
        ON (a.author_id = b.author_id)
        LEFT JOIN (
            SELECT member_id, 
                COUNT(1) FILTER (WHERE post_group = 1) AS feedback_cnt_1,
                COUNT(1) FILTER (WHERE post_group = 2) AS feedback_cnt_2,
                COUNT(1) FILTER (WHERE post_group = 3) AS feedback_cnt_3,
            FROM '/tmp/feedbacks.json'
            GROUP BY member_id
        ) AS c
        ON (a.member_id = c.member_id)
    """).fetchall()

    return results

def upload_deposits(data):
    print(data)

def run_calculate_deposits():
    publishers = get_sheets('PAP 시즌 2 퍼블리셔 제출 현황', 'season3_publisher')
    posts = get_sheets('PAP 시즌 2 퍼블리셔 제출 현황', 'season3_posts')
    feedbacks = get_sheets('PAP 시즌 2 퍼블리셔 제출 현황', 'season3_feedbacks')
    
    deposits = merge_deposits(publishers, posts, feedbacks)
    upload_deposits(deposits)


if __name__ == '__main__':
    run_calculate_deposits()

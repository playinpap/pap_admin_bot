# pap_admin_bot
​
## 준비
​
1) 모듈 설치
```
pip install -r requirements.txt
```
​
2) 환경변수 설정
​
소스 코드 실행을 위해 슬랙 봇 토큰과 구글 스프레드 시트 API credential 두 가지를 발급받아야 합니다.
슬랙 봇 토큰은 슬랙 API의 앱 관리에서 "OAuth & Permissions > OAuth Tokens for Your Workspace"에서 확인하실 수 있습니다.
참고 링크)
https://miaow-miaow.tistory.com/148
​
구글 스프레드 시트 API를 활용하기 위한 사전 작업은 아래 참고 링크의 "For Bots: Using Service Account" 내용을 참고하시면 됩니다.
과정을 따라가다 보면 json 형태의 credential 파일을 다운로드받을 수 있습니다.
참고 링크)
https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project
​
root 경로에 .env 파일을 생성한 다음 슬랙 봇 토큰과 json 포맷의 credential 파일을 참고해서 아래 정보를 기입해주세요.
```
SLACK_BOT_TOKEN=<슬랙 봇 토큰>
PROJECT_ID=<credential 파일의 "project_id" 속성>
PRIVATE_KEY_ID=<credential 파일의 "private_key_id" 속성>
PRIVATE_KEY=<credential 파일의 "private_key" 속성>
CLIENT_EMAIL=<credential 파일의 "client_email" 속성>
CLIENT_ID=<credential 파일의 "client_id" 속성>
CLIENT_CERT_URL=<credential 파일의 "client_x509_cert_url" 속성>
SPREADSHEET_NAME=<스프레드 시트명>
WORKSHEET_NAME=<워크시트명>
```
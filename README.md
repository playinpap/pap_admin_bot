# pap_admin_bot
​
## 환경 설정
​
### 1) 개발 환경 구성

```bash
# Python 환경 구성
# * Mac 기준으로 작성했기 때문에 brew를 사용했습니다.
# * 이미 세팅된 파이썬 환경이 있으실 경우 해당 환경을 사용하셔도 됩니다.
brew install asdf 
asdf plugin add python
asdf install python 3.11.0

# 디펜던시 설치
pip install poetry
poetry install
```
​
### 2) 환경변수 설정
​
소스 코드 실행을 위해 슬랙 봇 토큰과 구글 스프레드 시트 API credential 두 가지를 발급받아야 합니다.
슬랙 봇 토큰은 슬랙 API의 앱 관리에서 "OAuth & Permissions > OAuth Tokens for Your Workspace"에서 확인하실 수 있습니다.

참고 링크) https://miaow-miaow.tistory.com/148

구글 스프레드 시트 API를 활용하기 위한 사전 작업은 아래 참고 링크의 "For Bots: Using Service Account" 내용을 참고하시면 됩니다.
과정을 따라가다 보면 json 형태의 credential 파일을 다운로드받을 수 있습니다.

참고 링크) https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project

프로젝트 root 경로에 `.env` 파일을 생성한 다음 아래 정보를 기입해주세요.

```
CONTENTFUL_CMA_TOKEN=<Contentful Content Managemennt API 토큰>
CONTENTFUL_SPACE_ID=<Contentful Space ID>
CONTENTFUL_ENVIRONMENT_ID=<Contentful Environment ID>

SLACK_BOT_TOKEN=<슬랙 봇 토큰>

PROJECT_ID=<credential 파일의 "project_id" 속성>
PRIVATE_KEY_ID=<credential 파일의 "private_key_id" 속성>
PRIVATE_KEY=<credential 파일의 "private_key" 속성>
CLIENT_EMAIL=<credential 파일의 "client_email" 속성>
CLIENT_ID=<credential 파일의 "client_id" 속성>
CLIENT_CERT_URL=<credential 파일의 "client_x509_cert_url" 속성>
```

### 3) 스크립트 실행

- `TODO` 각 스크립트를 별도로 돌리는 대신 단일 태스크 러너를 개발하고자 합니다.

```bash
poetry run python src/deposit.py
```

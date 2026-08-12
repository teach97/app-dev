오늘 한눈에 보기

가상환경 → REST API·HTTP → FastAPI → 라우팅 → Swagger 테스트

Python 백엔드의 요청·응답 흐름을 이해하고 첫 API 서버를 구현한 날이었다.

━━━━━━━━━━━━━━━━━━━━

① 가상환경과 실행 준비

​

• 가상환경은 프로젝트별 Python과 패키지를 독립적으로 관리해 버전 충돌을 줄인다.

• Windows에서는 python -m venv .venv로 생성하고, PowerShell에서는 .venv\Scripts\Activate.ps1로 활성화한다.

• 프롬프트에 (.venv)가 표시되는지 확인한 뒤 python --version, python -m pip --version으로 실행 경로를 점검한다.

• fastapi[standard]를 설치하고, 프로젝트가 끝나면 deactivate로 가상환경을 종료한다.

예시 명령어

​

python -m venv .venv

.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install "fastapi[standard]"

fastapi dev main.py

━━━━━━━━━━━━━━━━━━━━

② REST API와 HTTP

​

• API는 프로그램이 서로 데이터를 주고받기 위한 약속이며, 클라이언트의 요청에 서버가 응답하는 구조로 동작한다.

• REST API는 자원을 기준으로 URI를 설계한다. URI에는 동작보다 명사를 사용하고, 보통 소문자와 복수형 컬렉션을 사용한다.

• HTTP 메서드는 자원에 수행할 작업을 나타낸다.

GET: 조회 / POST: 생성 / PUT: 전체 수정 / PATCH: 부분 수정 / DELETE: 삭제

​

• 주요 상태 코드는 200 성공

201 생성

204 내용 없음

400 잘못된 요청

401 인증 필요

403 권한 없음

404 찾을 수 없음

422 입력 검증 실패

500 서버 오류

​

예시 URI

GET /books

GET /books/2

POST /books

PATCH /books/2

DELETE /books/2

━━━━━━━━━━━━━━━━━━━━

③ FastAPI 핵심 구조

​

• FastAPI는 Python 타입 힌트를 활용해 요청 데이터를 검증하고, OpenAPI 기반의 문서와 Swagger UI를 자동으로 제공한다.

• Uvicorn은 FastAPI 애플리케이션을 실행하는 ASGI 서버이다. ASGI는 요청을 기다리는 동안 다른 작업을 처리할 수 있어 비동기 웹 애플리케이션에 적합하다.

• 요청 흐름은 클라이언트 → Uvicorn → FastAPI 라우터 → 함수·비즈니스 로직 → JSON 응답 순서로 이어진다.

​

첫 번째 API 예시

from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")

def say_hello():

return {"message": "안녕하세요"}

@app.post("/echo")

def echo(data: dict):

return {"받은 데이터": data}

━━━━━━━━━━━━━━━━━━━━

④ 첫 API 서버와 라우팅

​

• @app.get(), @app.post() 같은 데코레이터로 HTTP 메서드와 경로를 함수에 연결한다.

• 경로 매개변수는 특정 자원의 식별자에 사용하고, 쿼리 매개변수는 검색·필터·페이지 조건에 사용한다.

• 책 관리 API에서 /books/{book_id}는 도서 한 권을 조회하고, /books/search·/books/filter·/books/page는 검색·필터·페이지 기능을 제공한다.

• 고정 경로는 /books/{book_id}보다 먼저 선언해야 search·filter·page가 숫자형 book_id로 해석되는 문제를 막을 수 있다.

요청 예시

​

GET /books/2

GET /books/search?keyword=파이썬

GET /books/filter?author=김철수&sort=year

GET /books/page?skip=2&limit=2

━━━━━━━━━━━━━━━━━━━━

⑤ Swagger와 웹 연동

​

• 서버를 실행하면 /docs에서 Swagger UI를 열어 각 엔드포인트의 요청과 응답을 브라우저에서 테스트할 수 있다.

• Thunder Client 같은 도구로도 HTTP 요청을 보내 결과와 상태 코드를 확인할 수 있다.

• StaticFiles를 mount하면 HTML·CSS·JavaScript로 만든 정적 화면에서 fetch로 API를 호출할 수 있다.

• 프론트엔드와 API 서버의 주소·포트가 다르면 CORS 문제가 발생할 수 있으므로, 학습 환경에서는 FastAPI의 static 경로로 함께 제공하는 방식을 사용한다.

​

실행 명령어

fastapi dev main.py

uvicorn main:app --reload

uvicorn main:app --host 0.0.0.0 --port 8000

접속 주소: http://127.0.0.1:8000

문서 주소: http://127.0.0.1:8000/docs

━━━━━━━━━━━━━━━━━━━━

⑥ Git과 .gitignore

• .gitignore는 Git이 추적하지 않을 파일과 폴더를 지정하는 설정 파일이다.

• Python 프로젝트에서는 가상환경, 캐시, 환경변수, 로그처럼 로컬에서 생성되거나 공유하면 안 되는 파일을 예외 처리한다.

• 이미 커밋된 파일은 .gitignore에 추가해도 추적이 중단되지 않으므로, git rm --cached <파일명>으로 추적을 해제해야 한다.

예시 .gitignore

가상환경

.venv/

venv/

Python 캐시·테스트

pycache/

*.py[cod]

.pytest_cache/

.mypy_cache/

.ruff_cache/

환경변수·비밀정보

.env

.env.*

!.env.example

로그·개인 설정

*.log

.vscode/

.idea/

.DS_Store

Thumbs.db

필요할 때만 추가

*.db

*.sqlite3

커밋해야 하는 파일

• main.py 등 소스 코드

• requirements.txt 또는 pyproject.toml

• .env.example, README.md

공유하면 안 되는 파일

• .env에 저장한 API 키·비밀번호

• .venv/와 캐시 파일

• 개인 로그·로컬 데이터베이스 파일

━━━━━━━━━━━━━━━━━━━━

⑦ 오늘의 느낀 점

​

오늘은 Python 문법으로 작성한 함수가 HTTP 요청을 받는 API 엔드포인트가 되는 과정을 확인했다. 특히 REST의 자원 중심 설계, 경로·쿼리 매개변수의 역할, FastAPI의 자동 문서와 타입 검증이 연결되면서 백엔드 기능이 어떤 흐름으로 제공되는지 구체적으로 이해할 수 있었다. 또한 정상 응답뿐 아니라 404·422·500 같은 오류 상황까지 확인해야 API를 안정적으로 설계할 수 있다는 점을 배웠다.

━━━━━━━━━━━━━━━━━━━━

⑧ KPT 회고

​

KEEP | 계속 유지할 점

• 가상환경 활성화와 Python·pip 경로를 먼저 확인하는 습관

• Swagger에서 요청을 직접 보내고 상태 코드와 응답을 확인하는 방식

• API를 메서드·경로·입력·응답 단위로 나누어 정리하는 방법

​

PROBLEM | 아쉬웠던 점

• path parameter와 query parameter의 사용 기준을 실제 설계에서 바로 판단하려면 반복이 필요하다.

• FastAPI·Uvicorn·ASGI·OpenAPI의 역할이 연결되어 있어 초반에는 용어가 많게 느껴졌다.

• 라우트 순서, 포트 사용, CORS처럼 코드 외 환경에서 발생하는 오류 대응 경험이 부족하다.

​

TRY | 앞으로 시도할 점

• 책 관리 API에 생성·수정·삭제 기능을 추가해 CRUD 흐름 완성하기

• Pydantic 모델로 요청 데이터와 응답 형식을 명확하게 검증하기

• API 서버와 간단한 웹 화면을 연결하고 오류 응답까지 기록하기

━━━━━━━━━━━━━━━━━━━━

⑨ 다음 학습 목표

​

• FastAPI의 Pydantic 모델과 CRUD 구조 익히기

• API 예외 처리와 입력 검증을 체계적으로 적용하기

• Git으로 API 프로젝트의 변경 이력 관리하기

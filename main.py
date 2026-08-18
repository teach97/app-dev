# FastAPI 서버를 만들 때 필요한 도구를 가져온다.
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
import httpx

# 요청·응답 데이터 모델은 schemas.py에서 가져온다.
from schemas import BookCreate, BookResponse, ExternalBook, WeatherResponse, GoogleBooks
from external_api import fetch_weather, fetch_books, load_fallback_books

tags_metadata = [
    {"name": "시스템", "description": "서버 상태 확인"},
    {"name": "도서", "description": "도서 등록, 조회, 검색"},
    {"name": "외부 연동", "description": "Google Books와 날씨 API 연동"},
    {"name": "학습용", "description": "비동기 동작 확인용 엔드포인트"},
]

app = FastAPI(openapi_tags=tags_metadata)


# FastAPI 애플리케이션 객체를 만든다.
# app = FastAPI()

app = FastAPI(
    title="도서 관리 API",
    description="도서를 등록·조회하고 외부 검색으로 정보를 가져오는 API",
    version="1.0.0",
    contact={"name": "김훈", "email": "rlagns009@example.com"},
    openapi_tags=tags_metadata
)


# static 폴더 안의 HTML 파일을 /static 주소로 공개한다.
# 예: static/09-create-list.html
#     -> http://127.0.0.1:8000/static/09-create-list.html
app.mount("/static", StaticFiles(directory="static"), name="static")


# 실습에 사용하는 도서 데이터다.
# 현재는 데이터베이스 대신 파이썬 리스트에 저장한다.
# 따라서 서버를 종료하면 새로 등록한 데이터는 사라진다.
books = [
    {
        "id": 1,
        "title": "파이썬 입문",
        "author": "김철수",
        "year": 2021,
        "tags": [],
        "publisher": None,
    },
    {
        "id": 2,
        "title": "FastAPI 실전",
        "author": "이영희",
        "year": 2023,
        "tags": [],
        "publisher": None,
    },
    {
        "id": 3,
        "title": "파이썬 웹개발",
        "author": "김철수",
        "year": 2022,
        "tags": [],
        "publisher": None,
    },
    {
        "id": 4,
        "title": "데이터 분석 기초",
        "author": "박민수",
        "year": 2020,
        "tags": [],
        "publisher": None,
    },
    {
        "id": 5,
        "title": "FastAPI로 배우는 백엔드",
        "author": "이영희",
        "year": 2024,
        "tags": [],
        "publisher": None,
    },
]


# -------------------- 기본 정보 API --------------------


# 서버가 정상적으로 실행 중인지 확인하는 기본 주소다.
@app.get(
    "/",
    tags=["시스템"],
    summary="루트",
    response_description="서버 기본 응답",
)
def read_root():
    """서버가 정상적으로 실행 중인지 확인하는 기본 응답을 반환합니다."""
    return {"message": "Hello World!"}


# 서버 상태 확인 API다.
@app.get(
    "/health",
    tags=["시스템"],
    summary="헬스 체크",
    response_description="서버 상태 응답",
)
def health():
    """서버의 현재 상태를 반환합니다."""
    return {"status": "OK"}


# API 이름과 버전을 알려주는 API다.
@app.get(
    "/info",
    tags=["시스템"],
    summary="앱 정보",
    response_description="앱 이름과 버전 정보",
)
def info():
    """도서 관리 API의 이름과 버전을 반환합니다."""
    return {
        "name": "도서 관리 API",
        "version": "0.1.0",
    }


# -------------------- 도서 조회 API --------------------


# 모든 도서 목록을 반환하는 엔드포인트
@app.get(
    "/books",
    response_model=list[BookResponse],
    tags=["도서"],
    summary="도서 목록 조회",
    response_description="등록된 전체 도서 목록",
)
def list_books():
    """내 도서 목록에 등록된 모든 도서를 반환합니다."""
    return books


# 제목에 키워드가 포함된 도서를 검색한다.
@app.get(
    "/books/search",
    tags=["도서"],
    summary="도서 제목 검색",
    response_description="검색 조건에 맞는 도서 목록",
)
def search_books(keyword: str = ""):
    """
    제목에 키워드가 포함된 도서를 반환합니다.

    - **keyword**: 검색할 제목 키워드. 비우면 전체 목록을 반환합니다.
    """
    # 앞뒤 공백을 제거하고 대소문자를 구분하지 않도록 소문자로 바꾼다.
    keyword = keyword.strip().lower()

    return [
        book
        for book in books
        if keyword in book["title"].lower()
    ]


# 저자 이름으로 필터링하고, sort=year이면 연도순으로 정렬한다.
@app.get(
    "/books/filter",
    tags=["도서"],
    summary="도서 필터 및 연도 정렬",
    response_description="필터 및 정렬 결과 도서 목록",
)
def filter_books(keyword: str = "", sort: str = ""):
    """
    키워드로 도서를 필터링하고 연도순으로 정렬합니다.

    - **keyword**: 저자 필터에 사용할 키워드
    - **sort**: `year`이면 출판 연도 오름차순으로 정렬합니다.
    """
    result = books

    # 키워드를 입력한 경우에만 저자 필터를 적용한다.
    if keyword:
        result = [book for book in result if book["author"] == keyword]

    # sort 값이 year일 때만 연도 오름차순으로 정렬한다.
    if sort == "year":
        result = sorted(result, key=lambda book: book["year"])

    return result


# skip만큼 건너뛰고 limit개만 반환하는 페이지네이션 API다.
@app.get(
    "/books/page",
    tags=["도서"],
    summary="도서 페이지네이션",
    response_description="페이지 조건에 해당하는 도서 목록",
)
def page_books(skip: int = 0, limit: int = 2):
    """
    도서 목록을 건너뛰기와 개수 기준으로 나누어 반환합니다.

    - **skip**: 건너뛸 도서 개수
    - **limit**: 반환할 최대 도서 개수
    """
    return books[skip:skip + limit]


# 외부 Google Books API에서 도서를 검색한다.
# 고정된 경로를 동적 경로(/books/{book_id})보다 먼저 선언해야 한다.

# @app.get("/books/external", response_model=list[GoogleBooks])
# async def search_external_books(keyword: str, limit: int = 5):
#     return await fetch_books(keyword, limit)

@app.get(
    "/books/external",
    response_model=list[ExternalBook],
    tags=["외부 연동"],
    summary="Google Books 검색",
    response_description="검색된 외부 도서 목록",
    responses={
        502: {"description": "외부 API 연결 실패 또는 오류 응답"},
        504: {"description": "외부 API 응답 지연"},
    },
)
async def search_external_books(keyword: str, limit: int = 5, fallback: bool = False):
    """
    Google Books API에서 도서를 검색합니다.

    - **keyword**: 검색어
    - **limit**: 가져올 도서 개수. 기본값은 5입니다.
    - **fallback**: 외부 API 실패 시 예비 데이터를 사용할지 여부입니다.

    외부 API 오류는 502, 응답 지연은 504를 반환합니다.
    """
    try:
        return await fetch_books(keyword, limit)
    except httpx.TimeoutException:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=504, detail="외부 API 응답이 지연됩니다")
    except httpx.HTTPStatusError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API가 오류를 반환했습니다")
    except httpx.RequestError:
        if fallback:
            return load_fallback_books()
        raise HTTPException(status_code=502, detail="외부 API에 연결할 수 없습니다")

# 도서 번호로 도서 한 권을 조회한다.
@app.get(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["도서"],
    summary="도서 단건 조회",
    response_description="해당 번호의 도서 정보",
    responses={404: {"description": "해당 번호의 도서가 없습니다"}},
)
def read_book(book_id: int):
    """
    도서 번호로 도서 한 권을 조회합니다.

    - **book_id**: 조회할 도서 번호

    해당 번호의 도서가 없으면 404를 반환합니다.
    """
    for book in books:
        if book["id"] == book_id:
            return book

    # 도서를 찾지 못하면 200이 아니라 404 오류를 반환한다.
    raise HTTPException(
        status_code=404,
        detail="도서를 찾을 수 없습니다",
    )


# -------------------- 도서 등록 API --------------------


# 새로운 도서를 등록한다.
# 클라이언트는 title, author, year 등을 JSON으로 보내고,
# 서버는 새 id를 만들어 저장한 뒤 등록된 도서를 반환한다.
# @app.post ("/books",
#     response_model=BookResponse,
#     status_code=status.HTTP_201_CREATED)

# def create_book(book: BookCreate):
#     # 기존 도서 중 가장 큰 id에 1을 더해 새 id를 만든다.
#     new_id = max(
#         [book["id"] for book in books],
#         default=0,
#     ) + 1

#     # Pydantic 모델을 딕셔너리로 바꾼 뒤 id와 합친다.
#     new_book = {
#         "id": new_id,
#         **book.model_dump(),
#     }

#     # 새 도서를 리스트에 저장한다.
#     books.append(new_book)

#     # 등록 결과를 클라이언트에게 반환한다.
#     return new_book

#12-final

@app.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["도서"],
    summary="도서 등록",
    response_description="등록된 도서 정보",
    responses={409: {"description": "이미 등록된 제목입니다"}},
)

def create_book(book: BookCreate):
    """
    새 도서를 등록합니다.

    - **title**: 1자 이상 100자 이하
    - **author**: 1자 이상 50자 이하
    - **year**: 1900 이상 2100 이하
    - **tags**: 선택 사항인 문자열 목록
    - **publisher**: 선택 사항인 출판사 정보

    - 같은 제목이 이미 있으면 409를 반환합니다.
    """
    for existing_book in books:
        if existing_book["title"] == book.title:
            raise HTTPException(
                status_code=409,
                detail="이미 등록된 제목입니다"
            )

    new_id = max(
        [book["id"] for book in books],
        default=0
    ) + 1

    new_book = {
        "id": new_id,
        **book.model_dump()
    }

    books.append(new_book)

    return new_book

#한눈에 보기
#http://127.0.0.1:8000/static/index.html

# @app.get("/weather/raw")
# async def weather_raw():
#     async with httpx.AsyncClient(timeout=5.0) as client:
#         response = await client.get(
#             "https://api.open-meteo.com/v1/forecast",
#             params={
#                 "latitude": 36.8,
#                 "longitude": 127.1,
#                 "current": "temperature_2m",
#             },
#         )
#         return response.json()

@app.post(
    "/books/from-external",
    response_model=BookResponse,
    status_code=201,
    tags=["도서"],
    summary="외부 검색 결과 등록",
    response_description="내 도서 목록에 등록된 도서 정보",
    responses={409: {"description": "이미 등록된 제목입니다"}},
)
def create_from_external(book: ExternalBook):
    """
    외부 도서 검색 결과를 내 도서 목록에 등록합니다.

    - **title**: 등록할 도서 제목
    - **authors**: 외부 도서의 저자 목록
    - **published_date**: 외부 도서의 발행일

    같은 제목이 이미 있으면 409를 반환합니다.
    """
    for b in books:
        if b["title"] == book.title:
            raise HTTPException(status_code=409, detail="이미 등록된 제목입니다")

    year = 2000
    if book.published_date[:4].isdigit():
        year = int(book.published_date[:4])

    new_id = max([b["id"] for b in books], default=0) + 1
    new_book = {
        "id": new_id,
        "title": book.title,
        "author": book.authors[0] if book.authors else "미상",
        "year": year,
        "tags": ["외부검색"],
        "publisher": None,
    }
    books.append(new_book)
    return new_book

#항상 마지막으로
@app.get(
    "/weather",
    response_model=WeatherResponse,
    tags=["외부 연동"],
    summary="현재 날씨 조회",
    response_description="좌표와 현재 기온 정보",
    responses={
        502: {"description": "외부 API 연결 실패 또는 오류 응답"},
        504: {"description": "외부 API 응답 지연"},
    },
)
async def weather(latitude: float = 36.8, longitude: float = 127.1):
    """
    좌표를 기준으로 현재 날씨를 조회합니다.

    - **latitude**: 위도. 기본값은 36.8입니다.
    - **longitude**: 경도. 기본값은 127.1입니다.

    외부 API 오류는 502, 응답 지연은 504를 반환합니다.
    """
    return await fetch_weather(latitude, longitude)

#     async with httpx.AsyncClient(timeout=5.0) as client:
#         response = await client.get(
#                 "https://api.open-meteo.com/v1/forecast",
#             params={
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "current": "temperature_2m"
#                 },
#         )        
#         data = response.json()
    
#     return WeatherResponse(
#         latitude=data["latitude"],
#         longitude=data["longitude"],
#         temperature=data["current"]["temperature_2m"],
#         time=data["current"]["time"],
# )

# FastAPI 서버를 만들 때 필요한 도구를 가져온다.
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
import httpx

# 요청·응답 데이터 모델은 schemas.py에서 가져온다.
from schemas import BookCreate, BookResponse, BookUpdate, ExternalBook, WeatherResponse, GoogleBooks
from external_api import fetch_weather, fetch_books, load_fallback_books
from database import books, save_books
from routers import system



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

app.include_router(system.router)

# 실습에 사용하는 도서 데이터다.
# 현재는 데이터베이스 대신 파이썬 리스트에 저장한다.
# 따라서 서버를 종료하면 새로 등록한 데이터는 사라진다.


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



# 저자 이름으로 필터링하고, sort=year이면 연도순으로 정렬한다.
@app.get(
    "/books/filter",
    tags=["도서"],
    summary="도서 필터 및 연도 정렬",
    response_description="필터 및 정렬 결과 도서 목록",
)


# skip만큼 건너뛰고 limit개만 반환하는 페이지네이션 API다.
@app.get(
    "/books/page",
    tags=["도서"],
    summary="도서 페이지네이션",
    response_description="페이지 조건에 해당하는 도서 목록",
)


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
    return get_book_or_404(book_id)


# -------------------- 도서 등록 API --------------------

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
    save_books() 

    return new_book

@app.put("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def update_book(book_id: int, book: BookCreate):
    old = get_book_or_404(book_id)
    new_book = {"id": book_id, **book.model_dump()}
    books[books.index(old)] = new_book
    return new_book


@app.patch("/books/{book_id}", response_model=BookResponse, tags=["도서"])
def patch_book(book_id: int, patch: BookUpdate):
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    save_books()
    return book

def patch_book(book_id: int, patch: BookUpdate):
    """
    보낸 필드만 수정합니다. 보내지 않은 필드는 그대로 유지됩니다.
    """
    book = get_book_or_404(book_id)
    book.update(patch.model_dump(exclude_unset=True))
    return book

@app.delete("/books/{book_id}", status_code=204, tags=["도서"])
def delete_book(book_id: int):
    book = get_book_or_404(book_id)
    books.remove(book)
    return None


#한눈에 보기
#http://127.0.0.1:8000/static/index.html

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


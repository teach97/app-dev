# FastAPI 서버를 만들 때 필요한 도구를 가져온다.
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

# BaseModel: 요청 데이터의 형식을 정의할 때 사용한다.
# Field: 글자 수, 숫자 범위 같은 세부 검증 규칙을 추가할 때 사용한다.
from pydantic import BaseModel, Field, field_validator


# 출판사 정보를 표현하는 중첩 모델이다.
class Publisher(BaseModel):
    name: str
    city: str = "부천"  # 도시를 입력하지 않으면 기본값으로 부천을 사용한다.


# 클라이언트가 도서를 등록할 때 보내는 데이터 형식이다.
# id는 서버가 자동으로 만들기 때문에 등록 요청에는 넣지 않는다.
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1900, le=2026)
    tags: list[str] = Field(default_factory=list)
    publisher: Publisher | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()
        # 공백문자열 체크
        if not value:
            raise ValueError("제목은 필수 입력입니다. (공백 불가능)")
        return value


# 서버가 도서를 응답할 때 사용하는 데이터 형식이다.
# 등록 요청 형식(BookCreate)에 id를 추가한 형태다.
class BookResponse(BookCreate):
    id: int


# FastAPI 애플리케이션 객체를 만든다.
app = FastAPI()

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
@app.get("/")
def read_root():
    return {"message": "Hello World!"}


# 서버 상태 확인 API다.
@app.get("/health")
def health():
    return {"status": "healthy"}


# API 이름과 버전을 알려주는 API다.
@app.get("/info")
def info():
    return {
        "name": "도서 관리 API",
        "version": "0.1.0",
    }


# -------------------- 도서 조회 API --------------------


# 모든 도서 목록을 반환한다.
@app.get("/books", response_model=list[BookResponse])
def list_books():
    return books


# 제목에 키워드가 포함된 도서를 검색한다.
@app.get("/books/search")
def search_books(keyword: str = ""):
    # 앞뒤 공백을 제거하고 대소문자를 구분하지 않도록 소문자로 바꾼다.
    keyword = keyword.strip().lower()

    return [
        book
        for book in books
        if keyword in book["title"].lower()
    ]


# 저자 이름으로 필터링하고, sort=year이면 연도순으로 정렬한다.
@app.get("/books/filter")
def filter_books(keyword: str = "", sort: str = ""):
    result = books

    # 키워드를 입력한 경우에만 저자 필터를 적용한다.
    if keyword:
        result = [book for book in result if book["author"] == keyword]

    # sort 값이 year일 때만 연도 오름차순으로 정렬한다.
    if sort == "year":
        result = sorted(result, key=lambda book: book["year"])

    return result


# skip만큼 건너뛰고 limit개만 반환하는 페이지네이션 API다.
@app.get("/books/page")
def page_books(skip: int = 0, limit: int = 2):
    return books[skip:skip + limit]


# 도서 번호로 도서 한 권을 조회한다.
@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int):
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
    status_code=status.HTTP_201_CREATED
)
def create_book(book: BookCreate):
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

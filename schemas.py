from pydantic import BaseModel, Field, field_validator


class Publisher(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="출판사 이름",
        examples=["플레이 출판사"],
    )

    city: str = Field(
        min_length=1,
        max_length=100,
        description="출판사 주소",
        examples=["부천"],
        default="부천",
    )
                
    # 도시를 입력하지 않으면 기본값으로 부천을 사용한다.


# 클라이언트가 도서를 등록할 때 보내는 데이터 형식이다.
# id는 서버가 자동으로 만들기 때문에 등록 요청에는 넣지 않는다.
class BookCreate(BaseModel):

    title: str = Field(
        min_length=1,
        max_length=100,
        description="도서 제목",
        examples=["처음 시작하는 FastAPI"],
    )
    author: str = Field(
        min_length=1,
        max_length=50,
        description="도서 저자",
        examples=["홍길동"],
    )
    year: int = Field(
        ge=1400,
        le=2026,
        description="출판 연도",
        examples=[2024],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="도서 태그 목록",
        examples=[["python", "web"]],
    )

    publisher: Publisher | None = Field(
        default=None,
        description="출판사 정보",
    )

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        value = value.strip()
        # 공백문자열 체크
        if not value:
            raise ValueError("제목은 필수 입력입니다. (공백 불가능)")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "처음 시작하는 FastAPI",
                    "author": "홍길동",
                    "year": 2024,
                    "tags": ["python", "web"],
                    "publisher": {
                        "name": "플레이 출판사",
                        "city": "부천",
                    },
                }
            ]
        }
    }

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None, min_length=1, max_length=50)
    year  : int | None = Field(default=None, ge=1900, le=2026,
                            description="출판 연도",
                            examples=[2024],)
    tags : list[str] | None = Field(default=None,
                                description="도서 태그 목록",
                                examples=["python", "web"],)
    publisher : Publisher | None = Field(default=None, description="출판사 정보")

# 서버가 도서를 응답할 때 사용하는 데이터 형식이다.
# 등록 요청 형식(BookCreate)에 id를 추가한 형태다.
class BookResponse(BookCreate):
    id: int = Field(
        description="서버가 발급한 도서 번호",
        examples=[1],
    )


# 날씨 API 응답 데이터의 형식이다.
class WeatherResponse(BaseModel):
    latitude: float = Field(description="위도", examples=[36.8])
    longitude: float = Field(description="경도", examples=[127.1])
    temperature: float = Field(
        description="현재 기온(섭씨)",
        examples=[28.9],
    )
    time: str = Field(
        description="관측 시각",
        examples=["2026-08-04T09:00"],
    )

class GoogleBooks(BaseModel):
    title: str = Field(description="도서 제목", examples=["FastAPI 입문"])
    authors: list[str] = Field(
        default_factory=list,
        description="저자 목록",
        examples=[["홍길동"]],
    )
    published_date: str = Field(
        default="",
        description="발행일. 없을 수 있음",
        examples=["2024-07-01"],
    )

class ExternalBook(BaseModel):
    title: str = Field(
        description="도서 제목",
        examples=["처음 시작하는 FastAPI"],
    )
    authors: list[str] = Field(
        default_factory=list,
        description="저자 목록",
        examples=[["홍길동"]],
    )
    published_date: str = Field(
        default="",
        description="발행일. 없을 수 있음",
        examples=["2024-07-01"],
    )

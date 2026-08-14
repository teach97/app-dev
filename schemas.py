from pydantic import BaseModel, Field, field_validator


class Publisher(BaseModel):
    name: str
    city: str = "부천"  # 도시를 입력하지 않으면 기본값으로 부천을 사용한다.


# 클라이언트가 도서를 등록할 때 보내는 데이터 형식이다.
# id는 서버가 자동으로 만들기 때문에 등록 요청에는 넣지 않는다.
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1400, le=2026)
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


# 날씨 API 응답 데이터의 형식이다.
class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    time: str

class GoogleBooks(BaseModel):
    title: str
    author: list[str] = Field(default_factory=list)
    Published_data: str = ""
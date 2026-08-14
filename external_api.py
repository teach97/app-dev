import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from schemas import GoogleBooks, WeatherResponse


# 현재 파일과 같은 폴더에 있는 .env를 확실하게 읽는다.
ENV_FILE = Path(__file__).with_name(".env")
load_dotenv(ENV_FILE)

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
EXTERNAL_TIMEOUT = float(os.getenv("EXTERNAL_TIMEOUT", "5"))


async def fetch_weather(latitude: float, longitude: float) -> WeatherResponse:
    """Open-Meteo에서 현재 날씨를 가져온다."""
    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m",
            },
        )
        response.raise_for_status()
        data = response.json()

    return WeatherResponse(
        latitude=data["latitude"],
        longitude=data["longitude"],
        temperature=data["current"]["temperature_2m"],
        time=data["current"]["time"],
    )


async def fetch_books(
    keyword: str = "파이썬",
    limit: int = 5,
) -> list[GoogleBooks]:
    """Google Books에서 제목 키워드로 도서를 검색한다."""
    if not GOOGLE_BOOKS_API_KEY:
        raise RuntimeError(
            "GOOGLE_BOOKS_API_KEY가 없습니다. 프로젝트 폴더의 .env를 확인하세요."
        )

    keyword = keyword.strip()
    if not keyword:
        return []

    # Google Books API가 허용하는 검색 개수 범위 안으로 제한한다.
    limit = max(1, min(limit, 40))

    async with httpx.AsyncClient(timeout=EXTERNAL_TIMEOUT) as client:
        response = await client.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": keyword,
                "key": GOOGLE_BOOKS_API_KEY,
                "maxResults": limit,
            },
        )
        response.raise_for_status()
        data = response.json()

    result: list[GoogleBooks] = []

    for item in data.get("items", []):
        volume_info = item.get("volumeInfo", {})

        result.append(
            GoogleBooks(
                title=volume_info.get("title", "제목 없음"),
                author=volume_info.get("authors", []),
                Published_data=volume_info.get("publishedDate", ""),
            )
        )

    return result

"""잡코리아 API 클라이언트"""
import json
import requests
from src.config import JobKoreaConfig
from src.payload_manager import PayloadManager


class JobKoreaAPIClient:
    """잡코리아 API 클라이언트"""

    def __init__(self, config: JobKoreaConfig, payload_manager: PayloadManager):
        self.config = config
        self.payload_manager = payload_manager
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """세션 생성 및 설정"""
        session = requests.Session()
        session.headers.update(self.config.HEADERS)
        session.cookies.update(self._parse_cookies(self.config.COOKIE_STR))
        return session

    @staticmethod
    def _parse_cookies(cookie_str: str) -> dict:
        """쿠키 문자열을 딕셔너리로 변환"""
        return dict(x.strip().split("=", 1) for x in cookie_str.split("; ") if "=" in x)

    def search(self, page: int = 1, page_size: int = 10, **kwargs) -> requests.Response:
        """인재 검색 API 호출"""
        payload = self.payload_manager.create_payload(page, page_size, **kwargs)
        data = {"searchCondition": json.dumps(payload, ensure_ascii=False)}

        print(f"[요청] page={page}, ps={page_size}")
        response = self.session.post(self.config.API_URL, data=data)
        print(f"[응답] status={response.status_code}")

        return response

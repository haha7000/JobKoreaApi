"""잡코리아 API 클라이언트"""
import json
import requests
from src.config import JobKoreaConfig
from src.payload_manager import PayloadManager
from src.auth import JobKoreaAuth


class JobKoreaAPIClient:
    """잡코리아 API 클라이언트"""

    def __init__(self, config: JobKoreaConfig, payload_manager: PayloadManager):
        self.config = config
        self.payload_manager = payload_manager
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """세션 생성 및 설정 (자동 로그인 지원)"""
        if self.config.USE_AUTO_LOGIN:
            # 자동 로그인 사용
            if not self.config.USERNAME or not self.config.PASSWORD:
                print("⚠️  경고: USE_AUTO_LOGIN=True이지만 아이디/비밀번호가 설정되지 않았습니다.")
                print("   config.py에서 USERNAME과 PASSWORD를 설정하세요.")
                print("   임시로 쿠키 방식을 사용합니다.\n")
                return self._create_session_with_cookies()

            # 로그인 시도
            auth = JobKoreaAuth(self.config.USERNAME, self.config.PASSWORD)
            session = auth.login()

            if session:
                # 로그인 성공 - 헤더 추가
                session.headers.update(self.config.HEADERS)
                return session
            else:
                print("⚠️  로그인 실패! 쿠키 방식으로 전환합니다.\n")
                return self._create_session_with_cookies()
        else:
            # 수동 쿠키 사용
            return self._create_session_with_cookies()

    def _create_session_with_cookies(self) -> requests.Session:
        """쿠키 문자열로 세션 생성"""
        session = requests.Session()
        session.headers.update(self.config.HEADERS)
        session.cookies.update(self._parse_cookies(self.config.COOKIE_STR))
        return session

    @staticmethod
    def _parse_cookies(cookie_str: str) -> dict:
        """쿠키 문자열을 딕셔너리로 변환"""
        return dict(x.strip().split("=", 1) for x in cookie_str.split("; ") if "=" in x)

    def search(self, page: int = 1, page_size: int = 10, saveno: int = 0, **kwargs) -> requests.Response:
        """인재 검색 API 호출"""
        payload = self.payload_manager.create_payload(page, page_size, saveno=saveno, **kwargs)
        data = {"searchCondition": json.dumps(payload, ensure_ascii=False)}

        print(f"[요청] page={page}, ps={page_size}, saveno={saveno}")
        response = self.session.post(self.config.API_URL, data=data)
        print(f"[응답] status={response.status_code}")

        return response

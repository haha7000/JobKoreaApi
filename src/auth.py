"""잡코리아 로그인 인증"""
import requests
from typing import Optional


class JobKoreaAuth:
    """잡코리아 로그인 인증"""

    LOGIN_URL = "https://www.jobkorea.co.kr/Login/Login.asp"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def login(self) -> Optional[requests.Session]:
        """
        로그인하여 세션 반환

        Returns:
            로그인 성공 시 세션 객체, 실패 시 None
        """
        session = requests.Session()

        # 로그인 데이터
        data = {
            "re_url": "",
            "idx": "",
            "Div": "",
            "BNo": "",
            "IP_ONOFF": "Y",
            "Login_Stat": "",
            "LoginPage": "/Login/Logout.asp",
            "returnHost": "http://www.jobkorea.co.kr",
            "jkwww_host": "https://www.jobkorea.co.kr",
            "m_type": "",
            "NaverReferReURL_Stat": "",
            "DB_Name": "GI",
            "ignoreSession": "",
            "CapchaCheckUseTime": "False",
            "TargetDate": "",
            "M_ID": self.username,
            "M_PWD": self.password,
            "gtxt": ""
        }

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "upgrade-insecure-requests": "1"
        }

        try:
            print(f"🔐 로그인 시도: {self.username}")
            response = session.post(
                self.LOGIN_URL,
                data=data,
                headers=headers,
                allow_redirects=True
            )

            # 디버깅: 응답 상태 확인
            print(f"   응답 상태: {response.status_code}")
            print(f"   최종 URL: {response.url}")
            print(f"   쿠키 수: {len(session.cookies)}")

            # 받은 쿠키 출력
            if session.cookies:
                print(f"   받은 쿠키:")
                for cookie_name, cookie_value in session.cookies.items():
                    display_value = f"{cookie_value[:30]}..." if len(cookie_value) > 30 else cookie_value
                    print(f"      {cookie_name}={display_value}")

            # 로그인 성공 확인 (쿠키 확인)
            if self._check_login_success(session):
                print(f"✅ 로그인 성공!")
                return session
            else:
                print(f"❌ 로그인 실패: 인증 정보를 확인하세요")
                # 응답 본문에서 에러 메시지 찾기
                if "alert" in response.text.lower() or "script" in response.text.lower():
                    import re
                    alert_match = re.search(r'alert\(["\'](.+?)["\']\)', response.text)
                    if alert_match:
                        print(f"   서버 메시지: {alert_match.group(1)}")
                return None

        except Exception as e:
            print(f"❌ 로그인 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _check_login_success(self, session: requests.Session) -> bool:
        """
        로그인 성공 여부 확인 (쿠키 존재 확인)
        """
        # 잡코리아 로그인 토큰 확인
        # jkat (access token), jkrt (refresh token), JK_User 등이 있으면 로그인 성공
        login_cookies = ['JSESSIONID', 'JKUID', 'jkat', 'jkrt', 'JK_User']

        for cookie_name in login_cookies:
            if session.cookies.get(cookie_name):
                return True

        return False

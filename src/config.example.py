"""잡코리아 API 설정 예시"""


class JobKoreaConfig:
    """잡코리아 API 설정"""
    API_URL = "https://www.jobkorea.co.kr/corp/person/detailsearchajax"
    BASE_URL = "https://www.jobkorea.co.kr"

    # ==================== 인증 방법 선택 ====================
    # 방법 1: 자동 로그인 (권장)
    USE_AUTO_LOGIN = True  # True: 자동 로그인, False: 쿠키 직접 설정

    USERNAME = "your_id"      # 잡코리아 아이디 입력
    PASSWORD = "your_password"  # 잡코리아 비밀번호 입력

    # 방법 2: 수동 쿠키 설정 (USE_AUTO_LOGIN=False일 때만 사용)
    # 브라우저 개발자도구(F12) → Application/저장소 → Cookies에서 복사
    COOKIE_STR = "JSESSIONID=...; JKUID=...; ..."
    # ======================================================

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.jobkorea.co.kr/corp/person/find",
        "X-Requested-With": "XMLHttpRequest",
    }

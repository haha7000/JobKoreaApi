"""잡코리아 API 설정 예시"""


class JobKoreaConfig:
    """잡코리아 API 설정"""
    API_URL = "https://www.jobkorea.co.kr/corp/person/detailsearchajax"
    BASE_URL = "https://www.jobkorea.co.kr"

    # 여기에 브라우저 쿠키를 입력하세요
    # 브라우저 개발자도구(F12) → Application/저장소 → Cookies에서 복사
    COOKIE_STR = "JSESSIONID=...; JKUID=...; ..."

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.jobkorea.co.kr/corp/person/find",
        "X-Requested-With": "XMLHttpRequest",
    }

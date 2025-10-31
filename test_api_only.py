"""
잡코리아 API 단독 테스트
페이지네이션 동작 확인용
"""
import json
import requests
from bs4 import BeautifulSoup

print("="*80)
print("🧪 잡코리아 API 단독 테스트")
print("="*80)


# 로그인 정보 (쿠키 대신 사용 가능)
USERNAME = "kspac2022"
PASSWORD = "Kspac123!!"

# ============================================================================

API_URL = "https://www.jobkorea.co.kr/corp/person/detailsearchajax"
LOGIN_URL = "https://www.jobkorea.co.kr/Login/Login.asp"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://www.jobkorea.co.kr/corp/person/find",
    "X-Requested-With": "XMLHttpRequest",
}

# 세션 생성
session = requests.Session()
session.headers.update(HEADERS)


print(f"\n🔐 자동 로그인: {USERNAME}")
login_data = {
    "re_url": "",              # 로그인 후 리다이렉트할 URL (비어있으면 기본 페이지)
    "idx": "",                 # 인덱스/식별자 (선택적)
    "Div": "",                 # 구분자/카테고리 (개인/기업 등)
    "BNo": "",                 # 사업자번호 (기업 회원용)
    "IP_ONOFF": "Y",           # IP 체크 활성화 여부 (Y=사용, N=미사용)
    "Login_Stat": "",          # 로그인 상태 플래그
    "LoginPage": "/Login/Logout.asp",  # 로그인 처리 페이지 경로
    "returnHost": "http://www.jobkorea.co.kr",   # 로그인 후 반환될 호스트 (HTTP)
    "jkwww_host": "https://www.jobkorea.co.kr",  # 잡코리아 메인 호스트 (HTTPS)
    "m_type": "",              # 회원 타입 (모바일/PC 등)
    "NaverReferReURL_Stat": "", # 네이버 유입 추적용 (광고 분석)
    "DB_Name": "GI",           # 데이터베이스 이름 (GI = 일반/개인?)
    "ignoreSession": "",       # 세션 무시 플래그 (자동 로그인 등)
    "CapchaCheckUseTime": "False",  # 캡차 사용 시간 체크 (False=캡차 미사용)
    "TargetDate": "",          # 목표 날짜 (통계/추적용)
    "M_ID": USERNAME,          # 회원 아이디 (Member ID) - 실제 로그인 ID
    "M_PWD": PASSWORD,         # 회원 비밀번호 (Member Password) - 실제 비밀번호
    "gtxt": ""                 # Google reCAPTCHA 토큰 (캡차 응답값)
}

response = session.post(LOGIN_URL, data=login_data)
print(f"   응답: {response.status_code}")
print(f"   쿠키 {len(session.cookies)}개 획득")

# ============================================================================
# Payload 템플릿 로드
# ============================================================================
print("\n📦 Payload 템플릿 로드")
with open('data/payload_template.json', 'r', encoding='utf-8') as f:
    payload_template = json.load(f)

print(f"   템플릿 로드 완료")

# ============================================================================
# 테스트 1: 기본 1페이지 요청
# ============================================================================
print("\n" + "="*80)
print("📝 테스트 1: 1페이지 요청 (saveno=0)")
print("="*80)

payload1 = payload_template.copy()
payload1['p'] = 1
payload1['ps'] = 100
payload1['saveno'] = 0

data1 = {"searchCondition": json.dumps(payload1, ensure_ascii=False)}
response1 = session.post(API_URL, data=data1)

print(f"응답 코드: {response1.status_code}")
print(f"응답 크기: {len(response1.text)} bytes")

soup1 = BeautifulSoup(response1.text, 'html.parser')
cards1 = soup1.select('tr.dvResumeTr')
rnos1 = [c.get('data-rno') for c in cards1]

print(f"파싱 결과: {len(cards1)}명")
print(f"첫 5명 이력서번호: {rnos1[:5]}")

# saveNo 추출
saveno_elem = soup1.select_one('input#saveNo')
extracted_saveno = saveno_elem.get('value') if saveno_elem else None
print(f"📌 추출된 saveNo: {extracted_saveno}")

# ============================================================================
# 테스트 2: 2페이지 요청 (saveno 사용)
# ============================================================================
print("\n" + "="*80)
print(f"📝 테스트 2: 2페이지 요청 (saveno={extracted_saveno})")
print("="*80)

payload2 = payload_template.copy()
payload2['p'] = 2
payload2['ps'] = 100
payload2['saveno'] = int(extracted_saveno) if extracted_saveno else 0

data2 = {"searchCondition": json.dumps(payload2, ensure_ascii=False)}
response2 = session.post(API_URL, data=data2)

print(f"응답 코드: {response2.status_code}")
print(f"응답 크기: {len(response2.text)} bytes")

soup2 = BeautifulSoup(response2.text, 'html.parser')
cards2 = soup2.select('tr.dvResumeTr')
rnos2 = [c.get('data-rno') for c in cards2]

print(f"파싱 결과: {len(cards2)}명")
print(f"첫 5명 이력서번호: {rnos2[:5]}")

# ============================================================================
# 결과 비교
# ============================================================================
print("\n" + "="*80)
print("📊 결과 비교")
print("="*80)

print(f"1페이지 총: {len(cards1)}명")
print(f"2페이지 총: {len(cards2)}명")

print(f"\n첫 번째 이력서번호:")
print(f"  1페이지: {rnos1[0] if rnos1 else 'None'}")
print(f"  2페이지: {rnos2[0] if rnos2 else 'None'}")
print(f"  같은가? {rnos1[0] == rnos2[0] if rnos1 and rnos2 else 'N/A'}")

# 전체 비교
overlap = len(set(rnos1) & set(rnos2))
page1_only = len(set(rnos1) - set(rnos2))
page2_only = len(set(rnos2) - set(rnos1))

print(f"\n이력서번호 중복 분석:")
print(f"  동일한 사람: {overlap}명")
print(f"  1페이지만: {page1_only}명")
print(f"  2페이지만: {page2_only}명")

if rnos1 == rnos2:
    print("\n❌ 결론: 완전히 동일합니다!")
    print("   API가 페이지네이션을 제대로 지원하지 않습니다.")
elif overlap > 50:
    print("\n⚠️  결론: 대부분 겹칩니다!")
    print("   페이지네이션이 제대로 작동하지 않을 수 있습니다.")
else:
    print("\n✅ 결론: 다른 사람들입니다!")
    print("   페이지네이션이 정상 작동합니다.")

# ============================================================================
# 테스트 3: saveno 없이 2페이지 요청
# ============================================================================
print("\n" + "="*80)
print("📝 테스트 3: 2페이지 요청 (saveno=0, 비교용)")
print("="*80)

payload3 = payload_template.copy()
payload3['p'] = 2
payload3['ps'] = 100
payload3['saveno'] = 0

data3 = {"searchCondition": json.dumps(payload3, ensure_ascii=False)}
response3 = session.post(API_URL, data=data3)

soup3 = BeautifulSoup(response3.text, 'html.parser')
cards3 = soup3.select('tr.dvResumeTr')
rnos3 = [c.get('data-rno') for c in cards3]

print(f"파싱 결과: {len(cards3)}명")
print(f"첫 5명: {rnos3[:5]}")

if rnos3 == rnos1:
    print("   → saveno=0일 때 1페이지와 동일")
elif rnos3 == rnos2:
    print("   → saveno 있을 때와 동일 (saveno가 영향 없음)")
else:
    print("   → 1페이지, 2페이지와 모두 다름 (무작위?)")

print("\n" + "="*80)
print("테스트 완료")
print("="*80)


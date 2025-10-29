"""
실제 실행 중인 Chrome에 연결하여 자기소개서 추출
"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from src.account_manager import AccountManager
from src.auth import JobKoreaAuth



def extract_introduction_from_page(page):
    """현재 페이지에서 자기소개서 추출"""
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    intro_section = soup.select_one("div.base.introduction")
    if not intro_section:
        return None

    items = intro_section.select("ul.list-introduction > li.item")
    if not items:
        return None

    data = []
    for idx, li in enumerate(items, 1):
        title_elem = li.select_one("div.header")
        title = title_elem.get_text(strip=True) if title_elem else None

        body_elem = li.select_one("div.content#pfl_original") or li.select_one("div.content")
        if body_elem:
            body_text = body_elem.get_text(separator="\n", strip=True)
            if body_text.startswith("- 자기소개서-"):
                body_text = body_text.replace("- 자기소개서-", "", 1).strip()
        else:
            body_text = None

        data.append({
            "index": idx,
            "title": title,
            "body_text": body_text,
        })

    return data


def extract_certificates_from_page(page):
    """현재 페이지에서 자격증 정보 추출"""
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    cert_section = soup.select_one("div.base.certificate")
    if not cert_section:
        return None

    # > 제거: 직접 자식이 아니라 하위 요소 전체 검색
    items = cert_section.select("div.list-certificate div.item")
    if not items:
        return None

    data = []
    for item in items:
        # 취득일
        date_elem = item.select_one("div.date")
        date = date_elem.get_text(strip=True) if date_elem else None

        # 자격증명
        name_elem = item.select_one("div.content-header div.name")
        name = name_elem.get_text(strip=True) if name_elem else None

        # 발행기관
        agency_elem = item.select_one("div.content-header div.agency")
        agency = agency_elem.get_text(strip=True) if agency_elem else None

        if name:  # 자격증명이 있을 때만 추가
            data.append({
                "취득일": date,
                "자격증명": name,
                "발행기관": agency,
            })

    return data if data else None


def login_and_get_cookies(username: str, password: str):
    """
    잡코리아 로그인하여 쿠키 반환
    """
    print(f"🔐 잡코리아 로그인 시도: {username}")
    auth = JobKoreaAuth(username, password)
    session = auth.login()

    if not session:
        print("❌ 로그인 실패!")
        return None

    # requests 쿠키를 Playwright 형식으로 변환
    cookies = []
    for cookie_name, cookie_value in session.cookies.items():
        cookies.append({
            "name": cookie_name,
            "value": cookie_value,
            "domain": ".jobkorea.co.kr",
            "path": "/"
        })

    print(f"✅ 로그인 성공! {len(cookies)}개 쿠키 획득\n")
    return cookies


def extract_all_resumes(summary_json_path: str, max_count: int = None):
    """
    실행 중인 Chrome에 연결하여 자기소개서 일괄 추출
    """
    # 이력서 목록 로드
    with open(summary_json_path, 'r', encoding='utf-8') as f:
        resumes = json.load(f)

    print(f"📋 총 {len(resumes)}개 이력서 발견")

    if max_count:
        resumes = resumes[:max_count]
        print(f"   → {max_count}개만 처리합니다.\n")

    # 계정 정보 로드
    excel_path = "configs/jobkorea_Excel.xlsx"
    account_manager = AccountManager(excel_path)
    accounts = account_manager.list_accounts()

    if not accounts:
        print("❌ 계정이 없습니다.")
        return []

    credentials = account_manager.get_credentials(accounts[0])
    if not credentials:
        print("❌ 계정 정보를 불러올 수 없습니다.")
        return []

    username = credentials['username']
    password = credentials['password']

    # 로그인하여 쿠키 획득
    cookies = login_and_get_cookies(username, password)
    if not cookies:
        return []

    print("=" * 80)
    print("📌 사용 방법:")
    print("=" * 80)
    print("1. Chrome을 디버깅 모드로 실행해야 합니다:")
    print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
    print("\n2. 이 스크립트가 자동으로 로그인 + 이력서를 추출합니다")
    print("=" * 80)
    print("\n🔍 Chrome이 이미 실행 중인지 확인하는 중...\n")

    results = []

    with sync_playwright() as p:
        try:
            # 실행 중인 Chrome에 연결
            print("🔗 실행 중인 Chrome에 연결 시도...")
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ Chrome 연결 성공!\n")

            # 기본 컨텍스트 가져오기
            contexts = browser.contexts
            if not contexts:
                print("❌ Chrome 컨텍스트를 찾을 수 없습니다.")
                return []

            context = contexts[0]
            pages = context.pages

            if not pages:
                print("❌ 열린 탭이 없습니다. Chrome에서 새 탭을 열어주세요.")
                return []

            # 첫 번째 페이지 사용 (또는 새 탭 생성)
            page = pages[0]
            print(f"✅ 현재 탭 사용: {page.url}\n")

            # 🔥 쿠키 주입!
            print("🍪 로그인 쿠키 주입 중...")
            context.add_cookies(cookies)
            print("✅ 쿠키 주입 완료!\n")

            # 각 이력서 순회
            for idx, resume in enumerate(resumes, 1):
                resume_no = resume.get('이력서번호')
                resume_link = resume.get('이력서링크')
                name = resume.get('이름', 'Unknown')

                print(f"[{idx}/{len(resumes)}] {name} (rNo={resume_no})")

                try:
                    # 이력서 페이지 이동
                    page.goto(resume_link, wait_until='domcontentloaded', timeout=30000)

                    # JavaScript 실행 대기
                    time.sleep(3)

                    # 자기소개서 추출
                    intro_data = extract_introduction_from_page(page)

                    # 자격증 추출
                    cert_data = extract_certificates_from_page(page)

                    # 결과 구성
                    result = {
                        **resume,
                        "자기소개서": intro_data,
                        "자격증": cert_data,
                        "추출상태": "성공"
                    }
                    results.append(result)

                    # 출력
                    if intro_data:
                        print(f"   ✅ 자기소개서 {len(intro_data)}개 추출")
                        # 미리보기
                        if intro_data[0]['body_text']:
                            preview = intro_data[0]['body_text'][:100]
                            print(f"   📝 {preview}...")
                    else:
                        print(f"   ⚠️  자기소개서 없음")

                    if cert_data:
                        print(f"   ✅ 자격증 {len(cert_data)}개 추출")
                        # 자격증 목록 출력
                        cert_names = [c['자격증명'] for c in cert_data[:3]]
                        print(f"   🏆 {', '.join(cert_names)}{'...' if len(cert_data) > 3 else ''}")
                    else:
                        print(f"   ⚠️  자격증 없음")

                    print()

                    # 요청 간 간격
                    time.sleep(1)

                except Exception as e:
                    print(f"   ❌ 오류: {e}\n")

                    result = {
                        **resume,
                        "자기소개서": None,
                        "자격증": None,
                        "추출상태": f"오류: {str(e)}"
                    }
                    results.append(result)

                    time.sleep(1)

        except Exception as e:
            print(f"\n❌ Chrome 연결 실패: {e}")
            print("\n해결 방법:")
            print("1. Chrome을 디버깅 모드로 실행하세요:")
            print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
            print("\n2. 또는 다른 터미널에서 위 명령어를 실행한 후 다시 시도하세요")
            import traceback
            traceback.print_exc()
            return []

    return results


def main():
    # ⏱️ 시작 시간 기록
    start_time = time.time()

    # 이력서 목록 파일
    summary_json = "output/kspac2022_summary.json"

    if not Path(summary_json).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {summary_json}")
        return

    print(f"📂 파일: {summary_json}\n")

    # 테스트: 처음 3개만 처리
    # 전체 처리하려면 max_count=None으로 변경
    results = extract_all_resumes(
        summary_json_path=summary_json,
        max_count=100  # None으로 변경하면 전체 처리
    )

    if not results:
        return

    # 결과 저장
    output_file = "output/kspac2022_with_introduction.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ⏱️ 종료 시간 및 경과 시간 계산
    end_time = time.time()
    elapsed_time = end_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    # 통계
    success_count = sum(1 for r in results if r.get('추출상태') == '성공')
    fail_count = len(results) - success_count

    print("\n" + "="*80)
    print("✅ 완료!")
    print(f"   성공: {success_count}개")
    print(f"   실패: {fail_count}개")
    print(f"   총: {len(results)}개")
    print(f"\n💾 저장: {output_file}")
    print(f"\n⏱️  총 수행시간: {minutes}분 {seconds}초 ({elapsed_time:.2f}초)")
    if len(results) > 0:
        avg_time = elapsed_time / len(results)
        print(f"   평균 처리시간: {avg_time:.2f}초/건")
    print("="*80)


if __name__ == "__main__":
    main()

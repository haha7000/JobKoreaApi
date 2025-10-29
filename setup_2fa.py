"""
2차 인증 설정 - 한 번만 실행하면 됩니다
"""
from playwright.sync_api import sync_playwright
import time
from src.account_manager import AccountManager

def setup_2fa_login():
    """
    2차 인증을 위한 초기 설정
    브라우저를 열어두고 수동으로 로그인 + 2차 인증 완료
    """
    # 계정 정보
    excel_path = "configs/jobkorea_Excel.xlsx"
    account_manager = AccountManager(excel_path)
    accounts = account_manager.list_accounts()

    if not accounts:
        print("❌ 계정이 없습니다.")
        return

    credentials = account_manager.get_credentials(accounts[0])
    username = credentials['username']
    password = credentials['password']

    print(f"🔑 계정: {username}\n")

    # User Data Directory 경로
    user_data_dir = "./playwright_user_data"

    print("=" * 80)
    print("📌 2차 인증 설정 가이드")
    print("=" * 80)
    print("1. 브라우저가 열립니다")
    print("2. 로그인 페이지에서 아이디/비밀번호 입력")
    print("3. 2차 인증 완료 (SMS 또는 앱)")
    print("4. 로그인이 완료되면 이 창으로 돌아와서 Enter 키를 누르세요")
    print("=" * 80)
    input("\nEnter를 눌러 계속하세요...")

    with sync_playwright() as p:
        # User Data Directory를 사용하여 세션 유지
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        page = context.pages[0]  # 첫 번째 페이지 사용

        # 로그인 페이지로 이동
        print("\n🌐 로그인 페이지로 이동 중...")
        page.goto("https://www.jobkorea.co.kr/Login/Login.asp")
        time.sleep(2)

        # 자동 입력 (선택사항)
        try:
            page.fill('input[name="M_ID"]', username)
            page.fill('input[name="M_PWD"]', password)
            print(f"✅ 아이디/비밀번호 자동 입력 완료")
            print("   ⚠️  로그인 버튼을 직접 클릭하세요!")
        except:
            print("⚠️  수동으로 아이디/비밀번호를 입력하세요")

        print("\n" + "=" * 80)
        print("⏳ 수동 작업 대기 중...")
        print("=" * 80)
        print("1. 로그인 버튼 클릭")
        print("2. 로그인 완료 확인")
        print("3. 이 창에서 Enter 키 누르기")
        print("=" * 80)
        input("\n로그인이 완료되면 Enter를 누르세요...")

        # ⭐️ 중요: 이력서 페이지에 접근하여 2차 인증 트리거
        print("\n📄 이력서 페이지 접근 중 (2차 인증 트리거)...")
        print("=" * 80)

        try:
            # 첫 번째 이력서 페이지 접근
            page.goto("https://www.jobkorea.co.kr/corp/person/find/resume/view?rNo=28135740", timeout=10000)
            time.sleep(3)

            print("⚠️  2단계 인증 화면이 나타납니다!")
            print("\n📌 2단계 인증 완료 방법:")
            print("   1. 담당자 선택")
            print("   2. SMS/이메일로 인증 코드 받기")
            print("   3. 인증 코드 입력")
            print("   4. 이력서 페이지가 보이면 이 창에서 Enter 누르기")
            print("=" * 80)
            input("\n2단계 인증 완료 후 Enter를 누르세요...")

        except Exception as e:
            print(f"⚠️  페이지 접근 중 오류: {e}")
            print("   브라우저에서 수동으로 이력서 페이지에 접근해보세요.")
            input("\n이력서 페이지 접근 완료 후 Enter를 누르세요...")

        # 로그인 확인
        print("\n✅ 로그인 + 2차 인증 상태 저장 완료!")
        print(f"💾 User Data: {user_data_dir}")
        print("\n이제 extract_with_persistent.py를 실행하면 2차 인증 없이 작동합니다!")

        time.sleep(2)
        context.close()


if __name__ == "__main__":
    setup_2fa_login()



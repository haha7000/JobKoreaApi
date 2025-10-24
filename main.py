"""메인 실행 파일"""
from src.config import JobKoreaConfig
from src.payload_manager import PayloadManager
from src.scraper import JobKoreaScraper


def main():
    """메인 실행 함수"""
    # ==================== 🔧 검색 설정 ====================

    # 직무 설정 (선택 가능한 직무 예시)
    # "백엔드개발자", "프론트엔드개발자", "웹개발자", "앱개발자",
    # "데이터엔지니어", "데이터사이언티스트", "AI/ML엔지니어",
    # "시스템엔지니어", "네트워크엔지니어", "DBA", "보안엔지니어" 등
    JOB_NAME = "제품영업"

    # 지역 설정 (리스트로 여러 지역 선택 가능)
    #
    # 광역 단위: ["서울", "경기", "인천"]
    # 구/시 단위: ["강남구", "성남시 분당구", "수원시 영통구"]
    # 혼합 가능: ["서울", "성남시 분당구"] (서울 전체 + 성남시 분당구만)
    #
    # 사용 가능 지역:
    #   서울: 강남구, 강동구, 강북구, 강서구, 관악구, 광진구, 구로구, 금천구, 노원구, 등
    #   경기: 성남시 분당구, 수원시 영통구, 고양시 일산동구, 용인시 수지구, 등
    #   기타: 부산, 대구, 인천, 대전, 광주, 울산, 세종, 제주, 전국
    AREAS = ["서울", "경기"]

    # 학력 설정 (리스트로 여러 학력 선택 가능)
    # 예: ["대졸"], ["대졸", "대학원"], ["전문대", "대졸"] 등
    # 사용 가능: "대졸", "전문대", "대학원", "고졸"
    EDUCATION = ["대졸", "대학원"]  # None이면 학력 필터 미적용

    # 나이 설정 (✨ 정확한 나이 지정 가능!)
    # 방법 1: 단일 나이 - 정확히 26세만
    #   AGES = 26
    # 방법 2: 범위 - 26세부터 30세까지
    #   AGES = (26, 30)  또는  AGES = [26, 30]
    # 방법 3: 문자열 (고정 범위) - 레거시
    #   AGES = "26~30세"
    AGES = (26, 60)  # 28세만! (None이면 나이 필터 미적용)

    # 성별 설정 (리스트로 선택 가능)
    # 예: ["남"], ["여"], ["남", "여"] (둘 다 선택하면 전체와 동일)
    # 사용 가능: "남", "여"
    GENDERS = None  # None이면 성별 필터 미적용

    # 구직상태 설정 (리스트로 선택 가능)
    # 예: ["구직중"], ["재직중"], ["구직 준비중", "구직중"]
    # 사용 가능: "구직 준비중", "구직중", "재직중"
    JOB_STATUS = None  # None이면 구직상태 필터 미적용

    # 페이지 설정
    START_PAGE = 1
    END_PAGE = 1      # 여러 페이지 수집 시 숫자 증가
    PAGE_SIZE = 10    # 페이지당 결과 수 (최대 100)
    DELAY = 1.0       # 페이지 간 지연 시간(초)

    # =====================================================

    # 설정
    config = JobKoreaConfig()
    payload_manager = PayloadManager("data/payload_template.json")

    # 스크래퍼 생성
    scraper = JobKoreaScraper(
        config=config,
        payload_manager=payload_manager,
        output_dir="output"
    )

    # 나이 표시 문자열 생성
    if AGES is None:
        age_display = "미지정 (전체)"
    elif isinstance(AGES, int):
        age_display = f"{AGES}세"
    elif isinstance(AGES, (tuple, list)):
        if len(AGES) == 2:
            age_display = f"{AGES[0]}~{AGES[1]}세"
        else:
            age_display = str(AGES)
    else:
        age_display = str(AGES)

    print(f"\n{'='*60}")
    print(f"🔍 검색 조건:")
    print(f"   직무: {JOB_NAME}")
    print(f"   지역: {', '.join(AREAS)}")
    print(f"   학력: {', '.join(EDUCATION) if EDUCATION else '미지정 (전체)'}")
    print(f"   나이: {age_display}")
    print(f"   성별: {', '.join(GENDERS) if GENDERS else '미지정 (전체)'}")
    print(f"   구직상태: {', '.join(JOB_STATUS) if JOB_STATUS else '미지정 (전체)'}")
    print(f"   페이지: {START_PAGE} ~ {END_PAGE} (페이지당 {PAGE_SIZE}명)")
    print(f"{'='*60}\n")

    # 데이터 수집
    people = scraper.scrape(
        start_page=START_PAGE,
        end_page=END_PAGE,
        page_size=PAGE_SIZE,
        delay=DELAY,
        job_name=JOB_NAME,
        areas=AREAS,
        education=EDUCATION,
        ages=AGES,
        genders=GENDERS,
        job_status=JOB_STATUS
    )

    # 결과 저장
    scraper.save_results(people)


if __name__ == "__main__":
    main()
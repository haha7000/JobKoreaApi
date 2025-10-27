"""엑셀 설정 파일을 읽어서 실행하는 메인 파일"""
import pandas as pd
from pathlib import Path
from src.config import JobKoreaConfig
from src.payload_manager import PayloadManager
from src.scraper import JobKoreaScraper


def parse_age(age_str):
    """나이 문자열 파싱"""
    if pd.isna(age_str) or str(age_str).strip() == '':
        return None

    age_str = str(age_str).strip()

    # 범위: "26~60" 또는 "26-35"
    if '~' in age_str:
        parts = age_str.split('~')
        return (int(parts[0]), int(parts[1]))
    elif '-' in age_str:
        parts = age_str.split('-')
        return (int(parts[0]), int(parts[1]))

    # 단일: "28"
    return int(age_str)


def parse_list(value_str):
    """콤마로 구분된 문자열을 리스트로 변환"""
    if pd.isna(value_str) or str(value_str).strip() == '':
        return None

    return [x.strip() for x in str(value_str).split(',') if x.strip()]


def parse_area(area_str):
    """지역 문자열 파싱 (예: '서울전지역' → ['서울'])"""
    if pd.isna(area_str) or str(area_str).strip() == '':
        return None

    area_str = str(area_str).strip()

    # "서울전지역" → "서울"
    if '전지역' in area_str:
        area_str = area_str.replace('전지역', '')

    # 콤마로 구분된 경우
    if ',' in area_str:
        return [x.strip().replace('전지역', '') for x in area_str.split(',') if x.strip()]

    return [area_str]


def load_configs_from_excel(excel_path: str, sheet_name: str):
    """
    jobkorea_Excel.xlsx의 '검색조건' 시트에서 설정 로드

    형식:
    - 모든 행의 직무를 하나의 검색 조건으로 통합
    - 모든 행의 필터 값들을 수집 (OR 조건)
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    if len(df) == 0:
        return None

    # 모든 행에서 필터 값들 수집
    all_job_names = []
    categories = []
    all_areas = []
    all_education = []
    all_ages = []
    all_job_status = []

    for idx, row in df.iterrows():
        # 대분류 수집
        if pd.notna(row.get('대분류')):
            category = str(row['대분류']).strip()
            if category:
                categories.append(category)

        # 지역 수집
        if '지역' in df.columns and pd.notna(row['지역']):
            areas = parse_area(row['지역'])
            if areas:
                all_areas.extend(areas)

        # 학력 수집
        if '학력' in df.columns and pd.notna(row['학력']):
            edu = str(row['학력']).strip()
            if edu and edu not in all_education:
                all_education.append(edu)

        # 나이 수집 (첫 번째 유효한 값만 사용 - 범위는 하나만 가능)
        if '나이' in df.columns and pd.notna(row['나이']) and not all_ages:
            age = parse_age(row['나이'])
            if age:
                all_ages = age

        # 구직상태 수집
        if '구직상태' in df.columns and pd.notna(row['구직상태']):
            status = str(row['구직상태']).strip()
            if status and status not in all_job_status:
                all_job_status.append(status)

        # 중분류 직무들 수집 (중분류 컬럼부터 Unnamed 컬럼들까지)
        start_collecting = False
        for col in df.columns:
            if col == '중분류':
                start_collecting = True

            if start_collecting and pd.notna(row[col]):
                job = str(row[col]).strip()
                if job:
                    all_job_names.append(job)

    if not all_job_names:
        print("⚠️  직무가 없습니다.")
        return None

    # 중복 제거
    all_areas = list(set(all_areas)) if all_areas else None
    all_education = all_education if all_education else None
    all_job_status = all_job_status if all_job_status else None

    # 하나의 통합 config 생성
    config = {
        'categories': categories,  # 모든 대분류
        'job_names': all_job_names,  # 모든 직무
        'areas': all_areas,
        'education': all_education,
        'ages': all_ages if all_ages else None,
        'genders': None,  # 이 시트에는 성별 컬럼 없음
        'job_status': all_job_status,
    }

    return config


def run_from_excel(
    excel_path: str = "configs/jobkorea_Excel.xlsx",
    sheet_name: str = "검색조건",
    start_page: int = 1,
    end_page: int = 1,
    page_size: int = 100,
    delay: float = 1.0,
    output_dir: str = "output"
):
    """
    jobkorea_Excel.xlsx 파일에서 설정을 읽어서 실행

    Args:
        excel_path: 엑셀 파일 경로
        sheet_name: 시트명 (기본: "검색조건")
        start_page: 시작 페이지
        end_page: 끝 페이지
        page_size: 페이지당 크기
        delay: 지연 시간(초)
        output_dir: 출력 디렉토리
    """
    # 엑셀 파일 확인
    if not Path(excel_path).exists():
        print(f"❌ 엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return

    # 설정 로드 (모든 행을 하나의 검색 조건으로 통합)
    search_config = load_configs_from_excel(excel_path, sheet_name)

    if not search_config:
        print("⚠️  검색 설정이 없습니다.")
        return

    print(f"\n{'='*60}")
    print(f"📋 엑셀 설정 파일: {excel_path}")
    print(f"📄 시트: {sheet_name}")
    print(f"{'='*60}\n")

    print(f"🔍 검색 조건:")
    print(f"   대분류: {', '.join(search_config['categories'])}")
    print(f"   직무: {', '.join(search_config['job_names'][:5])}{'...' if len(search_config['job_names']) > 5 else ''} (총 {len(search_config['job_names'])}개)")
    print(f"   지역: {search_config['areas']}")
    print(f"   학력: {search_config['education']}")
    print(f"   나이: {search_config['ages']}")
    print(f"   구직상태: {search_config['job_status']}")
    print(f"   페이지: {start_page} ~ {end_page} (크기: {page_size})")
    print(f"{'='*60}\n")

    # 스크래퍼 초기화
    config = JobKoreaConfig()
    payload_manager = PayloadManager("data/payload_template.json")
    scraper = JobKoreaScraper(
        config=config,
        payload_manager=payload_manager,
        output_dir=output_dir
    )

    # 데이터 수집
    people = scraper.scrape(
        start_page=start_page,
        end_page=end_page,
        page_size=page_size,
        delay=delay,
        job_name=search_config['job_names'],
        areas=search_config['areas'],
        education=search_config['education'],
        ages=search_config['ages'],
        genders=search_config['genders'],
        job_status=search_config['job_status']
    )

    # 결과 저장
    if people:
        import json
        # 파일명: 시트명 기반
        safe_sheet_name = sheet_name.replace('@', '_').replace('.', '_')
        json_path = Path(output_dir) / f"{safe_sheet_name}_summary.json"
        excel_path = Path(output_dir) / f"{safe_sheet_name}_결과.xlsx"

        # JSON 저장
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(people, f, ensure_ascii=False, indent=2)

        # 엑셀 저장
        scraper.exporter.save(people, str(excel_path))

        print(f"\n✅ 완료: {len(people)}명 수집")
        print(f"   📄 JSON: {json_path}")
        print(f"   📊 Excel: {excel_path}")
    else:
        print(f"\n⚠️  수집된 데이터 없음")

    print(f"\n{'='*60}")
    print(f"🎉 완료!")
    print(f"{'='*60}\n")


def main():
    """메인 실행 함수"""
    # ==================== 🔧 실행 설정 ====================

    EXCEL_PATH = "configs/jobkorea_Excel.xlsx"  # 엑셀 파일 경로
    SHEET_NAME = "검색조건"  # 시트명

    # 페이지 설정
    START_PAGE = 1
    END_PAGE = 1
    PAGE_SIZE = 100
    DELAY = 1.0

    OUTPUT_DIR = "output"

    # =====================================================

    run_from_excel(
        excel_path=EXCEL_PATH,
        sheet_name=SHEET_NAME,
        start_page=START_PAGE,
        end_page=END_PAGE,
        page_size=PAGE_SIZE,
        delay=DELAY,
        output_dir=OUTPUT_DIR
    )


if __name__ == "__main__":
    main()

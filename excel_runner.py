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

    # 범위: "26-35"
    if '-' in age_str:
        parts = age_str.split('-')
        return (int(parts[0]), int(parts[1]))

    # 단일: "28"
    return int(age_str)

    
def parse_list(value_str):
    """콤마로 구분된 문자열을 리스트로 변환"""
    if pd.isna(value_str) or str(value_str).strip() == '':
        return None

    return [x.strip() for x in str(value_str).split(',') if x.strip()]


def load_configs_from_excel(excel_path: str, sheet_name: str):
    """엑셀에서 검색 설정 로드"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # 첫 번째 행 데이터 추출
    if len(df) == 0:
        return None

    first_row = df.iloc[0]

    config = {
        'job_names': [],  # 모든 행의 직무를 모음
        'areas': parse_list(first_row['지역']) if '지역' in df.columns and pd.notna(first_row['지역']) else None,
        'education': parse_list(first_row['학력']) if '학력' in df.columns and pd.notna(first_row['학력']) else None,
        'ages': parse_age(first_row['나이']) if '나이' in df.columns and pd.notna(first_row['나이']) else None,
        'genders': parse_list(first_row['성별']) if '성별' in df.columns and pd.notna(first_row['성별']) else None,
        'job_status': parse_list(first_row['구직상태']) if '구직상태' in df.columns and pd.notna(first_row['구직상태']) else None,
    }

    # 모든 행의 직무 수집
    if '직무' in df.columns:
        for idx, row in df.iterrows():
            if pd.notna(row['직무']):
                job = str(row['직무']).strip()
                if job:
                    config['job_names'].append(job)

    return config


def run_from_excel(
    excel_path: str = "configs/search_config.xlsx",
    sheet_name: str = None,
    start_page: int = 1,
    end_page: int = 1,
    page_size: int = 100,
    delay: float = 1.0,
    output_dir: str = "output"
):
    """
    엑셀 파일에서 설정을 읽어서 실행

    Args:
        excel_path: 엑셀 파일 경로
        sheet_name: 시트명 (계정명), None이면 첫 번째 시트
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

    # 시트명이 없으면 첫 번째 시트 사용
    if sheet_name is None:
        xl = pd.ExcelFile(excel_path)
        sheet_name = xl.sheet_names[0]
        print(f"ℹ️  시트명 미지정 → 첫 번째 시트 사용: '{sheet_name}'")

    # 설정 로드
    search_config = load_configs_from_excel(excel_path, sheet_name)

    if not search_config:
        print("⚠️  검색 설정이 없습니다.")
        return

    print(f"\n{'='*60}")
    print(f"📋 엑셀 설정 파일: {excel_path}")
    print(f"📄 시트: {sheet_name}")
    print(f"{'='*60}\n")

    print(f"🔍 검색 조건:")
    print(f"   직무: {', '.join(search_config['job_names']) if search_config['job_names'] else 'payload_template.json 사용'}")
    print(f"   지역: {search_config['areas']}")
    print(f"   학력: {search_config['education']}")
    print(f"   나이: {search_config['ages']}")
    print(f"   성별: {search_config['genders']}")
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
    # 직무 리스트를 그대로 전달 (PayloadManager가 여러 직무 처리)
    job_names = search_config['job_names'] if search_config['job_names'] else None

    people = scraper.scrape(
        start_page=start_page,
        end_page=end_page,
        page_size=page_size,
        delay=delay,
        job_name=job_names,  # ← 리스트로 전달
        areas=search_config['areas'],
        education=search_config['education'],
        ages=search_config['ages'],
        genders=search_config['genders'],
        job_status=search_config['job_status']
    )

    # 결과 저장
    if people:
        # 파일명 생성 (시트명 기반)
        import json
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

    EXCEL_PATH = "configs/search_config.xlsx"  # 엑셀 파일 경로
    SHEET_NAME = None  # 시트명 (None이면 첫 번째 시트)

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

"""엑셀 설정 파일 파싱"""
import pandas as pd
from typing import Optional, List, Union, Dict


class ExcelConfigParser:
    """엑셀 설정 파일을 파싱하여 검색 조건 추출"""

    def __init__(self, excel_path: str, sheet_name: str):
        """
        Args:
            excel_path: 엑셀 파일 경로
            sheet_name: 시트명
        """
        self.excel_path = excel_path
        self.sheet_name = sheet_name

    def parse(self) -> Optional[Dict]:
        """
        엑셀 파일에서 검색 조건 로드

        Returns:
            검색 조건 딕셔너리 또는 None
        """
        df = pd.read_excel(self.excel_path, sheet_name=self.sheet_name)

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
                areas = self._parse_area(row['지역'])
                if areas:
                    all_areas.extend(areas)

            # 학력 수집
            if '학력' in df.columns and pd.notna(row['학력']):
                edu = str(row['학력']).strip()
                if edu and edu not in all_education:
                    all_education.append(edu)

            # 나이 수집 (첫 번째 유효한 값만 사용 - 범위는 하나만 가능)
            if '나이' in df.columns and pd.notna(row['나이']) and not all_ages:
                age = self._parse_age(row['나이'])
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
        return {
            'categories': categories,
            'job_names': all_job_names,
            'areas': all_areas,
            'education': all_education,
            'ages': all_ages if all_ages else None,
            'genders': None,  # 이 시트에는 성별 컬럼 없음
            'job_status': all_job_status,
        }

    @staticmethod
    def _parse_age(age_str) -> Optional[Union[int, tuple]]:
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

    @staticmethod
    def _parse_area(area_str) -> Optional[List[str]]:
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

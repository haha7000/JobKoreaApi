"""검색 조건 payload 관리"""
import json
from pathlib import Path
from typing import List, Optional, Union


class PayloadManager:
    """검색 조건 payload 관리"""

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self._template = None

    def _load_template(self) -> dict:
        """브라우저 payload 템플릿 로드"""
        if self._template is None:
            with open(self.template_path, "r", encoding="utf-8") as f:
                self._template = json.load(f)
        return self._template.copy()

    def _find_job_by_name(self, job_name: str, job_list: list) -> Optional[dict]:
        """직무 이름으로 직무 항목 찾기 (재귀)"""
        for job in job_list:
            if job.get("t") == job_name:
                return job
            # 하위 children이 있으면 재귀 탐색
            if "children" in job:
                found = self._find_job_by_name(job_name, job["children"])
                if found:
                    return found
        return None

    def _reset_all_selections(self, job_list: list):
        """모든 직무 선택 초기화"""
        for job in job_list:
            job["s"] = 0
            job["c"] = 0
            if "children" in job:
                self._reset_all_selections(job["children"])

    def _find_job_category(self, job_name: str, ctgr_list: list) -> tuple:
        """직무가 속한 카테고리와 직무 찾기"""
        for category in ctgr_list:
            # 현재 카테고리의 하위에서 직무 찾기
            if "children" in category:
                job = self._find_job_by_name(job_name, category["children"])
                if job:
                    return (category, job)
        return (None, None)

    def _select_job(self, job_name: Union[str, List[str]], payload: dict):
        """
        특정 직무 선택 (전체 카테고리에서 검색)

        Args:
            job_name: 직무명 또는 직무명 리스트
            payload: payload 딕셔너리
        """
        job_type = payload.get("jobtype", {})
        ctgr = job_type.get("ctgr", [])

        # 모든 선택 초기화
        self._reset_all_selections(ctgr)

        # 문자열이면 리스트로 변환
        if isinstance(job_name, str):
            job_names = [job_name]
        else:
            job_names = job_name

        selected_categories = set()  # 중복 방지

        # 각 직무를 찾아서 선택
        for jname in job_names:
            category, job = self._find_job_category(jname, ctgr)

            if not category or not job:
                print(f"⚠️  직무 '{jname}'를 찾을 수 없습니다.")
                continue

            # 상위 카테고리 선택
            category["s"] = 1
            category["c"] = 1
            selected_categories.add(category.get('t'))

            # 직무 선택
            job["s"] = 1
            job["c"] = 1

            # "전체" 하위 항목도 선택
            if "children" in job:
                for child in job["children"]:
                    if child.get("t") == "전체":
                        child["s"] = 1
                        child["c"] = 1
                        break

            print(f"✅ 직무 '{jname}' 선택됨 (카테고리: {category.get('t')})")

        if selected_categories:
            print(f"💡 총 {len(job_names)}개 직무 선택 완료 (카테고리: {', '.join(selected_categories)})")

    def _find_area_by_name(self, area_name: str, area_list: list) -> Optional[dict]:
        """지역 이름으로 지역 항목 찾기 (재귀)"""
        for area in area_list:
            if area.get("t") == area_name:
                return area
            if "children" in area:
                found = self._find_area_by_name(area_name, area["children"])
                if found:
                    return found
        return None

    def _reset_all_areas(self, area_list: list):
        """모든 지역 선택 초기화"""
        for area in area_list:
            area["s"] = 0
            area["c"] = 0
            area["use"] = 0
            if "children" in area:
                self._reset_all_areas(area["children"])

    def _select_areas(self, area_names: List[str], payload: dict):
        """특정 지역들 선택"""
        workarea = payload.get("workarea", {})
        ctgr = workarea.get("ctgr", [])

        # 모든 지역 선택 초기화
        self._reset_all_areas(ctgr)

        for area_name in area_names:
            area = self._find_area_by_name(area_name, ctgr)
            if area:
                area["s"] = 1
                area["c"] = 1
                area["use"] = 1
                # "전지역" 하위 항목이 있으면 선택
                if "children" in area:
                    for child in area["children"]:
                        if "전지역" in child.get("t", ""):
                            child["s"] = 1
                            child["c"] = 1
                            child["use"] = 1
                            break
                print(f"✅ 지역 '{area_name}' 선택됨")
            else:
                print(f"⚠️  지역 '{area_name}'를 찾을 수 없습니다.")

    def _reset_all_education(self, education_list: list):
        """모든 학력 선택 초기화"""
        for edu in education_list:
            edu["s"] = 0
            edu["c"] = 0
            edu["use"] = 0

    def _select_education(self, education_names: List[str], payload: dict):
        """특정 학력들 선택"""
        education = payload.get("education", [])

        # 모든 학력 선택 초기화
        self._reset_all_education(education)

        # 학력 매핑 (사용자 친화적 이름 → API 이름)
        edu_mapping = {
            "대졸": "대학교(4년) 졸업",
            "대학교": "대학교(4년) 졸업",
            "4년제": "대학교(4년) 졸업",
            "전문대": "대학(2,3년) 졸업",
            "초대졸": "대학(2,3년) 졸업",
            "2년제": "대학(2,3년) 졸업",
            "3년제": "대학(2,3년) 졸업",
            "대학원": "대학원 졸업",
            "석사": "대학원 졸업",
            "박사": "대학원 졸업",
            "고졸": "고등학교 졸업 이하",
            "고등학교": "고등학교 졸업 이하",
        }

        for edu_name in education_names:
            # 매핑된 이름이 있으면 사용, 없으면 그대로 사용
            search_name = edu_mapping.get(edu_name, edu_name)

            found = False
            for edu in education:
                if search_name in edu.get("t", ""):
                    edu["s"] = 1
                    edu["c"] = 1
                    edu["use"] = 1
                    found = True
                    print(f"✅ 학력 '{edu.get('t')}' 선택됨")
                    break

            if not found:
                print(f"⚠️  학력 '{edu_name}'를 찾을 수 없습니다.")
                print(f"    사용 가능한 학력: 대졸, 전문대, 대학원, 고졸")

    def _reset_all_ages(self, age_list: list):
        """모든 나이 선택 초기화"""
        for age in age_list:
            age["s"] = 0
            age["c"] = 0
            age["use"] = 0

    def _select_ages(self, age_input: Union[int, tuple, List], payload: dict):
        """
        나이 필터 설정 (커스텀 범위 지원)

        Args:
            age_input: 나이 설정 방식
                - 단일 숫자: 26 → 26세만 (26~26)
                - 튜플: (26, 30) → 26세~30세
                - 리스트: [26, 30] → 26세~30세
                - 문자열: "26~30세" → 고정 범위 사용 (레거시)
        """
        age_data = payload.get("age", {})
        age_codes = age_data.get("code", [])

        # 모든 나이 선택 초기화
        self._reset_all_ages(age_codes)

        # 입력 타입에 따른 처리
        if isinstance(age_input, int):
            # 단일 나이: 26 → (26, 26)
            start_age = age_input
            end_age = age_input
            print(f"✅ 나이 {start_age}세만 선택됨")

        elif isinstance(age_input, (tuple, list)) and len(age_input) == 2:
            # 범위: (26, 30) 또는 [26, 30]
            try:
                start_age = int(age_input[0])
                end_age = int(age_input[1])
                print(f"✅ 나이 {start_age}세 ~ {end_age}세 선택됨")
            except (ValueError, TypeError):
                print(f"⚠️  나이 범위 '{age_input}'가 유효하지 않습니다.")
                return

        elif isinstance(age_input, str):
            # 레거시 문자열 방식: "26~30세" → 고정 범위 사용
            self._select_ages_legacy(age_input, payload)
            return

        else:
            print(f"⚠️  나이 입력 형식이 잘못되었습니다: {age_input}")
            print(f"    사용 가능 형식: 26 (단일), (26, 30) (범위), '26~30세' (고정 범위)")
            return

        # 커스텀 범위 설정 (s, e 필드 사용)
        age_data["s"] = str(start_age)
        age_data["e"] = str(end_age)

    def _select_ages_legacy(self, age_range: str, payload: dict):
        """
        레거시 방식: 고정된 나이대 선택

        Args:
            age_range: "26~30세", "31~35세" 등
        """
        age_data = payload.get("age", {})
        age_codes = age_data.get("code", [])

        # 나이 매핑
        age_mapping = {
            "25세이하": "~25세",
            "20대초반": "~25세",
            "26-30": "26~30세",
            "20대후반": "26~30세",
            "31-35": "31~35세",
            "30대초반": "31~35세",
            "36-40": "36~40세",
            "30대후반": "36~40세",
            "41-50": "41~50세",
            "40대": "41~50세",
            "51세이상": "51세 이상",
            "50대이상": "51세 이상",
        }

        # 매핑된 이름이 있으면 사용, 없으면 그대로 사용
        search_name = age_mapping.get(age_range, age_range)

        found = False
        for age in age_codes:
            if search_name == age.get("t"):
                age["s"] = 1
                age["c"] = 1
                age["use"] = 1
                found = True
                print(f"✅ 나이 '{age.get('t')}' 선택됨 (고정 범위)")
                break

        if not found:
            print(f"⚠️  나이 '{age_range}'를 찾을 수 없습니다.")
            print(f"    사용 가능한 나이대: ~25세, 26~30세, 31~35세, 36~40세, 41~50세, 51세 이상")

    def _select_gender(self, genders: List[str], payload: dict):
        """성별 선택"""
        gender_data = payload.get("gender", {})

        # 성별 매핑
        gender_mapping = {
            "남": "man",
            "남성": "man",
            "남자": "man",
            "여": "woman",
            "여성": "woman",
            "여자": "woman",
        }

        for gender in genders:
            # 매핑된 이름이 있으면 사용, 없으면 그대로 사용
            gender_key = gender_mapping.get(gender, gender.lower())

            if gender_key in gender_data:
                gender_data[gender_key]["s"] = 1
                gender_data[gender_key]["c"] = 1
                gender_data[gender_key]["use"] = 1
                print(f"✅ 성별 '{gender}' 선택됨")
            else:
                print(f"⚠️  성별 '{gender}'를 찾을 수 없습니다.")
                print(f"    사용 가능한 성별: 남, 여")

    def _reset_all_job_status(self, job_status_list: list):
        """모든 구직상태 선택 초기화"""
        for job_status in job_status_list:
            job_status["s"] = 0
            job_status["c"] = 0
            job_status["use"] = 0

    def _select_job_status(self, job_status_names: List[str], payload: dict):
        """구직상태 선택"""
        job_status_data = payload.get("job", [])

        # 모든 구직상태 선택 초기화
        self._reset_all_job_status(job_status_data)

        # 구직상태 매핑
        job_status_mapping = {
            "구직준비중": "구직 준비중",
            "준비중": "구직 준비중",
            "구직중": "구직중",
            "재직중": "재직중",
            "재직": "재직중",
        }

        for status_name in job_status_names:
            # 매핑된 이름이 있으면 사용, 없으면 그대로 사용
            search_name = job_status_mapping.get(status_name, status_name)

            found = False
            for job_status in job_status_data:
                if search_name == job_status.get("t"):
                    job_status["s"] = 1
                    job_status["c"] = 1
                    job_status["use"] = 1
                    found = True
                    print(f"✅ 구직상태 '{job_status.get('t')}' 선택됨")
                    break

            if not found:
                print(f"⚠️  구직상태 '{status_name}'를 찾을 수 없습니다.")
                print(f"    사용 가능한 구직상태: 구직 준비중, 구직중, 재직중")

    def create_payload(
        self,
        page: int = 1,
        page_size: int = 10,
        job_name: Optional[str] = None,
        areas: Optional[List[str]] = None,
        education: Optional[List[str]] = None,
        ages: Optional[Union[int, tuple, List, str]] = None,
        genders: Optional[List[str]] = None,
        job_status: Optional[List[str]] = None
    ) -> dict:
        """
        검색 payload 생성

        Args:
            page: 페이지 번호
            page_size: 페이지당 결과 수
            job_name: 직무명 (예: "백엔드개발자", "프론트엔드개발자", "데이터엔지니어")
            areas: 지역 리스트 (예: ["서울", "경기"])
            education: 학력 리스트 (예: ["대졸", "대학원"])
            ages: 나이 설정 - 단일 숫자: 26, 범위: (26, 30) or [26, 30], 문자열: "26~30세"
            genders: 성별 리스트 (예: ["남"], ["여"], ["남", "여"])
            job_status: 구직상태 리스트 (예: ["구직중"], ["재직중"], ["구직 준비중", "구직중"])
        """
        payload = self._load_template()
        payload["p"] = page
        payload["ps"] = page_size

        # 직무 설정
        if job_name:
            self._select_job(job_name, payload)

        # 지역 설정
        if areas:
            self._select_areas(areas, payload)

        # 학력 설정
        if education:
            self._select_education(education, payload)

        # 나이 설정
        if ages:
            self._select_ages(ages, payload)

        # 성별 설정
        if genders:
            self._select_gender(genders, payload)

        # 구직상태 설정
        if job_status:
            self._select_job_status(job_status, payload)

        return payload

"""인재 데이터 파싱"""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re


class PersonDataParser:
    """인재 데이터 파싱"""

    def __init__(self, base_url: str, filter_active_within_minutes: Optional[int] = None):
        """
        Args:
            base_url: 기본 URL
            filter_active_within_minutes: 최근 활동 필터링 (분 단위, None이면 필터링 안 함)
        """
        self.base_url = base_url
        self.filter_active_within_minutes = filter_active_within_minutes

    def parse_html(self, html: str, start_index: int = 1) -> List[Dict[str, str]]:
        """
        HTML에서 인재 정보 추출

        Args:
            html: HTML 문자열
            start_index: 시작 번호 (페이지 연속 번호용)
        """
        soup = BeautifulSoup(html, "html.parser")
        people = []

        for idx, card in enumerate(soup.select("tr.dvResumeTr"), start=start_index):
            person_data = self._extract_person_data(card, index=idx)
            if person_data:
                people.append(person_data)

        return people

    def _parse_activity_minutes(self, activity_text: str) -> Optional[int]:
        """
        활동 시간 텍스트에서 분 단위로 변환

        예:
        - "10분전 이력서 수정" → 10
        - "1시간전 공고 스크랩" → 60
        - "2시간 30분전 입사지원" → 150
        - "최근 활동 인재" → None
        """
        if not activity_text:
            return None

        total_minutes = 0

        # "1시간전", "2시간 전" 형식
        hour_match = re.search(r'(\d+)\s*시간', activity_text)
        if hour_match:
            hours = int(hour_match.group(1))
            total_minutes += hours * 60

        # "10분전", "30분 전" 형식
        minute_match = re.search(r'(\d+)\s*분', activity_text)
        if minute_match:
            minutes = int(minute_match.group(1))
            total_minutes += minutes

        # 시간 정보가 없으면 None
        if total_minutes == 0:
            return None

        return total_minutes

    def _extract_person_data(self, card, index: int) -> Optional[Dict[str, str]]:
        """카드에서 개인 정보 추출"""
        # 이름/나이
        name_elem = card.select_one(".nameAge dt a")
        age_elem = card.select_one(".nameAge dd")

        # 성별과 나이 분리 (HTML 원본: "(여, 만 35세)")
        gender = ""
        age = ""
        if age_elem:
            age_text = age_elem.get_text(strip=True)
            # "(여, 만 35세)" 형식에서 분리
            if "," in age_text:
                parts = age_text.replace("(", "").replace(")", "").split(",")
                if len(parts) == 2:
                    gender = parts[0].strip()  # "여" 또는 "남"
                    age = parts[1].strip()     # "만 35세"
            else:
                # 콤마가 없으면 전체를 나이로 처리
                age = age_text

        # 이력서 링크
        resume_url = ""
        if name_elem and name_elem.get("href"):
            resume_url = self.base_url + name_elem.get("href")

        # 경력
        career_elem = card.select_one(".careerIcon .career")
        career = ""
        if career_elem:
            career_text = career_elem.get_text(strip=True)
            # "경력\r\n                                                2년2개월" 형식에서 "2년2개월"만 추출
            career = career_text.replace("경력", "").replace("\r", "").replace("\n", "").strip()

        # 경력이 비어있으면 "신입"
        if not career:
            career = "신입"

        # 제목 (이력서 제목)
        # p.title.active > a 에 제목이 표시됨
        title_p = card.select_one("p.title.active")
        resume_title_elem = None
        if title_p:
            resume_title_elem = title_p.select_one("a")

        # 학력 (항상 .ico_edu 위치에 있음)
        education_elem = card.select_one(".ico_edu span")

        # 지역
        area_elem = card.select_one(".ico_pin span")

        # 직무 키워드
        job_keywords = [btn.get_text(strip=True) for btn in card.select(".keywordSkill button")]

        # 기술 스킬
        tech_skills = [btn.get_text(strip=True) for btn in card.select(".keywordJob button")]

        # 이력서 번호
        rno = card.get("data-rno", "")

        # 🔥 최근 활동 정보 수집 (bullList)
        # "이력서 수정", "공고 스크랩", "입사지원" 모두 통합
        bull_list = card.select("ul.bullList li")
        activity_items = []
        latest_activity_minutes = None
        latest_activity_text = ""

        for li in bull_list:
            text = li.get_text(strip=True)

            # 시간 정보가 있는 활동만 수집
            activity_minutes = self._parse_activity_minutes(text)

            if activity_minutes is not None:
                activity_items.append(text)

                # 가장 최근 활동 시간 기록
                if latest_activity_minutes is None or activity_minutes < latest_activity_minutes:
                    latest_activity_minutes = activity_minutes
                    latest_activity_text = text

        # 🔥 30분 이내 활동 필터링 (설정된 경우)
        if self.filter_active_within_minutes is not None:
            if latest_activity_minutes is None or latest_activity_minutes > self.filter_active_within_minutes:
                return None  # 필터링 조건에 맞지 않으면 제외

        # 모든 활동을 ", "로 조인
        recent_activity = ", ".join(activity_items) if activity_items else ""

        return {
            "번호": index,
            "이름": name_elem.get_text(strip=True) if name_elem else "",
            "성별": gender,
            "나이": age,
            "제목": resume_title_elem.get_text(strip=True) if resume_title_elem else "",
            "경력": career,
            "학력": education_elem.get_text(strip=True) if education_elem else "",
            "지역": area_elem.get_text(strip=True) if area_elem else "",
            "직무": ", ".join(job_keywords),
            "기술스택": ", ".join(tech_skills),
            "이력서번호": rno,
            "이력서링크": resume_url,
            "최근활동": recent_activity
        }


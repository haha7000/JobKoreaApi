"""인재 데이터 파싱"""
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class PersonDataParser:
    """인재 데이터 파싱"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def parse_html(self, html: str) -> List[Dict[str, str]]:
        """HTML에서 인재 정보 추출"""
        soup = BeautifulSoup(html, "html.parser")
        people = []

        for card in soup.select("tr.dvResumeTr"):
            person_data = self._extract_person_data(card)
            if person_data:
                people.append(person_data)

        return people

    def _extract_person_data(self, card) -> Optional[Dict[str, str]]:
        """카드에서 개인 정보 추출"""
        # 이름/나이
        name_elem = card.select_one(".nameAge dt a")
        age_elem = card.select_one(".nameAge dd")

        # 이력서 링크
        resume_url = ""
        if name_elem and name_elem.get("href"):
            resume_url = self.base_url + name_elem.get("href")

        # 경력
        career_elem = card.select_one(".careerIcon .career")

        # 학력
        title_elem = card.select_one(".title a")

        # 지역
        area_elem = card.select_one(".ico_pin span")

        # 직무 키워드
        job_keywords = [btn.get_text(strip=True) for btn in card.select(".keywordSkill button")]

        # 기술 스킬
        tech_skills = [btn.get_text(strip=True) for btn in card.select(".keywordJob button")]

        # 이력서 번호
        rno = card.get("data-rno", "")

        return {
            "이름": name_elem.get_text(strip=True) if name_elem else "",
            "나이": age_elem.get_text(strip=True) if age_elem else "",
            "경력": career_elem.get_text(strip=True) if career_elem else "신입",
            "학력": title_elem.get_text(strip=True) if title_elem else "",
            "지역": area_elem.get_text(strip=True) if area_elem else "",
            "직무": ", ".join(job_keywords),
            "기술스택": ", ".join(tech_skills),
            "이력서번호": rno,
            "이력서링크": resume_url,
        }

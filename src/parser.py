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

        # 제목 (이력서 제목 / 희망직무)
        # 로그인 시 p.title.active > a 에 제목이 표시됨
        # 비로그인 시 p.title > a 에 학력이 표시됨
        title_p = card.select_one("p.title")
        resume_title_elem = None
        education_elem = None

        if title_p:
            title_link = title_p.select_one("a")
            # active 클래스가 있으면 제목, 없으면 학력
            if "active" in title_p.get("class", []):
                resume_title_elem = title_link
            else:
                education_elem = title_link

        # 학력이 없으면 다른 위치 확인
        if not education_elem:
            education_elem = card.select_one(".userInfo .title a")

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
        }

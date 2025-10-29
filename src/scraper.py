"""잡코리아 스크래퍼 메인 클래스"""
import json
import time
from pathlib import Path
from typing import List, Dict

from src.config import JobKoreaConfig
from src.payload_manager import PayloadManager
from src.api_client import JobKoreaAPIClient
from src.parser import PersonDataParser
from src.exporter import ExcelExporter


class JobKoreaScraper:
    """잡코리아 인재 검색 스크래퍼 메인 클래스"""

    def __init__(
        self,
        config: JobKoreaConfig,
        payload_manager: PayloadManager,
        output_dir: str = "."
    ):
        self.config = config
        self.api_client = JobKoreaAPIClient(config, payload_manager)
        self.parser = PersonDataParser(config.BASE_URL)
        self.exporter = ExcelExporter()
        self.output_dir = Path(output_dir)

    def scrape(
        self,
        start_page: int = 1,
        end_page: int = 1,
        page_size: int = 10,
        delay: float = 1.0,
        **search_options
    ) -> List[Dict[str, str]]:

        """
        인재 검색 및 데이터 수집

        Args:
            start_page: 시작 페이지
            end_page: 종료 페이지
            page_size: 페이지당 결과 수
            delay: 페이지 간 지연 시간(초)
            **search_options: 검색 옵션 (job_name, areas, education)
        """
        all_people = []
        current_index = 1  # 전체 누적 번호
        saveno = 0  # 🔥 검색 세션 ID (1페이지는 0, 2페이지부터 필요)

        for page in range(start_page, end_page + 1):
            # saveno 포함하여 검색
            response = self.api_client.search(page, page_size, saveno=saveno, **search_options)

            if "application/json" in response.headers.get("Content-Type", ""):
                self._save_json(response.json(), page)
            else:
                # 🔥 HTML에서 saveNo 추출 (다음 페이지 요청용)
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                saveno_elem = soup.select_one('input#saveNo')
                if saveno_elem and saveno_elem.get('value'):
                    saveno = int(saveno_elem.get('value'))
                    print(f"📌 saveNo 추출: {saveno}")

                # 데이터 파싱
                people = self._process_html(response.text, page, start_index=current_index)
                all_people.extend(people)
                current_index += len(people)  # 다음 페이지 시작 번호

            if page < end_page:
                time.sleep(delay)

        return all_people

    def _save_json(self, data: dict, page: int):
        """JSON 응답 저장"""
        filepath = self.output_dir / f"result_page{page}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {filepath} 저장 완료")

    def _process_html(self, html: str, page: int, start_index: int = 1) -> List[Dict[str, str]]:
        """HTML 응답 처리 및 저장"""
        # HTML 파일 저장
        html_filepath = self.output_dir / f"result_page{page}.html"
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html)

        # 데이터 파싱 (시작 번호 전달)
        people = self.parser.parse_html(html, start_index=start_index)
        print(f"✅ {len(people)}명 파싱 완료 (page {page}, 번호 {start_index}~{start_index+len(people)-1})")

        return people

    def save_results(self, people: List[Dict[str, str]]):
        """수집한 데이터 저장 (JSON + Excel)"""
        if not people:
            print("⚠️  수집된 데이터가 없습니다.")
            return

        print(f"\n총 {len(people)}명 수집됨")

        # JSON 저장
        json_filepath = self.output_dir / "people_summary.json"
        with open(json_filepath, "w", encoding="utf-8") as f:
            json.dump(people, f, ensure_ascii=False, indent=2)

        # 엑셀 저장
        excel_filepath = self.output_dir / "백엔드개발자_검색결과.xlsx"
        self.exporter.save(people, str(excel_filepath))

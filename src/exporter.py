"""데이터 내보내기"""
from typing import List, Dict
import openpyxl
from openpyxl.styles import Font, Alignment


class ExcelExporter:
    """엑셀 파일 저장"""

    COLUMNS = ["이름", "나이", "경력", "학력", "지역", "직무", "기술스택", "이력서번호", "이력서링크"]
    COLUMN_WIDTHS = {
        'A': 12, 'B': 15, 'C': 12, 'D': 30, 'E': 20,
        'F': 30, 'G': 50, 'H': 15, 'I': 60
    }

    def save(self, people: List[Dict[str, str]], filename: str = "백엔드개발자_검색결과.xlsx"):
        """데이터를 엑셀 파일로 저장"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "백엔드개발자"

        self._write_headers(ws)
        self._write_data(ws, people)
        self._adjust_columns(ws)

        wb.save(filename)
        print(f"✅ 엑셀 파일 저장 완료: {filename}")

    def _write_headers(self, ws):
        """헤더 작성 및 스타일 적용"""
        ws.append(self.COLUMNS)
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')

    def _write_data(self, ws, people: List[Dict[str, str]]):
        """데이터 작성"""
        for person in people:
            row = [person.get(col, "") for col in self.COLUMNS]
            ws.append(row)

    def _adjust_columns(self, ws):
        """열 너비 조정"""
        for col, width in self.COLUMN_WIDTHS.items():
            ws.column_dimensions[col].width = width

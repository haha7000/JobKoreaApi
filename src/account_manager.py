"""계정 관리 - 엑셀에서 계정 정보 읽기"""
import pandas as pd
from typing import Optional, Dict
from pathlib import Path


class AccountManager:
    """엑셀 '계정' 시트에서 아이디/비밀번호 관리"""

    def __init__(self, excel_path: str, account_sheet_name: str = "계정"):
        """
        Args:
            excel_path: 엑셀 파일 경로
            account_sheet_name: 계정 시트명 (기본: "계정")
        """
        self.excel_path = Path(excel_path)
        self.account_sheet_name = account_sheet_name

    def get_credentials(self, username: str) -> Optional[Dict[str, str]]:
        """
        특정 아이디의 인증 정보 가져오기

        Args:
            username: 찾을 아이디

        Returns:
            {"username": "...", "password": "..."} 또는 None
        """
        if not self.excel_path.exists():
            print(f"❌ 엑셀 파일을 찾을 수 없습니다: {self.excel_path}")
            return None

        try:
            # '계정' 시트 읽기
            df = pd.read_excel(self.excel_path, sheet_name=self.account_sheet_name)

            # 컬럼명 확인
            if "아이디" not in df.columns or "비밀번호" not in df.columns:
                print(f"❌ '계정' 시트에 '아이디', '비밀번호' 컬럼이 없습니다.")
                print(f"   현재 컬럼: {list(df.columns)}")
                return None

            # 아이디로 검색
            matched = df[df["아이디"] == username]

            if matched.empty:
                print(f"❌ 계정을 찾을 수 없습니다: {username}")
                print(f"   사용 가능한 계정: {list(df['아이디'].dropna())}")
                return None

            # 첫 번째 매칭된 행에서 비밀번호 가져오기
            password = matched.iloc[0]["비밀번호"]

            if pd.isna(password) or str(password).strip() == "":
                print(f"❌ 계정 '{username}'의 비밀번호가 비어있습니다.")
                return None

            print(f"✅ 계정 '{username}' 인증 정보 로드 완료")
            return {
                "username": username,
                "password": str(password).strip()
            }

        except Exception as e:
            print(f"❌ 계정 정보 읽기 오류: {e}")
            return None

    def list_accounts(self) -> list:
        """
        사용 가능한 모든 계정 목록 반환

        Returns:
            아이디 리스트
        """
        if not self.excel_path.exists():
            return []

        try:
            df = pd.read_excel(self.excel_path, sheet_name=self.account_sheet_name)

            if "아이디" not in df.columns:
                return []

            return list(df["아이디"].dropna())

        except Exception as e:
            print(f"❌ 계정 목록 읽기 오류: {e}")
            return []

    def get_all_sheet_names(self) -> list:
        """
        엑셀 파일의 모든 시트명 반환

        Returns:
            시트명 리스트
        """
        if not self.excel_path.exists():
            return []

        try:
            xl_file = pd.ExcelFile(self.excel_path)
            return xl_file.sheet_names

        except Exception as e:
            print(f"❌ 시트 목록 읽기 오류: {e}")
            return []

    def get_valid_account_sheets(self, excluded_sheets: list = None) -> list:
        """
        실행 가능한 계정 시트 목록 반환
        (고정 시트 제외 + 계정 시트에 존재하는 아이디만)

        Args:
            excluded_sheets: 제외할 시트명 리스트 (기본: ["직무스킬", "계정", "매핑"])

        Returns:
            실행 가능한 계정 시트명 리스트
        """
        if excluded_sheets is None:
            excluded_sheets = ["직무스킬", "계정", "매핑"]

        # 1. 모든 시트명 가져오기
        all_sheets = self.get_all_sheet_names()

        # 2. 고정 시트 제외
        candidate_sheets = [s for s in all_sheets if s not in excluded_sheets]

        # 3. 계정 목록 가져오기
        valid_accounts = self.list_accounts()

        # 4. 계정 시트에 있는 시트만 필터링
        valid_sheets = [s for s in candidate_sheets if s in valid_accounts]

        return valid_sheets

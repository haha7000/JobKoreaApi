# 잡코리아 인재 검색 스크래퍼

백엔드개발자 인재 정보를 검색하고 엑셀 파일로 저장하는 스크래퍼입니다.

## 📁 프로젝트 구조

```
apiTEst/
├── main.py                 # 🚀 메인 실행 파일
├── realTest.py             # ♻️  레거시 호환
│
├── src/                    # 📦 소스 코드
│   ├── __init__.py
│   ├── config.py           # ⚙️  설정 (API URL, 쿠키)
│   ├── payload_manager.py  # 📋 검색 조건 관리
│   ├── api_client.py       # 🌐 API 통신
│   ├── parser.py           # 🔍 데이터 파싱
│   ├── exporter.py         # 📊 엑셀 저장
│   └── scraper.py          # 🤖 스크래퍼 메인 로직
│
├── data/                   # 📄 데이터 파일
│   ├── payload_template.json
│   └── *.txt
│
├── output/                 # 📤 출력 파일
│   ├── 백엔드개발자_검색결과.xlsx
│   ├── people_summary.json
│   └── result_page*.html
│
└── docs/                   # 📚 문서
    └── README.md
```

## 🚀 빠른 시작

```bash
# 1. 설치
pip install requests beautifulsoup4 openpyxl

# 2. 쿠키 설정 (src/config.py)
COOKIE_STR = "브라우저에서 복사한 쿠키"

# 3. 실행
python main.py
```

## 📤 출력

- `output/백엔드개발자_검색결과.xlsx` - 엑셀
- `output/people_summary.json` - JSON
- `output/result_page*.html` - HTML 원본

# 잡코리아 인재 검색 스크래퍼 🔍

백엔드개발자 인재 정보를 자동으로 검색하고 엑셀 파일로 저장하는 스크래퍼입니다.

## 📁 프로젝트 구조

```
apiTEst/
├── main.py                 # 🚀 메인 실행 파일
├── realTest.py            # ♻️  레거시 호환
│
├── src/                   # 📦 소스 코드
│   ├── config.py          # ⚙️  설정 (API, 쿠키)
│   ├── payload_manager.py # 📋 검색 조건 관리
│   ├── api_client.py      # 🌐 API 통신
│   ├── parser.py          # 🔍 HTML 파싱
│   ├── exporter.py        # 📊 엑셀 저장
│   └── scraper.py         # 🤖 메인 로직
│
├── data/                  # 📄 입력 데이터
│   └── payload_template.json
│
├── output/                # 📤 출력 파일
│   ├── 백엔드개발자_검색결과.xlsx
│   ├── people_summary.json
│   └── result_page*.html
│
└── docs/                  # 📚 문서
    └── README.md
```

## 🚀 빠른 시작

### 1. 설치
```bash
pip install requests beautifulsoup4 openpyxl
```

### 2. 설정
`src/config.py`에 브라우저 쿠키 입력:
```python
COOKIE_STR = "JSESSIONID=...; JKUID=...; ..."
```

### 3. 실행
```bash
python main.py
```

## 📤 출력 파일

- `output/백엔드개발자_검색결과.xlsx` - 인재 정보 엑셀
- `output/people_summary.json` - JSON 형식
- `output/result_page*.html` - 원본 HTML

## 📖 상세 문서

[docs/README.md](docs/README.md) 참고

## 🏗️ 주요 기능

✅ 백엔드개발자 필터링 검색
✅ 이름, 경력, 기술스택, 학력, 지역 추출
✅ 이력서 링크 포함
✅ 엑셀/JSON 저장
✅ 페이지네이션 지원

## ⚙️ 설정 변경

`main.py`:
```python
people = scraper.scrape(
    start_page=1,     # 시작 페이지
    end_page=10,      # 종료 페이지  
    page_size=100,    # 페이지당 인원
    delay=1.0         # 대기 시간(초)
)
```

## 📝 라이센스

개인 사용 및 학습 목적

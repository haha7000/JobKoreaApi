"""1페이지, 2페이지, 4페이지 payload 비교"""
import re
import json
import urllib.parse

def extract_payload_from_curl(file_path):
    """cURL 파일에서 searchCondition payload 추출"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --data-raw 'searchCondition=...' 부분 찾기
    match = re.search(r'searchCondition=([^\s\'\"]+)', content)
    if match:
        encoded = match.group(1)
        decoded = urllib.parse.unquote(encoded)
        return json.loads(decoded)
    return None

# 각 페이지 payload 추출
page1 = extract_payload_from_curl('detailsearchajaxCurl/detailsearchajax1Page.txt')
page2 = extract_payload_from_curl('detailsearchajaxCurl/detailsearchajax2Page.txt')
page4 = extract_payload_from_curl('detailsearchajaxCurl/detailsearchajax4Page.txt')

print("="*80)
print("📊 1페이지, 2페이지, 4페이지 Payload 비교")
print("="*80)

# 기본 정보 비교
print("\n🔍 핵심 필드 비교:")
print(f"{'필드':<15} {'1페이지':<20} {'2페이지':<20} {'4페이지':<20}")
print("-"*80)

fields = ['p', 'ps', 'saveno', 'sf', 'ff', 'savectgrcode']
for field in fields:
    v1 = page1.get(field, 'N/A')
    v2 = page2.get(field, 'N/A')
    v4 = page4.get(field, 'N/A')
    print(f"{field:<15} {str(v1):<20} {str(v2):<20} {str(v4):<20}")

# 차이점 찾기
print("\n"+"="*80)
print("🔥 차이점 분석")
print("="*80)

all_keys = set(page1.keys()) | set(page2.keys()) | set(page4.keys())
diff_fields = []

for key in sorted(all_keys):
    v1 = page1.get(key)
    v2 = page2.get(key)
    v4 = page4.get(key)

    if not (v1 == v2 == v4):
        diff_fields.append(key)
        print(f"\n[{key}]")
        print(f"  1페이지: {v1}")
        print(f"  2페이지: {v2}")
        print(f"  4페이지: {v4}")

if not diff_fields:
    print("\n차이점 없음!")
else:
    print(f"\n총 {len(diff_fields)}개 필드가 다릅니다: {diff_fields}")

print("\n"+"="*80)

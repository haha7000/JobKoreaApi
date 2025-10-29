"""1~4페이지 모든 payload 비교"""
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
pages = {}
for i in range(1, 5):
    pages[i] = extract_payload_from_curl(f'detailsearchajaxCurl/detailsearchajax{i}Page.txt')

print("="*80)
print("📊 1~4페이지 모든 Payload 비교")
print("="*80)

# 기본 정보 비교
print("\n🔍 핵심 필드 비교:")
print(f"{'필드':<15} {'1페이지':<15} {'2페이지':<15} {'3페이지':<15} {'4페이지':<15}")
print("-"*80)

fields = ['p', 'ps', 'saveno', 'sf', 'ff', 'savectgrcode']
for field in fields:
    values = [str(pages[i].get(field, 'N/A')) for i in range(1, 5)]
    print(f"{field:<15} {values[0]:<15} {values[1]:<15} {values[2]:<15} {values[3]:<15}")

# saveno 변화 추적
print("\n" + "="*80)
print("🔥 saveno 변화 추적 (핵심!)")
print("="*80)
for i in range(1, 5):
    saveno = pages[i].get('saveno')
    p = pages[i].get('p')
    print(f"{i}페이지: p={p}, saveno={saveno}")

# 차이점 분석
print("\n" + "="*80)
print("📝 차이점 분석")
print("="*80)

all_keys = set()
for page in pages.values():
    all_keys.update(page.keys())

diff_fields = []
for key in sorted(all_keys):
    values = [pages[i].get(key) for i in range(1, 5)]

    # 모두 같은지 확인
    if not all(v == values[0] for v in values):
        diff_fields.append(key)

if diff_fields:
    print(f"\n다른 필드: {diff_fields}")
    for field in diff_fields:
        print(f"\n[{field}]")
        for i in range(1, 5):
            print(f"  {i}페이지: {pages[i].get(field)}")
else:
    print("\n모든 필드가 동일합니다!")

# 결론
print("\n" + "="*80)
print("✅ 결론")
print("="*80)

# saveno 패턴 확인
savenos = [pages[i].get('saveno') for i in range(1, 5)]
if savenos[0] == 0 and all(s == savenos[1] for s in savenos[1:]):
    print("✅ 1페이지: saveno=0")
    print(f"✅ 2~4페이지: 동일한 saveno={savenos[1]} 사용")
    print("\n👉 이것이 정상입니다! 첫 검색에서 받은 saveno를 계속 재사용합니다.")
elif len(set(savenos)) == 4:
    print("⚠️  모든 페이지가 다른 saveno를 사용합니다.")
else:
    print(f"🤔 saveno 패턴: {savenos}")

print("="*80)

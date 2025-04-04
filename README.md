# 네이버 지도 가챠샵 크롤러

이 프로젝트는 네이버 지도에서 가챠샵(캡슐토이샵) 정보를 자동으로 수집하는 크롤러입니다. Selenium을 사용하여 웹 브라우저를 제어하고, 검색 결과에서 상점명, 주소, 전화번호, 영업시간 등의 정보를 추출합니다.

## 기능

- 네이버 지도에서 가챠샵 정보 자동 수집
- 상점명, 카테고리, 주소, 전화번호, 영업시간, 인스타그램, 홈페이지, 스마트스토어, 시설정보, 위치정보 추출
- CSV 파일로 결과 저장

## 설치 방법

1. Python 3.6 이상이 설치되어 있어야 합니다.
2. Chrome 브라우저가 설치되어 있어야 합니다.
3. 다음 명령어로 필요한 패키지를 설치합니다:

```bash
pip install selenium
```

4. Chrome 웹 드라이버가 필요합니다. 크롬 브라우저 버전에 맞는 웹 드라이버를 다운로드하거나, 다음 명령어로 자동 설치할 수 있습니다:

```bash
pip install webdriver-manager
```

## 실행 방법

1. 프로젝트를 클론하거나 다운로드합니다.
2. 터미널이나 명령 프롬프트에서 다음 명령어를 실행합니다:

```bash
python navermap/NaverMapSelenium.py
```

3. 프로그램이 실행되면 Chrome 브라우저가 자동으로 열리고 가챠샵 정보를 수집합니다.
4. 수집된 결과는 `gacha_shops_[날짜]_[시간].csv` 형식의 파일로 저장됩니다.

## 검색어 추가 방법

검색어를 추가하거나 변경하려면 `NaverMapSelenium.py` 파일의 32번째 줄에 있는 `search_queries` 리스트를 수정하세요:

```python
# 검색어 목록
search_queries = ["홍대 갓챠", "성수 갓챠"]
```

원하는 검색어를 리스트에 추가하면 됩니다. 예를 들어:

```python
# 검색어 목록
search_queries = ["홍대 갓챠", "성수 갓챠", "강남 가챠", "종로 캡슐토이"]
```

## 출력 결과

크롤링 결과는 다음 형식으로 CSV 파일에 저장됩니다:

- 상점명: 가챠샵 이름
- 카테고리: 상점 카테고리 (주로 장난감, 취미 등)
- 주소: 상점 주소
- 전화번호: 상점 연락처
- 영업시간: 요일별 영업시간
- 검색어: 해당 상점을 찾은 검색어
- 인스타그램: 인스타그램 링크 (있는 경우)
- 홈페이지: 홈페이지 링크 (있는 경우)
- 스마트스토어: 네이버 스마트스토어 링크 (있는 경우)
- 시설정보: 시설 관련 정보
- 위치정보: 근처 지하철역 등 위치 정보

## 주의사항

이 크롤러는 학습 및 연구 목적으로만 사용해야 합니다. 네이버 서비스 이용약관을 준수하고, 수집한 데이터를 상업적으로 이용하지 마세요. 
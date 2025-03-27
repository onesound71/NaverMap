# 네이버 지도 가챠샵 크롤러
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv
import os
import re

# 결과를 저장할 CSV 파일 생성 (타임스탬프 추가)
timestamp = time.strftime("%Y%m%d_%H%M%S")
output_file = f'gacha_shops_{timestamp}.csv'
with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['상점명', '카테고리', '주소', '전화번호', '영업시간', '검색어', '인스타그램', '홈페이지', '스마트스토어', '시설정보', '위치정보'])

options = Options()
# options.add_argument('--headless')  # 화면을 표시하지 않음 (디버깅하려면 주석 처리)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("--disable-notifications")
options.add_argument("--lang=ko")

print("브라우저 시작 중...")
driver = webdriver.Chrome(options=options)

# 검색어 목록
search_queries = ["홍대 갓챠", "성수 갓챠"]
collected_names = set()  # 중복 확인용 상점명 세트
total_items = 0

# 카테고리 정보 - 특정 키워드가 있으면 카테고리로 인식
category_keywords = ["장난감", "문구", "팬시", "완구", "캡슐토이", "피규어", "취미"]

try:
    # 검색어로 크롤링 실행
    for search_query in search_queries:
        # 검색 시작 전 변수 초기화
        name = ""
        address = ""
        category = ""
        tel = ""
        hours = ""
        instagram = ""
        homepage = ""
        smartstore = ""
        facilities = ""
        location = ""
        detailed_address = ""
        
        driver.get(f"https://map.naver.com/p/search/{search_query}")
        
        # 페이지 로딩 기다리기
        time.sleep(5)
        
        # 검색 결과 iframe으로 전환
        try:
            search_frame = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe"))
            )
            driver.switch_to.frame(search_frame)
        except TimeoutException:
            continue
        
        # 검색 결과 항목들 가져오기
        try:
            items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.VLTHu, li.UEzoS"))
            )
            
            # 최대 20개의 항목만 처리
            for idx, item in enumerate(items[:20], 1):
                try:
                    # 이름 추출
                    name = ""
                    # 검색 결과 목록에서 이름 추출 시도 (YwYLL 클래스를 우선적으로 찾음)
                    try:
                        # place_bluelink 내부에 있는 YwYLL 클래스의 span 요소를 찾음
                        name_el = item.find_element(By.CSS_SELECTOR, "div.place_bluelink span.YwYLL, .place_bluelink span.YwYLL")
                        name = name_el.text.strip()
                    except:
                        # 기존 방식으로 시도
                        for name_selector in [".place_bluelink", ".TYaxT", "a.name"]:
                            try:
                                name_el = item.find_element(By.CSS_SELECTOR, name_selector)
                                name = name_el.text.strip()
                                if name:
                                    break
                            except:
                                continue
                    
                    # 이름이 없거나 이미 수집한 항목이면 건너뜀
                    if not name or name in collected_names:
                        continue
                    
                    # 주소 및 카테고리 추출
                    address = ""
                    category = ""
                    for el in item.find_elements(By.TAG_NAME, "span"):
                        text = el.text.strip()
                        if any(keyword in text for keyword in ["시", "구", "동", "읍", "면", "로", "길"]):
                            address = text
                        elif "·" in text and len(text) < 20:
                            category = text.split("·")[0].strip()
                    
                    # 카테고리가 없으면 장난감 카테고리로 설정 (가챠샵은 대체로 장난감 카테고리)
                    if not category and "가챠" in name.lower():
                        category = "장난감"
                    
                    # 클릭하여 상세 정보 가져오기
                    try:
                        # 항목 클릭
                        for click_selector in [".place_bluelink", "a"]:
                            try:
                                item.find_element(By.CSS_SELECTOR, click_selector).click()
                                break
                            except:
                                continue
                        
                        # 상세 정보 패널 로드 대기
                        time.sleep(3)
                        
                        # 원래 iframe에서 나가기
                        driver.switch_to.default_content()
                        
                        # 상세 정보 iframe으로 전환
                        detail_frame = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#entryIframe"))
                        )
                        driver.switch_to.frame(detail_frame)
                        
                        # YwYLL 클래스로 상세 페이지에서 더 정확한 상점명 추출 시도
                        try:
                            name_element = driver.find_element(By.CSS_SELECTOR, "span.YwYLL")
                            if name_element:
                                detailed_name = name_element.text.strip()
                                if detailed_name:
                                    name = detailed_name
                        except:
                            pass
                        
                        # 전화번호, 주소, 영업시간, 추가정보 초기화
                        tel = ""
                        hours = ""
                        detailed_address = ""
                        instagram = ""
                        homepage = ""
                        smartstore = ""
                        facilities = ""
                        location = ""
                        
                        # 카테고리 정보 업데이트
                        try:
                            for category_selector in [".DJJvD", ".category", ".OXiLu", ".cQ4J9"]:
                                try:
                                    category_element = driver.find_element(By.CSS_SELECTOR, category_selector)
                                    category_text = category_element.text.strip()
                                    if category_text:
                                        category = category_text
                                        break
                                except:
                                    continue
                            
                            # 카테고리가 없는 경우 키워드 검색
                            if not category:
                                page_text = driver.find_element(By.TAG_NAME, "body").text
                                for keyword in category_keywords:
                                    if keyword in page_text:
                                        category = keyword
                                        break
                        except:
                            pass
                        
                        # 주소 추출 - 여러 방법으로 시도
                        try:
                            # 1. LDgIH 클래스로 주소 찾기 (iframe에서의 주소 표시)
                            try:
                                address_elements = driver.find_elements(By.CSS_SELECTOR, ".LDgIH")
                                if address_elements:
                                    address = address_elements[0].text.strip()
                            except:
                                pass
                                
                            # 2. 도로명/지번 주소 찾기 (nQ7Lh 클래스 사용)
                            if not address:
                                try:
                                    address_elements = driver.find_elements(By.CSS_SELECTOR, ".nQ7Lh")
                                    for address_element in address_elements:
                                        address_text = address_element.text.strip()
                                        if "도로명" in address_text:
                                            # "도로명" 텍스트 제거하고 "복사" 텍스트도 제거
                                            road_address = address_text.replace("도로명", "").replace("복사", "").strip()
                                            address = road_address
                                            break
                                        elif "지번" in address_text:
                                            # "지번" 텍스트 제거하고 "복사" 텍스트도 제거
                                            jibun_address = address_text.replace("지번", "").replace("복사", "").strip()
                                            if not address:
                                                address = jibun_address
                                except:
                                    pass
                            
                            # 3. vV_z_ 클래스로 추가 주소 정보 찾기
                            try:
                                address_info_element = driver.find_element(By.CSS_SELECTOR, ".vV_z_")
                                if address_info_element:
                                    address_info = address_info_element.text.strip()
                                    if address_info and "복사" not in address_info:
                                        # 이미 추출한 주소와 중복되지 않는지 확인
                                        if address and address not in address_info and address_info not in address:
                                            address = f"{address} ({address_info})"
                                        elif not address:
                                            address = address_info
                            except:
                                pass
                        except:
                            pass
                        
                        # 전화번호 추출 - 특정 클래스 사용
                        try:
                            # xlx7Q 클래스로 정확히 찾기
                            phone_element = driver.find_element(By.CSS_SELECTOR, ".xlx7Q")
                            if phone_element:
                                tel = phone_element.text.strip()
                        except:
                            pass

                        # 영업시간 추출 - 여러 방법으로 추출
                        try:
                            # "펼쳐보기" 버튼 클릭 시도
                            try:
                                # "펼쳐보기" 텍스트가 있는 요소를 찾아 부모 요소를 클릭
                                expand_blind_elements = driver.find_elements(By.CSS_SELECTOR, "span.place_blind")
                                for blind_element in expand_blind_elements:
                                    if "펼쳐보기" in blind_element.text:
                                        # 부모 요소(span._UCia)를 찾아 클릭
                                        parent_element = blind_element.find_element(By.XPATH, "..")
                                        parent_element.click()
                                        time.sleep(1)  # 펼쳐지는 동안 잠시 대기
                                        break
                            except:
                                # 대체 방법으로 직접 span._UCia 요소 찾기 시도
                                try:
                                    expand_buttons = driver.find_elements(By.CSS_SELECTOR, "span._UCia")
                                    for button in expand_buttons:
                                        if button.find_elements(By.CSS_SELECTOR, "span.place_blind"):
                                            button.click()
                                            time.sleep(1)
                                            break
                                except:
                                    pass
                            
                            # <time> 태그 찾기
                            time_elements = driver.find_elements(By.TAG_NAME, "time")
                            if time_elements:
                                for time_element in time_elements:
                                    time_text = time_element.text.strip()
                                    if time_text and "영업" in time_text:
                                        hours = time_text
                                        break
                            
                            # 요일별 영업시간 정보 추출
                            days_info = []
                            day_elements = driver.find_elements(By.CSS_SELECTOR, "div.w9QyJ")
                            for day_element in day_elements:
                                try:
                                    day = day_element.find_element(By.CSS_SELECTOR, "span.i8cJw").text.strip()
                                    time_or_status = day_element.find_element(By.CSS_SELECTOR, "div.H3ua4").text.strip()
                                    days_info.append(f"{day}: {time_or_status}")
                                except:
                                    pass
                            
                            # 영업 중 상태 및 곧 종료 정보 추출
                            try:
                                status_element = driver.find_element(By.CSS_SELECTOR, "div.w9QyJ.vI8SM")
                                if status_element:
                                    status = status_element.text.strip()
                                    if status and "영업 중" in status:
                                        if days_info:
                                            days_info.insert(0, status)
                                        else:
                                            days_info.append(status)
                            except:
                                pass
                                
                            # 요일별 영업시간 정보를 hours에 저장
                            if days_info:
                                # 중복 내용 제거 (시간 형식이 다른 경우 예: "20:00에 영업 종료"와 "20시 0분에 영업 종료")
                                filtered_info = []
                                time_patterns = {}  # 시간 패턴을 저장할 딕셔너리
                                
                                for info in days_info:
                                    # 숫자만 추출하여 패턴 비교 (시간 값만 추출)
                                    numbers = re.findall(r'\d+', info)
                                    time_pattern = ''.join(numbers) if numbers else ''
                                    
                                    # 이미 동일한 숫자 패턴이 있고, "place_blind"가 포함된 텍스트인 경우 스킵
                                    if time_pattern in time_patterns and "place_blind" in info:
                                        continue
                                    
                                    # 매우 유사한 내용이 이미 있는지 확인 (예: "20:00에 영업 종료"와 "20시 0분에 영업 종료")
                                    similar_exists = False
                                    for existing_info in filtered_info:
                                        # 동일한 숫자 패턴을 가지고 있고 내용이 비슷한 경우
                                        if time_pattern and time_pattern in time_patterns.get(existing_info, '') and \
                                           (("영업 종료" in info and "영업 종료" in existing_info) or 
                                            ("영업 시작" in info and "영업 시작" in existing_info)):
                                            similar_exists = True
                                            break
                                    
                                    if not similar_exists:
                                        filtered_info.append(info)
                                        if time_pattern:
                                            time_patterns[info] = time_pattern
                                
                                hours = " | ".join(filtered_info)
                            
                            # 기존 방식의 영업 시간 추출 (H3ua4 클래스) - 요일별 정보가 없는 경우
                            if not hours:
                                try:
                                    time_div = driver.find_element(By.CSS_SELECTOR, "div.H3ua4")
                                    if time_div:
                                        hours = time_div.text.strip()
                                except:
                                    pass
                                    
                                # 영업일 정보 추출 (A_cdD 클래스)
                                try:
                                    day_span = driver.find_element(By.CSS_SELECTOR, "span.A_cdD span.i8cJw")
                                    if day_span:
                                        day_info = day_span.text.strip()
                                        if day_info and hours:
                                            hours = f"{day_info} {hours}"
                                        elif day_info:
                                            hours = day_info
                                except:
                                    pass
                        except:
                            pass
                        
                        # 인스타그램, 홈페이지, 스마트스토어 링크 추출
                        try:
                            links = driver.find_elements(By.CSS_SELECTOR, ".place_bluelink")
                            for link in links:
                                href = link.get_attribute("href")
                                if href:
                                    if "instagram.com" in href:
                                        instagram = href
                                    elif "smartstore.naver.com" in href:
                                        smartstore = href
                                    elif not href.startswith("https://map.naver.com") and not href.startswith("tel:"):
                                        homepage = href
                        except:
                            pass
                        
                        # 시설정보 추출
                        try:
                            facility_element = driver.find_element(By.CSS_SELECTOR, ".xPvPE")
                            facilities = facility_element.text.strip()
                        except:
                            pass
                        
                        # 위치정보 추출
                        try:
                            location_elements = driver.find_elements(By.CSS_SELECTOR, ".nZapA")
                            for location_element in location_elements:
                                if "출구에서" in location_element.text:
                                    location = location_element.text.strip()
                                    # 첫 글자가 숫자인 경우 삭제
                                    if location and location[0].isdigit():
                                        location = location[1:].strip()
                                    # "미터" 텍스트가 있는 경우 삭제
                                    location = location.replace("미터", "").strip()
                                    # 줄바꿈이 있는 경우 첫 번째 줄만 사용
                                    if "\n" in location:
                                        location = location.split("\n")[0].strip()
                                    break
                        except:
                            pass
                        
                        # 상세 정보 추출 (영업시간과 전화번호가 아직 없는 경우)
                        if not hours or not tel:
                            for content_selector in [".place_section_content", ".O8qbU", ".kGc0c"]:
                                try:
                                    sections = driver.find_elements(By.CSS_SELECTOR, content_selector)
                                    for section in sections:
                                        text = section.text
                                        
                                        # 영업시간 추출 (아직 없는 경우)
                                        if not hours and "영업시간" in text:
                                            hours_lines = []
                                            for line in text.split('\n'):
                                                if "영업시간" in line or (hours_lines and any(day in line for day in ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일", "공휴일", "매일"])):
                                                    hours_lines.append(line.strip())
                                            
                                            if hours_lines:
                                                hours = " | ".join(hours_lines)
                                                if hours == "영업시간":
                                                    # 영업시간만 있는 경우, 다음 줄까지 포함
                                                    lines = text.split('\n')
                                                    for i, line in enumerate(lines):
                                                        if "영업시간" in line and i+1 < len(lines):
                                                            hours = f"{line} {lines[i+1]}"
                                                            break
                                        
                                        # 전화번호 추출 (아직 없는 경우)
                                        if not tel and "전화" in text:
                                            for line in text.split('\n'):
                                                if "전화" in line and '-' in line:
                                                    parts = line.split(':', 1)
                                                    if len(parts) > 1:
                                                        tel = parts[1].strip()
                                                        break
                                                        
                                        # 상세 주소 추출 (아직 없는 경우)
                                        if not address and ("지번 주소" in text or "도로명 주소" in text):
                                            for line in text.split('\n'):
                                                if "지번 주소" in line or "도로명 주소" in line:
                                                    parts = line.split(':', 1)
                                                    if len(parts) > 1:
                                                        detailed_address = parts[1].strip()
                                                        address = detailed_address
                                                        break
                                except:
                                    continue
                            
                        # 다시 원래 검색 결과 iframe으로 복귀
                        driver.switch_to.default_content()
                        driver.switch_to.frame(search_frame)
                        
                    except Exception as e:
                        pass
                    
                    # 카테고리 확인 - 가챠/캡슐토이 관련 상점은 장난감으로 분류
                    if not category and any(keyword in name.lower() for keyword in ["가챠", "캡슐", "토이"]):
                        category = "장난감"
                    
                    # 수집 결과 출력 및 저장
                    print("\n" + "=" * 60)
                    print(f"상호명 : {name}")
                    print(f"카테고리: {category or '장난감'}")  # 카테고리 정보가 없으면 '장난감'으로 표시
                    print(f"주소: {address or '정보 없음'}")
                    print(f"전화번호: {tel or '정보 없음'}")
                    print(f"영업시간: {hours or '정보 없음'}")
                    if instagram:
                        print(f"인스타그램: {instagram}")
                    if homepage:
                        print(f"홈페이지: {homepage}")
                    if smartstore:
                        print(f"스마트스토어: {smartstore}")
                    if facilities:
                        print(f"시설정보: {facilities}")
                    if location:
                        print(f"위치정보: {location}")
                        
                    print("=" * 60)
                    
                    # CSV 파일에 저장
                    with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow([name, category or '장난감', address, tel, hours, search_query, instagram, homepage, smartstore, facilities, location])
                    
                    # 수집된 상점명에 추가
                    collected_names.add(name)
                    total_items += 1
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            continue
            
    print(f"\n크롤링 완료!")
    print(f"총 {total_items}개 항목을 '{output_file}' 파일에 저장했습니다.")
    print(f"고유한 상점 수: {len(collected_names)}개")
    
except Exception as e:
    print(f"오류 발생: {str(e)}")

finally:
    # 웹페이지 닫음
    driver.quit()

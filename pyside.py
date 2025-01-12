from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QCoreApplication, Signal, Slot
from tracking_ui import Ui_MainWindow
import pandas as pd
import time
from datetime import timedelta
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import pyautogui
import configparser
from bs4 import BeautifulSoup
import datetime
from webdriver_manager.chrome import ChromeDriverManager  # 크롬드라이버 자동업데이트

class MainWindow(QMainWindow, Ui_MainWindow):
    service = None
    driver = None
    config = configparser.ConfigParser()
    ini_filename = './save.ini'
    section_name = 'Section1'
    key_username = 'alie_username'
    key_password = 'alie_password'
    list_tracking = []
    list_shipmemo = []
    update_text_signal = Signal(str) ##셀레니움이 비동기로 작동하기 때문에 셀레니움 작업중에 내용을 ui에 표시하려면 PyQt에서 시그널 및 슬롯을 사용하여 Selenium 관련 코드와 GUI 업데이트를 연결해야 함.
    chk_state = int
    
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.read_ini()
        self.update_text_signal.connect(self.update_text_browser)
        tMessage ="엑셀 파일을 넣어주세요."
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()

        
    def start(self):
        ship_url = 'https://www.aliexpress.com/p/order/index.html?tab=shipped'
        self.random_sec = random.uniform(1,2.5)
        self.random_sec2 = random.uniform(1,3)
        start_time = time.time()
        
        tMessage ="배송조회 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        alie_ID = self.lineEdit_id.text()
        alie_PW = self.lineEdit_pw.text()
        
        if alie_ID == "" or alie_PW == "":
            tMessage ="아이디 또는 패스워드를 입력해 주세요."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            
        else:
            print(alie_ID)
            print(alie_PW)
        
        exUrl = self.lineEdit_path.text()
        
        if exUrl =="":
            tMessage ="배송리스트 엑셀 파일을 선택해 주세요."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            
        else:pass
        
        self.write_ini(self.ini_filename, self.section_name, self.key_username, alie_ID)
        self.write_ini(self.ini_filename, self.section_name, self.key_password, alie_PW)
        
        self.filter_state()
        
        combo_date = self.combo_date.currentText()
        delay_date = int(combo_date)
        
        df = pd.DataFrame()
        df = self.read_files(exUrl, self.chk_state,delay_date) #특정 송장번호(직접전달, slx택배, 기타택배)만 조회
        df_shiptrack = pd.DataFrame()
        
        try:
         df_shiptrack = df[['주문일','주문고유코드','해외주문번호','수령자']] #특정 필드만 추출하여 새 테이블에 담는다
         
        except:
            tMessage ="불러온 엑셀파일의 필드명을 확인해 주세요."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()  
           
        df_shiptrack = df_shiptrack.astype(str)
        input_list = df_shiptrack['해외주문번호'].values.tolist()
        total_cnt = len(input_list)
        tMessage ='조회 대상 주문 건수: '+ str(total_cnt) +'개'
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        
        #브라우저 자동꺼짐 방지
        options = Options()
        options.add_experimental_option('detach',True)
        options.add_argument("--disable-blink-features=AutomationControlled") #셀레니움으로 조작하고 있다는 사실을 감춤
        options.add_argument("disable-gpu")   # 가속 사용 x
        options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
        options.add_argument("--disable-images") # 이미지 표시 x
        options.add_argument("--start-maximized") # 브라우저 최대
        options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36)")
        options.add_experimental_option("excludeSwitches", ['enable-logging', 'enable-automation'])#자동화 되고 있다는 표시 가림
        options.add_argument('--no-sandbox') #웹사이트가 봇 탐지를 위해 사용하는 보안 검사를 우회
        options.add_experimental_option('useAutomationExtension', False) #Chrome의 자동화 확장 프로그램을 비활성화 #셀레니움 자동화 관련 끔
        
        prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        
        # 추가적인 알림 비활성화 (선택적)
        "profile.default_content_setting_values.notifications": 2,  # 알림 차단
        "profile.default_content_setting_values.media_stream_mic": 2,  # 마이크 접근 차단
        "profile.default_content_setting_values.media_stream_camera": 2,  # 카메라 접근 차단
        "profile.default_content_setting_values.geolocation": 2  # 위치 정보 접근 차단
        }
        options.add_experimental_option("prefs", prefs)

        self.service = Service()
        self.driver = webdriver.Chrome(service=self.service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.sign_In(ship_url,alie_ID,alie_PW)
        
        orderid_list = []
        orderid_list = self.shipped_parcing()
        
        self.list_shipmemo, self.list_tracking, tracking_num = self.ship_stat(input_list,orderid_list)
        #tracking_num = self.get_trNum()
        dcompany = self.find_company(tracking_num)
        
        self.driver.quit()
        df_shiptrack = df_shiptrack.copy()
        df_shiptrack['송장번호'] = tracking_num
        df_shiptrack['택배사'] = dcompany
        df_shiptrack['상태메모'] = self.list_shipmemo
        df_shiptrack['추적Url'] = self.list_tracking
        
        ship_condition = ['한국통관중', '관세납부요청','한국통관완료','한국세관반출','배송실패','국내택배사인계','국내배송시작','국내배송출발','배송완료']
        df_shiptrack2 = df_shiptrack.loc[df_shiptrack['상태메모'].isin(ship_condition)]
        
        now = datetime.datetime.now()
        genTime = now.strftime("%y-%m-%d_%H-%M-%S")
        excel_filename = './조회결과_'+genTime + '.xlsx'
        excel_filename2 = './업로드용_'+genTime + '.xlsx'
        df_shiptrack.astype(str)
        df_shiptrack2.astype(str)
        df_shiptrack.to_excel(excel_filename,index=False)
        df_shiptrack2.to_excel(excel_filename2,index=False)
        
        tMessage ="엑셀파일 저장 완료!!"
        print(tMessage)
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        elapsed_timedelta = timedelta(seconds=int(elapsed_time))
        strTime = str(elapsed_timedelta)
        
        tMessage ="모든 작업 완료!!"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        tMessage = f"총 소요시간: {strTime}"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        print(tMessage)
    
    @Slot(int)
    def filter_state(self):
        if self.chkBox_filter.isChecked():
            print('체크박스 상태: 체크됨')
            self.chk_state = 0
            
        else:
            print('체크박스 상태: 해제됨')
            self.chk_state = 1
            
    def read_ini(self):
        ini_filename = './save.ini'
        section_name = 'Section1'
        key_username = 'alie_username'
        key_password = 'alie_password'
        alie_ID = None
        alie_PW = None
        
        try:
            self.config.read(ini_filename, encoding='utf-8')
            
        except configparser.MissingSectionHeaderError:
            tMessage ="INI 파일이 존재하지 않거나 형식이 잘못되었습니다."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            
            return None, None

        if self.config.has_section(section_name) and self.config.has_option(section_name, key_username):
            alie_ID = self.config.get(section_name, key_username)
            alie_PW = self.config.get(section_name, key_password)
            
            self.lineEdit_id.setText(alie_ID)
            self.lineEdit_pw.setText(alie_PW)
            
            
        else:
            tMessage ="INI 파일이 존재하지 않거나 형식이 잘못되었습니다."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            
            
        return alie_ID, alie_PW
            
    def write_ini(self,filename, section, key, value):
        self.config = configparser.ConfigParser()
        
        try:
            self.config.read(filename,encoding='utf-8')
            
        except configparser.MissingSectionHeaderError:
            tMessage ="save.ini파일에 쓸 수 없습니다."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            

        # Check if the section exists, if not, create it
        if not self.config.has_section(section):
            self.config.add_section(section)

        # Set the value in the specified section
        self.config.set(section, key, value)

        # Write the changes back to the INI file
        with open(filename, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
        
    def read_files(self, exUrl, chk_state, delay_date):
        delay_date = delay_date
        today = datetime.datetime.today()
        days_ago = today - datetime.timedelta(days=delay_date)
        
        tMessage = "엑셀파일 읽기 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        try:  
            df = pd.read_excel(exUrl, header=0, dtype={'수령자': str, '해외주문번호': str, '주문고유코드': str})
            df['주문일'] = pd.to_datetime(df['주문일'])
            
            if chk_state == 0:
                target = ['SLX택배', '기타택배', '직접전달']
                df_true = df.loc[df['택배사'].isin(target)]
                df_true2 = df_true[df_true["주문일"] <= days_ago]
                return df_true2
            
            else:
                return df
            
        except FileNotFoundError:
            error_message = f"* 파일을 찾을 수 없습니다: {exUrl}"
            self.update_text_signal.emit(error_message)
        
        except PermissionError:
            error_message = f"* 파일에 접근할 권한이 없습니다: {exUrl}"
            self.update_text_signal.emit(error_message)
        
        except pd.errors.EmptyDataError:
            error_message = "* 엑셀 파일이 비어 있습니다."
            self.update_text_signal.emit(error_message)
        
        except pd.errors.ParserError:
            error_message = "* 엑셀 파일 파싱 중 오류가 발생했습니다. 파일 형식을 확인해주세요."
            self.update_text_signal.emit(error_message)
        
        except KeyError as e:
            error_message = f"* 엑셀 파일에서 필요한 열을 찾을 수 없습니다: {str(e)}"
            self.update_text_signal.emit(error_message)
            
        except Exception as e:
            error_message = f"* 예상치 못한 오류가 발생했습니다: {str(e)}"
            self.update_text_signal.emit(error_message)
        
        return None
             

    def filedialog_open(self):
        fname = QFileDialog.getOpenFileName(self, '', '', "Excel Files (*.xlsx *.xls)")
        if fname[0]:
            file_path = fname[0]
            self.lineEdit_path.setText(file_path)
            
            _, file_extension = os.path.splitext(file_path)
            
            try:
                if file_extension.lower() == '.xlsx':
                    df = pd.read_excel(file_path, engine='openpyxl')
                elif file_extension.lower() == '.xls':
                    df = pd.read_excel(file_path, engine='xlrd')
                else:
                    raise ValueError("지원되지 않는 파일 형식입니다.")
                
                print(f"파일을 성공적으로 읽었습니다. 행 수: {len(df)}")
                
            except Exception as e:
                error_message = f"파일 읽기 오류: {str(e)}"
                self.update_text_signal.emit(error_message)
                print(error_message)
        else:
            pass

            
    def sign_In(self,ship_url, alie_ID, alie_PW):
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(ship_url)
        self.driver.implicitly_wait(self.random_sec)

        get_url = self.driver.current_url
        
        if 'https://login.aliexpress.com' not in get_url:
            self.driver.implicitly_wait(self.random_sec)
            return
        
        else:
            try:
                input_id = self.driver.find_element(By.CLASS_NAME,'cosmos-input')
                input_id.click()
                pyautogui.write(alie_ID, interval=0.03)
                time.sleep(self.random_sec)
                input_email = self.driver.find_element(By.CLASS_NAME,'nfm-multiple-email-prefix')
                input_email.click()
                time.sleep(self.random_sec)
                btn_continue = self.driver.find_element(By.CLASS_NAME,'cosmos-btn')
                btn_continue.click()
                time.sleep(self.random_sec2)
                
                input_pass = self.driver.find_element(By.ID,'fm-login-password')
                input_pass.click()
                pyautogui.write(alie_PW, interval=0.05)
                time.sleep(self.random_sec)
                
                btn_signin = self.driver.find_element(By.CLASS_NAME,'cosmos-btn')
                btn_signin.click()
                time.sleep(2)  # 로그인 버튼 클릭 후 충분한 대기 시간
                
                '''
                try:
                    wait = WebDriverWait(self.driver, 5)
                    wait.until(EC.presence_of_element_located((By.ID, "baxia-dialog-content")))
                    
                    iframes = self.driver.find_elements(By.ID, "baxia-dialog-content")
                    
                    for iframe in iframes:
                        try:
                            self.driver.switch_to.frame(iframe)
                            # 다양한 선택자로 슬라이더 찾기 시도
                            slider_selectors = [
                                (By.CLASS_NAME, "nc_iconfont"),
                                (By.ID, "nc_1_n1z"),
                                (By.CLASS_NAME, "nc-lang-cnt"),                               
                                (By.CSS_SELECTOR, "#nc_1_n1z"),
                                (By.XPATH, "//span[contains(@class, 'nc_iconfont')]"),
                                (By.XPATH, "//div[contains(@class, 'nc_scale')]//span")                                
                            ]
                            # 슬라이더 조작하기
                            for selector_type, selector_value in slider_selectors:
                                try:
                                    slider = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                                    if slider and slider.is_displayed():
                                        
                                        action = ActionChains(self.driver)
                                        action.click_and_hold(slider)
                                        move_distance_x = 760  # x축 이동 거리
                                        steps = 30  # 고정된 스텝 수
                                        move_duration = 2  # 슬라이더 이동 시간 (초)
                                        sleep_time = move_duration / steps  # 각 스텝 사이의 대기 시간

                                        for step in range(steps):
                                            # 랜덤한 y축 이동
                                            random_y = random.uniform(-25, 15)  # y축에서의 랜덤 이동
                                            
                                            # 가속도를 주기 위해 이동 거리 계산
                                            acceleration_factor = (step + 1) / steps  # 1에서 steps까지 비율
                                            move_x = (move_distance_x / steps) * acceleration_factor  # 가속 적용

                                            # x축과 y축 모두 이동
                                            action.move_by_offset(
                                                move_x,  # 가속이 적용된 x축 이동
                                                random_y  # y축 이동 (랜덤)
                                            )
                                            time.sleep(sleep_time)  # 각 스텝 사이의 대기 시간
                                       
                                        action.perform()
                                        time.sleep(1)  # 슬라이더 이동 후 대기 시간
                                        action.release().perform()
                                        break
                                except Exception as e:
                                    print(f"슬라이더 처리 중 오류 발생: {str(e)}")
                                    continue
                            
                            self.driver.switch_to.default_content()
                            break
                            
                        except Exception as e:
                            self.driver.switch_to.default_content()
                            continue
          
                except Exception as e:
                    print(f"로그인 처리 중 오류 발생: {str(e)}")
                    # 디버깅을 위한 스크린샷 저장
                    self.driver.save_screenshot("slider_error.png")
                '''     
            except Exception as e:
                print(f"로그인 처리 중 오류 발생: {str(e)}")
                self.driver.save_screenshot("login_error.png")
                
    def shipped_parcing(self):
        import re
        self.driver.implicitly_wait(30)
        # 버튼을 몇 번 눌러야 하는지 계산 
        btn_shipped = self.driver.find_element(By.XPATH,'//*[@id="root"]/div[1]/div[1]/div[1]/div[1]/div/div/div[4]')
        count = btn_shipped.text
        tMessage = '현재 배송중인 주문 수: '+ str(count)
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        numbers = re.findall(r'\d+', count)
        num = numbers[0] 
        int_numbers =  int(num)
        btn_count = (int_numbers-1)//10
        #print(f'버튼개수: {btn_count}')
        num = 1
        # 페이지 누르기
        tMessage = "주문번호 매칭 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        while num <= btn_count:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[2]/button')))
                order_id_div = self.driver.find_element(By.XPATH,'//*[@id="root"]/div[1]/div[2]/div[2]/button')
                order_id_div.click()
                print(str(num) + "번째 클릭")
                time.sleep(self.random_sec)
                num += 1
                
            except NoSuchElementException:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print("버튼 없음")
                
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        shipped_html = self.driver.page_source
        
        soup = BeautifulSoup(shipped_html, 'html.parser')
        elements = soup.find_all('div','order-item-header-right-info')
        order_ids = []
        
        for element in elements:
            text_content = element.text
            if "Order ID:" in text_content:
                order_id = text_content.split("Order ID:")[1].split("Copy")[0].strip()
                order_ids.append(order_id)
        
        tMessage = "주문번호 매칭 완료"  
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        return order_ids
    
    def ship_stat(self,input_list, orderid_list):
        #self.textBrowser.append("배송상태 조회 시작")
        print(input_list)
        print(orderid_list)
        maxNum = len(input_list)
        print(f'조회할 수량:" {maxNum}개')
        cnt = 1
        tracking_num = []
        tMessage = "배송상태 조회 시작"  
        self.update_text_signal.emit(tMessage)
        self.driver.implicitly_wait(1)
        QCoreApplication.processEvents()
        
        for num in input_list:
            tMessage = '조회중... '+'('+ str(cnt) +'/'+ str(maxNum) +')'+'번 째'
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            print(f'{cnt}번: {num}')
            
            if num in orderid_list:
                if str(num).startswith('1'): 
                    tracking_url = 'https://www.aliexpress.com/p/tracking/index.html?_addShare=no&_login=yes&tradeOrderId='+num
                    print(f"{cnt}번: 현재 배송중인 번호: {tracking_url}")
                    self.list_tracking.append(tracking_url)
                    self.driver.get(tracking_url)
                    
                    try:
                        WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[3]/div[3]/div[2]/div')) #버튼이 로딩될 때까지 기다림. 시간 내 못찾으면 타임아웃으로 넘겨버림.
                        )
                        
                        btn_view_more = self.driver.find_element(By.XPATH,"//div[@class='logistic-info-v2--viewMoreBtn--iuFWB5S']") #view more 버튼을 찾는다.
                        btn_view_more.click() #버튼 클릭
                        
                    except TimeoutException:
                        print('버튼 로딩 타임아웃, 버튼을 찾지 못 함.')  # 타임아웃 발생 시

                    except Exception as e:
                        print(f'기타 오류 발생: {e}')
                    
                    logistic_txt = ""
                                       
                    try:                       
                        logistic_top = self.driver.find_element(By.CLASS_NAME, "logistic-info-v2--track--1nqL7Vl") #배송 상태 가장 상위 클래스
                        logistic_sub = logistic_top.find_elements(By.XPATH, ".//div[text()]") #배송 상태 하위
                        
                        for logistic_sub in logistic_sub:
                            logistic_txt = logistic_sub.text
                        
                        tr_num = self.driver.find_element(By.XPATH,'//*[@id="root"]/div/div[3]/div[2]/div/span[2]') #송장번호 획득
                        tr_txt = tr_num.text
                        
                        ship_step = self.driver.find_element(By.XPATH,'//div[@class="logistic-info-v2--nodeDesc--2U3A3Yt"]') #배송상태 획득
                        shipstep_txt = ship_step.text
                        
                    except NoSuchElementException:
                        shipstep_txt = "취소/종료/알수없음"
                        tr_txt = ""
                    
                    ship_memo = ""
                
                    try:
                        status_mapping = {
                            'Package delivered': '배송완료',
                            'Your package has been delivered' : '배송완료',
                            'Order canceled': '주문취소',
                            'Shipment canceled': '배송취소',
                            'Delivery failed. Unable to deliver outside business hours.' : '배송실패-영업일아님',
                            'Delivery attempt unsuccessful': '배송실패',
                            'Out for delivery': '국내배송출발',
                            "We're preparing your package for delivery" : '국내배송출발',
                            'Arrived at destination country/region sorting center': '국내배송시작',
                            'Arrived at sorting center in destination country/region' : '국내배송시작',
                            'Your package has left the sorting center in the destination country/region': '국내배송시작',
                            'Arrived at sorting center in destination country/region': '국내택배사인계',
                            'Your package arrived at local Facility': '국내택배사인계',
                            'Your package has been received by the local delivery company' : '국내택배사인계',
                            'Received by local delivery company': '국내택배사인계',
                            'Left from destination country/region sorting center': '국내택배사인계',
                            'Package arrived at local sorting center.':'국내택배사인계',
                            'Your package has left the sorting center in the destination country/region':'국내택배사인계',
                            'Your package encountered an unforseen issue on its way to the distribution center in the destination country/region': '확인필요-세관통관후 오류',
                            'Departed from customs': '한국세관반출',
                            'Left from customs': '한국세관반출',
                            'Clearing Customs': '한국통관완료',
                            'Customs duties payment requested': '관세납부요청',
                            'Import customs clearance started': '한국통관시작',
                            'Arrived at customs': '한국통관준비',
                            'Your package arrived at local airport': '한국공항도착',
                            'Arrived at destination country/region sorting center': '한국도착-통관준비',
                            'Customs clearance started': ('한국통관중' if ('Leaving from departure country/region' in logistic_txt or 'Left from departure country/region sorting center' in logistic_txt or 'Left from departure country/region' in logistic_txt) else '중국수출통관중'),
                            'Customs clearance complete': ('한국통관완료' if ('Leaving from departure country/region' in logistic_txt or 'Left from departure country/region sorting center' in logistic_txt) else '중국통관완료'),
                            'Departed from departure country/region': '중국출발',
                            'Flight departure': '중국출발',
                            'Awaiting flight': '중국출발대기',
                            'Leaving from departure country/region': '중국출발',
                            'Package leaving origin country/region.':'중국출발',
                            'Left from departure country/region sorting center': '중국출발',
                            'Left from departure country/region': '중국출발',
                            'Flight prepared to departure from country of destination': '중국출발대기',
                            'Package arrived at airport':'중국공항도착',
                            'Export customs clearance complete': '중국수출통관완료',
                            'Export customs clearance started': '중국수출통관중',
                            'Arrived at line-haul office': ('한국 입항중' if ('Leaving from departure country/region' in logistic_txt or 'Left from departure country/region sorting center' in logistic_txt or 'Left from departure country/region' in logistic_txt) else '간선운송업체 도착'),
                            'Handed over to line-haul': ('한국 입항중' if ('Leaving from departure country/region' in logistic_txt or 'Left from departure country/region sorting center' in logistic_txt or 'Left from departure country/region' in logistic_txt) else '간선운송업체에 인계'),
                            'Arrived at departure transport hub': '중국공항도착',
                            'Your package arrived at airport. Awaiting transit.' : '중국공항도착대기',
                            'Package shipped out from warehouse': '중국내배송출발',
                            'Sorry, there is no updated logistics information': '배송정보없음',
                            'Processing at sorting center': '중국내배송중',
                            'Processing at departure country/region sorting center': '중국내배송중',
                            'Delivery company has picked up the large shipment': '중국내배송중',
                            'Package left sorting center of origin':'중국내배송중',
                            'Order has been packed into a large shipment and ready for the delivery company to pick up.': '대형화물로픽업준비',
                            'Received by logistics company': '중국택배사집화완료',
                            'Left from warehouse': '현지상품 출하',
                            'Package left warehouse':'판매자상품 출하',
                            'Shipment info received by warehouse' : '배송정보확인',
                            'Package ready for shipping from warehouse': '상품준비중',
                            'Ready to be shipped by warehouse' : '상품준비중',
                            'Your order is being packed' : '상품준비중',
                        }

                        # 상태를 확인하고 메모에 기록한다.
                        for key, value in status_mapping.items():
                            if key in shipstep_txt:
                                ship_memo = value
                                break
                        else:
                            ship_memo = '집화전/기타상태'
                            
                        print(num+": "+ship_memo)
                        
                    except NoSuchElementException:    
                        ship_memo = '상태불명'
                    
                    self.list_shipmemo.append(ship_memo)
                    tracking_num.append(tr_txt)
                    time.sleep(self.random_sec)
                
            else:
                if str(num).startswith('1'):
                    self.list_shipmemo.append("판매자발송전")
                    self.list_tracking.append('판매자발송전')
                    tracking_num.append('')
                    time.sleep(self.random_sec)
                    print(f'{cnt}번: 배송중이 아닌 알리 주문번호: {num}')
                    
                else:
                    self.list_shipmemo.append("알리주문아님")
                    self.list_tracking.append('알리주문아님')
                    tracking_num.append('')
                    print(f'{cnt}번: 배송중이 아 알리 외 주문번호: {num}')
                    time.sleep(self.random_sec)
            cnt += 1    

        tMessage = "배송상태 조회 완료"  
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        return self.list_shipmemo, self.list_tracking, tracking_num
    
    def find_company(self, tracking_num):
        self.update_text_signal.emit("택배사 찾기 시작")
        QCoreApplication.processEvents()

        # 택배사 매핑 딕셔너리 형식
        courier_mapping = {
            '55': 'CJ대한통운', '56': 'CJ대한통운', '57': 'CJ대한통운', '58': 'CJ대한통운', '50': 'CJ대한통운',
            '59': 'CJ대한통운', '75': 'CJ대한통운',
            '51': '한진택배', '80': '한진택배',
            '60': '우체국택배', '68': '우체국택배',
            'EX': '업체직송',
            'LB': 'EMS', 'LP': 'EMS', 'LX': 'EMS', 'SG': 'EMS', 'CN': 'EMS', 'CP': 'EMS',
            'YP': 'EMS', 'TW': 'EMS',
            'SYAE': '순유물류',
            'SYRM': '업체직송',
            '37': 'DHL',
            'SY': 'CJ대한통운특송', 'EB': 'CJ대한통운특송', 'EV': 'CJ대한통운특송',
            'EZ': 'CJ대한통운특송', 'UU': 'CJ대한통운특송',
            '89': 'FEDEX',
            'WJS': '웅지익스프레스', 'UG': '웅지익스프레스',
            'WJ': '우진화물',
            'Wl': '위니온로지스',
            'EKC': '업체직송', 'UD': '업체직송', 'RU': '업제직송', 'NL': '업체직송', 'TY': '업체직송',
            'PCTN': '범한판토스',
            '1Z': 'UPS',
        }
        

        def get_company_name(trNumber):
            if trNumber == '알리주문아님':
                return ''
            if trNumber.startswith('31'):
                return 'DHL' if len(trNumber) == 10 else '롯데택배'
            if trNumber.startswith('7511'):
                return 'yunda택배'
            if trNumber.startswith('LPO'):
                return 'EMS'
            
            for prefix_length in [4, 3, 2]:
                prefix = trNumber[:prefix_length]
                if prefix in courier_mapping:
                    return courier_mapping[prefix]
            
            return ''

        company_name = [get_company_name(trNumber) for trNumber in tracking_num]

        self.update_text_signal.emit("택배사 찾기 완료")
        QCoreApplication.processEvents()

        return company_name 
    
    @Slot(str)
    def update_text_browser(self, message):
        self.textBrowser.append(message)

app = QApplication()
window = MainWindow()
window.show()
app.exec()
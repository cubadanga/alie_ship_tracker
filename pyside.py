from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog
from PySide6.QtCore import QObject, Signal, Slot
from tracking_ui import Ui_MainWindow
import pandas as pd
import time
from datetime import timedelta
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pyautogui
import configparser
from bs4 import BeautifulSoup
from PySide6.QtCore import QCoreApplication
import datetime
 # 크롬드라이버 자동업데이트
from webdriver_manager.chrome import ChromeDriverManager
#브라우저 자동꺼짐 방지
options = Options()
options.add_experimental_option('detach',True)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("disable-gpu")   # 가속 사용 x
options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36)")

#불필요한 에러메시지 없애기

options.add_experimental_option("excludeSwitches", ['enable-logging'])

class MainWindow(QMainWindow, Ui_MainWindow):
    random_sec = None
    service = None
    driver = None
    config = configparser.ConfigParser()
    ini_filename = './save.ini'
    section_name = 'Section1'
    key_username = 'alie_username'
    key_password = 'alie_password'
    list_tracking = []
    list_shipmemo = []
    update_text_signal = Signal(str) ##셀레니움이 비동기로 작동하기 때문에 셀레니움 작업중에 내용을 ui에 표시하려면 PyQt에서 시그널 및 슬롯을 사용하여 Selenium 관련 코드와 GUI 업데이트를 연결해야 한다.
    chk_state = int
    
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.read_ini()
        self.update_text_signal.connect(self.update_text_browser)
        print("Signal connected successfully.")
        
    def start(self):
        ship_url = 'https://www.aliexpress.com/p/order/index.html?tab=shipped'
           
        alie_ID = self.lineEdit_id.text()
        alie_PW = self.lineEdit_pw.text()
        exUrl = self.lineEdit_path.text()
        combo_date = self.combo_date.currentText()
        delay_date = int(combo_date)
        self.random_sec = random.uniform(1.5,3)
        self.random_sec2 = random.uniform(0.5,1)
        start_time = time.time()
        
        tMessage ="배송조회 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        
        if alie_ID == "" or alie_PW == "":
            tMessage ="아이디 또는 패스워드를 입력해 주세요."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            
        else:
            print(alie_ID)
            print(alie_PW)
        
        if exUrl =="":
            tMessage ="배송리스트 엑셀 파일을 선택해 주세요."
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            
        else:pass
        
        self.write_ini(self.ini_filename, self.section_name, self.key_username, alie_ID)
        self.write_ini(self.ini_filename, self.section_name, self.key_password, alie_PW)
        
        self.filter_state()
        
        df = pd.DataFrame()
        df = self.read_files(exUrl, self.chk_state,delay_date)
        
        df_shiptrack = pd.DataFrame()
        df_shiptrack = df[['주문일','주문고유코드','해외주문번호','수령자']]
        df_shiptrack = df_shiptrack.astype(str)
        input_list = df_shiptrack['해외주문번호'].values.tolist()
        total_cnt = len(input_list)
        tMessage ='확인 대상 주문 건수: '+ str(total_cnt) +'개'
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        
        #브라우저 자동꺼짐 방지
        options = Options()
        options.add_experimental_option('detach',True)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("disable-gpu")   # 가속 사용 x
        options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
        options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36)")

        #불필요한 에러메시지 없애기

        options.add_experimental_option("excludeSwitches", ['enable-logging'])

        self.service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)
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
        
        ship_condition = ['한국통관중', '관세납부요청','한국통관완료','한국세관반출','배송실패','국내택배사인계','국내배송시작','배송완료']
        df_shiptrack2 = df_shiptrack.loc[df_shiptrack['상태메모'].isin(ship_condition)]
        
        now = datetime.datetime.now()
        genTime = now.strftime("%y%m%d%H%M%S")
        excel_filename = './output_file_'+genTime + '.xlsx'
        excel_filename2 = './forUpload_file_'+genTime + '.xlsx'
        df_shiptrack.astype(str)
        df_shiptrack2.astype(str)
        df_shiptrack.to_excel(excel_filename,index=False)
        df_shiptrack2.to_excel(excel_filename2,index=False)
        
        tMessage ="엑셀파일 저장 완료!!"
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
        self.driver.quit()
    
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
            tMessage ="INI 파일이 존재하지 않거나 형식이 잘못되었습니다.2"
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
        
    def read_files(self,exUrl,chk_state,delay_date):
        delay_date = delay_date
        today = datetime.datetime.today()
        days_ago = today - datetime.timedelta(days=delay_date)
        
        tMessage = "엑셀파일 읽기 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        df = pd.read_excel(exUrl,header=0,dtype={'수령자': str, '해외주문번호': str, '주문고유코드': str})
        df['주문일'] = pd.to_datetime(df['주문일'])
        
        if chk_state == 0:
            target = ['SLX택배', '기타택배', '직접전달']
            df_true = df.loc[df['택배사'].isin(target)]
            df_true2 = df_true[df_true["주문일"] <= days_ago]
            return df_true2
        
        else:
            return df
         
    def filedialog_open(self):
        fname=QFileDialog.getOpenFileName(self,'','',"xlsx(*.xlsx)")
        if fname[0]:
            file_path = fname[0]
            self.lineEdit_path.setText(file_path)
            
        else:pass
            
    def sign_In(self,ship_url, alie_ID, alie_PW):
        self.driver.get(ship_url)
        self.driver.implicitly_wait(self.random_sec)

        get_url = self.driver.current_url
        #브라우저에서 현재 url을 가져와 로그인 페이지인지 확인
        
        if 'https://login.aliexpress.com' not in get_url:
            self.driver.implicitly_wait(self.random_sec)
            return
        
        else:
            try:
                judge = self.driver.find_element(By.CLASS_NAME,'fm-sns-new-btns')
                print(f"{judge}: 뉴 유아이")
                input_id = self.driver.find_element(By.CLASS_NAME,'comet-input-label-content')
                input_id.click()
                pyautogui.write(alie_ID, interval=0.03)
                time.sleep(self.random_sec)
                input_email = self.driver.find_element(By.CLASS_NAME,'nfm-multiple-email-prefix')
                input_email.click()
                time.sleep(self.random_sec)
                btn_continue = self.driver.find_element(By.CLASS_NAME,'comet-btn')
                btn_continue.click()
                time.sleep(self.random_sec2)
                
                input_pass = self.driver.find_element(By.ID,'fm-login-password')
                input_pass.click()
                pyautogui.write(alie_PW, interval=0.02)
                time.sleep(self.random_sec)
                
                btn_signin = self.driver.find_element(By.CLASS_NAME,'comet-btn-primary')
                btn_signin.click()
                time.sleep(self.random_sec)
                return
            except:
                print("올드 유아이")
                input_id = self.driver.find_element(By.ID,'fm-login-id')
                input_id.click()
                pyautogui.write(alie_ID, interval=0.03)
                pyautogui.press('tab')
                time.sleep(self.random_sec)
                
                input_pass = self.driver.find_element(By.ID,'fm-login-password')
                input_pass.click()
                pyautogui.write(alie_PW, interval=0.02)
                time.sleep(self.random_sec)
                
                btn_signin = self.driver.find_element(By.CLASS_NAME,'comet-btn-primary')
                btn_signin.click()
                time.sleep(self.random_sec)
            return
        
        
    def shipped_parcing(self):
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
        btn_count = int_numbers//10
        #print(f'버튼개수: {btn_count}')
        num = 0
        # 페이지 누르기
        tMessage = "주문번호 매칭 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        while num < btn_count:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[2]/button')))
            time.sleep(self.random_sec)
            try:
                order_id_div = self.driver.find_element(By.XPATH,'//*[@id="root"]/div[1]/div[2]/div[2]/button')
                order_id_div.click()
            except NoSuchElementException:
                print("버튼 없음")
                
            num += 1
            
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
        QCoreApplication.processEvents()
        
        for num in input_list:
            tMessage = '조회중... '+'('+ str(cnt) +'/'+ str(maxNum) +')'+'번 째'
            self.update_text_signal.emit(tMessage)
            QCoreApplication.processEvents()
            print(f'{cnt}번: {num}')
            
            if num in orderid_list:
                if str(num).startswith('1'): 
                    tracking_url = 'https://track.aliexpress.com/logisticsdetail.htm?tradeId='+num
                    print(f"{cnt}번: 현재 배송중인 번호: {tracking_url}")
                    self.list_tracking.append(tracking_url)
                    self.driver.get(tracking_url)
                    self.driver.implicitly_wait(4)
                    
                    try:
                        ship_step = self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[1]/div[2]/div[2]/div/ul') #배송상태 획득
                        shipstep_txt = ship_step.text
                        tr_num = self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[1]/div/div/div[2]/span/a') #송장번호 획득
                        tr_txt = tr_num.text
                        
                    except NoSuchElementException:
                        shipstep_txt = "취소/종료/알수없음"
                        tr_txt = ""
                    
                    ship_memo = ""
                    
                    try:
                        if 'Package delivered' in shipstep_txt:
                            ship_memo = '배송완료'
                        
                        elif 'Order canceled' in shipstep_txt:
                            ship_memo = '주문취소'
                            
                        elif 'Delivery attempt unsuccessful' in shipstep_txt:    
                            ship_memo = '배송실패'
                        
                        elif 'Arrived at destination country/region sorting center' in shipstep_txt:
                            ship_memo = '국내배송시작'
                            
                        elif 'Received by local delivery company' in shipstep_txt:
                            ship_memo = '국내택배사인계'
                        
                        elif 'Departed from customs' in shipstep_txt:
                            ship_memo = '한국세관반출'
                            
                        elif 'Clearing Customs' in shipstep_txt:
                            ship_memo = '한국통관완료'
                            
                        elif 'Customs duties payment requested' in shipstep_txt:
                            ship_memo = '관세납부요청'
                        
                        elif 'Import customs clearance started' in shipstep_txt:
                            ship_memo = '한국통관중'
                        
                        elif 'Departed from departure country/region' in shipstep_txt:
                            ship_memo = '중국출발'
                        
                        elif 'Leaving from departure country/region' in shipstep_txt:
                            ship_memo = '중국출발'
                        
                        elif 'Export customs clearance started' in shipstep_txt:
                            ship_memo = '중국통관중'
                            
                        elif 'Package shipped out from warehouse' in shipstep_txt:
                            ship_memo = '중국내배송출발'
                            
                        elif 'Sorry, there is no updated logistics information' in shipstep_txt:
                            ship_memo = '배송정보없음'
                            
                        elif 'Processing at sorting center' in shipstep_txt:
                            ship_memo = '중국내배송중'
                        
                        elif 'Delivery company has picked up the large shipment' in shipstep_txt:
                            ship_memo = '중국내배송중'
                        
                        elif 'Package ready for shipping from warehouse' in shipstep_txt:
                            ship_memo = '상품준비중'
                        
                        else:
                            ship_memo = '상태불명/집화전'
                            
                    except NoSuchElementException:    
                        ship_memo = '상태불명'

                    self.list_shipmemo.append(ship_memo)
                    tracking_num.append(tr_txt)
                    time.sleep(self.random_sec2)
                
            else:
                if str(num).startswith('1'):
                    self.list_shipmemo.append("판매자발송전")
                    self.list_tracking.append('판매자발송전')
                    tracking_num.append('')
                    time.sleep(self.random_sec2)
                    print(f'{cnt}번: 배송중이 아닌 알리 주문번호: {num}')
                    
                else:
                    self.list_shipmemo.append("알리주문아님")
                    self.list_tracking.append('알리주문아님')
                    tracking_num.append('')
                    print(f'{cnt}번: 배송중이 아닌 알리 외 주문번호: {num}')
                    time.sleep(self.random_sec2)
            cnt += 1    

        tMessage = "배송상태 조회 완료"  
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        return self.list_shipmemo, self.list_tracking, tracking_num
    
    def find_company(self,tracking_num):
        
        tMessage = "택배사 찾기 시작"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        company_name = []
        for num in tracking_num:
            
            if num != '알리주문아님':
                if num[:2] =='55':
                    company_name.append("CJ대한통운")
                elif num[:4] == '7511':
                    company_name.append("yunda택배")
                elif num[:2] =='56':
                    company_name.append("CJ대한통운")
                elif num[:2] =='57':
                    company_name.append("CJ대한통운")
                elif num[:2] =='58':
                    company_name.append("CJ대한통운")
                elif num[:2] =='75':
                    company_name.append("CJ대한통운")
                elif num[:2] =='51':
                    company_name.append("한진택배")
                elif num[:2] =='80':
                    company_name.append("한진택배")
                elif num[:2] =='60':
                    company_name.append("우체국택배")
                elif num[:2] =='68':
                    company_name.append("우체국택배")
                elif num[:2] =='EX':
                    company_name.append("업체직송")
                elif num[:2] =='LB':
                    company_name.append("EMS")
                elif num[:3] =='LPO':
                    company_name.append("EMS")
                elif num[:2] =='LP':
                    company_name.append("EMS")
                elif num[:2] =='SG':
                    company_name.append("EMS")
                elif num[:2] =='CN':
                    company_name.append("EMS")
                elif num[:2] =='CP':
                    company_name.append("EMS")
                elif num[:4] =='SYAE':
                    company_name.append("순유물류")
                elif num[:4] =='SYRM':
                    company_name.append("업체직송")
                elif num[:2] =='SY':
                    company_name.append("CJ대한통운특송") 
                elif num[:2] =='EB':
                    company_name.append("CJ대한통운특송")
                elif num[:2] =='EV':
                    company_name.append("CJ대한통운특송")
                elif num[:2] =='EZ':
                    company_name.append("CJ대한통운특송")
                elif num[:2] =='UU':
                    company_name.append("CJ대한통운특송")
                elif num[:2] =='89':
                    company_name.append("FEDEX")
                elif num[:3] =='WJS':
                    company_name.append("웅지익스프레스")
                elif num[:2] =='WJ':
                    company_name.append("우진화물")
                elif num[:2] =='Wl':
                    company_name.append("위니온로지스")
                elif num[:3] =='EKC':
                    company_name.append("업체직송")
                elif num[:2] =='UG':
                    company_name.append("웅지익스프레스")
                elif num[:2] =='UD':
                    company_name.append("업체직송")
                elif num[:2] =='RU':
                    company_name.append("업제직송")
                elif num[:2] =='NL':
                    company_name.append("업체직송")
                elif num[:2] =='YP':
                    company_name.append("EMS")
                elif num[:2] =='LX':
                    company_name.append("EMS")
                elif num[:2] =='TW':
                    company_name.append("EMS")
                elif num[:2] =='TY':
                    company_name.append("업체직송")
                else:
                    company_name.append('')
            else:
                company_name.append('')
        
        tMessage = "택배사 찾기 완료"
        self.update_text_signal.emit(tMessage)
        QCoreApplication.processEvents()
        
        return company_name  
    
    @Slot(str)
    def update_text_browser(self, message):
        self.textBrowser.append(message)

app = QApplication()
window = MainWindow()
window.show()
app.exec()




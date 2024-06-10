import time
import re
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pyautogui
from bs4 import BeautifulSoup
from colorama import init, Fore
import re
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon

random_sec = random.uniform(1.5,3)
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

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

ship_url = 'https://www.aliexpress.com/p/order/index.html?tab=shipped'
alie_ID = 'guruma78@gmail.com'
alie_PW = 'cubase78'

def read_files():
    print(f"파일읽기 실행")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"디렉토리: {current_directory}")
    xlsx_files = []
    
    for file in os.listdir(current_directory):
        if file.endswith('.xlsx') and '배송중' in file.lower() and '~$' not in file.lower():
            xlsx_files.append(file)
    try:
        if len(xlsx_files) == 1:
            file_name = xlsx_files[0]
            exUrl = os.path.join(current_directory, file_name)
            print(f"파일이름: {file_name}")
            print(f"경로: {exUrl}")
            df = pd.read_excel(exUrl,header=0)
            return df
   
    except ValueError as e:
        print(Fore.RED + '오류 - 엑셀 시트의 시트명이 다르거나 올바른 파일이 아닙니다.'+'\n')
        print(Fore.RESET + "엔터를 누르면 종료합니다.")
        aInput = input("")
        sys.exit()

    except FileNotFoundError as e:
        print(Fore.RED + '오류 - 배송중 ~ .xlsx 파일을 찾을 수 없습니다.'+'\n'+'이런 경우, 파일명이 잘못된 경우가 대부분이었습니다.'+' 이 파일은 필수 파일입니다.'+'\n')
        print(Fore.RESET + "엔터를 누르면 종료합니다.")
        aInput = input("")
        sys.exit()

def sign_In(ship_url, alie_ID, alie_PW):
    driver.get(ship_url)
    driver.implicitly_wait(random_sec)

    get_url = driver.current_url
    #브라우저에서 현재 url을 가져와 로그인 페이지인지 확인

    if 'https://login.aliexpress.com' not in get_url:
        driver.implicitly_wait(random_sec)
        return
    else:
        input_id = driver.find_element(By.ID,'fm-login-id')
        input_id.click()
        pyautogui.write(alie_ID, interval=0.03)
        pyautogui.press('tab')
        time.sleep(random_sec)
        
        input_pass = driver.find_element(By.ID,'fm-login-password')
        input_pass.click()
        pyautogui.write(alie_PW, interval=0.02)
        time.sleep(random_sec)
        
        btn_signin = driver.find_element(By.CLASS_NAME,'comet-btn-primary')
        btn_signin.click()
        time.sleep(random_sec)
        
        return
    
def shipped_parcing():
    driver.implicitly_wait(30)
    # 버튼을 몇 번 눌러야 하는지 계산 
    btn_shipped = driver.find_element(By.XPATH,'//*[@id="root"]/div[1]/div[1]/div[1]/div[1]/div/div/div[4]')
    count = btn_shipped.text
    print(f'배송중인 개수: {count}')
    numbers = re.findall(r'\d+', count)
    num = numbers[0] 
    int_numbers =  int(num)
    btn_count = int_numbers//10
    print(f'버튼개수: {btn_count}')
    num = 0
    # 페이지 누르기
    while num < btn_count:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random_sec)
        try:
            order_id_div = driver.find_element(By.XPATH,'//*[@id="root"]/div[1]/div[2]/div[2]/button')
            order_id_div.click()
        except NoSuchElementException:
            print("버튼 없음")
        num += 1
        driver.implicitly_wait(random_sec)
    
    shipped_html = driver.page_source
    soup = BeautifulSoup(shipped_html, 'html.parser')
    elements = soup.find_all('div','order-item-header-right-info')
    order_ids = []
    
    for element in elements:
        text_content = element.text
        if "Order ID:" in text_content:
            order_id = text_content.split("Order ID:")[1].split("Copy")[0].strip()
            order_ids.append(order_id)
    return order_ids

def get_trNum(list_tracking):
    tracking_num = []
    for tr_url in list_tracking:
        if tr_url == '알리주문아님':
           tracking_num.append('알리주문아님')
        else:
            driver.get(tr_url)
            driver.implicitly_wait(30)
            if tr_url == driver.current_url:
                tr_num = driver.find_element(By.XPATH,'//*[@id="root"]/div/div[3]/div[2]/div/div/span')
                tr_txt = tr_num.text
                tracking_num.append(tr_txt)
                time.sleep(random_sec)
            else:
                print ('배송중아님.')
    return tracking_num

def ship_stat(input_list, orderid_list):
    input_list = input_list
    orderid_list = orderid_list
    
    for num in input_list:
        if num in orderid_list:
            if str(num).startswith('1'): 
                driver.implicitly_wait(30)
                tracking_url = 'https://track.aliexpress.com/logisticsdetail.htm?tradeId='+num
                print(f'트래킹url: {tracking_url}')
                list_tracking.append(tracking_url)
                driver.get(tracking_url)
                driver.implicitly_wait(30)
                ship_step = driver.find_element(By.XPATH,'//*[@id="root"]/div/div[3]/div[4]/div/div[1]/div[2]')
                shipstep_txt = ship_step.text
                
                try:
                    if 'Package delivered' in shipstep_txt:
                        ship_memo = '배송완료'
                    
                    elif 'Arrived at destination country/region sorting center' in shipstep_txt:
                        ship_memo = '국내배송시작'
                    
                    elif 'Import customs clearance started' in shipstep_txt:
                        ship_memo = '한국통관중'
                    
                    elif 'Departed from departure country/region' in shipstep_txt:
                        ship_memo = '중국출발'
                    
                    elif 'Export customs clearance started' in shipstep_txt:
                        ship_memo = '중국통관중'
                        
                    elif 'Sorry, there is no updated logistics information' in shipstep_txt:
                        ship_memo = '배송정보없음'
                    
                    elif 'Customs duties payment requested' in shipstep_txt:
                        ship_memo = '관세납부요청'
                        
                    elif 'Order canceled' in shipstep_txt:
                        ship_memo = '주문취소'
                        
                except NoSuchElementException:    
                    ship_memo = '상태불명'
            
                list_shipmemo.append(ship_memo)
                time.sleep(random_sec)
            else:
                ship_memo = "배송중이 아님"
        else:
            list_tracking.append('알리주문아님')
            list_shipmemo.append("")
            time.sleep(random_sec)
    return list_shipmemo, list_tracking

def filedialog_open(self):
    fname = QFileDialog.getOpenFileName(self, 'Open File', '',
                                        'All File(*);; *.xlsx')
    if fname[0]:
        # 튜플 데이터에서 첫 번째 인자 값이 주소이다.
        self.lineEdit_path.setText(fname[0])
        print('filepath : ', fname[0])
        print('filesort : ', fname[1])
    else:
        QMessageBox.about(self, 'Warning', '파일을 선택하지 않았습니다.')
def find_company(tracking_num):
    company_name = []
    for num in tracking_num:
        
        if num != '알리주문아님':
            if num[:2] =='55':
                company_name.append("cj대한통운")
            elif num[:2] == '7511':
                company_name.append("yunda택배")
            elif num[:2] =='56':
                company_name.append("cj대한통운")
            elif num[:2] =='57':
                company_name.append("cj대한통운")
            elif num[:2] =='58':
                company_name.append("cj대한통운")
            elif num[:2] =='75':
                company_name.append("cj대한통운")
            elif num[:2] =='51':
                company_name.append("한진택배 또는 통관후 우체국택배")
            elif num[:2] =='80':
                company_name.append("한진택배")
            elif num[:2] =='60':
                company_name.append("우체국택배")
            elif num[:2] =='68':
                company_name.append("우체국택배")
            elif num[:2] =='LB':
                company_name.append("우체국EMS")
            elif num[:2] =='LP':
                company_name.append("우체국EMS") 
            elif num[:2] =='SYAE':
                company_name.append("순유물류") 
            elif num[:2] =='SY':
                company_name.append("cj대한통운특송") 
            elif num[:2] =='EB':
                company_name.append("cj대한통운특송")
            elif num[:2] =='EV':
                company_name.append("cj대한통운특송")
            elif num[:2] =='EZ':
                company_name.append("cj대한통운특송")
            elif num[:2] =='89':
                company_name.append("페덱스")
            elif num[:2] =='WJ':
                company_name.append("우진화물")
            elif num[:2] =='WJS':
                company_name.append("웅지익스프레스")
            elif num[:2] =='EKC':
                company_name.append("배터리연계된택배사 재조회")
            elif num[:2] =='UG':
                company_name.append("웅지택배-준등기로 우체국조회")
            elif num[:2] =='UD':
                company_name.append("얀웬")
            else:
                company_name.append('알수없는택배사')
        else:
            company_name.append('알리주문아님')
    return company_name        


def loadLoginInfo():pass
def inputLoginInfo():pass
def writeLoginInfo():pass

tracking_url = ''
list_tracking = []
list_shipmemo = []
df = pd.DataFrame()
df = read_files()
df_shiptrack = pd.DataFrame()
df_shiptrack = df[['주문고유코드','해외주문번호','수령자']]
input_list = df_shiptrack['해외주문번호'].values.tolist()

sign_In(ship_url,alie_ID,alie_PW)
orderid_list = shipped_parcing()


list_shipmemo, list_tracking = ship_stat(input_list,orderid_list)
tracking_num = get_trNum(list_tracking)
dcompany = find_company(tracking_num)
df_shiptrack = df_shiptrack.copy()
df_shiptrack['송장번호'] = tracking_num
df_shiptrack['택배사'] = dcompany
df_shiptrack['메모'] = list_shipmemo
df_shiptrack['추적Url'] = list_tracking

excel_filename = './output_file.xlsx'
df_shiptrack.to_excel(excel_filename)

print(df_shiptrack)
print("완료!!")
driver.quit()



    




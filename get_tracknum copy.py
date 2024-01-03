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

df = pd.DataFrame()
df = read_files()
df_shiptrack = pd.DataFrame()
print(type(df))
df_shiptrack = df[['주문고유코드','해외주문번호','수령자']]
'''
try:    
        df_shiptrack = df[['주문고유코드'],['해외주문번호'],['수령자']]
        
except Exception as e:
    print(f"오류: 데이터프레임을 읽을 수 없습니다.{e}")

'''

print(f"원본 프레임: {df}")
print(f"새 프레임: {df_shiptrack}")

input_list = ['1102092595499640']


print(input_list)
    




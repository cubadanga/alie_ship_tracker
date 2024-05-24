import random
from datetime import date

# 오늘 날짜 가져오기
today = date.today()
year = str(today.year)
month = str(today.month).zfill(2)  # 월을 2자리로 만들기 (e.g., 01, 02, ...)
day = str(today.day).zfill(2)  # 일을 2자리로 만들기

# 사용자로부터 생성 개수 입력 받기
count = int(input("생성 개수를 입력해 주세요: "))

# 숫자 세트 생성 및 출력
for _ in range(count):
    random_digits = str(random.randint(4000, 9999))  # 뒤의 4자리 랜덤 생성
    number_set = year + month + day + random_digits
    print(number_set)

a = input("엔터를 누르면 종료")

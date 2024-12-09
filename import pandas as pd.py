import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('통합주문관리-12-06.csv')

# '쇼핑몰ID'별 '실결제금액' 합계 계산
result = df.groupby('쇼핑몰ID')['실결제금액'].sum().reset_index()

# 결과 출력
print(result)
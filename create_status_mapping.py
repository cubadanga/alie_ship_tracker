import json
import os

# 현재 스크립트의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))

# status_mapping.json 파일의 전체 경로
json_path = os.path.join(current_dir, 'status_mapping.json')

# 상태 매핑 데이터
status_mapping = {
    "Package delivered": "배송완료",
    "Your package has been delivered": "배송완료",
    "Order canceled": "주문취소",
    "Shipment canceled": "배송취소",
    "Delivery failed. Unable to deliver outside business hours.": "배송실패-영업일아님",
    "Delivery attempt unsuccessful": "배송실패",
    "Out for delivery": "국내배송출발",
    "We're preparing your package for delivery": "국내배송출발",
    "Arrived at destination country/region sorting center": "국내배송시작",
    "Arrived at sorting center in destination country/region": "국내배송시작",
    "Your package has left the sorting center in the destination country/region": "국내배송시작",
    "Your package has been received by the local delivery company": "국내택배사인계",
    "Received by local delivery company": "국내택배사인계",
    "Left from destination country/region sorting center": "국내택배사인계",
    "Departed from customs": "한국세관반출",
    "Your package encountered an unforseen issue on its way to the distribution center in the destination country/region": "확인-세관반출후 이상발생",
    "Left from customs": "한국세관반출",
    "Clearing Customs": "한국통관완료",
    "Customs duties payment requested": "관세납부요청",
    "Import customs clearance started": "한국통관시작",
    "Your package arrived at local airport": "한국도착-통관준비",
    "Customs clearance started": "한국통관중",
    "Customs clearance complete": "한국통관완료",
    "Departed from departure country/region": "중국출발",
    "Leaving from departure country/region": "중국출발",
    "Left from departure country/region sorting center": "중국출발",
    "Left from departure country/region": "중국출발",
    "Flight prepared to departure from country of destination": "중국출발대기",
    "Package arrived at airport": "중국공항도착",
    "Export customs clearance complete": "중국수출통관완료",
    "Export customs clearance started": "중국수출통관중",
    "Arrived at line-haul office": "한국 입항중",
    "Handed over to line-haul": "한국 입항중",
    "Arrived at departure transport hub": "중국공항도착",
    "Package shipped out from warehouse": "중국내배송출발",
    "Sorry, there is no updated logistics information": "배송정보없음",
    "Processing at sorting center": "중국내배송중",
    "Processing at departure country/region sorting center": "중국내배송중",
    "Delivery company has picked up the large shipment": "중국내배송중",
    "Order has been packed into a large shipment and ready for the delivery company to pick up.": "대형화물로픽업준비",
    "Received by logistics company": "중국택배사집화완료",
    "Left from warehouse": "현지상품 출하",
    "Shipment info received by warehouse": "배송정보확인",
    "Package ready for shipping from warehouse": "상품준비중"
}

# JSON 파일 생성
try:
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(status_mapping, f, ensure_ascii=False, indent=4)
    print(f"status_mapping.json 파일이 생성되었습니다.\n위치: {json_path}")
except Exception as e:
    print(f"파일 생성 중 오류 발생: {e}")
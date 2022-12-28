import pandas as pd
import streamlit as st
import requests
import json
import pydeck as pdk


#따릉이 시각화 크롤링 코드
api_key = "757766614b74616c374a46696a55"
bike_dict = {"rackTotCnt":[], "stationName":[],
             "parkingBikeTotCnt":[], "shared":[],
             "latitude":[], "longitude":[]}
num = 0
while True:
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/bikeList/{1 + 1000 * num}/{1000 + 1000 * num}/"
    data = requests.get(url)
    result = json.loads(data.text)  # json --> dict
    for row in result["rentBikeStatus"]["row"]:
        bike_dict["rackTotCnt"].append(int(row["rackTotCnt"]))
        bike_dict["stationName"].append(row["stationName"])
        bike_dict["parkingBikeTotCnt"].append(int(row["parkingBikeTotCnt"]))
        bike_dict["shared"].append(int(row["shared"]))
        bike_dict["latitude"].append(float(row["stationLatitude"]))
        bike_dict["longitude"].append(float(row["stationLongitude"]))
    if len(result["rentBikeStatus"]["row"]) != 1000:
        break
    num += 1

df = pd.DataFrame(bike_dict)
st.write("# 따릉이 시각화 결과")
st.write(df)

#pydeck모듈로 시각화
layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position=["longitude", "latitude"],
    get_fill_color=["255-shared", "255-shared", "255"], #점의 색깔, RGB 컬러 (0~255까지 존재함), 칼럼 이름을 그대로 넣는 수식도 활용 가능하다.
    get_radius="60*shared/100", # 점의 크기를 60으로, shared에 따라서 100으로 나눠준 크기만큼 표기
    pickable=True #마우스로 지도를 이동할 수 있도록 하는 기능
)
lat_center = df["latitude"].mean()
lon_center = df["longitude"].mean()
initial_view = pdk.ViewState(latitude=lat_center, longitude=lon_center, zoom = 10) #서울의 중심을 띄우라는 명령어, 중심점을 구하는 과정
map = pdk.Deck(layers=[layer], initial_view_state=initial_view,
               tooltip={"text":"대여소 : {stationName}\n현재 주차 대수 : {parkingBikeTotCnt}"})
st.pydeck_chart(map)

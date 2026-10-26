import pandas as pd

url = "https://raw.githubusercontent.com/qazybekb/AirDatakz-OpenData/main/stations.csv"

try:
    stations = pd.read_csv(url)
    stations.to_csv("stations.csv", index=False)
    print("Каталог станций загружен!")
    print(stations.head())
    print("Колонки:", list(stations.columns))
except Exception as e:
    print("Ошибка загрузки:", e)
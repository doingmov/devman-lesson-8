import json
import os
import folium
import requests
from dotenv import load_dotenv
from geopy import distance

load_dotenv()
api_key = os.getenv("API_KEY")

def fetch_coordinates(api_key, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": api_key,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lon, lat

def get_distance(cafe):
    return cafe["distance"]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "coffee.json")

    with open(file_path, "r", encoding="cp1251") as my_file:
        coffee = json.load(my_file)

    city_user = input("Где вы находитесь? ")
    coords_user = fetch_coordinates(api_key, city_user)
    if coords_user is None:
        return

    user_lon, user_lat = coords_user

    coffee_with_distance = []
    for cafe in coffee:
        name = cafe["Name"]
        lat = float(cafe["Latitude_WGS84"])
        lon = float(cafe["Longitude_WGS84"])
        dist = distance.distance((user_lat, user_lon), (lat, lon)).km
        coffee_with_distance.append(
            {
                "title": name,
                "latitude": lat,
                "longitude": lon,
                "distance": dist,
            }
        )

    coffee_with_distance.sort(key=get_distance)
    nearest = coffee_with_distance[:5]

    for cafe in nearest:
        print(cafe["title"])

    m = folium.Map(location=[user_lat, user_lon], zoom_start=15)
    folium.Marker(
        location=[user_lat, user_lon],
        popup=f"Ваше местоположение: {city_user}",
        tooltip="Вы здесь",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)

    for cafe in nearest:
        folium.Marker(
            location=[cafe["latitude"], cafe["longitude"]],
            popup=f'{cafe["title"]} - {cafe["distance"]:.2f} км',
            tooltip=cafe["title"],
            icon=folium.Icon(color="green", icon="coffee"),
        ).add_to(m)

    m.save("nearest_cafe_map.html")

if __name__ == "__main__":
    main()

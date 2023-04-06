from io import BytesIO

import requests
import pygame


def init_geocoder_connection(*toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        print("Error connecting to geocoder")
        return -1

    return response


def coords_creation(response):
    json_response = response.json()
    coords_response = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]["Point"]["pos"]
    coords = ",".join([str(elem) for elem in coords_response.split()])
    return coords


def calculate_spn(lower_corner, upper_corner):
    spn = [abs(round(upper_corner[0] - lower_corner[0], 6)), abs(round(upper_corner[1] - lower_corner[1], 6))]
    return spn


def find_toponym_spn(response):
    json_response = response.json()

    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    borders = toponym['boundedBy']['Envelope']
    lower_corner = list(map(float, borders['lowerCorner'].split()))
    upper_corner = list(map(float, borders['upperCorner'].split()))
    spn = calculate_spn(lower_corner, upper_corner)

    return spn


def create_image_response(coords, spn):
    map_params = {
        "ll": coords,
        "spn": ",".join([str(elem) for elem in spn]),
        "l": "map"
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"

    response = requests.get(map_api_server, params=map_params)

    return response


if __name__ == "__main__":
    toponym = "37.60519,55.82307"
    geocoder_response = init_geocoder_connection(toponym)
    coords = coords_creation(geocoder_response)
    spn = find_toponym_spn(geocoder_response)

    image = create_image_response(coords, spn)
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(BytesIO(image.content)), (0, 0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()

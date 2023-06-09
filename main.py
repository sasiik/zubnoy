import sys
from io import BytesIO

import pygame
import requests


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
        "l": "map",
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"

    response = requests.get(map_api_server, params=map_params)

    return response


def increase_zoom(spn):
    if round(spn[0] / 1.5, 6) >= 0.002 and round(spn[1] / 1.5, 6) >= 0.001:
        spn = list(map(lambda x: round(x / 1.5, 6), spn))
    return spn


def decrease_zoom(spn):
    if round(spn[0] * 1.5, 6) <= 180 and round(spn[1] * 1.2, 6) <= 90:
        spn = list(map(lambda x: round(x * 1.5, 6), spn))
    return spn


if __name__ == "__main__":
    toponym = "37.60519,55.82307"
    scale = 1.0
    geocoder_response = init_geocoder_connection(toponym)
    coords = coords_creation(geocoder_response)
    spn = find_toponym_spn(geocoder_response)

    image = create_image_response(coords, spn)
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    spn = increase_zoom(spn)
                    image = create_image_response(coords, spn)
                if event.key == pygame.K_DOWN:
                    spn = decrease_zoom(spn)
                    image = create_image_response(coords, spn)
        screen.blit(pygame.image.load(BytesIO(image.content)), (0, 0))
        pygame.display.flip()

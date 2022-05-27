import os
import random

import requests
from dotenv import load_dotenv


def get_link(vk_access_token, group_id):
    url_method = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'group_id': group_id,
        'access_token': vk_access_token,
        'v': '5.131.'
    }
    response = requests.get(url_method, params=params)

    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])

    upload_link = decoded_response['response']['upload_url']
    return upload_link


def upload_photo_to_server(upload_link):
    with open('comics.jpg', 'rb') as file:
        files = {
            'photo': file,

        }

        response = requests.post(upload_link, files=files)
    decoded_response = response.json()

    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])

    server = decoded_response['server']
    photo = decoded_response['photo']
    photo_hash = decoded_response['hash']
    return server, photo, photo_hash


def save_photo_album(vk_access_token, server, photo, hash_photo):
    url_method = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'group_id': '213493929',
        'access_token': vk_access_token,
        'v': '5.131.',
        'server': server,
        'photo': photo,
        'hash': hash_photo,
    }
    response = requests.post(url_method, params=params)
    decoded_response = response.json()

    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])

    media_id = decoded_response['response'][0]['id']
    photo_owner_id = decoded_response['response'][0]['owner_id']

    return media_id, photo_owner_id


def walk_post(vk_access_token, group_owner_id, media_id, photo_owner_id, commentary=None):
    url_method = 'https://api.vk.com/method/wall.post'
    params = {
        'access_token': vk_access_token,
        'v': '5.131.',
        'from_group': 1,
        'owner_id': f'-{group_owner_id}',
        'attachments': f'photo{photo_owner_id}_{media_id}',
        'message': commentary,
    }
    response = requests.get(url_method, params=params)
    decoded_response = response.json()
    if 'error' in decoded_response:
        raise requests.exceptions.HTTPError(decoded_response['error'])
    return response.json()


def download_random_comic():
    response = requests.get(f'https://xkcd.com/info.0.json')
    response.raise_for_status()
    response = response.json()
    last_number_comic = response['num']
    random_comic_number = str(random.randint(1, last_number_comic))
    response = requests.get(f'https://xkcd.com/{random_comic_number}/info.0.json')
    response.raise_for_status()
    response = response.json()
    img_link = response['img']
    photo_commentary = response['alt']

    with open('comics.jpg', 'wb') as file:
        file.write(requests.get(img_link).content)

    return img_link, photo_commentary


def main():
    load_dotenv()
    group_id = os.getenv('GROUP_ID')
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    img_link, photo_commentary = download_random_comic()
    try:
        img_link, photo_commentary = download_random_comic()
        upload_link = get_link(vk_access_token, group_id)
        server, photo, hash_photo = upload_photo_to_server(upload_link)

        media_id, photo_owner_id = save_photo_album(
            vk_access_token,
            server,
            photo,
            hash_photo
        )

        walk_post(
            vk_access_token,
            group_id,
            media_id,
            photo_owner_id,
            photo_commentary

        )
    finally:
        os.remove('comics.jpg')


if __name__ == '__main__':
    main()

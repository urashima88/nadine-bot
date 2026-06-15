import requests

def download_image_bytes(bot_token: str, file_id: str) -> bytes:
    url = f"https://api.telegram.org/bot{bot_token}/getFile"
    resp = requests.get(url, params={"file_id": file_id})
    resp.raise_for_status()
    file_path = resp.json()["result"]["file_path"]

    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    image_resp = requests.get(download_url)
    image_resp.raise_for_status()
    return image_resp.content
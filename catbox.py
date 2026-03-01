import requests

def upload(img_path: str) -> str:
    """이미지를 Catbox에 업로드하고 URL 반환"""
    with open(img_path, "rb") as f:
        r = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            timeout=30,
        )
    url = r.text.strip()
    if not url.startswith("https://"):
        raise ValueError(f"Catbox 업로드 실패: {r.text}")
    return url

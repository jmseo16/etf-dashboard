import os
import requests

API_KEY  = os.environ.get("NOTION_API_KEY", "")
PAGE_ID  = os.environ.get("NOTION_PAGE_ID", "")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def delete_all_blocks(page_id: str = PAGE_ID):
    """페이지 내 모든 블록 삭제"""
    r = requests.get(
        f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100",
        headers=HEADERS,
    )
    for block in r.json().get("results", []):
        requests.delete(
            f"https://api.notion.com/v1/blocks/{block['id']}",
            headers=HEADERS,
        )

def update_title(title: str, page_id: str = PAGE_ID):
    """페이지 제목 업데이트"""
    requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=HEADERS,
        json={"properties": {"title": {"title": [{"text": {"content": title}}]}}},
    )

def append_blocks(blocks: list, page_id: str = PAGE_ID):
    """블록 리스트를 페이지에 추가"""
    # 노션 API는 한번에 100개 블록 제한
    for i in range(0, len(blocks), 100):
        chunk = blocks[i:i+100]
        r = requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=HEADERS,
            json={"children": chunk},
        )
        if r.status_code != 200:
            raise ValueError(f"노션 블록 추가 실패: {r.text}")

def divider():
    return {"object": "block", "type": "divider", "divider": {}}

def heading(text: str, level: int = 2):
    t = f"heading_{level}"
    return {"object": "block", "type": t, t: {
        "rich_text": [{"type": "text", "text": {"content": text}}]
    }}

def callout(text: str, emoji: str = "📅", color: str = "blue_background"):
    return {"object": "block", "type": "callout", "callout": {
        "rich_text": [{"type": "text", "text": {"content": text}}],
        "icon": {"emoji": emoji},
        "color": color,
    }}

def image_block(url: str):
    return {"object": "block", "type": "image",
            "image": {"type": "external", "external": {"url": url}}}

import os
import time
import random
import requests
import subprocess
import multiprocessing
import urllib.parse
from bs4 import BeautifulSoup
import webbrowser
import threading

# ---------------------------
# 설정 및 상수
# ---------------------------
USER_AGENTS = [
    # Android (Chrome, Samsung, Edge, Firefox, Opera) 등 모바일 UA 리스트
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A536N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.196 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-N970F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Chrome/110.0.5481.153 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S908U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/120.0.6099.224 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/16.0 Chrome/92.0.4515.159 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/92.0.4515.159 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 3a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.2151.42 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Edge/118.0.2088.46 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Moto G Power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; OnePlus 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Nokia 7.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; LG G7 ThinQ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.2088.46 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Sony Xperia 1 II) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.224 Mobile Safari/537.36",
]

IMAGE_SAVE_DIR = os.path.join(os.environ.get("USERPROFILE", "."), "Downloads", "rome_mgallary_image")
OUTPUT_DIR = "output"

# ---------------------------
# 유틸리티 함수
# ---------------------------
def get_random_headers(referer: str = "https://m.dcinside.com/") -> dict:
    """랜덤 User-Agent와 기본 Referer를 포함한 헤더 반환."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": referer,
    }

def make_dirs(path: str):
    """디렉토리가 없으면 생성."""
    os.makedirs(path, exist_ok=True)

# ---------------------------
# 이미지 다운로드 관련
# ---------------------------
def download_image(image_url: str, post_id: str, index: int = 0, save_dir: str = IMAGE_SAVE_DIR,
                   max_retries: int = 3, base_name: str = None) -> str:
    """
    이미지 다운로드 함수.
    
    - 403 오류인 경우 건너뛰며, 429 오류시 재시도합니다.
    - 다운로드한 이미지가 placeholder일 경우 삭제 후 None 반환.
    """
    parsed = urllib.parse.urlparse(image_url)
    filename = os.path.basename(parsed.path)
    name, ext = os.path.splitext(filename)
    if not ext or ext.lower() in ['.php', '.asp', '.aspx']:
        ext = ".jpg"
    local_filename = f"post_{base_name if base_name else post_id}_img{index}{ext}"
    local_filepath = os.path.join(save_dir, local_filename)
    make_dirs(os.path.dirname(local_filepath))

    for attempt in range(max_retries):
        try:
            response = requests.get(
                image_url, stream=True, 
                headers={"User-Agent": random.choice(USER_AGENTS)}
            )
            if response.status_code == 429:
                wait_time = random.uniform(5, 15)
                print(f"🚨 {post_id} 이미지 다운로드 429 - {wait_time:.1f}s 후 재시도")
                time.sleep(wait_time)
                continue
            if response.status_code == 403:
                print(f"⛔ {post_id} 이미지 다운로드 403 - 건너뜀")
                return None

            response.raise_for_status()
            with open(local_filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(local_filepath)
            # 파일 크기가 특정 크기(예: 574바이트)일 경우 placeholder로 판단
            if "btn_close02.gif" in image_url or file_size == 574:
                print(f"⛔ {post_id} placeholder 이미지로 판단되어 건너뜀: {image_url}")
                os.remove(local_filepath)
                return None

            print(f"✅ {post_id} 이미지 다운로드 완료: {local_filepath}")
            return local_filepath

        except requests.exceptions.RequestException as e:
            print(f"❌ {post_id} 이미지 다운로드 실패 (재시도 {attempt + 1}/{max_retries}): {image_url}\n오류: {e}")
            time.sleep(0.1)
    print(f"🚨 {post_id} 이미지 다운로드 실패 - 최종 실패")
    return None

# ---------------------------
# 댓글 처리 관련
# ---------------------------
def process_comments(soup: BeautifulSoup, post_id: str) -> list:
    """
    DCInside 댓글 영역(#comment_box) 내 댓글 및 답글 파싱.
    
    댓글 내 이미지가 있으면 로컬 경로로 대체합니다.
    """
    comments_data = []
    comment_box = soup.find("div", id="comment_box")
    if not comment_box:
        print("댓글 영역을 찾지 못함.")
        return comments_data

    comment_items = comment_box.select("ul.all-comment-lst > li")
    current_main = None

    for li in comment_items:
        txt_tag = li.find("p", class_="txt")
        if txt_tag:
            for idx, img in enumerate(txt_tag.find_all("img"), start=1):
                img_url = img.get("data-original") or img.get("src")
                if not img_url:
                    continue
                local_filepath = download_image(img_url, post_id, index=idx, save_dir=IMAGE_SAVE_DIR)
                if local_filepath:
                    img["src"] = local_filepath
                    img.attrs.pop("data-original", None)
                else:
                    print(f"댓글 이미지 다운로드 실패: {img_url}")
            content = str(txt_tag)
        else:
            content = ""

        nickname = li.find("a", class_="nick").get_text(strip=True) if li.find("a", class_="nick") else ""
        date_text = li.find("span", class_="date").get_text(strip=True) if li.find("span", class_="date") else ""

        comment_info = {
            "nickname": nickname,
            "content": content,
            "date": date_text,
            "html": str(li)
        }

        classes = li.get("class", [])
        if "comment" in classes and "comment-add" not in classes:
            current_main = comment_info
            current_main["replies"] = []
            comments_data.append(current_main)
        elif "comment-add" in classes:
            if current_main:
                current_main["replies"].append(comment_info)
            else:
                comments_data.append(comment_info)
        else:
            comments_data.append(comment_info)
    return comments_data

# ---------------------------
# 크롤링 함수
# ---------------------------
def fetch_dcinside_page(page_number: int, max_retries: int = 5) -> list:
    """
    주어진 페이지 번호의 게시글들을 크롤링합니다.
    
    조건에 맞는 게시글(예: '연재' 포함)인 경우 상세 페이지를 파싱합니다.
    """
    session = requests.Session()
    session.headers.update(get_random_headers())

    page_url = f"https://m.dcinside.com/board/rome?page={page_number}"
    print(f"👉 페이지 {page_number} 크롤링 중: {page_url}")

    for attempt in range(max_retries):
        try:
            response = session.get(page_url, timeout=30)
        except requests.exceptions.ReadTimeout as e:
            print(f"🚨 페이지 {page_number} ReadTimeout 발생 (재시도 {attempt + 1}/{max_retries}): {e}")
            time.sleep(10)
            continue

        if response.status_code == 429:
            print(f"🚨 페이지 {page_number}: 429 Too Many Requests")
            time.sleep(10)
            continue

        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ 페이지 {page_number} 요청 실패: {e}")
            time.sleep(10)
            continue
        break
    else:
        print(f"❌ 페이지 {page_number} 크롤링 실패")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    posts = soup.select("ul.gall-detail-lst > li:not(.adv-inner)")
    crawled_posts = []

    for post in posts:
        ginfo = post.select_one("ul.ginfo")
        if not ginfo:
            continue

        li_list = ginfo.find_all("li")
        category = li_list[0].get_text(strip=True) if li_list else ""

        # 기본 정보 파싱
        recommend = 0
        nickname = ""
        time_info = ""
        if li_list:
            try:
                recommend = int(li_list[-1].find("span").get_text(strip=True))
            except (ValueError, AttributeError):
                recommend = 0
            if len(li_list) >= 3:
                nickname = li_list[1].get_text(strip=True)
                time_info = li_list[2].get_text(strip=True)

        # '연재' 카테고리 필터링
        if '연재' in category:
            a_tag = post.find("a", class_="lt")
            if not a_tag or not a_tag.has_attr("href"):
                continue
            detail_url = a_tag["href"]
            print("→ 조건 충족, 상세 페이지 URL:", detail_url)

            try:
                detail_resp = session.get(detail_url, timeout=100)
                detail_resp.raise_for_status()
            except Exception as e:
                print("상세 페이지 요청 실패:", e)
                continue

            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
            parsed_detail = urllib.parse.urlparse(detail_url)
            post_id = os.path.basename(parsed_detail.path)

            # 상세 페이지 내 이미지 다운로드 및 src 수정
            for idx, img in enumerate(detail_soup.find_all("img"), start=1):
                img_url = img.get("data-original") or img.get("src")
                if not img_url:
                    continue
                local_filepath = download_image(img_url, post_id, index=idx, save_dir=IMAGE_SAVE_DIR)
                if local_filepath:
                    img["src"] = local_filepath
                    img.attrs.pop("data-original", None)
                else:
                    print(f"다운로드 실패: {img_url}")

            # 본문 파싱 (광고 스크립트/태그 제거)
            content_tag = detail_soup.select_one("div.gall-thum-btm div.thum-txt > div.thum-txtin")
            if content_tag:
                for tag in content_tag.find_all(["div", "script"], class_="adv-groupno"):
                    tag.decompose()
                for script in content_tag.find_all("script"):
                    script.decompose()
                content = str(content_tag)
            else:
                content = "(본문 없음)"

            comments_data = process_comments(detail_soup, post_id)

            post_data = {
                "post_id": post_id,
                "title": post.select_one("span.subjectin").get_text(strip=True) if post.select_one("span.subjectin") else "",
                "content": content,
                "comments": comments_data,
                "recommend": recommend,
                "nickname": nickname,
                "time_info": time_info
            }
            crawled_posts.append(post_data)
            print(f"✅ 게시글 {post_id} 크롤링 완료: {post_data['title'][:20]}")

    return crawled_posts

# ---------------------------
# HTML 저장 관련
# ---------------------------
def generate_html(post: dict, output_dir: str = OUTPUT_DIR):
    """
    개별 게시글을 HTML 파일로 저장합니다.
    """
    make_dirs(output_dir)
    post_id = post.get("post_id", "unknown")
    filename = os.path.join(output_dir, f"post_{post_id}.html")

    recommend = post.get("recommend", 0)
    nickname = post.get("nickname", "익명")
    time_info = post.get("time_info", "")

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{post['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .post {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }}
        .comments {{ margin-top: 10px; padding-left: 20px; }}
        .reply {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <div class="post">
        <h2>{post['title']} (추천수: {recommend})</h2>
        <p><strong>글쓴이:</strong> {nickname} | <strong>작성 시각:</strong> {time_info}</p>
        <div class="content">{post['content']}</div>
    </div>
    <div class="comments">
        <h3>댓글</h3>
        <ul>
    """
    for comment in post.get("comments", []):
        comment_nick = comment.get("nickname", "익명")
        comment_content = comment.get("content", "")
        html_content += f"<li><strong>{comment_nick}:</strong> {comment_content}</li>\n"
        if "replies" in comment:
            html_content += "<ul>\n"
            for reply in comment["replies"]:
                reply_nick = reply.get("nickname", "익명")
                reply_content = reply.get("content", "")
                html_content += f"<li class='reply'><strong>{reply_nick}:</strong> {reply_content}</li>\n"
            html_content += "</ul>\n"
    html_content += """
        </ul>
    </div>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ 저장 완료: {filename}")

def save_all_posts(all_posts: list):
    """전체 게시글을 개별 HTML 파일로 저장합니다."""
    for post in all_posts:
        generate_html(post)

# ---------------------------
# 멀티프로세스 크롤링
# ---------------------------
def multiprocess_crawl(start_page: int, end_page: int, num_workers: int) -> list:
    """
    멀티프로세스를 사용하여 페이지 단위 크롤링 후 모든 게시글 데이터 리스트를 반환합니다.
    """
    page_numbers = list(range(start_page, end_page + 1))
    all_posts = []
    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(fetch_dcinside_page, page_numbers)
    for page_posts in results:
        if page_posts:
            all_posts.extend(page_posts)
    return all_posts

# ---------------------------
# main 함수
# ---------------------------
def main():
    multiprocessing.freeze_support()
    start_page = 1
    end_page = 10  # 예제용: 10페이지
    num_workers = 20

    all_posts = multiprocess_crawl(start_page, end_page, num_workers)
    print(f"📂 총 {len(all_posts)}개의 게시글 크롤링 완료, 저장 시작...")
    save_all_posts(all_posts)
    print("🎉 모든 게시글 저장 완료!")

if __name__ == "__main__":
    main()

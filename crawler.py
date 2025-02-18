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

# 모바일 환경에서 사용할 User-Agent 리스트
USER_AGENTS = [
    # ✅ Android (Chrome, Samsung, Edge, Firefox, Opera)
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

    # ✅ iOS (Safari, Chrome, Firefox, Edge, Opera)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.8 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.224 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.224 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/118.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/119.0.2151.42 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) OPR/120.0.6099.224 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/118.0.2088.46 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.224 Mobile/15E148 Safari/604.1",
]     
IMAGE_SAVE_DIR = "C:\\Users\\Master\\Downloads\\rome_mgallary_image"

def download_image(image_url, post_id, index=0, save_dir=IMAGE_SAVE_DIR, max_retries=3, base_name=None):
    """
    이미지 다운로드 (403: 건너뜀, 429: 재시도)
    base_name이 주어지면 해당 이름을 기본으로 파일명을 생성합니다.
    다운로드 후 파일 크기가 min_size(기본 5KB) 미만이면 재시도합니다.
    """
    parsed = urllib.parse.urlparse(image_url)
    filename = os.path.basename(parsed.path)
    name, ext = os.path.splitext(filename)
    # 확장자가 없거나 이미지 확장자가 아닌 경우 .jpg로 지정
    if not ext or ext.lower() in ['.php', '.asp', '.aspx']:
        ext = ".jpg"
    if base_name is not None:
        local_filename = f"post_{base_name}_img{index}{ext}"
    else:
        local_filename = f"post_{post_id}_img{index}{ext}"
    local_filepath = os.path.join(save_dir, local_filename)
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                image_url, stream=True, 
                headers={"User-Agent": random.choice(USER_AGENTS)}
            )
            if response.status_code == 429:
                wait_time = random.uniform(5, 15)
                print(f"🚨 {post_id} 이미지 다운로드 429 - {wait_time:.1f}s 대기 후 재시도")
                time.sleep(wait_time)
                continue
            if response.status_code == 403:
                print(f"⛔ {post_id} 이미지 다운로드 403 - 건너뜀")
                return None
            response.raise_for_status()

            # 파일 다운로드
            with open(local_filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            file_size = os.path.getsize(local_filepath)
            # 파일 크기 검증: min_size와 일치하면 재시도 대상
            if "btn_close02.gif" in image_url or file_size == 574:
                        print(f"⛔ {post_id} 로딩 중 이미지(placeholder)로 판단되어 건너뜀: {image_url}")
                        os.remove(local_filepath)
                        return []
                
            print(f"✅ {post_id} 이미지 다운로드 완료: {local_filepath}")
            return local_filepath
    
    print(f"🚨 {post_id} 이미지 다운로드 실패 - 최종적으로 다운로드하지 못함")
    return None
	
def process_comments(soup, post_id):
    """
    DCInside 댓글 영역(#comment_box)에서 메인 댓글과 답글을 그룹화하여 파싱합니다.
    댓글 본문 내의 이미지(디시콘 등)가 있다면 다운로드하고, src를 로컬 경로로 대체한 후 HTML을 그대로 보존합니다.
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
            # 댓글 본문 내 이미지 다운로드 처리
            for idx, img in enumerate(txt_tag.find_all("img"), start=1):
                img_url = img.get("data-original") or img.get("src")
                if not img_url:
                    continue
                local_filepath = download_image(img_url, post_id, index=idx, save_dir=IMAGE_SAVE_DIR)
                if local_filepath:
                    img["src"] = local_filepath
                    if "data-original" in img.attrs:
                        del img["data-original"]
                else:
                    print(f"댓글 이미지 다운로드 실패: {img_url}")
            # 텍스트만 추출하는 대신, HTML 그대로 보존
            content = str(txt_tag)
        else:
            content = ""

        nick_tag = li.find("a", class_="nick")
        nickname = nick_tag.get_text(strip=True) if nick_tag else ""
        date_tag = li.find("span", class_="date")
        date_text = date_tag.get_text(strip=True) if date_tag else ""

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


def fetch_dcinside_page(page_number, max_retries=5):
    """ DCInside 게시글 크롤링 + 429(재시도) + 403(건너뛰기) """
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://m.dcinside.com/",
    })

    page_url = f"https://m.dcinside.com/board/rome?page={page_number}"
    print(f"👉 페이지 {page_number} 크롤링 중: {page_url}")

    for attempt in range(max_retries):
        try:
            response = session.get(page_url, timeout=10)
            if response.status_code == 429:
                print(f"🚨 페이지 {page_number}: 429 Too Many Requests")
                time.sleep(10)
                continue
            response.raise_for_status()
            break
        except Exception as e:
            print(f"페이지 {page_number} 요청 실패 (시도 {attempt+1}/{max_retries}): {e}")
            time.sleep(5)
    else:
        print(f"❌ 페이지 {page_number} 크롤링 실패")
        return []  # 실패하면 빈 리스트 반환

    soup = BeautifulSoup(response.text, "html.parser")
    posts = soup.select("ul.gall-detail-lst > li:not(.adv-inner)")
    crawled_posts = []

    for post in posts:
        ginfo = post.select_one("ul.ginfo")
        if not ginfo:
            continue
        li_list = ginfo.find_all("li")
    
        category = li_list[0].get_text(strip=True) if li_list else ""
    
        recommend = 0
        if li_list:
            rec_li = li_list[-1]
            span_tag = rec_li.find("span")
            if span_tag:
                try:
                    recommend = int(span_tag.get_text(strip=True))
                except ValueError:
                    recommend = 0

        subjectin = post.select_one("span.subjectin")
        title = subjectin.get_text(strip=True) if subjectin else ""
    
        # 조건
    
        if '판도' in title:
            a_tag = post.find("a", class_="lt")
            if not a_tag or not a_tag.has_attr("href"):
                continue
            detail_url = a_tag["href"]
            print("→ 조건 충족, 상세 페이지 URL:", detail_url)

            try:
                detail_resp = session.get(detail_url, timeout=10)
                detail_resp.raise_for_status()
            except Exception as e:
                print("상세 페이지 요청 실패:", e)
                continue
            
            detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
            
            # URL의 경로를 사용해 post_id를 추출 (쿼리문 제거)
            parsed_detail = urllib.parse.urlparse(detail_url)
            post_id = os.path.basename(parsed_detail.path)

            for idx, img in enumerate(detail_soup.find_all("img"), start=1):
                img_url = img.get("data-original") or img.get("src")
                if not img_url:
                    continue
                local_filepath = download_image(img_url, post_id, index=idx, save_dir=IMAGE_SAVE_DIR)
                if local_filepath:
                    img["src"] = local_filepath
                    if "data-original" in img.attrs:
                        del img["data-original"]
                else:
                    print(f"다운로드 실패: {img_url}")

            content_tag = detail_soup.select_one("div.gall-thum-btm div.thum-txt > div.thum-txtin")
            if content_tag:
                # 광고 관련 태그 제거: adv-groupno 클래스나 script 태그 제거
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
                "title": title,
                "content": content,
                "comments": comments_data,
                "recommend": recommend,  
            }
            crawled_posts.append(post_data)
            print(f"✅ 게시글 {post_id} 크롤링 완료: {title[:20]}")

    return crawled_posts

def generate_html(all_posts, filename="dcinside_crawled_posts.html"):
    """
    누적된 게시글 정보를 HTML 형식으로 변환하여 파일에 저장합니다.
    각 게시글은 제목, 본문, 댓글(메인 댓글 및 답글) 순으로 출력됩니다.
    댓글의 작성자 닉네임은 익명화되어 "ㅇㅇ1", "ㅇㅇ2", ... 형식으로 대체됩니다.
    """
    # 익명 닉네임 매핑 사전과 카운터
    nick_mapping = {}
    next_anonym = 1

    def get_anonym(nickname):
        nonlocal next_anonym
        # 닉네임이 없으면 "익명" 처리
        if not nickname:
            return "익명"
        if nickname not in nick_mapping:
            nick_mapping[nickname] = f"ㅇㅇ{next_anonym}"
            next_anonym += 1
        return nick_mapping[nickname]

    html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>DCInside 크롤링 결과</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .post { border: 1px solid #ccc; margin: 20px 0; padding: 10px; }
        .post h2 { margin: 0; }
        .comments { margin-top: 10px; padding-left: 20px; }
        .reply { margin-left: 20px; }
    </style>
</head>
<body>
    <h1>DCInside 크롤링 결과</h1>
"""
    for post in all_posts:
        recommend = post.get("recommend", 0)
        post_html = f"<div class='post'>\n"
        post_html += f"<h2>{post['title']} (게시글 번호: {post['post_id']}, 추천수: {recommend})</h2>\n"
        post_html += f"<div class='content'><p>{post['content'].replace(chr(10), '<br>')}</p></div>\n"
        
        if post.get("comments"):
            post_html += "<div class='comments'><h3>댓글:</h3><ul>\n"
            for comment in post["comments"]:
                # 익명화된 닉네임으로 변환
                anon_nick = get_anonym(comment.get("nickname", "익명"))
                content   = comment.get("content", "")
                post_html += f"<li><strong>{anon_nick}:</strong> {content}</li>\n"
                if comment.get("replies"):
                    post_html += "<ul>\n"
                    for reply in comment["replies"]:
                        rep_anon = get_anonym(reply.get("nickname", "익명"))
                        rep_content = reply.get("content", "")
                        post_html += f"<li class='reply'><strong>{rep_anon}:</strong> {rep_content}</li>\n"
                    post_html += "</ul>\n"
            post_html += "</ul></div>\n"
        else:
            post_html += "<div class='comments'><p>댓글 없음</p></div>\n"
        post_html += "</div>\n"
        html += post_html

    html += """
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML 업데이트 완료 ({len(all_posts)}개 게시글) → {filename}")

def multiprocess_crawl(start_page, end_page, num_workers):
    """멀티프로세스로 페이지 단위 크롤링 후 결과 리스트를 반환합니다."""
    page_numbers = list(range(start_page, end_page + 1))
    all_posts = []
    with multiprocessing.Pool(num_workers) as pool:
        # 각 페이지에 대해 fetch_dcinside_page를 실행
        results = pool.map(fetch_dcinside_page, page_numbers)
    # 결과(리스트의 리스트)를 평탄화
    for page_posts in results:
        all_posts.extend(page_posts)
    return all_posts
        
if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windows에서 multiprocess 안정화
    # 원하는 페이지 범위 설정 (예: 1페이지부터 100페이지까지)
    start_page = 1
    end_page = 22644
    num_workers = 15
    all_posts = multiprocess_crawl(start_page, end_page, num_workers)
    html_filename = "dcinside_crawled_posts.html"
    generate_html(all_posts, html_filename)

import streamlit as st
import requests
import os
import zipfile
from io import BytesIO
from PIL import Image
from urllib.parse import quote

# 🔑 API 키 설정
UNSPLASH_KEY = "j5lyiOKj0bj6iMFPgvCnO0cCB_eWEyx5NsXZr3VRR94"
PIXABAY_KEY = "51462455-6f4af1014e035b145b2e7731b"
KOGOL_KEY = "NBzHjXyev6wbzDaiuwiq+/U4WpluDs7pZypSHayREgTmJo32rmlp5ssiFGnUlZvFH1u+S3YjH7jJv+3w7eFNUg=="

DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 🔽 이미지 다운로드 함수
def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

# 🖼 Unsplash 검색
def search_unsplash(keyword, count):
    st.markdown("### 🟦 Unsplash")
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": keyword, "per_page": count}
    try:
        r = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            results = r.json().get("results", [])
            for i in range(0, len(results), 5):
                cols = st.columns(5)
                for j in range(5):
                    if i + j < len(results):
                        url = results[i + j]["urls"]["regular"]
                        path = os.path.join(DOWNLOAD_DIR, f"unsplash_{i + j + 1}.jpg")
                        if download_image(url, path):
                            cols[j].image(path, use_column_width="always", caption=f"Unsplash #{i + j + 1}")
    except Exception:
        st.warning("🔸 Unsplash에서 이미지를 가져올 수 없습니다.")

# 🖼 Pixabay 검색
def search_pixabay(keyword, count):
    st.markdown("### 🟨 Pixabay")
    try:
        r = requests.get(f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={quote(keyword)}&per_page={count}", timeout=10)
        if r.status_code == 200:
            results = r.json().get("hits", [])
            for i in range(0, len(results), 5):
                cols = st.columns(5)
                for j in range(5):
                    if i + j < len(results):
                        url = results[i + j]["largeImageURL"]
                        path = os.path.join(DOWNLOAD_DIR, f"pixabay_{i + j + 1}.jpg")
                        if download_image(url, path):
                            cols[j].image(path, use_column_width="always", caption=f"Pixabay #{i + j + 1}")
    except Exception:
        st.warning("🔸 Pixabay에서 이미지를 가져올 수 없습니다.")

# 🖼 Pexels 검색
def search_pexels(keyword, count):
    st.markdown("### 🟩 Pexels")
    headers = {"Authorization": os.getenv("PEXELS_KEY", ""), "User-Agent": "Mozilla/5.0"}
    if not headers["Authorization"]:
        headers["Authorization"] = PEXELS_KEY  # fallback

    try:
        r = requests.get("https://api.pexels.com/v1/search", headers=headers, params={"query": keyword, "per_page": count}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for i in range(0, len(photos), 5):
                cols = st.columns(5)
                for j in range(5):
                    if i + j < len(photos):
                        url = photos[i + j]["src"]["original"]
                        path = os.path.join(DOWNLOAD_DIR, f"pexels_{i + j + 1}.jpg")
                        if download_image(url, path):
                            cols[j].image(path, use_column_width="always", caption=f"Pexels #{i + j + 1}")
    except Exception:
        st.warning("🔸 Pexels에서 이미지를 가져올 수 없습니다.")

# 🖼 공공누리 검색
def search_kogol(keyword, count):
    st.markdown("### 🟥 공공누리(KOGOL)")
    url = f"http://api.kogl.or.kr/search/portalDataSearch.do?ServiceKey={KOGOL_KEY}&pageNo=1&pageSize={count}&query={quote(keyword)}&sort=score&license=ko&format=json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            items = r.json().get("result", {}).get("items", [])
            for i in range(0, len(items), 5):
                cols = st.columns(5)
                for j in range(5):
                    if i + j < len(items):
                        item = items[i + j]
                        img_url = item.get("imageUrl", "")
                        if not img_url:
                            continue
                        path = os.path.join(DOWNLOAD_DIR, f"kogol_{i + j + 1}.jpg")
                        if download_image(img_url, path):
                            cols[j].image(path, use_column_width="always", caption=f"KOGOL #{i + j + 1}")
    except Exception:
        st.warning("🔸 공공누리에서 이미지를 가져올 수 없습니다.")

# 📦 다운로드 zip 생성
def create_zip():
    zip_path = os.path.join(DOWNLOAD_DIR, "images.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(DOWNLOAD_DIR):
            if filename.endswith(".jpg"):
                zipf.write(os.path.join(DOWNLOAD_DIR, filename), arcname=filename)
    return zip_path

# 🌐 Streamlit UI
st.title("🔍 이미지 멀티 검색 앱")
keyword = st.text_input("검색 키워드 (예: 제주오름)", value="제주오름")
count = st.slider("이미지 개수 (API별)", min_value=5, max_value=30, step=5, value=10)

if st.button("검색 시작"):
    # 기존 이미지 삭제
    for f in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

    with st.spinner("이미지를 검색 중입니다..."):
        search_unsplash(keyword, count)
        search_pixabay(keyword, count)
        search_pexels(keyword, count)
        search_kogol(keyword, count)

    zip_path = create_zip()
    with open(zip_path, "rb") as f:
        st.download_button(label="📦 이미지 ZIP 다운로드", data=f, file_name="images.zip", mime="application/zip")

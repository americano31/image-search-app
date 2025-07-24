import streamlit as st
import requests
import os
import zipfile
from io import BytesIO
from PIL import Image
from urllib.parse import quote

# API 키 설정
UNSPLASH_KEY = "j5lyiOKj0bj6iMFPgvCnO0cCB_eWEyx5NsXZr3VRR94"
PIXABAY_KEY = "51462455-6f4af1014e035b145b2e7731b"
KOGOL_KEY = "NBzHjXyew6bzDaUiwvq+/U4WpluS7p3YzpShAyREgzTJmo32rmWp5siFGnUWZvfH1u+S3VjH71jv+J7wEFnUg=="

DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 이미지 다운로드
def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        return False
    return False

# Unsplash 검색
def search_unsplash(keyword, count):
    st.markdown("### 📸 Unsplash")
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": keyword, "per_page": count}
    res = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
    results = res.json().get("results", [])

    unsplash_dir = os.path.join(DOWNLOAD_DIR, "Unsplash")
    os.makedirs(unsplash_dir, exist_ok=True)

    for i, img in enumerate(results):
        url = img["urls"]["small"]
        path = os.path.join(unsplash_dir, f"{keyword}_unsplash_{i+1}.jpg")
        if download_image(url, path):
            st.image(path, width=150, caption=f"Unsplash {i+1}")
    return unsplash_dir

# Pixabay 검색
def search_pixabay(keyword, count):
    st.markdown("### 🖼️ Pixabay")
    params = {"key": PIXABAY_KEY, "q": keyword, "per_page": count}
    res = requests.get("https://pixabay.com/api/", params=params)
    hits = res.json().get("hits", [])

    pixabay_dir = os.path.join(DOWNLOAD_DIR, "Pixabay")
    os.makedirs(pixabay_dir, exist_ok=True)

    for i, img in enumerate(hits):
        url = img["webformatURL"]
        path = os.path.join(pixabay_dir, f"{keyword}_pixabay_{i+1}.jpg")
        if download_image(url, path):
            st.image(path, width=150, caption=f"Pixabay {i+1}")
    return pixabay_dir

# 공공누리 예시 (일단 요청만)
def search_kogl(keyword, count):
    st.markdown("### 🇰🇷 공공누리 (미지원 - 시범)")
    st.warning("공공누리는 현재 Streamlit 미리보기 및 자동 다운로드 기능이 불안정합니다.")
    return None

# ZIP으로 묶기
def zip_images(root_dir):
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, 'w') as zipf:
        for foldername, _, filenames in os.walk(root_dir):
            for fname in filenames:
                full_path = os.path.join(foldername, fname)
                rel_path = os.path.relpath(full_path, root_dir)
                zipf.write(full_path, arcname=rel_path)
    zip_buf.seek(0)
    return zip_buf

# --- Streamlit UI ---
st.set_page_config(page_title="멀티 이미지 수집기", layout="wide")
st.title("🔍 이미지 검색 & 다운로드 툴")
keyword = st.text_input("검색할 키워드", placeholder="예: 제주 오름")
num = st.slider("이미지 수 (API별)", 5, 20, 10)

if st.button("검색 시작"):
    with st.spinner("이미지를 수집 중입니다..."):
        dirs = []
        try:
            dirs.append(search_unsplash(keyword, num))
        except:
            st.error("❌ Unsplash에서 오류 발생")
        try:
            dirs.append(search_pixabay(keyword, num))
        except:
            st.error("❌ Pixabay에서 오류 발생")
        try:
            kogl_dir = search_kogl(keyword, num)
            if kogl_dir:
                dirs.append(kogl_dir)
        except:
            st.error("❌ 공공누리에서 오류 발생")

        # ZIP 생성 및 다운로드
        zip_file = zip_images(DOWNLOAD_DIR)
        st.success("✅ 이미지 수집 완료!")
        st.download_button("📦 이미지 ZIP 다운로드", zip_file, file_name="images.zip")


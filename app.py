import streamlit as st
import requests
import os
import zipfile
from io import BytesIO
from PIL import Image
from urllib.parse import quote

# API 키 설정
UNSPLASH_KEY = "j5lyiOKj0bj6iMFPgvCnO0cCB_eWEyx5NsXZr3VRR94"
PIXABAY_KEY = "51462455-6f4af1014e035b145b2e7731e"
PEXELS_KEY = "kd1frTIFwfExQIR5DIGn1eKJ7gEGUIbbWDKSmi3sLjGhv9nDVP0Qmnnh"
KOGOL_KEY = "NBzHjXyev6wbzDaluiwq/U44Wplus7p3yzpSHAyREgTm3o2mzmlp5siFGnUlZvFH1u+S3VjH7j1vvJw9FeRUg=="

DOWNLOAD_DIR = "images"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 이미지 다운로드 함수
def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        pass
    return False

# Unsplash 검색
def search_unsplash(keyword, count):
    st.markdown("### 🖼️ Unsplash")
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    url = f"https://api.unsplash.com/search/photos?query={quote(keyword)}&per_page={count}"
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        cols = st.columns(5)
        for i, item in enumerate(data['results']):
            img_url = item['urls']['small']
            filename = f"unsplash_{i+1}.jpg"
            path = os.path.join(DOWNLOAD_DIR, filename)
            download_image(img_url, path)
            with cols[i % 5]:
                st.image(img_url, caption=f"Unsplash #{i+1}", use_container_width=True)
    except:
        st.warning("Unsplash에서 이미지를 가져올 수 없습니다.")

# Pixabay 검색
def search_pixabay(keyword, count):
    st.markdown("### 📸 Pixabay")
    url = f"https://pixabay.com/api/?key={PIXABAY_KEY}&q={quote(keyword)}&per_page={count}"
    try:
        res = requests.get(url)
        data = res.json()
        cols = st.columns(5)
        for i, item in enumerate(data['hits']):
            img_url = item['webformatURL']
            filename = f"pixabay_{i+1}.jpg"
            path = os.path.join(DOWNLOAD_DIR, filename)
            download_image(img_url, path)
            with cols[i % 5]:
                st.image(img_url, caption=f"Pixabay #{i+1}", use_container_width=True)
    except:
        st.warning("Pixabay에서 이미지를 가져올 수 없습니다.")

# Pexels 검색
def search_pexels(keyword, count):
    st.markdown("### 📷 Pexels")
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/v1/search?query={quote(keyword)}&per_page={count}"
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        cols = st.columns(5)
        for i, item in enumerate(data['photos']):
            img_url = item['src']['medium']
            filename = f"pexels_{i+1}.jpg"
            path = os.path.join(DOWNLOAD_DIR, filename)
            download_image(img_url, path)
            with cols[i % 5]:
                st.image(img_url, caption=f"Pexels #{i+1}", use_container_width=True)
    except:
        st.warning("Pexels에서 이미지를 가져올 수 없습니다.")

# 압축 다운로드 함수
def create_zip():
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for f in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, f)
            if os.path.isfile(file_path):
                zip_file.write(file_path, arcname=f)
    zip_buffer.seek(0)
    return zip_buffer

# 스트림릿 UI
st.title("🔍 이미지 멀티 검색기")
keyword = st.text_input("검색어를 입력하세요")
count = st.slider("이미지 개수 (API별)", 1, 30, 10)

if st.button("검색하기") and keyword:
    # 기존 이미지 제거
    for f in os.listdir(DOWNLOAD_DIR):
        path = os.path.join(DOWNLOAD_DIR, f)
        if os.path.isfile(path):
            os.remove(path)

    search_unsplash(keyword, count)
    search_pixabay(keyword, count)
    search_pexels(keyword, count)

    # ZIP 파일 다운로드 제공
    zip_file = create_zip()
    st.download_button(
        label="📦 이미지 ZIP 다운로드",
        data=zip_file,
        file_name=f"{keyword}_images.zip",
        mime="application/zip"
    )

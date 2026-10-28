import os
import requests
import boto3
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
TARGET_PAGE_URL = "https://www.esaral.com/ncert-class-10-social-science-book-pdf-2026-27-chapter-wise-free-download/"

B2_KEY_ID = os.environ.get('B2_KEY_ID')
B2_APP_KEY = os.environ.get('B2_APP_KEY')
B2_BUCKET = 'ias-machine-storage500'
B2_ENDPOINT = 'https://s3.us-east-005.backblazeb2.com'

# Initialize B2
s3 = boto3.client('s3', endpoint_url=B2_ENDPOINT, aws_access_key_id=B2_KEY_ID, aws_secret_access_key=B2_APP_KEY)

def upload_to_b2(file_content, filename):
    try:
        print(f"  ☁️ Uploading to B2: {filename}")
        s3.put_object(Bucket=B2_BUCKET, Key=f"vip_library/{filename}", Body=file_content)
        return f"https://f005.backblazeb2.com/file/{B2_BUCKET}/vip_library/{filename}"
    except Exception as e:
        print(f"  ❌ B2 Upload Error: {e}")
        return None

def main():
    print(f"🔍 Fetching links from: {TARGET_PAGE_URL}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        res = requests.get(TARGET_PAGE_URL, headers=headers, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to load page: {e}")
        return

    soup = BeautifulSoup(res.text, 'html.parser')
    pdf_links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf') and 'media/uploads' in href:
            pdf_links.append(href)

    if not pdf_links:
        print("⚠️ No PDF links found.")
        return

    print(f"✅ Found {len(pdf_links)} PDFs. Starting direct transfer to B2...")
    
    for url in pdf_links:
        filename = url.split('/')[-1]
        print(f"  ⬇️ Downloading: {filename}")
        
        try:
            file_res = requests.get(url, headers=headers, timeout=30)
            file_res.raise_for_status()
            b2_url = upload_to_b2(file_res.content, filename)
            if b2_url:
                print(f"     ✅ Done!")
        except Exception as e:
            print(f"     ❌ Failed: {e}")

    print("\n🎉 All transfers finished! Check your B2 bucket.")

if __name__ == "__main__":
    main()

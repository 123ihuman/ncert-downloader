import os
import requests
import boto3
from bs4 import BeautifulSoup
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
# Add all the books you want here. The script will create folders for each.
TARGET_BOOKS = {
    "Class_6_SocialScience": "https://www.esaral.com/ncert-class-6-social-science-book-pdf/",
    "Class_7_SocialScience": "https://www.esaral.com/ncert-class-7-social-science-book-pdf/",
    "Class_8_SocialScience": "https://www.esaral.com/ncert-class-8-social-science-book-pdf/",
    "Class_9_SocialScience": "https://www.esaral.com/ncert-class-9-social-science-book-pdf/",
    "Class_10_SocialScience": "https://www.esaral.com/ncert-class-10-social-science-book-pdf-2026-27-chapter-wise-free-download/",
    
    "Class_11_History": "https://www.esaral.com/ncert-class-11-history-book-pdf/",
    "Class_12_History": "https://www.esaral.com/ncert-class-12-history-book-pdf/",
    
    "Class_11_Polity": "https://www.esaral.com/ncert-class-11-political-science-book-pdf/",
    "Class_12_Polity": "https://www.esaral.com/ncert-class-12-political-science-book-pdf/",
    
    "Class_11_Geography": "https://www.esaral.com/ncert-class-11-geography-book-pdf/",
    "Class_12_Geography": "https://www.esaral.com/ncert-class-12-geography-book-pdf/",
    
    "Class_11_Economics": "https://www.esaral.com/ncert-class-11-economics-book-pdf/",
    "Class_12_Economics": "https://www.esaral.com/ncert-class-12-economics-book-pdf/",
}

B2_KEY_ID = os.environ.get('B2_KEY_ID')
B2_APP_KEY = os.environ.get('B2_APP_KEY')
B2_BUCKET = 'ias-machine-storage500'
B2_ENDPOINT = 'https://s3.us-east-005.backblazeb2.com'

s3 = boto3.client('s3', endpoint_url=B2_ENDPOINT, aws_access_key_id=B2_KEY_ID, aws_secret_access_key=B2_APP_KEY)

def upload_to_b2(file_content, folder_name, filename):
    try:
        b2_key = f"vip_library/{folder_name}/{filename}"
        s3.put_object(Bucket=B2_BUCKET, Key=b2_key, Body=file_content)
        return True
    except Exception as e:
        print(f"  ❌ B2 Upload Error: {e}")
        return False

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    total_uploaded = 0

    for folder_name, url in TARGET_BOOKS.items():
        print(f"\n📂 Processing: {folder_name}")
        try:
            res = requests.get(url, headers=headers, timeout=15, verify=False)
            res.raise_for_status()
        except Exception as e:
            print(f"  ❌ Failed to load page: {e}")
            continue

        soup = BeautifulSoup(res.text, 'html.parser')
        pdf_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf') and 'media/uploads' in href:
                pdf_links.append(href)

        if not pdf_links:
            print("  ⚠️ No PDF links found.")
            continue

        print(f"  ✅ Found {len(pdf_links)} PDFs.")
        
        for pdf_url in pdf_links:
            filename = pdf_url.split('/')[-1]
            print(f"  ⬇️ Downloading: {filename}")
            try:
                file_res = requests.get(pdf_url, headers=headers, timeout=30, verify=False)
                file_res.raise_for_status()
                if upload_to_b2(file_res.content, folder_name, filename):
                    print(f"     ✅ Uploaded to B2/{folder_name}")
                    total_uploaded += 1
                time.sleep(0.5) # Prevent spamming the server
            except Exception as e:
                print(f"     ❌ Failed: {e}")

    print(f"\n🎉 Process finished! Uploaded {total_uploaded} files to B2.")

if __name__ == "__main__":
    main()

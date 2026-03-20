import os
import requests

def fetch_knmi_file(api_key, base_url, destination_dir):
    """
    Common utility to fetch the latest file from any KNMI Open Data dataset.
    """
    headers = {"Authorization": api_key}
    
    # 1. Get latest filename
    res = requests.get(base_url, headers=headers, params={"maxKeys": 1, "sorting": "desc"})
    res.raise_for_status() # Raise error if API is down
    filename = res.json()["files"][0]["filename"]
    
    # 2. Get the temporary download URL
    url_endpoint = f"{base_url}/{filename}/url"
    url_res = requests.get(url_endpoint, headers=headers)
    url_res.raise_for_status()
    download_url = url_res.json()["temporaryDownloadUrl"]
    
    # 3. Download the binary content
    local_path = os.path.join(destination_dir, filename)
    file_data = requests.get(download_url)
    
    with open(local_path, "wb") as f:
        f.write(file_data.content)
    
    return local_path
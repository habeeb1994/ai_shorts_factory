import requests
import os

class ScoutAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos/search"

    def find_high_energy_clips(self, keywords, count=1):
        headers = {"Authorization": self.api_key}
        links = []
        
        # Split the comma-separated keywords string into a list dynamically
        if isinstance(keywords, str):
            keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        else:
            keyword_list = keywords
            
        for kw in keyword_list:
            params = {"query": kw, "orientation": "portrait", "per_page": count}
            response = requests.get(self.base_url, headers=headers, params=params).json()
            for v in response.get('videos', []):
                if v.get('video_files'):
                    links.append(v['video_files'][0]['link'])
                    
        return links

    def download_clips(self, links, save_path):
        paths = []
        for i, link in enumerate(links):
            file_path = os.path.join(save_path, f"clip_{i}.mp4")
            with requests.get(link, stream=True) as r:
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            paths.append(os.path.abspath(file_path))
        return paths
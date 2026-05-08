import requests
import os
import random

class ScoutAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.pexels.com/videos/search"

    def find_high_energy_clips(self, keywords, count=1):
        headers = {"Authorization": self.api_key}
        links = set()
        
        # 1. Robust keyword parsing
        keyword_list = []
        if isinstance(keywords, str):
            # Remove brackets and quotes if it was accidentally passed as a stringified list
            clean_str = keywords.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
            raw_list = [k.strip() for k in clean_str.split(',') if k.strip()]
        else:
            raw_list = keywords
            
        # 2. Split any comma-separated strings within the list and clean up
        for kw in raw_list:
            if isinstance(kw, str):
                keyword_list.extend([k.strip() for k in kw.split(',') if k.strip()])
                
        # 3. Deduplicate keywords to prevent redundant API calls
        keyword_list = list(set(keyword_list))

        for kw in keyword_list:
            print(f"🔍 Scouting Pexels for: {kw}")
            params = {"query": kw, "orientation": "portrait", "per_page": 15}
            response = requests.get(self.base_url, headers=headers, params=params).json()
            
            videos = response.get('videos', [])
            if videos:
                random.shuffle(videos)
                added = 0
                for v in videos:
                    if added >= count:
                        break
                    if v.get('video_files'):
                        # Prefer HD quality files if available, otherwise pick the first
                        hd_files = [f for f in v['video_files'] if f.get('quality') == 'hd']
                        best_file = hd_files[0] if hd_files else v['video_files'][0]
                        links.add(best_file['link'])
                        added += 1
                    
        return list(links)

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
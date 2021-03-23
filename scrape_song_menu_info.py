import requests
import re
from urllib.parse import urljoin
import pymongo
from tqdm import tqdm

base_url = 'https://music.163.com'
url = "https://music.163.com/discover/playlist/?cat={category}&limit={limit}&offset={offset}"
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'refer': 'https://music.163.com/',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
}

proxies = {
    'http': '112.80.248.73:80',
    'http': '202.108.22.5:80',
    'http': '112.80.248.75:80'
}

def res_scrape(url, headers, proxies):
    html = requests.get(url=url, headers=headers, proxies=proxies).text
    infos = tqdm(re.findall('href="(.*?)" class="msk"', html))
    for info in infos:
        level2_url = urljoin(base_url, info)
        data = homepage_scrape(url=level2_url, headers=headers, proxies=proxies)
        save_data(data)

def homepage_scrape(url, headers, proxies):
    '''
    歌单名称 | 创建者 | 创建时间 | 播放量 | 收藏量 | 分享量 | 评论数 | 歌曲数量
    return: data
    '''
    res = requests.get(url=url, headers=headers, proxies=proxies).text
    view_counts = re.search('<strong id="play-count" class="s-fc6">(.*?)</strong>次', res).group(1)
    collection_counts = re.search('data-count="(.*?)"\ndata-res-action="fav"', res).group(1)
    share_counts = re.search('data-count="(.*?)"\ndata-res-action="share"', res).group(1)
    comments_counts = re.search('<span id="cnt_comment_count">(.*?)</span>', res).group(1)
    song_counts = re.search('<span id="playlist-track-count">(.*?)</span>首歌</span>', res).group(1)
    try:
        data = {
            'songList_name': re.search('data-res-name="(.*?)"', res).group(1),
            'createList_author': re.search('data-res-author="(.*?)"', res).group(1),
            'createList_time': re.search('<span class="time s-fc4">(.*?)&nbsp;创建</span>', res).group(1),
            'view_counts': int(view_counts) if view_counts.isdigit() else 0,
            'collection_counts': int(collection_counts) if collection_counts.isdigit() else 0,
            'share_counts': int(share_counts) if share_counts.isdigit() else 0,
            'comments_counts': int(comments_counts) if comments_counts.isdigit() else 0,  # 评论数
            'song_counts': int(song_counts) if song_counts.isdigit() else 0
        }
    except:
        print(url)
    return data

def save_data(data:dict):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['wangyiyun_data']
    collection = db[data_collection]
    collection.insert(data)

def main():
    for page in tqdm(range(pages_number), desc='Total Processing'):
        res_scrape(url=url.format(category=category, limit=limit, offset=page*limit), headers=headers, proxies=proxies)

if __name__ == '__main__':
    limit = 35
    pages_number = 38
    data_collection = 'song_list_info_huayu'
    category='华语'
    main()
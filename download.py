import bs4 as bs
import sys
import urllib.request

import pytube
import argparse
import logging
import os

from PyQt5.QtWebEngineWidgets import QWebEnginePage 
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtCore import QUrl


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s::%(message)s', datefmt='%H:%M:%S')
logging = logging.getLogger(__name__)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser(description='kill me pls')
parser.add_argument('url', type=str)
parser.add_argument('--playlist', type=str2bool, help="Describe if url is yt playlist or single song.", default=False)
parser.add_argument('--audio', type=str2bool, help="Only audio?", default=False)

args = parser.parse_args()


class Page(QWebEnginePage): 
    def __init__(self, url): 
        self.app = QApplication(sys.argv) 
        QWebEnginePage.__init__(self) 
        self.html = '' 
        self.loadFinished.connect(self._on_load_finished) 
        self.load(QUrl(url)) 
        self.app.exec_() 
  
    def _on_load_finished(self): 
        self.html = self.toHtml(self.Callable) 
        logging.info('Load finished')
  
    def Callable(self, html_str): 
        self.html = html_str 
        self.app.quit() 
  
  
links = [] 
  
if args.playlist:
    def exact_link(link):
        vid_id = link.split('=')
        str = ""
        for i in vid_id[0:2]:
            str += i + "="

        str_new = str[0:len(str) - 1]
        index = str_new.find("&")

        new_link = "https://www.youtube.com" + str_new[0:index]
        return new_link

    page = Page(args.url)
    count = 0

    soup = bs.BeautifulSoup(page.html, 'html.parser')
    for link in soup.find_all('a', id='thumbnail', href=True):

        if count == 0:
            count += 1
            continue
        else:
            vid_src = link['href']
            new_link = exact_link(vid_src)
            links.append(new_link)
else:
    links.append(args.url)

for link in links:
    logging.info(f"Trying to download: {link}")
    try:
        yt = pytube.YouTube(link)
    except Exception as e:
        logging.debug(e)
        continue

    stream = yt.streams.filter(only_audio=args.audio).first()
    try: 
        stream.download(output_path=f"{os.path.abspath(os.getcwd())}/downloaded")
        logging.info(f"Downloaded: {link}")
    except Exception as e:
        logging.debug(e)
        logging.error(f"Some error in downloading: {link}")

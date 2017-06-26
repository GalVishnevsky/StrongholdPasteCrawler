import datetime
import json
import logging
import re
import threading

from flask import Flask, jsonify

import requests
from lxml import html

from model import Paste

# config logger
logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, filename='app.log',
                    format=logger_format)

logger = logging.getLogger(__name__)

# Tor proxy
proxies = {
    'http': 'http://127.0.0.1:8118',
    'https': 'http://127.0.0.1:8118',
}

BASE_URL = 'http://nzxj65x32vh2fkhk.onion/all?page=%s'

CHECK_TOR_URL = 'https://check.torproject.org'

TOR_CHECK = "This browser is configured to use Tor"

INTERVAL_FETCH = 60 * 4

app = Flask(__name__, static_url_path='')


@app.route("/db")
def db():
    """
    :return: db as json
    """
    with open('db.json') as data_file:
        return jsonify(json.loads(data_file.read()))


@app.route("/logs")
def log():
    with open('app.log') as data_file:
        return data_file.read().replace('\n', '<br>')


def crawl(page):
    """
    crawl on pastes site
    :param page: current page are fetch
    :return: continue running
    """

    stop = False
    url = BASE_URL % page

    logging.info('Fetching: %s' % url)

    res = requests.get(url, proxies=proxies)

    root = html.fromstring(res.content)

    pastes_xpath = "//section[@id='list']//div[@class='row' and position() < last()]"
    pastes_html = root.xpath(pastes_xpath)

    for paste_html in pastes_html[1:]:
        paste = Paste()
        try:
            link_xpath = ".//div[contains(@class,'pre-header')]//a[contains(text(),'Show paste')]"
            paste.link = paste_html.xpath(link_xpath)[0].attrib['href']

            paste.title = paste_html.xpath(".//div[contains(@class,'pre-header')]//h4")[
                0].text_content().strip()

            footer_node = paste_html.xpath(".//div[contains(@class,'pre-footer')]")[0]

            metadata_node = footer_node.xpath(".//div[contains(text(),'Posted by')]")[0]

            metadata_re = r'Posted by (.*?) at (.*?) UTC'
            metadata = re.findall(metadata_re, metadata_node.text_content())[0]

            paste.author = metadata[0].strip()

            date_string = metadata[1]

            paste.date = datetime.datetime.strptime(date_string, "%d %b %Y, %H:%M:%S")

            # Check if paste exist in db
            if paste.exist_post():
                stop = True
                break

            res_paste = requests.get(paste.link, proxies=proxies)

            root_paste = html.fromstring(res_paste.content)

            # Extract the raw paste
            raw_link = root_paste.xpath("//a[contains(text(),'Raw')]")[0].attrib['href']

            paste.content = requests.get(raw_link, proxies=proxies).text

            # Save the paste in db
            paste.save()
        except Exception:
            logging.exception("Paste: %s (%s)" % (paste.title, paste.link))
    return stop


def main():
    try:
        logger.info('Start fetching pastes')
        res_check_tor = requests.get(CHECK_TOR_URL, proxies=proxies)
        if TOR_CHECK in str(res_check_tor.content):
            logger.info('Connect to darknet!')
            # Running on all the pages
            for page in range(1, 41):
                stop = crawl(page)
                # If get to last paste
                if stop:
                    break
        else:
            logger.error('Not connect to darknet!')
        threading.Timer(INTERVAL_FETCH, main).start()
    except Exception:
        logging.exception("The program crash")


if __name__ == '__main__':
    threading.Thread(target=main).start()
    app.run(host='0.0.0.0', port=80, debug=False)

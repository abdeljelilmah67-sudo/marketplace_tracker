import re
import requests
import time
import logger
import html
import traceback
import config_handler

def get_differentiating_key():
    return "url"

def page_parser(request_delay, request_timeout):
    url_request_list = config_handler.read("urls.cfg", "ebay", delimiters=["\n"])

    item_info_list = []
    for request_url in url_request_list:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.7,ja;q=0.3',
                'Referer': 'https://www.ebay.com/sch/i.html?_fsrp=1&rt=nc&_nkw=wacom&_sop=10&LH_PrefLoc=2&_pgn=2&imm=1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Priority': 'u=0, i',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }
            page = requests.get(request_url, headers=headers, timeout=request_timeout).text
        except Exception:
            logger.error_log("eBay request failed. Request url: " + str(request_url), traceback.format_exc())
            continue

        listing_containers = re.findall(r"data-viewport=.*?</div></li>", page)
        for listing_container in listing_containers:
            item_info = {}
            url = re.findall(r"(?<=<a class=image-treatment href=)https://www.ebay.\w+/itm/\d+", listing_container)
            thumbnail = re.findall(r"https://i\.ebayimg\.com/images/g/.+?/s-l\d+\.\w+", listing_container)
            title = re.findall(r"(?<=<span class=\"su-styled-text primary default\">).*?(?=</span>)", listing_container)
            price = re.findall(r"(?<=<span class=\"su-styled-text primary bold large-1 s-card__price\">).*?(?=</span>)", listing_container)
            shipping = [*re.findall(r"(?<=<div class=\"s-card__attribute-row\"><span class=\"su-styled-text secondary large\">)\+.*? delivery(?=</span>)", listing_container), *re.findall(r"(?<=<span class=\"su-styled-text secondary large\">)Free delivery(?=</span>)", listing_container)]
            purchase_option = re.findall(r"(?<=<div class=s-card__attribute-row><span class=\"su-styled-text secondary large\">).*?(Buy It Now|or Best Offer)(?=</span>)", listing_container)
            bidcount = re.findall(r"(?<=<div class=s-card__attribute-row><span class=\"su-styled-text secondary large\">).*?bids?(?=</span>)", listing_container)

            if len(url) > 0:
                item_info["url"] = strip_excess_html(url[0])
            else:
                continue

            if len(thumbnail) > 0:
                item_info["thumbnail"] = strip_excess_html(thumbnail[0])
            else:
                item_info["thumbnail"] = ""

            if len(title) > 0:
                item_info["title"] = strip_excess_html(title[0])
            else:
                item_info["title"] = ""

            if len(price) == 1 and len(bidcount) == 0:
                item_info["buy_it_now_price"] = strip_excess_html(price[0])
                item_info["bidding_price"] = ""
            elif len(price) == 1 and len(bidcount) > 0:
                item_info["buy_it_now_price"] = ""
                item_info["bidding_price"] = strip_excess_html(price[0])
            elif len(price) == 2:
                item_info["buy_it_now_price"] = strip_excess_html(price[0])
                item_info["bidding_price"] = strip_excess_html(price[1])
            else:
                item_info["buy_it_now_price"] = ""
                item_info["bidding_price"] = ""

            if len(shipping) > 0:
                item_info["shipping"] = strip_excess_html(shipping[0])
            else:
                item_info["shipping"] = ""

            if len(purchase_option) > 0:
                item_info["purchase_option"] = strip_excess_html(purchase_option[0])
            else:
                item_info["purchase_option"] = ""

            if len(bidcount) > 0:
                item_info["bidcount"] = strip_excess_html(bidcount[0])
            else:
                item_info["bidcount"] = ""

            item_info_list.append(item_info)

        time.sleep(request_delay)

    return item_info_list

def strip_excess_html(string):
    return html.unescape(re.sub(r"<.*?>", "", string))
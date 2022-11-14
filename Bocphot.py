import json

import requests
from lxml import html


def fetch_html_response(url):
    headers = {
        "authority": "bocphot.club",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    response = requests.request("GET", url, headers=headers)

    return response


def peel_article(response):
    tree = html.fromstring(response.content.decode(response.encoding))
    peel_elements = tree.xpath('//div[@class="row"]//div[@class="col-12 mt-3"]//tbody//tr')

    peel_arr = []

    for peel_element in peel_elements:
        titles = peel_element.xpath('.//td[2]//a//text()')
        title = "".join(titles)
        shop_names = peel_element.xpath('.//td[1]//a//text()')
        shop_name = "".join(shop_names).strip()
        link_shops = peel_element.xpath('.//td[3]//a//@href')
        link_shop = "".join(link_shops)
        shop_phones = peel_element.xpath('.//td[4]//text()')
        shop_phone = "".join(shop_phones)
        link = peel_element.xpath('.//td[1]//a//@href')
        link_post = "".join(link)

        peel_arr.append({
            'title': title,
            'link_post': link_post,
            'shop_name': shop_name,
            'link_shop': link_shop,
            'shop_phone': shop_phone

        })

    return peel_arr


def peel_articles_detail(response):
    tree = html.fromstring(response.content.decode(response.encoding))

    img = tree.xpath('//div[@id="primary"]//div[@class="carousel-item"]//img//@src')
    content = tree.xpath('//div[@id="primary"]//form//div[@class="font-weight-400"]//p[1]//text()')

    return {
        'img': img,
        'content': content
    }


if __name__ == '__main__':
    i = 0

    file = open("Bocphot.json", "a+", encoding='utf-8')
    while True:
        i += 1
        url = 'https://bocphot.club/tim-kiem-shop-online/page/', str(i)

        ulrs = "".join(url)

        peel_response = fetch_html_response(url=ulrs)
        peel_articles = peel_article(peel_response)
        if not peel_articles:
            break

        for p_article in peel_articles:
            peel_response_detail = fetch_html_response(url=p_article["link_post"])
            peel_article_detail = peel_articles_detail(peel_response_detail)

            text = {"title": p_article["title"], "content": peel_article_detail["content"],
                    "link_post": p_article["link_post"],
                    "name_shop": p_article["shop_name"], "phone_number": p_article["shop_phone"],
                    "link_shop": p_article["link_shop"], "img": peel_article_detail["img"]}

            file.write(json.dumps(text, ensure_ascii=False) + '\n')

    file.close()

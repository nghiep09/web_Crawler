import json
import time
import asyncio
import requests
from lxml import html


def fetch_html_response(url):
    headers = {
        "authority": "phongchongluadao.vn",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/107.0.0.0 Safari/537.36 "
    }
    # TODO handle response when wanning robot

    count = 0
    while True:
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            tree = html.fromstring(response.text)
            robot = tree.xpath(
                '//div[@id="__layout"]//div[@class="yt-issue-view"]//div[@class="yt-issue-layout '
                'vertical-center"]//img//@src')
            if robot:
                time.sleep(2)
                count += 1
                if count >= 5:
                    continue
            else:
                break

    return response


async def parse_article(response):
    tree = html.fromstring(response.content.decode(response.encoding))
    elements = tree.xpath('//div[@class="app__view"]//div[@class="yt-page__block"]//div[@class="yt-dropzone"]')

    articles = []

    for element in elements:
        title = element.xpath('.//span[@class="yt-issue-summary"]//text()')
        link_posts = element.xpath('.//span//a[@class="ring-link ring-link_pseudo yt-issue-title '
                                   'yt-issues-issue__summary"]//@href')
        if not link_posts:
            continue

        link_post = 'https://phongchongluadao.vn', link_posts[0]

        articles.append({
            'title': title,
            'link_post': "".join(link_post)
        })

    return articles


async def parse_article_detail(response):
    tree = html.fromstring(response.content.decode(response.encoding))

    STK_bank = tree.xpath('//tbody//tr[3]//span[@class="ring-link ring-link_pseudo"]//text()')
    phone_number = tree.xpath('//tbody//tr//span//a[not(@target)]//text()')
    link_MXH = tree.xpath('//tbody//tr//a[@target="_blank"]//@href')
    img = tree.xpath('//div[@id="__layout"]//div[@class="yt-issue-view"]//p//img//@src')
    createdDate = tree.xpath('//div[@id="__layout"]//div//span[2]//span//span[3]//@title')
    contents = tree.xpath('//div[@id="__layout"]//div[@class="body"]//p[1]//text()')

    content = "".join(contents)

    return {

        'STK_bank': STK_bank,
        'phone_number': phone_number,
        'link_MXH': link_MXH,
        'img': img,
        'createdDate': createdDate,
        'content': content
    }


if __name__ == '__main__':
    i = 0
    err_html = ""
    file = open("PCluadao.json", "w+", encoding='utf-8')
    while True:

        i += 1

        urls = 'https://phongchongluadao.vn/lua-dao?p=', str(i)

        PCLD_response = fetch_html_response(url="".join(urls))
        elements = asyncio.run(parse_article(PCLD_response)
)
        if not elements:
            break

        for ele in elements:
            PCLD_response_detail = fetch_html_response(url=ele['link_post'])
            elements_detail = asyncio.run(parse_article_detail(PCLD_response_detail))

            print(elements_detail)

            text = {"title": ele["title"], "link_post": ele["link_post"],
                    "phone_number": elements_detail["phone_number"],
                    "STK_bank": elements_detail["STK_bank"], "link": elements_detail["link_MXH"],
                    "img": elements_detail["img"], "createdDate": elements_detail["createdDate"],
                    "content": elements_detail["content"]}

            print(text)
            print('\n')
            file.write(json.dumps(text, ensure_ascii=False) + '\n')

    file.close()

import json
import re
from lxml import html

import requests

url = "https://api.antiscam.vn/api/Post/GetPosts"

i = 0

type_post = {
    4: "phone_number",
    6: "Bank_acc_name",
    7: "Bank_acc",
    8: "Website",
    9: "Address",
    10: "Email",
    12: "HovaTen",
    13: "Momo",
    14: "Facebook",
}

while True:

    i += 1
    payload = json.dumps({
        "searchModel": {
            "currentPage": i,
            "searchText": "",
            "typeId": 0,
            "sortType": 1,
            "kindOfValue": 2,
            "pageSize": 10,
            "total": 0,
            "totalPage": 0,
            "isMine": False
        }
    })
    headers = {
        'content-type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    articles = []
    file = open("Antiscam.json", "a+", encoding='utf-8')

    if response.status_code == 200:

        for record in response.json().get("data").get("data"):
            result = {}
            for tp in record.get('typePosts'):
                obj_data = tp.get('object')
                type_id = tp.get('typeId')
                key_obj = type_post.get(type_id)
                if not result.get(key_obj):
                    result[key_obj] = []

                result[key_obj].append(obj_data)

            # TODO continue handle

            articles.append({
                'title': record.get('title'),
                'type_posts': result,
                'createdDate': record.get('createdDate')
            })

        for ar in articles:
            file.write(json.dumps(ar, ensure_ascii=False) + '\n')

        if not articles:
            break

    file.close()

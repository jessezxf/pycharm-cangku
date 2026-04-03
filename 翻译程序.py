from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests

# ========== （语言映射）==========
LANG_NAMES = {
    "cn": "中文",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "it": "意大利语",
    "pt": "葡萄牙语",
    "ar": "阿拉伯语",
    "th": "泰语",
    "vi": "越南语"
}
# ===========================================

'''
1.机器翻译2.0，请填写在讯飞开放平台-控制台-对应能力页面获取的APPID、APISecret、APIKey。
 2.目前仅支持中文与其他语种的互译，不包含中文的两个语种之间不能直接翻译。
 3.翻译文本不能超过5000个字符，即汉语不超过15000个字节，英文不超过5000个字节。
 4.此接口调用返回时长上有优化、通过个性化术语资源使用可以做到词语个性化翻译、后面会支持更多的翻译语种。
'''
APPId = "57723fab"
APISecret = "MDIyZGU4YjQ4MzM3ODNiOWNlMmFhMzY2"
APIKey = "27cce8384e5cc6f5448e206edbbb1a51"
# 术语资源唯一标识，请根据控制台定义的RES_ID替换具体值，如不需术语可以不用传递此参数
RES_ID = "its_en_cn_word"
# 翻译原文本内容
# TEXT = input("输入要翻译的内容：")


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(self, host, path, schema):
        self.host = host
        self.path = path
        self.schema = schema
        pass



def get_lang_name(lang_code):
    """获取语言的中文名称"""
    return LANG_NAMES.get(lang_code, lang_code)


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="POST", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    # print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    # print(signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    # print(authorization_origin)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)


print("翻译程序已启动xxxxxxxx，输入 'q' 退出\n")

while True:

    target_lang = "en"  # 默认英语
    TEXT = input("请输入要翻译的文本（输入“q”退出）: ")

    if TEXT.lower() == 'q':
        print("再见！")
        break

    if not TEXT.strip():
        print("请输入有效的文本\n")
        continue

    # 原来的翻译代码放在这里
    url = 'https://itrans.xf-yun.com/v1/its'

    body = {
        "header": {
            "app_id": APPId,
            "status": 3,
            "res_id": RES_ID
        },
        "parameter": {
            "its": {
                "from": "cn",
                "to": "en",
                "result": {}
            }
        },
        "payload": {
            "input_data": {
                "encoding": "utf8",
                "status": 3,
                "text": base64.b64encode(TEXT.encode("utf-8")).decode('utf-8')
            }
        }
    }

    request_url = assemble_ws_auth_url(url, "POST", APIKey, APISecret)

    headers = {'content-type': "application/json", 'host': 'itrans.xf-yun.com', 'app_id': APPId}
    # print(request_url)


    # response = requests.post(request_url, data=json.dumps(body), headers=headers)
    # print(headers)
    # print(response)
    # print(response.content)
    # tempResult = json.loads(response.content.decode())
    # print('text字段Base64解码后=>' + base64.b64decode(tempResult['payload']['result']['text']).decode())


    response = requests.post(request_url, data=json.dumps(body), headers=headers)

    if response.status_code == 200:
        tempResult = json.loads(response.content.decode())

        # 检查是否成功
        if tempResult.get("header", {}).get("code") == 0:
            # 解码获取翻译结果
            text_base64 = tempResult.get("payload", {}).get("result", {}).get("text", "")
            if text_base64:
                decoded = json.loads(base64.b64decode(text_base64).decode('utf-8'))
                src_text = decoded.get("trans_result", {}).get("src", "")
                dst_text = decoded.get("trans_result", {}).get("dst", "")

                # 输出格式：原文和译文
                print("-" * 50)
                print(f"📖 原文({body['parameter']['its']['from']}): {src_text}")
                print(f"📝 译文({body['parameter']['its']['to']}): {dst_text}")
                print("-" * 50)
            else:
                print("❌ 没有找到翻译结果")
        else:
            error_code = tempResult.get("header", {}).get("code")
            error_msg = tempResult.get("header", {}).get("message")
            print(f"❌ API错误 [{error_code}]: {error_msg}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")

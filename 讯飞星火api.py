import requests
#juIOWjehPFefnDyiSgGz:zwjRBFdPXFSfSklRKcvG
# 替换成你的 API Password
API_PASSWORD = "juIOWjehPFefnDyiSgGz:zwjRBFdPXFSfSklRKcvG"

url = "https://spark-api-open.xf-yun.com/v1/chat/completions"


headers = {
    "Authorization": f"Bearer {API_PASSWORD}",
    "Content-Type": "application/json"
}

data = {
    "model": "4.0Ultra",
    "messages": [
        {"role": "user",
         "content": "把'Hello'翻译成中文"}
    ],
    "max_tokens": 100
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"错误码: {response.status_code}")
    print(response.text)
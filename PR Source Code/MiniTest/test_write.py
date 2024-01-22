#!/usr/bin/env python3

import requests
import time

global url
url = "https://ddos-control-panel.de.r.appspot.com"

# 登录并获取token
def authenticate():
    global url
    credentials = {"username": "caonima", "password": "123"}
    response = requests.post(url+"/authenticate", json=credentials)
    if response.status_code == 200:
        print("Log in successful!")
        return response.json()['token']  # 假设token是返回JSON中的一个字段
    else:
        raise ValueError("无法认证，状态码：", response.status_code)

# 获取信息
def get_info(token):
    global url
    headers = {'Authorization': f'Bearer {token}'}  # 将token加入请求头中
    response = requests.get(url+"/get-info", headers=headers)
    print(token)
    
    if response.status_code == 200:
        data = response.json()
        # ... 根据获取的数据执行相关操作
        print(f"执行程序，数据：{data}")
    elif response.status_code == 403:
        print("没有权限访问资源，等待...")
        time.sleep(5)  # 等待5秒后重试
        get_info(token)  # 使用相同的token重试
    else:
        print(f"HTTP错误：{response.status_code}")

# 主程序
def main():
    try:
        token = authenticate()  # 登录并获取token
        get_info(token)  # 使用token获取信息
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误：{e}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()

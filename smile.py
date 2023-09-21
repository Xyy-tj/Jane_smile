from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import itertools
import requests
from concurrent.futures import ThreadPoolExecutor
import ipapi
from translate import Translator
import json

# 没用不用看
def translate_content_ch(city_en, org_en):
    # 实现英文转中文
    translator=Translator(to_lang='chinese')
    city = translator.translate(city_en)
    org = translator.translate(org_en)
    return city + org

# 没用不用看
def check_proxy(protocol, ip, port, available_proxies):
    try:
        proxy = {
            protocol: f'{protocol}://{ip}:{port}'
        }
        response = requests.get('https://www.baidu.com', proxies=proxy, timeout=5)
        if response.status_code == 200:
            location = ipapi.location(ip)  # 获取IP地址的位置信息
            city_en = location.get('city', '')
            org_en = location.get('org', '')
            result = translate_content_ch(city_en, org_en)
            print('\033[1;32m' + f'{proxy} is available, location: {result}' + '\033[0m')
            available_proxies.append(f'http://{ip}:{port}')  # 将可用的代理服务器IP添加到共享列表中
    except:
        print('\033[1;31m' + f'{proxy} is not available' + '\033[0m')

# 没用不用看
def get_proxy_list():
    proxies = ['182.34.35.87:9999',
               '182.140.244.163:8118',
               '113.121.37.249:9999',
               '113.124.85.37:9999',
               '183.247.221.119:30001',
               '113.121.21.231:9999',
               '111.3.102.207:30001',
               ]  # 代理服务器列表
    
    available_proxies = []  # 可用的代理服务器IP列表
    with ThreadPoolExecutor(max_workers=10) as executor:  # 创建最大并发数为10的线程池
        for proxy in proxies:
            try:
                protocol, address = proxy.split('://')  # 获取协议和地址
            except ValueError:
                protocol, address = 'http', proxy
            ip, port = address.split(':')  # 获取IP地址和端口号
            executor.submit(check_proxy, protocol, ip, port, available_proxies)  # 提交任务到线程池
    return available_proxies  # 返回可用的代理服务器IP列表

def get_proxy(headers):
    #API_url为ip代理池的API
    API_url = 'http://get.3ip.cn/dmgetip.asp?apikey=37c26b33&pwd=c15287e1366c93e0c5f0ccf7e645112c&getnum=1&httptype=2&geshi=2&fenge=1&fengefu=&Contenttype=1&operate=2'
    if not API_url:
        print('出错了:请从www.3ip.cn生成api地址')
        proxy = {}
        return proxy
    try:
        aaa = requests.get(API_url, headers=headers).text
        aaa_json = json.loads(aaa)
        if not aaa_json or aaa_json['code'] != 0:
            proxy = {}
        else:
            proxy_host = aaa_json['data'][0]['ip'] + ':' + str(aaa_json['data'][0]['port'])
            proxy_city = aaa_json['data'][0]['city']
            print('代理IP为：'+proxy_host)
            proxy = 'socks5://' + proxy_host
    except Exception as e:
        print('获取代理IP失败：', e)
        proxy = {}
    return proxy, proxy_city


if __name__ == '__main__':
    # 读取Excel文件，注意修改文件路径，获取第二列，去掉表头组成列表
    df = pd.read_excel('0919.xlsx')
    column_oid = df.iloc[:, 0].tolist()
    column2 = df.iloc[:, 1].tolist()
    # 验证是否读取成功
    for i in column2:
        print(i)

    ls_new_df = []
    # 从Excel文件中读取数据，然后在网页中搜索
    for idx, smile_id_i in enumerate(column2):
        # 伪造浏览器UA标识
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)'}
        proxy, proxy_city = get_proxy(headers)
        
        if not proxy:
            print('获取代理失败,停止继续执行')
        else:
            print('\033[1;32m'+"本轮查询使用的跳板代理服务器：{}\t \033[1;33m所在地区：{}".format(proxy, proxy_city)+'\033[0m')
            edge_options = webdriver.EdgeOptions()
            edge_options.add_argument('--proxy-type=http')
            edge_options.add_argument(f' --proxy-server={proxy}')
            one_driver = webdriver.Edge(options=edge_options)
            # 注释掉的代码用于访问ip.cn测试ip所在的地理位置
            # try:
            #     one_driver.get(r'https://www.ip.cn/')
            #     one_driver.implicitly_wait(10)
            #     continue
            # except Exception as e:
            #     print(e)
            try:
                one_driver.get(r'http://www.swissadme.ch/')
                one_driver.implicitly_wait(10)
                
                search_box = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[4]/form/textarea")
                print(smile_id_i)
                search_box.clear()
                sleep(0.5)
                search_box.send_keys(smile_id_i)

                search_button = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[4]/form/div/input[3]")
                search_button.click()
                one_driver.implicitly_wait(10)

                result = [column_oid[idx], smile_id_i,]
                # 取出需要的结果
                for i in list(range(11, 28)):
                    # search_text = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[11]/div[1]/div[4]/table/tbody/tr["+str(i)+"]")
                    search_text= one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[11]/div[1]/div[4]/table/tbody/tr["+str(i)+"]")
                    one_driver.implicitly_wait(3)
                    result.append(search_text.text.strip())
                    
                result = [s.split('\n')[-1] for s in result]
                result = [x for x in result if x not in ['Pharmacokinetics', 'Druglikeness']]
                ls_new_df.append(result)
                one_driver.close()
            except Exception as e:
                print(e)
                ls_new_df.append([smile_id_i, 'No result'])
                
            # 休眠一段时间，防止网页反爬虫 
            rand_sleep = np.random.rand() * 5
            sleep(rand_sleep)
            print('\033[1;34m'+"随机休眠时间(s)：{}".format(rand_sleep)+'\033[0m \n -------------------------------------------------------\n')
    # df_out = pd.concat(pd.DataFrame(ls_new_df), axis=0)
    df_out = pd.DataFrame(ls_new_df)
    # 将结果保存到Excel文件中
    with pd.ExcelWriter("result.xlsx", engine="openpyxl") as writer:
        df_out.to_excel(writer, sheet_name="Output", index=False)
            
    print(result)
    sleep(1)
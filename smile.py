from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import itertools

# 读取Excel文件，注意修改文件路径，获取第二列，去掉表头组成列表
df = pd.read_excel('0919.xlsx')
column_oid = df.iloc[:, 0].tolist()
column2 = df.iloc[:, 1].tolist()
# 验证是否读取成功
for i in column2:
    print(i)

ls_new_df = []
# 从Excel文件中读取数据，然后在网页中搜索
proxy_list = ["","http://124.222.246.189:7890", "socks5://154.12.95.148:1080"]
proxy_list = ["", "socks5://154.12.95.148:1080"]
proxy_cycle = itertools.cycle(proxy_list)

for idx, smile_id_i in enumerate(column2):
    PROXY = next(proxy_cycle)
    print('\033[1;32m'+"本轮查询使用的跳板代理服务器：{}".format(PROXY)+'\033[0m')
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument('--proxy-server=%s' % PROXY)
    one_driver = webdriver.Edge(options=edge_options)
    try:
        one_driver.get(r'https://www.ip.cn/')
        one_driver.implicitly_wait(10)

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
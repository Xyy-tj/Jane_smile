# Author: ZyFan
# Data: 2023/09/07
# Script: SMILE Target Prediction for Jane

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os 
import time
try:
    import pretty_errors
except:
    pass

# 读取Excel文件，注意修改文件路径，获取第二列，去掉表头组成列表
df = pd.read_excel('smile.xlsx')
column_oid = df.iloc[:, 0].tolist()
column2 = df.iloc[:, 1].tolist()
# 验证是否读取成功
for i in column2:
    print(i)

# 浏览器设置，默认下载路径
options = webdriver.EdgeOptions()
prefs = {"download.default_directory": "D:\\GitHub\\Jane_smile\\downloads\\", "download.prompt_for_download": False}
options.add_experimental_option("prefs", prefs)
one_driver = webdriver.Edge(options=options)

ls_new_df = []
# 从Excel文件中读取数据，然后在网页中搜索
for idx, smile_id_i in enumerate(column2):
    
    download_path = r"D:\\GitHub\\Jane_smile\\downloads\\"
    old_file_name = 'SwissTargetPrediction.xlsx'
    new_file_name = "{}.xlsx".format(column_oid[idx])
    old_file_path = download_path + old_file_name
    new_file_path = download_path + new_file_name

    # 如果文件已经存在，则跳过
    if os.path.exists(new_file_path):
        continue
    # 如果文件不存在，则下载，使用try语句避免下载失败
    try:   
        print('\033[1;34m' + "{} is begining, smile: {}".format(column_oid[idx], smile_id_i) + '\033[0m')
        one_driver.get(r'http://swisstargetprediction.ch/')
        # one_driver.implicitly_wait(10)
        wait = WebDriverWait(one_driver, 20) # 指定最长等待时间为20秒
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[3]/div[2]/div/form/div[1]/div[3]/input')))
        
        search_box.clear()
        search_box.send_keys(smile_id_i)
        search_box.click()

        search_button = one_driver.find_element(by=By.ID, value="submitButton")
        one_driver.implicitly_wait(15)
        search_button.click()
        download_button = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[4]/div/button[3]")
        one_driver.implicitly_wait(15)
        download_button.click()

        while not os.path.exists(old_file_path):
            time.sleep(1) # 等待1秒钟再次检查是否存在
        sleep(0.5)
        os.rename(old_file_path, new_file_path)
        print('\033[1;32m' + "Successfully Downloaded: {}".format(column_oid[idx]) + '\033[0m')
    except Exception as e:
        print(e)
        print('\033[1;31m' + "Failed Downloaded: {}".format(column_oid[idx]) + '\033[0m')
        
    sleep(0.5)
sleep(0.5)
one_driver.quit()

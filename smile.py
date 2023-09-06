from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

# 读取Excel文件，注意修改文件路径，获取第二列，去掉表头组成列表
df = pd.read_excel('smile.xlsx')
column_oid = df.iloc[:, 0].tolist()
column2 = df.iloc[:, 1].tolist()
# 验证是否读取成功
for i in column2:
    print(i)


driverfile_path = r'msedgedriver.exe'
one_driver = webdriver.Edge(executable_path=driverfile_path)

one_driver.get(r'http://www.swissadme.ch/')
one_driver.implicitly_wait(10)

ls_new_df = []
# 从Excel文件中读取数据，然后在网页中搜索
for idx, smile_id_i in enumerate(column2):
    search_box = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[4]/form/textarea")
    print(smile_id_i)
    search_box.clear()
    search_box.send_keys(smile_id_i)

    search_button = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[4]/form/div/input[3]")
    search_button.click()
    one_driver.implicitly_wait(10)

    result = [column_oid[idx], smile_id_i,]
    # 取出需要的结果
    try:
        for i in list(range(11, 28)):
            # search_text = one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[11]/div[1]/div[4]/table/tbody/tr["+str(i)+"]")
            search_text= one_driver.find_element(by=By.XPATH, value="/html/body/div[1]/div[3]/div[2]/div/div[11]/div[1]/div[4]/table/tbody/tr["+str(i)+"]")
            one_driver.implicitly_wait(3)
            result.append(search_text.text.strip())
            
        result = [s.split('\n')[-1] for s in result]
        result = [x for x in result if x not in ['Pharmacokinetics', 'Druglikeness']]
        ls_new_df.append(result)
    except Exception as e:
        print(e)
        ls_new_df.append([smile_id_i, 'No result'])
# df_out = pd.concat(pd.DataFrame(ls_new_df), axis=0)
df_out = pd.DataFrame(ls_new_df)
# 将结果保存到Excel文件中
with pd.ExcelWriter("result.xlsx", engine="openpyxl") as writer:
    df_out.to_excel(writer, sheet_name="Output", index=False)
        
print(result)
sleep(1)
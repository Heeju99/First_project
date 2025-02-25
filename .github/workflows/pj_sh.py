import sqlite3
import pandas as pd
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pyautogui

def create_db():
    conn = sqlite3.connect('dak_products_20250223_5.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_url TEXT
            brand TEXT,
            name TEXT,
            price TEXT,
            protein TEXT,
            calories TEXT,
            stars TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(df):
    conn = sqlite3.connect('dak_products_20250223_5.db')
    df.to_sql('products', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

dak_name_list = [] 
dak_price_list = []
dak_sales_list = []
dak_brand_list = []
dak_star_list = []
dak_protein_list = [] 
dak_cal_list = []
dak_img_list = []

# Selenium으로 웹 크롤링
url = "https://www.rankingdak.com/product/list?depth1=R019"
driver = wb.Chrome()
driver.get(url)
driver.maximize_window()
time.sleep(0.5)
pyautogui.moveTo(1570,670)
pyautogui.click()
pyautogui.moveTo(1570,785)
pyautogui.click()
time.sleep(0.5)
cnt = 0
n = 8
body_dak = driver.find_element(By.TAG_NAME, "body")
for _ in range(n):
    body_dak.send_keys(Keys.END)
    time.sleep(0.5)
time.sleep(1)

for i in range(30):
    time.sleep(2)
    print(cnt)
    body_dak2 = driver.find_element(By.TAG_NAME, "body")
    for _ in range(10):
        body_dak2.send_keys(Keys.PAGE_DOWN)
        
    time.sleep(1)

    try:
        dak_img = driver.find_elements(By.CLASS_NAME, "lozad")
        img_url = dak_img[i].get_attribute("src")
        dak_img_list.append(img_url)
            
        dak_img = driver.find_elements(By.CLASS_NAME, "lozad")
        dak_img[i].click()
        time.sleep(1)

        # 이름 가져오기
        name = driver.find_element(By.CLASS_NAME, "goods-tit")
        names = name.text
        dak_brands = names.split(" ")[0].replace('[', '').replace(']', '')
        dak_names = ' '.join(names.split(" ")[1:])
            
        # 가격 가져오기
        price = driver.find_element(By.CSS_SELECTOR, "div.option")
        prices = price.text
        dak_price = ""
        is_true = False
        for y in range(len(prices)):
            if(prices[y] == ":"):
                is_true = True
            elif(prices[y] == "~"):
                break
            elif(is_true and prices[y].isdigit()):
                dak_price += prices[y]

        dak_price += "원"
            
        # 별점 & 후기 개수 가져오기
        star = driver.find_element(By.CLASS_NAME, "score")
        stars = star.text

        num = driver.find_element(By.CSS_SELECTOR, "a.num")
        stars += num.text      

        try:
            protein = driver.find_element(By.CSS_SELECTOR, "tr.ingredient_prod_table_bot > td:nth-of-type(2)")
            proteins = protein.text
        except:
            proteins = "N/A" 
        try:
            cal = driver.find_element(By.CSS_SELECTOR, "tr.ingredient_prod_table_bot > td:nth-of-type(1)")
            cals = cal.text
        except:
            cals = "N/A"

        dak_name_list.append(dak_names)
        dak_price_list.append(dak_price)
        dak_brand_list.append(dak_brands)
        dak_protein_list.append(proteins)
        dak_cal_list.append(cals)
        dak_star_list.append(stars)
        cnt += 1
        driver.back()
    except:
        print("품절된 제품이 있습니다. 다음 제품으로 넘어갑니다.")
        element = driver.find_element(By.TAG_NAME, "body")  
        element.send_keys(Keys.ENTER)
        dak_name_list.append("N/A")
        dak_brand_list.append("N/A")
        dak_price_list.append("N/A")
        dak_protein_list.append("N/A")
        dak_cal_list.append("N/A")
        dak_star_list.append("N/A")
        continue  

d_dic = {"이름": dak_name_list,
         "브랜드": dak_brand_list,
         "가격": dak_price_list,
         "단백질": dak_protein_list,
         "칼로리": dak_cal_list,
         "별점": dak_star_list,
         "이미지_URL": dak_img_list}

df = pd.DataFrame(d_dic)

create_db() 
save_to_db(df)

conn = sqlite3.connect("dak_products_20250223_5.db")  
sql = "SELECT * FROM products" 
df = pd.read_sql(sql, conn)
print(df) 

driver.quit()

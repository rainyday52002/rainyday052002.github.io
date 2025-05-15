
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import pandas as pd

#%% 樂譜爬蟲函式（模仿書籍版本）
def scrape_sheet_data():
    time.sleep(1)
    
    # 抓取每張樂譜卡片
    items = driver.find_elements(By.CLASS_NAME, "OAIWc")

    for item in items:
        # 標題
        try:
            title_element = item.find_element(By.CLASS_NAME, "csb5I")
            title = title_element.text.strip()
        except:
            title = "無"

        # 星星數（幾個星形圖示）
        stars = len(item.find_elements(By.CLASS_NAME, "Dj5dM"))

        # 投票數
        try:
            vote_element = item.find_element(By.CSS_SELECTOR, "div.S7NhW > span")
            votes = vote_element.text.strip()
        except:
            votes = "無"

        # 額外資訊（頁數、長度、觀看數）
        try:
            info_element = item.find_element(By.CSS_SELECTOR, "span.AZHap")
            info = info_element.text.strip()
        except:
            info = "無"

        # 整合資訊（模仿誠品書局格式）
        data_list.append({
            "標題": title,
            "星星數": stars,
            "投票數": votes,
            "資訊": info,
        })

#%% 啟動瀏覽器並搜尋 animenz 樂譜
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://musescore.com/")
driver.maximize_window()
time.sleep(2)

# 搜尋 animenz
search_box = driver.find_element(By.CSS_SELECTOR, 'input.bkmfh.NCQLn.FJVtZ')
search_box.send_keys("animenz")
search_box.send_keys(Keys.ENTER)

# 模擬滾動頁面
data_list = []
count = 0

while count < 3:
    time.sleep(2)
    scrape_sheet_data()
    
    try:
        # 找下一頁按鈕（根據 aria-label="Next"）
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[isnext="true"]')
        if next_button.is_enabled():
            next_button.click()
            count += 1
            time.sleep(3)
        else:
            break
    except (NoSuchElementException, ElementNotInteractableException):
        print("沒有下一頁了或按鈕無法點擊")
        break


#%% 印出前幾筆結果
for i in range(min(20, len(data_list))):
    name = data_list[i]["標題"]
    stars = data_list[i]["星星數"]
    votes = data_list[i]["投票數"]
    print(f"[標題 : {name} -> {stars} | {votes}]")

#%% 關閉瀏覽器
driver.quit()

#%% 輸出 CSV
df = pd.DataFrame(data_list)
df.to_csv("animenz_樂譜搜尋結果.csv", index=False, encoding="utf-8-sig")

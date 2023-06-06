import time
from io import BytesIO
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import pandas as pd
from PIL import Image


# загрузка таблицы
url = 'https://docs.google.com/spreadsheets/d/1aUnWpG35KpxSQeCGJ3fPcyM0BwJsvshTZWjXZkmGeQE/export?format=csv'
df = pd.read_csv(url)

# создание списка городов и штатов
cities = []

for _, row in df.iterrows():
    urls = row[3].split('\n')
    if urls != ['-']:
        city_data = {'state': row[0], 'district': row[1], 'city': row[2], 'urls': urls}
    else:
        city_data = {'state': row[0], 'district': row[1], 'city': row[2], 'urls': []}
    cities.append(city_data)

for i in cities:
    print(i)

# папка, в которую будут сохраняться изображения
image_folder = 'images'

# создаем папку, если она не существует
if not os.path.exists(image_folder):
    os.makedirs(image_folder)
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver_path = '/chromedriver.exe'
browser = webdriver.Chrome(executable_path=driver_path, options=options)

# проходим по списку городов и скачиваем изображения
for city in cities:
    try:
        state_folder = os.path.join(image_folder, city['state'])
        if not os.path.exists(state_folder):
            os.makedirs(state_folder)

        if city['district'][0] != '-':
            district_folder = os.path.join(state_folder, city['district'])
            if not os.path.exists(district_folder):
                os.makedirs(district_folder)
            city_folder = os.path.join(district_folder, city['city'])
            if not os.path.exists(city_folder):
                os.makedirs(city_folder)
        else:
            city_folder = os.path.join(state_folder, city['city'])
            if not os.path.exists(city_folder):
                os.makedirs(city_folder)


        c = 0
        # загружаем страницу с картой
        for i in city['urls']:
            url = i
            browser.get(url)
            time.sleep(5)
            try:
                buttons = browser.find_elements(By.TAG_NAME, 'button')
                for button in buttons:
                    if 'Принять все' in button.text or 'Accept all' in button.text:
                        button.click()
                        break
            except:
                pass
            time.sleep(10)
            print(url)
            buttons = browser.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                if 'Все' in button.text or 'Фото' in button.text or 'Photo' in button.text:
                    time.sleep(1)
                    browser.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(1)
                    button.click()
                    break

            time.sleep(15)
            # получаем все изображения на странице
            saved_urls = set()
            elements = []
            for i in range(1000):
                try:
                    div_element = browser.find_element(By.XPATH, '//div[@class="lXJj5c Hk4XGb "]')
                    browser.execute_script("arguments[0].scrollIntoView();", div_element)
                    time.sleep(2)
                except:
                    if i == 0:
                        browser.refresh()
                    else:
                        print('dsafffffffffffffffffff\nasfasdfffffff\nasdfffffffffffffff\nasdfffff\nadsfdsafdsaf')
                        break
            time.sleep(5)
            elements += (browser.find_elements(By.CSS_SELECTOR, '*[style*="background-image"]'))
            for element in elements:
                style = element.get_attribute('style')
                if 'url("' in style:
                    url = str(style.split('url("')[1].split('")')[0])
                    url = url[:url.find('=')] + '=s0'
                    # проверяем, что ссылка на фотографию не дублируется
                    if url not in saved_urls:
                        try:
                            response = requests.get(url)
                            img = Image.open(BytesIO(response.content))
                            file_ext = '.' + response.headers['content-type'].split('/')[-1]
                            if city["district"] != '-':
                                file_name = f'{city["state"].lower()}_{city["district"].lower()}_{city["city"].lower()}_{c}{file_ext}'
                            else:
                                file_name = f'{city["state"].lower()}_{city["city"].lower()}_{c}{file_ext}'
                            c += 1
                            file_path = os.path.join(city_folder, file_name)
                            with open(file_path, 'wb') as f:
                                f.write(response.content)
                            # добавляем ссылку на фотографию в множество
                            saved_urls.add(url)
                            print(1324444432142413421343214231432)
                        except:
                            pass

                    print(url)
    except Exception as e:
        print(e)

        # закрываем браузер
browser.quit()
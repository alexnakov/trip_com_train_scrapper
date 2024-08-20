from datetime import datetime, timedelta
from firebase_admin import credentials, firestore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
import firebase_admin
import asyncio
import json 
import os
import traceback

now = datetime.now()
selected_date = now.replace(hour=22, minute=0, second=0, microsecond=0) + timedelta(days=1)

date_str = selected_date.strftime(f'%Y-%m-%d')
trip_com_q_string = f'https://uk.trip.com/trains/list?departurecitycode=GB2278&arrivalcitycode=GB1594&departurecity=Sheffield&arrivalcity=London%20(Any)&departdate={date_str}&departhouript=22&departminuteipt=00&scheduleType=single&hidadultnum=1&hidchildnum=0&railcards=%7B%22YNG%22%3A1%7D&isregularlink=1&biztype=UK&locale=en-GB&curr=GBP'

def find_elements(selector, query):
    """ Tries to find an element within 15 secs and returns it. """
    attempts = 0
    while attempts < 10:
        try:
            return WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((selector, query)))
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
            attempts += 1
            time.sleep(1)
    return "Could not find element you were looking for"
           
def decline_cookies():
    try:
        decline_btn = find_elements(By.CLASS_NAME, 'cookie-banner-btn-more')[0]
        decline_btn.click()
    except NoSuchElementException:
        print('No cookie banner was found')

def get_last_time_element():
    take_screenshot()
    attempts = 0
    while attempts < 10:
        try:
            all_h4s = find_elements(By.TAG_NAME, 'h4')
            return_list = list(filter(lambda el: ':' in el.text, all_h4s))
            return return_list[-2]
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
            print(f'stale exception #{attempts} in get_last_time_element() occured')
        finally:
            if attempts > 0:
                print('stale exception for get_last_time_element() is now clear')

def get_times():
    take_screenshot()
    attempts = 0
    while attempts < 10:
        try:
            all_h4s = find_elements(By.TAG_NAME, 'h4')
            return_list = list(map(lambda x:x.text, list(filter(lambda el: ':' in el.text, all_h4s))))
            return return_list[::2] 
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
            print(f'stale exception #{attempts} in get_times() occured')
        finally:
            if attempts > 0:
                print('stale exception for get_times() is now clear')

def get_prices():
    take_screenshot()
    attempts = 0
    while attempts < 10:
        try:
            all_spans = find_elements(By.TAG_NAME, 'span')
            return_list = list(map(lambda x:x.text, list(filter(lambda el: '£' in el.text and el.value_of_css_property('color')=='rgba(15, 41, 77, 1)', all_spans))))
            return return_list
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
            print(f'stale exception #{attempts} in get_prices() occured')
        finally:
            if attempts > 0:
                print('stale exception for get_prices() is now clear')

def click_next_btn():
    take_screenshot()
    attempts = 0
    while attempts < 10:
        try:
            all_divs = find_elements(By.TAG_NAME, 'div')
            btn_as_list = list(filter(lambda el: 'View later trains' in el.text and len(el.text) == 17, all_divs))
            if len(btn_as_list) == 0:
                pass
            else:
                btn_as_list[0].click()
                attempts = 0
                break
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
            print(f'stale exception #{attempts} in click_next_btn() occured')
        finally:
            if attempts > 0:
                print('stale exception for click_next_btn() is now clear')
                break

def write_to_txt_file(hour,price):
    with open('real_data.txt','a') as file:
        file.write(f'{hour},{price}\n')

def count_lines_in_txt_file():
    filename = 'real_data.txt'
    with open(filename, 'r') as file:
        line_count = sum(1 for line in file)
    return line_count

def take_screenshot():
    files = os.listdir('./screenshots')          
    driver.save_screenshot(rf'./screenshots/{datetime.now()}.png')
    
    if len(files) > 7:
        sorted_files = sorted(os.listdir('./screenshots').copy())
        file_path = os.path.join('./screenshots', sorted_files[0])
        os.remove(file_path)

def setup_data_file():
    try:
        os.remove('real_data.txt')
    except:
        pass 

def scroll_to_next_btn(action_chains):
    last_time_element = get_last_time_element()
    take_screenshot()
    action_chains.move_to_element(last_time_element).scroll_by_amount(0, 200).perform()
    take_screenshot()

def clear_collection(collection_name):
    collection_ref = db.collection(collection_name)
    batch_size = 500
    docs = collection_ref.limit(batch_size).stream()

    deleted = 0
    while True:
        for doc in docs:
            doc.reference.delete()
            deleted += 1
            print(f'Deleted document: {doc.id}')

        if deleted < batch_size:
            break
        docs = collection_ref.limit(batch_size).stream()

def upload_to_fb_collection():        
    now = datetime.now()

    dates = []
    times = []
    prices = []

    # Putting the data into lists to be POSTED
    with open('real-data.txt','r') as file:
        hour1 = 0
        for line in file:
            line1 = line.strip()

            hour2 = int(line1[:2])

            if hour2 < hour1:
                now += timedelta(days=1)

            times.append(line1[:5])
            prices.append(line1[-5:])
            dates.append(now.strftime(r'%d/%m/%Y'))

            hour1 = hour2

    # connect to cloud db
    cred = credentials.Certificate(r"firebase_key.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    # clearing old data
    clear_collection('dates_times_n_prices')

    batch = db.batch()

    # jsonifying and uploading new data
    for i in range(len(dates)):
        data_to_upload = {
            'date': dates[i],
            'time0': times[i],
            'price': prices[i]
        }

        doc_ref = db.collection('dates_times_n_prices').document()
        batch.set(doc_ref, data_to_upload)

    batch.commit()

if __name__ == '__main__':
    try:
        data_length = 0
        setup_data_file()
        driver = webdriver.Chrome()
        action_chains = ActionChains(driver, 100)

        driver.get(trip_com_q_string)
        decline_cookies()
        time.sleep(2)

        start = time.time()

        while data_length < 50:
            times = get_times()
            prices = get_prices()

            if len(times) < 1 or len(prices) < 1:
                print('something happened to len time or prices')
                continue

            for i in range(len(times)):
                write_to_txt_file(times[i],prices[i])

            scroll_to_next_btn(action_chains)
            click_next_btn()
            time.sleep(0.3)
            data_length = count_lines_in_txt_file()
            print(data_length)
        else:


        print('-'*30)
        print(time.time() - start, 'secs')
        print('scrapper did a good job')
    except Exception as err:
        file = "not-sound-1.wav"
        os.system("afplay " + file)
        print('Something unexpected happened')
        print('This is what happened ', err)
        traceback.print_exc()

    driver.quit()

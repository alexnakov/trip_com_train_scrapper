from dotenv import load_dotenv
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
import requests
import firebase_admin
import asyncio
import json 
import os
import traceback
import pprint

# .env and constants
load_dotenv()
BIN_ID = os.getenv('BIN_ID')
API_KEY = os.getenv('API_KEY')
DATA_POINTS = int(os.getenv('DATA_POINTS')) # Number of journeys I want to scrape
TRIP_COM_DATE_FORMAT = r'%Y-%m-%d'
DISPLAY_DATE_FORMAT = r'%d/%m/%Y'

# query string: Tomorrow 8pm.
now = datetime.now()
now = datetime(2024, 10, 19) # Specific selected date
selected_date = now.replace(hour=13, minute=0, second=0, microsecond=0) + timedelta(days=1)
date_str = selected_date.strftime(TRIP_COM_DATE_FORMAT)
date_hour = selected_date.hour
trip_com_q_string = f'https://uk.trip.com/trains/list?departurecitycode=GB2278&arrivalcitycode=GB1594&departurecity=Sheffield&arrivalcity=London%20(Any)&departdate={date_str}&departhouript={date_hour}&departminuteipt=00&scheduleType=single&hidadultnum=1&hidchildnum=0&railcards=%7B%22YNG%22%3A1%7D&isregularlink=1&biztype=UK&locale=en-GB&curr=GBP'
           
def decline_cookies():
    attempts = 0
    while attempts < 10:
        try:
            decline_btn = find_elements(By.CLASS_NAME, 'cookie-banner-btn')[0]
            decline_btn.click()
            print('cookies declined')
            return
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
            print(f'stale exception #{attempts} in decline_cookies() occured')
        except (NoSuchElementException, TimeoutException):
            attempts += 1
            time.sleep(1)
            print('Element is not here yet')
        finally:
            if attempts > 0:
                print('stale exception for decline_cookies() is now clear')
            attempts = 0

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

def get_dates_and_times():
    global selected_date
    take_screenshot()
    attempts = 0
    while attempts < 10:
        try:
            all_h4s = find_elements(By.TAG_NAME, 'h4')
            times_list = list(map(lambda x:x.text, list(filter(lambda el: ':' in el.text, all_h4s))))
            times0 = times_list[::2]
            dates = []

            hour1 = 0
            for time_txt in times0:
                hour2 = int(time_txt[:2])
                if hour2 < hour1:
                    selected_date += timedelta(days=1)

                hour1 = hour2
                dates.append(selected_date.strftime(TRIP_COM_DATE_FORMAT))

            return [dates, times_list[::2], times_list[1::2]]
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
            print(f'stale exception #{attempts} in get_dates_and_times() occured')
        finally:
            if attempts > 0:
                print('stale exception for get_dates_and_times() is now clear')

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

def write_to_txt_file(date, time0, time1, price):
    with open('real_data.txt','a') as file:
        file.write(f'{date},{time0},{time1},{price}\n')

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
        with open('real_data.txt', 'a') as file:
            pass
    except:
        pass 

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

def scroll_to_next_btn(action_chains):
    last_time_element = get_last_time_element()
    take_screenshot()
    action_chains.move_to_element(last_time_element).scroll_by_amount(0, 200).perform()
    take_screenshot()

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

def add_date_to_hour_price_data():
    dates = []
    times0 = []
    times1 = []
    prices = []
    with open('real_data.txt', 'r') as file:
        all_lines = file.readlines()
        hour1 = 0
        for line in file:
            stripped_line = line.strip()
            hour2 = int(stripped_line[:2])
            if hour2 < hour1:
                selected_date += timedelta(days=1)

            dates.append(f"{selected_date.strftime(r'%d/%m/%Y')}")
            times0.append(stripped_line[:5])
            times1.append(stripped_line[6:11])
            prices.append(stripped_line[12:])

            hour1 = hour2

    with open('real_data.txt','w') as file:
        if len(dates) == len(times0):
            for i in range(len(times0)):
                file.writeline(f'{dates[i]},{times0[i]},{times1[i]},{prices[i]}')
        else:
            print('Lengths of dates and times data are different')

def get_next_trip_q_string():
    with open('real_data.txt','r') as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-1]
            last_date = last_line[:10]
            last_hour = last_line[11:13]
            new_trip_com_q_string = f'https://uk.trip.com/trains/list?departurecitycode=GB2278&arrivalcitycode=GB1594&departurecity=Sheffield&arrivalcity=London%20(Any)&departdate={last_date}&departhouript={last_hour}&departminuteipt=00&scheduleType=single&hidadultnum=1&hidchildnum=0&railcards=%7B%22YNG%22%3A1%7D&isregularlink=1&biztype=UK&locale=en-GB&curr=GBP'
            return new_trip_com_q_string

def show_all_scrapped_data_for_vid():
    with open('real_data.txt', 'r') as txt_file:
        print(txt_file.read())

def convert_seconds(seconds):
    minutes = int(seconds // 60)  # Calculate whole minutes
    remaining_seconds = int(seconds % 60)  # Calculate remaining whole seconds
    return f"{minutes} mins and {remaining_seconds} secs"

if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    program_tries = 0
    setup_data_file()
    data_length = 0
    start_t = time.time()
    while program_tries < 10:
        driver = webdriver.Chrome(options=options)
        action_chains = ActionChains(driver, 100)
        driver.get(trip_com_q_string)

        try:
            decline_cookies()
            time.sleep(1.7)
            while data_length < DATA_POINTS:
                dates, times0, times1 = get_dates_and_times()
                times1 = list(map(lambda hour: hour[:5], times1)) # Clean up for +1 day roll-over
                prices = get_prices()

                if len(times0) < 1 or len(prices) < 1:
                    continue

                for i in range(len(times0)):
                    write_to_txt_file(dates[i],times0[i],times1[i],prices[i])

                scroll_to_next_btn(action_chains)
                click_next_btn()
                time.sleep(0.3)
                data_length = count_lines_in_txt_file()
                print(data_length)
            else:
                if DATA_POINTS < 50:
                    show_all_scrapped_data_for_vid()

                time_taken = convert_seconds(time.time() - start_t)
                print(f'Trip.com was scrapped successfully in {time_taken}')
                break
        except Exception as err:
            print(f'Trying again: Try #{program_tries}')
            traceback.print_exc()
            print('-------------------')
            program_tries += 1
            trip_com_q_string = get_next_trip_q_string()
            driver.quit()

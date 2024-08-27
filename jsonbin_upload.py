import requests
import os
from dotenv import load_dotenv
import json

with open('test_data_for_upload.txt','r') as txt_file:
    entered_dates = []
    data = []
    for _ in txt_file:
        line = _.strip('\n')
        date = line[:10]
        time0 = line[11:16]
        time1 = line[17:22]
        price = line[24:]

        if date in entered_dates:
            last_data_array = data[-1]
            if len(last_data_array) == 4:
                current_lowest_price = last_data_array[-1]
                if price < current_lowest_price:
                    for item in [price, time1, time0]:
                        last_data_array.insert(1, item)
                for item in [time0, time1, price]:
                    last_data_array.append(item)
            elif len(last_data_array) == 7:
                price0 = last_data_array[3]
                price1 = last_data_array[-1]
                if price < price0:
                    for item in [price, time1, time0]:
                        last_data_array.insert(1, item)
                elif price0 < price < price1:
                    for item in [time0, time1, price]:
                        last_data_array.append(item)
            while len(last_data_array) != 7:
                last_data_array.pop()
        else:
            data.append([date, time0, time1, price])
            entered_dates.append(date)

# with open('json_data0.json','w') as json_file:
#     json.dump(data, json_file)

# Currently 4 data pts w the date
# dummy_line_arr = ["2024-08-28", "21:01", "23:16", "16.80", "20:00", "22:07", "20.10", "20:00", "22:07", "20.10", "20:00", "22:07", "20.10"]
# data2 = []
# for i in range(90):
#     data2.append(dummy_line_arr)
# json_string = json.dumps(data2)
# size_in_bytes = len(json_string.encode('utf-8'))
# size_in_bits = size_in_bytes * 8
# size_in_kilobits = size_in_bits / 1000
# print(f"JSON file size: {size_in_kilobits:.2f} kilobits")

load_dotenv()
BIN_ID = os.getenv('BIN_ID')
API_KEY = os.getenv('API_KEY')
url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
headers = {
  'Content-Type': 'application/json',
  'X-Master-Key': f'{API_KEY}',
}

req = requests.put(url, json=data, headers=headers)

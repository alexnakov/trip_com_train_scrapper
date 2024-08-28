import requests
import os
from dotenv import load_dotenv
import json
import pprint

with open('test_data_for_upload.txt','r') as txt_file:
    entered_dates = []
    data = []
    for _ in txt_file:
        line = _.strip('\n')
        date, time0, time1, price = line.split(',')
        price = float(price[1:]) # This will be needed for sorting the arrays
        if date in entered_dates:
            for attr in [time0, time1, price]:
                data[-1].append(attr)
        else:
            data.append([date, time0, time1, price])
            entered_dates.append(date)

    sorted_data = []
    for data_point in data:
        date = data_point[0]
        not_date_arr = data_point[1:]
        arr_of_3s = []
        for i in range(0, len(not_date_arr), 3):
            arr_of_3s.append([not_date_arr[i],not_date_arr[i+1],not_date_arr[i+2]])
        arr_of_3s.sort(key=lambda arr3: arr3[-1])
        new_data_point = [date]
        for arr3 in arr_of_3s:
            for element in arr3:
                new_data_point.append(element)
        sorted_data.append(new_data_point)

    pprint.pp(sorted_data, width=80, compact=True)

        # if date in entered_dates:
        #     last_data_array = data[-1]
        #     if len(last_data_array) == 4:
        #         current_lowest_price = last_data_array[-1]
        #         if price < current_lowest_price:
        #             for item in [price, time1, time0]:
        #                 last_data_array.insert(1, item)
        #         for item in [time0, time1, price]:
        #             last_data_array.append(item)
        #     elif len(last_data_array) == 7:
        #         price0 = last_data_array[3]
        #         price1 = last_data_array[-1]
        #         if price < price0:
        #             for item in [price, time1, time0]:
        #                 last_data_array.insert(1, item)
        #         elif price0 < price < price1:
        #             for item in [time0, time1, price]:
        #                 last_data_array.append(item)
        #     while len(last_data_array) != 7:
        #         last_data_array.pop()
        # else:
        #     data.append([date, time0, time1, price])
        #     entered_dates.append(date)

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

# load_dotenv()
# BIN_ID = os.getenv('BIN_ID')
# API_KEY = os.getenv('API_KEY')
# url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
# headers = {
#   'Content-Type': 'application/json',
#   'X-Master-Key': f'{API_KEY}',
# }

# req = requests.put(url, json=data, headers=headers)

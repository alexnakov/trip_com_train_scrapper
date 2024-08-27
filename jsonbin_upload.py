import requests
import os
from dotenv import load_dotenv
import json

with open('real_data.txt','r') as txt_file:
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

with open('json_data.json','w') as json_file:
    json.dump(data, json_file)



load_dotenv()
BIN_ID = os.getenv('BIN_ID')
API_KEY = os.getenv('API_KEY')
url = f'https://api.jsonbin.io/v3/b/{BIN_ID}'
headers = {
  'Content-Type': 'application/json',
  'X-Master-Key': f'{API_KEY}',
}

# req = requests.put(url, json=data, headers=headers)

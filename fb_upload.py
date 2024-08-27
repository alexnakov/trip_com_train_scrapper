import firebase_admin
from firebase_admin import credentials, firestore
from do_it import MyWeirdData

cred = credentials.Certificate("fb_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def flatten_nested_arrays(data):
    flattened_data = {}
    
    for key, value in data.items():
        if isinstance(value, list) and all(isinstance(i, list) for i in value):
            # Flatten the list of lists
            flattened_data[key] = [item for sublist in value for item in sublist]
        else:
            # Keep the original value if it's not a list of lists
            flattened_data[key] = value
            
    return flattened_data

my_weird_data = MyWeirdData()
flatten_data = flatten_nested_arrays(my_weird_data.data)

doc_ref = db.collection('train_prices').document('A')
doc_ref.set(flatten_data)

print("Data uploaded successfully!")

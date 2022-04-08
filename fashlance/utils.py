import joblib
import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors
from PIL import Image
import json
import requests


feature_list = np.array(joblib.load(open('image_embed_1.pkl', 'rb')))
filenames = joblib.load(open('_file_name_1.pkl', 'rb'))
myjsonfile = open('_final_csvjson.json', 'r')
model = load_model("product_model.h5")
jsondata = myjsonfile.read()

products = json.loads(jsondata)

def recommend(image_url, feature_list):
    reco_product_id = []
    digit = ''
    img = Image.open(requests.get(image_url, stream=True).raw)
    img = img.resize((80,60), Image.NEAREST)
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result /  norm(result)
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors = neighbors.fit(feature_list)
    indices = neighbors.kneighbors([normalized_result])[1]

    for file in indices[0][1:6]:
        target = filenames[file]
        digits = [d for d in target if d.isdigit()]
        digit = ''.join(digits)
        reco_product_id.append(digit)
    return reco_product_id

def image_search_recommend(img, feature_list):
    reco_product_id = []
    digit = ''
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result /  norm(result)
    neighbors = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
    neighbors = neighbors.fit(feature_list)
    indices = neighbors.kneighbors([normalized_result])[1]
    for file in indices[0]:
        target = filenames[file]
        digits = [d for d in target if d.isdigit()]
        digit = ''.join(digits)
        reco_product_id.append(digit)
    return reco_product_id


def filter_opt(target):
    my_dict = {i:target.count(i) for i in target}
    my_dict = sorted(my_dict.items(), key=lambda x: x[1], reverse=True)
    result = {k: v for k, v in my_dict}
    return result
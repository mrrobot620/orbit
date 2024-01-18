from django.shortcuts import render , HttpResponse , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db import IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
import json
import csv
import os
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import uuid
from django.core.files.storage import default_storage
from django.conf import settings
import os
from io import BytesIO
from django.db.models import Q
from django.utils.timezone import localtime, make_aware
from keras.applications.inception_v3 import InceptionV3, preprocess_input, decode_predictions
from keras.preprocessing import image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import pytesseract
import random
from selenium import webdriver
import os 
from select import select
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC3
from selenium.webdriver.common.action_chains import ActionChains
import time
import tensorflow as tf
import os
from idna import valid_contextj
from datetime import datetime, timedelta
import logging
import shutil
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import threading
import re
from .models import Pendency
import cv2


op = webdriver.ChromeOptions()
# op.add_argument('--headless=new')
prefs = {
    'profile.default_content_settings.popups': 0,
    'download.default_directory' : r"/home/administrator/cbs_bag_hold/data",
    'directory_upgrade': True
}
op.add_experimental_option('prefs' , prefs)
driver = webdriver.Chrome(options=op)

inception_model = InceptionV3(weights='imagenet')
model = tf.keras.applications.VGG16(
    weights='imagenet', include_top=False, input_shape=(224, 224, 3))


session = HTMLSession()


def preprocess_image(img_path):
    img = cv2.imread(img_path)
    if img is not None and img.size > 0:
        img = cv2.resize(img, (224, 224))  # resize the image to (224, 224)
    img = tf.keras.applications.vgg16.preprocess_input(img)
    img = np.expand_dims(img, axis=0)  # Add a batch dimension
    return img


def extract_features(img_path):
    img = preprocess_image(img_path)
    features = model.predict(img)
    features = np.reshape(features, (7*7*512,))
    return features


def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    sim = dot / norm
    return sim

def find_similar_images(query_img_path, target_img_path, top_k=5):
    query_features = extract_features_vgg16(query_img_path)
    target_features = extract_features_vgg16(target_img_path)
    similarity = cosine_similarity(query_features, target_features)

    return similarity

def extract_features_vgg16(img_path):
    img = preprocess_image(img_path)
    intermediate_layer_model = tf.keras.models.Model(inputs=model.input, outputs=model.get_layer('block5_conv2').output)
    features = intermediate_layer_model.predict(img)
    features = np.reshape(features, (features.shape[1]*features.shape[2]*features.shape[3],))

    return features


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request , username=username , password=password)
        print(username , password)
        if user is not None:
            login(request , user)
            return redirect('home')
        else:
            return render(request , 'login.html' , {'error': "Invalid Username or Password"})
    return render(request , 'login.html')


def home(request):
    return render(request , 'home.html')
    
def add_orphan_page(request):
    return render(request , 'add_orphan.html')

def add_pendency(request):
    tids = [] 
    if request.method == "POST":
        tids_input = request.POST.get("tracking_ids", "")
        tids = tids_input.split() 
        print(tids)
        threads = []
        for id in tids:
            thread = threading.Thread(target=download_tracking_page, args=(id,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    return render(request, "pendency.html", {'tids': tids})

def is_white(color, threshold=200):
    return all(value >= threshold for value in color)

def extract_dominant_color(img_array, k=3):
    img_array_flat = img_array.reshape((-1, 3))

    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(img_array_flat)

    dominant_color_centers = kmeans.cluster_centers_.astype(int)

    dominant_colors = [tuple(color) for color in dominant_color_centers if not is_white(color)]

    if not dominant_colors:
        dominant_colors = [tuple(color) for color in dominant_color_centers[1:]]

    return dominant_colors

@csrf_exempt
def classify_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        uploaded_image = request.FILES['image']
        img = Image.open(uploaded_image)
        img = img.resize((299, 299))
        img_array = np.expand_dims(np.array(img), axis=0)
        img_array = preprocess_input(img_array)
        predictions = inception_model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=1)[0]
        classification_result = decoded_predictions[0][1]
        dominant_colors = extract_dominant_color(np.array(img))
        text = pytesseract.image_to_string(img)
        print(f"Text:  {text}")
        dominant_colors = [[int(value) for value in color] for color in dominant_colors]
        result = {
            'classification_result': classification_result,
            'dominant_colors': dominant_colors,
            "extracted_text": text,
        }
        return JsonResponse(result, encoder=DjangoJSONEncoder)
    return JsonResponse({'error': 'Invalid request'})


def index(request):
    return render(request, 'add_orphan.html')

def logout_view(request):
    logout(request)
    return redirect('login_view')


def login_flo():
    driver.get("http://10.24.2.16/fklshipping/")
    time.sleep(5)
    username = driver.find_element(By.XPATH , "/html/body/div[2]/div[2]/div/div/form/div/div[4]/input[1]")
    username.send_keys("ca.2670054")

    password = driver.find_element(By.XPATH , "/html/body/div[2]/div[2]/div/div/form/div/div[4]/input[2]")
    password.send_keys("Chauhan@8091")
    time.sleep(2)
    try:
        cross = driver.find_element(By.XPATH , "/html/body/div[4]/div/button")
        cross.click()
    except:
        print("Cross Button Failed")
    time.sleep(1)
    submit = driver.find_element(By.XPATH , "/html/body/div[2]/div[2]/div/div/form/div/div[4]/div[4]/button/span")
    submit.click()
    time.sleep(10)

def select_facility():
    facility_dropdown = driver.find_element(By.XPATH , "/html/body/div[3]/div/div[2]/div[1]/form/div[1]/div/a")
    facility_dropdown.click()
    print("Clicked")
    facility_dropdown.send_keys("YKB")
    facility_dropdown.send_keys(Keys.RETURN)
    facility_submit = driver.find_element(By.XPATH , "/html/body/div[3]/div/div[2]/div[1]/form/div[3]/input")
    facility_submit.click()
    tracking = driver.find_element(By.XPATH , "/html/body/div[1]/div[3]/div/ol/li[3]/a/span").click()
    time.sleep(3)


def extract_images_info(data):
    images_info = []
    if 'data' in data and 'staticContentInfo' in data['data']:
        static_content_info = data['data']['staticContentInfo']
        for content in static_content_info.get('staticcontents', []):
            for trans_content in content.get('transContents', []):
                attribute_values = trans_content.get('attributeValues', {})
                path_values = attribute_values.get('path', {}).get('valuesList', [])
                if path_values:
                    image_url = path_values[0].get('value', '')
                    if image_url.startswith("http:/"):
                        if image_url[6:].startswith("//"):
                            image_url = "http:" + image_url[6:]
                        else:
                            image_url = "http://" + image_url[6:]
                    images_info.append({'image_url': image_url})
    return images_info

def download_image(image_url, filename):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        image_path = os.path.join(settings.MEDIA_ROOT, filename)
        with open(image_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Image downloaded successfully: {image_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
        print(f"Image URL: {image_url}")
        print(f"Filename: {filename}")


def download_tracking_page(id):
    regex_pattern = r'\b[A-Z0-9]{16}\b'
    global download_counter
    download_counter = 0
    response = session.get(f"http://10.24.2.16/fklshipping/shipments/track/?id={id}&ts=1705207057878")
    a = response.html.html
    if a is not None:
        ids = re.findall(regex_pattern, a)
        pid = ids[-1]
        try:
            api = requests.get(f"http://10.83.47.208/v2/product/xif0q/{pid}")
            raw_api = api.json()
            images_link = extract_images_info(raw_api)
            metadata = raw_api.get("metadata" , {})
            product_attributes1  = metadata.get("productAttributes" , {})
            vertical = product_attributes1.get("vertical" , "")
            data = raw_api.get('data', {})
            product_attributes = data.get('productAttributes', {})
            attribute_map = product_attributes.get('attributeMap', {})
            brand_map = attribute_map.get("brand" , {})
            brand_name  = brand_map.get("value" , "")
            keys_to_extract = ['description', 'color', 'weight', 'height', 'brand', 'keywords', 'price']
            result_data = {}
            for key in keys_to_extract:
                value = attribute_map.get(key)
                result_data[key] = value
            try:
                product = Pendency.objects.create(
                    description=result_data.get('description', ''),
                    color=result_data.get('color', ''),
                    brand=brand_name,
                    keywords=result_data.get('keywords', ''),
                    price=result_data.get('price', 0.0),
                    pid = pid,
                    tid = id,
                    vertical = vertical,
                    image=f"{id}.jpg" 
                )
                print(f"Product saved to the database: {product}")

                if images_link:

                    image_url = images_link[0].get('image_url')
                    download_image(image_url, f"{id}.jpg")
                    download_counter += 1
                    print(f"Tid {download_counter} => {id} => {pid} => {image_url}")
                else:
                    print(f"No images found for Tid {id}")

            except Exception as e:
                print(f"Error saving product to the database: {e}")

        except Exception as e:
            print(f"Error in running API: {e}")
    else:
        print(f"Unable to find Pid for Tid {id}")

    
op.add_experimental_option('prefs' , prefs)
driver = webdriver.Chrome(options=op)

def open_new_tab():
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

@csrf_exempt
def search_view(request):
    results = []
    unique_verticals = Pendency.objects.values('vertical').distinct()

    if request.method == 'POST':
        brand = request.POST.get('brand')
        uploaded_image = request.FILES.get('image')
        vertical = request.POST.getlist("vertical")

        if not (uploaded_image and (brand or vertical)):
            return render(request, 'search.html', {'results': results, 'unique_verticals': unique_verticals, 'error_message': 'Invalid input'})

        queryset = Pendency.objects.all()
        if vertical:
            queryset = queryset.filter(vertical__in=vertical)
        if brand:
            queryset = queryset.filter(brand=brand)

        print(f"Vertical: {vertical}, Brand: {brand}")

        unique_brands = Pendency.objects.filter(vertical=vertical).values('brand').distinct()
        if uploaded_image:
            uploaded_image_path, unique_filename = handle_uploaded_image(uploaded_image)

            print(f"Uploaded Image Path: {uploaded_image_path}")

            if not os.path.exists(uploaded_image_path):
                return render(request, 'search.html', {'results': results, 'unique_verticals': unique_verticals, 'unique_brands': unique_brands, 'error_message': 'Uploaded Image File Does Not Exist!'})

            try:
                print(f"Queryset before loop: {queryset}")
                for pendency in queryset:
                    print(f"Processing pendency: {pendency}")
                    pendency_image_path = pendency.image.path
                    similarity = find_similar_images(uploaded_image_path, pendency_image_path)
                    print(f"Similarity for TID {pendency.tid}: {similarity}")
                    results.append({'tid': pendency.tid, 'similarity': similarity, 'uploaded_image_name': unique_filename, 'pendency_image_name': pendency.image.name})

                print(f"Search Results: {results}")
                results.sort(key=lambda x: x['similarity'], reverse=True)

                # Redirect to the results page with the search results
                return render(request, 'results.html', {'results': results, 'unique_verticals': unique_verticals, 'unique_brands': unique_brands})

            except Exception as e:
                print(f"Error processing image: {e}")
                return render(request, 'search.html', {'results': results, 'unique_verticals': unique_verticals, 'unique_brands': unique_brands, 'error_message': 'Error processing image'})

    return render(request, 'search.html', {'results': results, 'unique_verticals': unique_verticals, 'error_message': 'No Results Found!'})

def handle_uploaded_image(uploaded_image):
    unique_filename = f"{uuid.uuid4().hex[:10]}.jpg"
    uploaded_image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images', unique_filename)

    try:
        os.makedirs(os.path.dirname(uploaded_image_path), exist_ok=True)

        with open(uploaded_image_path, 'wb+') as destination:
            for chunk in uploaded_image.chunks():
                destination.write(chunk)

        return uploaded_image_path , unique_filename

    except Exception as e:
        print(f"Error saving image: {e}")
        return None
    
def get_brands_for_vertical(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        vertical_param = request.GET.get('vertical', None)

        if vertical_param:
            vertical_list = vertical_param.split(',')  # Convert the comma-separated string to a list
            unique_brands = Pendency.objects.filter(vertical__in=vertical_list).values('brand').distinct()
            brands_list = list(unique_brands.values_list('brand', flat=True))
            print(brands_list)
            return JsonResponse({'brands': brands_list})

    return JsonResponse({'error': 'Invalid request'})

def results_view(request):
    return render(request, 'results.html')

def get_details(request, tid):
    pendency = get_object_or_404(Pendency, tid=tid)
    details_data = {
        'tid': pendency.tid,
        'description': pendency.description,
        'color': pendency.color,
        'brand': pendency.brand,
        'vertical': pendency.vertical,
        'image_url': os.path.join(settings.MEDIA_URL, pendency.image.name),
    }
    return JsonResponse(details_data, encoder=DjangoJSONEncoder)


# login_flo()
# select_facility()
# session_cookie = driver.get_cookies()
# print(session_cookie)
# selenium_user_agent = driver.execute_script("return navigator.userAgent;")
# print(selenium_user_agent)
# session.headers.update({"user-agent": selenium_user_agent})
# for cookie in driver.get_cookies():
#     session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
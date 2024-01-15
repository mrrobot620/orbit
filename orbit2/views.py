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

IMAGE_FOLDER = os.path.join('static', 'images')

op = webdriver.ChromeOptions()
# op.add_argument('--headless=new')
prefs = {
    'profile.default_content_settings.popups': 0,
    'download.default_directory' : r"/home/administrator/cbs_bag_hold/data",
    'directory_upgrade': True
}
op.add_experimental_option('prefs' , prefs)
driver = webdriver.Chrome(options=op)

session = HTMLSession()

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request , username=username , password=password)
        print(username , password)
        if user is not None:
            login(request , user)
            return redirect('login')
        else:
            return render(request , 'login.html' , {'error': "Invalid Username or Password"})
    return render(request , 'login.html')


def home(request):
    return render(request , 'home.html')
    

def add_orphan_page(request):
    return render(request , 'add_orphan.html')

inception_model = InceptionV3(weights='imagenet')

def is_white(color, threshold=200):
    return all(value >= threshold for value in color)

def extract_dominant_color(img_array, k=3):
    img_array_flat = img_array.reshape((-1, 3))

    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(img_array_flat)

    dominant_color_centers = kmeans.cluster_centers_.astype(int)

    # Filter out white or near-white colors
    dominant_colors = [tuple(color) for color in dominant_color_centers if not is_white(color)]

    if not dominant_colors:
        # If all dominant colors are white, use the second most dominant color
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

        # Make predictions
        predictions = inception_model.predict(img_array)
        decoded_predictions = decode_predictions(predictions, top=1)[0]
        classification_result = decoded_predictions[0][1]

        # Extract dominant colors
        dominant_colors = extract_dominant_color(np.array(img))

        text = pytesseract.image_to_string(img)

        random_number = random.randint(10000000, 99999999)
        orphan_id = f"OID{random_number}"

        print(f"Text:  {text}")

        # Convert np.int64 to regular int for serialization
        dominant_colors = [[int(value) for value in color] for color in dominant_colors]

        result = {
            'classification_result': classification_result,
            'dominant_colors': dominant_colors,
            "extracted_text": text,
            "orphan_id": orphan_id
        }
        return JsonResponse(result, encoder=DjangoJSONEncoder)
    return JsonResponse({'error': 'Invalid request'})


def index(request):
    return render(request, 'add_orphan.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def login():
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
        image_path = os.path.join(IMAGE_FOLDER, filename)
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
            if images_link:
                # Download the first image
                image_url = images_link[0].get('image_url')
                download_image(image_url, f"{id}.jpg")
                download_counter += 1
                print(f"Tid {download_counter} => {id} => {pid} => {image_url}")
            else:
                print(f"No images found for Tid {id}")
        except Exception as e:
            print(f"Error in running API: {e}")
    else:
        print(f"Unable to find Pid for Tid {id}")

        
def tracking_page():
    session_cookie = driver.get_cookies()
    print(session_cookie)
    selenium_user_agent = driver.execute_script("return navigator.userAgent;")
    print(selenium_user_agent)
    with open('a.txt', 'r') as f:
        tids = [line.strip() for line in f.readlines()]
        print(tids.count)

    session.headers.update({"user-agent": selenium_user_agent})
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    threads = []
    for id in tids:
        thread = threading.Thread(target=download_tracking_page, args=(id,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

op.add_experimental_option('prefs' , prefs)
driver = webdriver.Chrome(options=op)

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully: {filename}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

def open_new_tab():
    driver.execute_script("window.open('', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])
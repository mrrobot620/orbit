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
import tensorflow as tf
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
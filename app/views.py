from django.shortcuts import render, redirect
from .forms import *
from .models import *
import io
import os
from PIL import Image
import numpy as np
import base64
from tensorflow import keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.preprocessing import image as proimage
from keras.preprocessing.image import img_to_array
from pneumoray.settings import BASE_DIR

def get_model():
    global model
    # from_here = 'https://pneumoray.s3.us-east-2.amazonaws.com/static/img/pneum.h5'
    # static/img/pneum.h5
    model = keras.models.load_model('static/img/pneum.h5')
    print("Model Loaded")


def pneum_predict(img_path, model):
    img = proimage.load_img(img_path, target_size=(224, 224))
    print('STEP 1')
    x = proimage.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x, mode='caffe')
    get_model()
    pred = model.predict(x)
    return np.argmax(pred)

def preprocess_image(img, target_size):
    if img.mode!="RGB":
        img=img.convert("RGB")
    img=img.resize(target_size)
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x, mode='caffe')
    return x

print("Loading Keras Model")
get_model()



# @app.route('/check', methods=['POST'])
def predict(image):
    # message = request.get_json(force=True)
    # encoded = message['image']
    # decoded =  base64.b64decode(encoded)
    # img = Image.open(io.BytesIO(decoded))   
    processed_image = preprocess_image(image, target_size=(224,224))
    prediction=model.predict(preprocess_image)



    response={
        'result':{  
            'pneumonia':np.argmax(prediction)
        }
    }

    print('prediction: ', response)
    return jsonify(response)

def home(request):

    context = {}
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.xray = request.FILES['xray']
            print('file uploaded', obj.xray.url)
            obj.save()
            file_path = "{}{}".format(BASE_DIR, obj.xray.url)
            print(file_path)
            print('prediction: ', pneum_predict(file_path, model))
            endresult = pneum_predict(file_path, model)
            all_objs = Document.objects.all()
            if all_objs.exists():
                for a in all_objs:
                    a.xray.delete()
                all_objs.delete()
                print('------------- images deleted -------------')
            if endresult == 0:
                print('image processed')
                print('- - - - - - - -')
                print('result negative')
                return redirect('gresults')
            else:
                print('image processed')
                print('- - - - - - - -')
                print('result positive')
                return redirect('results')


        
        file_path = "{}{}".format(BASE_DIR, obj.xray.url)
        print(file_path)
        print('new url: ', file_path)

        print('image processed')
        return render(request, 'app/home.html', context)
    else:
        form = DocumentForm()
        context['form'] = form

        # print(pneum_predict('/Users/vladyslav/Desktop/pneumoray/media/xrays/NORMAL2-IM-0341-0001.jpeg', model))
        # print(pneum_predict('/Users/vladyslav/Desktop/pneumoray/media/xrays/person24_virus_58.jpeg', model))
        # file_path = os.path.join(BASE_DIR, str(xray.url))
        # print(BASE_DIR)
        return render(request, 'app/home.html', context)
    
    return render(request, 'app/home.html', context)

def results(request):
    context = {}

    return render(request, 'app/results.html', context)

def gresults(request):
    context = {}

    return render(request, 'app/gresults.html', context)

def about(request):
    context = {}

    return render(request, 'app/about.html', context)

def check(request):
    context = {}

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.xray = request.FILES['file']
            print('file uploaded', xray.url)
            # obj.author = request.user
            obj.save()
        return render(request, 'app/check.html', context)
    else:
        form = DocumentForm()
        context['form'] = form
    
        return render(request, 'app/check.html', context)
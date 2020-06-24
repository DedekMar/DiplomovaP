print("Loading packages")
from flask import Flask, redirect, url_for, request, render_template, jsonify, make_response

from io import BytesIO
import urllib.request
import tensorflow as tf
from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.applications.inception_resnet_v2 import preprocess_input
datagen = ImageDataGenerator(preprocessing_function = preprocess_input)
from PIL import Image

import numpy as np

import os
print("Loading model")
modelname = "model.hdf5"
currentScriptPath = os.path.dirname(__file__)
abs_file_path = os.path.join(currentScriptPath, modelname)
try:
    model = load_model(abs_file_path)
except OSError as err:
    print("OS error: {0}".format(err))
    print("Model nenalezen v root adresari aplikace, zadejte cestu k modelu")
    while True:
        try:
            userpath = input()
            print(userpath)
            model = load_model(userpath)
            print("Model loaded")
            break
        except OSError as err:
            print("OS error: {0}".format(err))
            print("Invalidni cesta nebo model")
    
    

import json
with open('dict.json', 'r') as jsfile:
    loaded = json.load(jsfile)
    #inverze slovnika tak, aby labely byly klice
    class_names = {v: k for k, v in loaded.items()}







UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
   return render_template("createoffer.html")


from db import init_db, db_session
from models.OfferModel import OfferModel
from models.ImagesModel import ImagesModel
from io import BytesIO
from werkzeug.utils import secure_filename

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    
@app.route('/listings/')
def listings():
    offersList = []
    init_db()
    #ziskat vsechny inzeraty
    results = OfferModel.query.all()
    #pro kazdy inzerat ziskat vsechny obrazky k nemu patrici a pridat je jako list
    for result in results:
        imagesList = db_session.query(ImagesModel).join(OfferModel).filter(OfferModel.id == result.id)
        result.imagesList = list(imagesList)
        offersList.append(result)
    return render_template("listings.html", offersList = offersList)

#metoda pro vraceni predikci na ajax request
@app.route('/receive/', methods = ['POST'])
def receive():
    if request.method == 'POST':
        print(request.files)
        files = request.files.to_dict()
        files = request.files.getlist("images[]")
        if(len(files) > 0 ):
            

            predictionsDict = {}
            predictions = batch_predict(list(files))
            predClassDict = {}
            THRESHOLD = 0.9
            
            predictedClasses = pred_classes(predictions, THRESHOLD)
            for i, pred in enumerate(predictions):                
                predictionsDict.update({files[i].filename : pred})
                
            for i, pred in enumerate(predictedClasses):
                predClassDict.update({files[i].filename : pred})

            
            
            data = {'message': 'lenght of files' + str(len(files)), 'code': 'SUCCESS', 'predictions' : predictionsDict, 
                    'predClasses' : predClassDict}
            return make_response(jsonify(data), 201)
        else:
            data = ({"message" : "files are empty"})
            return make_response(jsonify(data), 400)
        
    
@app.route('/postoffer/', methods = ["POST"])
def post_offer():
    if request.method == 'POST':
        files = request.files.getlist("images[]")
        #dalsi validace by byla v produkcnim prostredi nutna
        location = request.form["location"]
        area = request.form["area"]
        price = request.form["price"]
        email = request.form["email"]
        description = request.form["description"]        
        
        
        init_db()
        offer = OfferModel(location = location, email = email,
                           area = int(area), price = float(price), 
                           description = description)
        db_session.add(offer)
        db_session.flush()
        resultID = offer.id
        db_session.commit()
        predictions = batch_predict(list(files))
        predictedClasses = pred_classes(predictions, 0.9)
        finalClasspredDict = {}
        finalProbsDict = {}
        
        #inzeraty bez obrazku jsou mozne, pro ne nasledujici cyklus neprobehne, kvuli delce files 0
        for i, file in enumerate(files):
            if(allowed_file(files[i].filename)):
                fileobj = files[i]
                filename = secure_filename(fileobj.filename)
                finalClasspredDict.update({ files[i].filename : predictedClasses[i]})
                finalProbsDict.update({ files[i].filename : predictions[i]})
                
                fileobj.stream.seek(0)
                fileobj.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if (len(predictedClasses[i])>0):
                    imgobj = ImagesModel(predictedClasses[i][0], resultID, filename)
                else:
                    imgobj = ImagesModel("", resultID, filename)    
                db_session.add(imgobj)
                db_session.commit()     
        data = {"cool" : "cool", "predClasses" : finalClasspredDict, "predprobs" : finalProbsDict, "redirect" : resultID }
        return make_response(jsonify(data), 201)
    
    
#hodit sem ziskany predikce, pro ne predikovat classy na zaklade thresholdu, vratit list nebo dict ziskanejch class
def pred_classes(pred_probs, threshold):
    predictedClassesDict = []
    for pred in pred_probs:
        individualPredClass = []
        for label in pred:
            if(pred[label] >= threshold):
                individualPredClass.append(label)

        predictedClassesDict.append(individualPredClass)
    return predictedClassesDict    

#davkova predikce
def batch_predict(files):
    batch = np.zeros((len(files), 256, 256, 3))
    for i, img in enumerate(files):
        img.stream.seek(0)
        img.read()
        #otevrit img skrz PIL, ekvivalent pro keras image loadimg

        
        openedimg = Image.open(img)
        convertedimg = openedimg.convert("RGB")
        resizedimg = convertedimg.resize((256,256))

        batch[i,] = resizedimg #loadedimg
        
    batch = datagen.standardize(batch) 
    

    predictions = model.predict(batch, batch_size=len(files))
    finalPreds = []
    ## udelat nice looking list of prediction dictionaries to make working with it easier later. need np float 64 pro json
    for prediction in predictions:
        preddictionary = {}
        for label in class_names:
            class_name = class_names.get(label)
            preddictionary.update({class_name : prediction[label].astype(np.float64)})
        finalPreds.append(preddictionary)
       
    return finalPreds 


from flask import send_from_directory
@app.route('/files/<path:filename>')
def download_file(filename):
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/offer/<offerID>")
def offer(offerID):
    offersList = []
    init_db()
    result = OfferModel.query.filter(OfferModel.id == offerID).first()
    #pro kazdou nabidku ziskat vsechny obrazky a pridat je do listu
    imageList = list(db_session.query(ImagesModel).join(OfferModel).filter(OfferModel.id == result.id)) 
    result.imageList = imageList
    return render_template("offer.html",  result = result)


@app.route("/createoffer/")
def createoffer():
    return render_template("createoffer.html")  


#vypnout debug pred deploys, use_reloader false pro notebook a ide typu Spyder
if __name__ == '__main__':
   #model = load_model('K:/DP/WD/plan_no_weighting.h5')
   app.run(debug = True, use_reloader = True)


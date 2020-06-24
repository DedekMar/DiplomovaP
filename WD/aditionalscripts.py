# -*- coding: utf-8 -*-
"""

@author: Martin
"""
#pridavne skripty
from tensorflow.python.keras.preprocessing import image
import os
#zmenit na vase work directory
os.chdir("K:\DP\WebApp")


#Nacteni npy souboru, kde je ulozena historie uceni a jejich konverze na csv soubory, kontrola ze radky v csv odpovidaji radkum v dict
import numpy as np

firstRun = np.load("K:/DP/WD/firstRun.npy", allow_pickle = True)
secondRun = np.load("K:/DP/WD/secondRun.npy", allow_pickle = True)
thirdRun = np.load("K:/DP/WD/thirdRun.npy", allow_pickle = True)

type(firstRun)
firstRunList = firstRun.tolist()
len(firstRunList["loss"])
secondRunList = secondRun.tolist()
len(secondRunList["loss"])
thirdRunList = thirdRun.tolist()
len(thirdRunList["loss"])
import csv
column_names = ["loss", "accuracy", "val_loss", "val_accuracy"]
keys = sorted(firstRun.keys())
with open("test.csv", "w") as outfile:
   writer = csv.writer(outfile, delimiter = ",")
   writer.writerow(keys)
   writer.writerows(zip(*[firstRun[key] for key in keys]))
   
   
with open("firstRun.csv", "w") as outfile:
   writer = csv.writer(outfile)
   writer.writerow(firstRunList.keys())
   writer.writerows(zip(*firstRunList.values())) 
   
with open("secondRun.csv", "w") as outfile:
   writer = csv.writer(outfile)
   writer.writerow(secondRunList.keys())
   writer.writerows(zip(*secondRunList.values()))    
 
with open("thirdRun.csv", "w") as outfile:
   writer = csv.writer(outfile)
   writer.writerow(thirdRunList.keys())
   writer.writerows(zip(*thirdRunList.values()))   
   
   
from io import BytesIO
import urllib.request
import tensorflow as tf
from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.preprocessing import image
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.keras.applications.inception_resnet_v2 import preprocess_input
datagen = ImageDataGenerator(preprocessing_function = preprocess_input)
model = load_model("model.hdf5")
import json
with open('K:/DP/WebApp/dict.json', 'r') as jsfile:
    loaded = json.load(jsfile)
    #inverted the dictionary so that labels are keys
    class_names = {v: k for k, v in loaded.items()}
import numpy as np
import os


from time import process_time 
from time import process_time_ns


#test batch predikce
start = process_time() 

img_dir = "K:/data/manual test"
batch = np.zeros((len(os.listdir(img_dir)), 256, 256, 3))
for i, img in enumerate(os.listdir(img_dir)):
    loadedimg = image.load_img(os.path.join(img_dir,img), target_size=(256, 256))
    batch[i,] = loadedimg
batch = datagen.standardize(batch)    
predictions = model.predict_proba(batch, batch_size=len(os.listdir(img_dir))) #.tolist()[0]
finalPreds = []
for prediction in predictions:
    print(prediction)
    dictionary = {}
    for label in class_names:
        class_name = class_names.get(label)
        dictionary.update({class_name : prediction[label]})
    finalPreds.append(dictionary)
assignDict = {}
filelist = os.listdir(img_dir)
for i, pred in enumerate(finalPreds):
    print(i)
    assignDict.update({filelist[i] : pred})   
stop = process_time() 
print("Ubehly cas:", stop-start)    


def predict_for_image(img):
    imaget = image.load_img(img, target_size=(256, 256))
    imaget = image.img_to_array(imaget)
    imaget = np.expand_dims(imaget, axis=0)
    imaget = datagen.standardize(imaget)
    print(img)
    classes = model.predict_classes(imaget)      
    predicted_class = str(class_names.get(classes[0]))
    predicted_probs = model.predict_proba(imaget).tolist()[0]

    dictionary = {}
    for label in class_names:

        class_name = class_names.get(label)
        dictionary.update({class_name : predicted_probs[label]})
   
    return dictionary

#test pro individualni klasifikaci
t1_start = process_time()
predictionsindividual = []
for i, img in enumerate(os.listdir(img_dir)):
    predictionsindividual.append(predict_for_image(os.path.join(img_dir,img)))
t1_stop = process_time() 
print("Elapsed time during the whole program in seconds:", 
                                     t1_stop-t1_start)     
   






#skripty pro manipulaci se soubory
#presun vsech kategorii ze jedne slozky do jine
def movefromto(srcdir, destdir):
  import math
  import shutil
  import os
  from os import listdir
  from os.path import isfile, join
  import random
  categories = os.listdir(srcdir)
  for category in categories:
    srcpath = join(srcdir, category, "")
    files = [f for f in listdir(srcpath) if isfile(join(srcpath, f))]
    random.seed(55)

    for file in files:
      shutil.move(srcpath + file, join(destdir, category, ""))
      
for category in ["bathroom", "bedroom", "kitchen", "living_room", "plan"]:
    movefromto("K:/data/finalset/test/", "K:/data/finalset/train/")      
      
      
import math
import shutil
from os import listdir
from os.path import isfile, join
import random
#testovaci a validacni split
def split(valperct, testperct, traindir, valdir, testdir):
  categories = os.listdir(traindir)
  for category in categories:
    srcpath = join(traindir, category, "")
    files = [f for f in listdir(srcpath) if isfile(join(srcpath, f))]
    random.seed(55)
    totalLen = len(files)
    print(totalLen)
    shuffledval = random.sample(files, math.floor(totalLen*valperct))
    #odstranit data pouzita pro val, ulozit si celkovou delku
    new_list = [item for item in files if item not in shuffledval]
    shuffledtrain =  random.sample(new_list, math.floor(totalLen*testperct))

    for file in shuffledval:
      shutil.move(srcpath + file, join(valdir, category, ""))
    for file in shuffledtrain:
      shutil.move(srcpath + file, join(testdir, category, ""))


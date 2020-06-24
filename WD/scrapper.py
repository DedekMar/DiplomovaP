# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 16:47:12 2020

@author: Martin
"""

import os
import urllib.request
import json
from urllib.parse import urlparse
import os
from os.path import join
os.chdir("K:\DP\WD")

jsonlist = []
with open ("K:/imgs_vids_floorplan_None_eda39a3ee_e_02_02..json") as fp:
    for jsonObj in fp:
        jsonDict = json.loads(jsonObj)
        jsonlist.append(jsonDict)
jsonlist[2]["item_download_url"]     

import urllib.request
from urllib.error import URLError
def download_img(url, itemid, savepath):
    if not os.path.exists(join(savepath, "")):
        os.mkdir(join(savepath, ""))
    print(url)
    
    try:
        urllib.request.urlretrieve(url, savepath + str(itemid) + ".jpg")
    except URLError:
        print("not found " + url)
    
for item in jsonlist:
    download_img(item["item_download_url"], item["item_server_identifier"], "K:/data/flickr100mFloorPlan/")
    
    
    
from bs4 import BeautifulSoup
import requests    



from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time 
from urllib.parse import urlparse

#inicializovat options
options = Options()

def scroll(driver, timeout):
    
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    #nejprve je potreba odkliknout to, ze souhlasime s cookies
    
    cookiesbtn = driver.find_elements_by_class_name("primary")
    if len(cookiesbtn) == 0:
            print("no button")
    else:
        driver.execute_script("document.getElementsByClassName('primary')[0].click()")
        print("click")  
    #potom je potreba nechat driver scrollovat dokud nenajede dolu a nenarazi na tlacitko, kdyz na nej narazi tak klikne, jinak scrolluje        
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #pockat nez se nactou obrazky
        time.sleep(timeout)
        newHeight = driver.execute_script("return document.body.scrollHeight")
        
        #zkusit kliknout na tlacitko vice
        elems = driver.find_elements_by_class_name("more-res")
        
        if len(elems) == 0:
            print("no button")
        else:
            #pockat nez se nactou obrazky
            time.sleep(timeout)
            driver.execute_script("document.getElementsByClassName('more-res')[0].click()")
            last_height = driver.execute_script("return document.body.scrollHeight")
            print("click")
            
        #pokud dojde k tomu , ze nova vyska je stejna jako stara a neni pritomne tlacitko,  vyskocit z cyklu
        if newHeight == lastHeight:
            break
        lastHeight = newHeight  


def getImgUrls(url):
    #inicializace driveru pomocí geckodriveru pro Mozillu Firefox
    driver = webdriver.Firefox(executable_path='K:/geckodriver.exe')
    
    #otevření stránky v driveruww
    driver.get(url)
    # Zavloání metody scroll
    scroll(driver, 5)
    # Využítí BeautifulSoup pro přečtení zdroje stránky
    soup_a = BeautifulSoup(driver.page_source, 'lxml')

    driver.close()

    # nalezení vsech img v dokumentu
    imglist = []
    imgs = soup_a.findAll("img")
    for img in imgs:
        imgsrc = img.get("src")
        
        #pokud je src daného img validní url, ulozit ji jako zdroj
        if(urlparse(imgsrc)):
            print(imgsrc)
            imglist.append(imgsrc)

    return imglist
allimages = getImgUrls("https://images.search.yahoo.com/search/images;_ylt=AwrExlRlRYdeEhoAvSuJzbkF?p=floor+plan&fr=yfp-t&imgl=fsu&fr2=p%3As%2Cv%3Ai")

import hashlib 

#stahnout soubory, zahashovat nazvy do slozky
for file in allimages:
    if(str(file) != "None"):
        print(hashlib.md5(str(file).encode('utf-8')).hexdigest())
        download_img(file, hashlib.md5(str(file).encode('utf-8')).hexdigest(), "K:/data/yahooscrape/")



    
import json
import time
import sys
import re
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import csv
import nltk
import tensorflow as tf
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import nltk
#from sentence_transformers import SentenceTransformer
from flask import Flask , render_template, url_for, flash, redirect
from flask import jsonify
from forms import RegistrationForm, LoginForm

#sbert_model = SentenceTransformer('bert-base-nli-mean-tokens')

def connect2ES():
    es = Elasticsearch([{"host": "localhost", "port": 9200}], timeout=60, max_retries=10, retry_on_timeout=True)
    if es.ping():
        print("Connect to ES!")
    else:
        print("Could not connect")
        sys.exit()
        
    print("************************************************************")
    return es

def keywordSearch(es, q):
    #processing text
    q = re.sub(r"\[[0-9]*\]", " ",q)
    q = q.lower()
    q = re.sub(' +', ' ', q)
    q = re.sub(r'[^\w\s]', '', q)

    #remove stopwords
    text_tokens = word_tokenize(q)
    tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
    q = (" ").join(tokens_without_sw)
        
    b = {
            "query":{
                "match":{
                    "title":q
                    }
                }
        }

    res = es.search(index="questions-index", body=b)
    return res

def sentenceSimilaritybyNN(es, sent):
    query_vector = sbert_model.encode([sent]).tolist()[0]
        

    b = {"query":{
  "script_score": {
    "query": {"match_all": {}},
    "script": {
      "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
      "params": {"query_vector": query_vector}
    }}}}
    #print(b)
    
    res = es.search(index = "questions-index", body=b)
    return res


app = Flask(__name__)
app.static_folder = 'static'
es = connect2ES()

@app.route("/search/<query>")
def search(query):
    q = query.replace("+", " ")
    res_kw = keywordSearch(es, q)
    #res_sw = sentenceSimilaritybyNN(es, q)
    
    #ret = []
    #for hit in res_kw["hits"]["hits"]:
        #dic = {"score": str(hit["_score"]),
              #"title": str(hit["_source"]["title"]),
               #"link": str(hit["_source"]["link"]),
               #"date_published" :str(hit["_source"]["date_published"]),
               #"views": str(hit["_source"]["views"]),
               #"answer_description" : str(hit["_source"]["answer_description"]),
               # "tags":str(hit["_source"]["tags"])}
       # ret.append(dic)
     
    return render_template('searchResult.html', res=res_kw)

@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/login")
def login():
    login_form = LoginForm()
    return render_template('login.html', login_form = login_form )

@app.route("/signup")
def signup():
    signup_form = RegistrationForm()
    return render_template('signup.html', signup_form = signup_form)

if __name__ == "__main__":
    app.run(debug=True)

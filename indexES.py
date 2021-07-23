import json
import time
import sys
import re
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import csv
import tensorflow as tf
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
#from sentence_transformers import SentenceTransformer
#sbert_model = SentenceTransformer('bert-base-nli-mean-tokens')

#connect to ES on local host on port 9200

es = Elasticsearch([{"host": "localhost", "port": 9200}], timeout=30, max_retries=10, retry_on_timeout=True)
if es.ping():
    print("Connected to ES")
else:
    print("Could not connect to elastic search")

print("********************************************************************************")
r = es.indices.get_alias("*")
for Name in r:
    print(Name)
print("********************************************************************************")   
#Read each question and index into an index called questions
#Define the index
#Mapping: Structure of the index
#Property/Field: name/type

b = {"mapping":{
        "properties":{
            "title":{
                "type":"text"
                },
            "link":{
                "type": "text"
                },
            "date_published":{
                "type":"text"
                },
            "views":{
                "type":"text"
                },
            "answer_description":{
                "type":"text"
                },
            "tags":{
                "type":"text"
                },
            #"title_vector":{
                #"type": "dense_vector",
                #"dims": 768
                #}
            }
        }
     }

ret = es.indices.create(index="questions-index", ignore=400, body=b)
print(json.dumps(ret, indent = 4))

print("********************************************************************************")

#load USE4 model
#embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")
#print("USE-Done")
count = 0
#sbert_model = SentenceTransformer('bert-base-nli-mean-tokens')
with open("data\dataset.csv",encoding="utf8") as csvfile:
    readCSV = csv.reader(csvfile, delimiter = ",")
    next(readCSV, None) #skip the header
    for row in readCSV:
        doc_id = row[1]
        title = row[3]
        link = row[5]
        date_published = row[7]
        views = row[6]
        ans = row[4]
        tag = row[2]
        
        
        #processing title
        
        title = re.sub(r"\[[0-9]*\]", " ",title)
        title = title.lower()
        title = re.sub(' +', ' ', title)
        title = re.sub(r'[^\w\s]', '', title)
        
        #vec = sbert_model.encode([title]).tolist()[0]
        #print(len(vec))
        b = {
            "title": title,
            "link":link,
            "date_published": date_published,
            "views": views,
            "answer_description":ans,
            "tags":tag,
            #"title_vector": vec,
            }
        res = es.index(index = "questions-index", id = doc_id, body = b)

        #print(type(title))
        #print(type(vec))
        #print(b)
    print("Completed indexing....")

    
        

import json
import time
import sys
import re
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from flask_sqlalchemy import SQLAlchemy
import csv
import nltk
import tensorflow as tf
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
import nltk
import indexES
#from sentence_transformers import SentenceTransformer
from flask import Flask , render_template, url_for, flash, redirect
from flask import jsonify
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_login import login_user, LoginManager, current_user, logout_user

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
                    "title":{
                        "query": q,
                        "fuzziness": "Auto",
                        "operator":"and"
                        }
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

app.config['SECRET_KEY']= 'b97000541f6faa63839f00bb2e7d8b42'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager=LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    firstname = db.Column(db.String(50), unique=False, nullable=False)
    lastname = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=False, nullable=False)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.fistname}','{self.password}')"



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
    for hit in res_kw["hits"]["hits"]:
        hit["_source"]["views"] = int(hit["_source"]["views"])
    res = sorted(res_kw["hits"]["hits"], key=lambda k: k['_source']['views'], reverse = True)
    return render_template('searchResult.html', res=res)

@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/login" , methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash(f'Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful. Please enter valid credentials.','danger')
    return render_template('login.html', login_form = login_form )

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    signup_form = RegistrationForm()
    if signup_form.validate_on_submit():
        hashed_password= bcrypt.generate_password_hash(signup_form.password.data).decode('utf-8')
        user = User(username = signup_form.username.data,firstname = signup_form.firstname.data, lastname=signup_form.lastname.data, email = signup_form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created! Please login', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', signup_form = signup_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

import os

from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'When in reme do as the remans do'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


bootstrap = Bootstrap(app)
db = SQLAlchemy(app)



@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    
    return render_template('schedule.html')

@app.route('/shopping')
def shopping():

    return render_template('shopping.html')
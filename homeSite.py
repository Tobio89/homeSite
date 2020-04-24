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


# FORMS

class ItemForm(FlaskForm):
    item = StringField('Enter item:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddItemForm(FlaskForm):
    item = StringField('Enter item:', validators=[DataRequired()])
    quant = IntegerField('Enter quantity:',validators=[Optional()] )
    submit = SubmitField('Submit')
 



@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    
    return render_template('schedule.html')

@app.route('/shopping')
def shopping():
    # shoppingItems = Grocery.query.all()
    shoppingItems=['nought']
    return render_template('shopping.html', items=shoppingItems)
    
@app.route('/shopping/add', methods=['GET', 'POST'])
def shoppingAdd():
    # shoppingItems = Grocery.query.all()
    shoppingItems=['nought']
    form = AddItemForm()
    session['itemToAdd'] = form.item.data
    session['itemQuantity'] = form.quant.data
    if form.validate_on_submit():
        newItem = session.get('itemToAdd')
        
        if session['itemQuantity'] and session['itemQuantity'] > 1:
            # db.session.add(Grocery(itemName=newItem, quantity=session['itemQuantity']))
            print('this happened')
        else:
            # db.session.add(Grocery(itemName=newItem))
            print('that happened')
        # db.session.commit()

        return redirect(url_for('shoppingAdd'))

    return render_template('add.html', form=form, items=shoppingItems)
    
@app.route('/shopping/remove')
def shoppingRemove():

    return render_template('remove.html')
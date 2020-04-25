import os

from flask import Flask, render_template, session, redirect, url_for, request
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'When in reme do as the remans do'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

# SQL DATABASE TABLES

class Grocery(db.Model):
    __tablename__ = 'groceries'
    id = db.Column(db.Integer, primary_key=True)
    itemName = db.Column(db.String(64), unique=True)
    quantity = db.Column(db.Integer) #Setting quantity to optional so 'rice' doesn't need a quantity

    def __repr__(self):
        return f'<Grocery {self.itemName}>'

    def __str__(self):
        if self.quantity:
            return f'{self.itemName} x {self.quantity}'
        else:
            return f'{self.itemName}'




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

    # Clear the shopping states
    session['removedItem'] = None
    session['successState'] = False
    
    return render_template('index.html')

@app.route('/schedule')
def schedule():

    # Clear the shopping states
    session['removedItem'] = None
    session['successState'] = False
    
    return render_template('schedule.html')

@app.route('/shopping')
def shopping():

    # Clear the shopping states
    session['removedItem'] = None
    session['successState'] = False

    shoppingItems = Grocery.query.all()
    # shoppingItems=['nought']
    return render_template('shopping.html', items=shoppingItems)
    
@app.route('/shopping/add', methods=['GET', 'POST'])
def shoppingAdd():

    # Clear the shopping states
    session['removedItem'] = None
    session['successState'] = False

    shoppingItems = Grocery.query.all()
    # shoppingItems=['nought']
    form = AddItemForm()
    session['itemToAdd'] = form.item.data
    session['itemQuantity'] = form.quant.data
    if form.validate_on_submit():
        newItem = session.get('itemToAdd')
        if newItem[0].islower():
            newItem = newItem.capitalize()
        
        if session['itemQuantity'] and session['itemQuantity'] > 1:
            db.session.add(Grocery(itemName=newItem, quantity=session['itemQuantity']))
            # print('this happened')
        else:
            db.session.add(Grocery(itemName=newItem))
            # print('that happened')
        db.session.commit()

        return redirect(url_for('shoppingAdd'))

    return render_template('add.html', form=form, items=shoppingItems)
    
# @app.route('/shopping/remove')
# def shoppingRemove():

#     return render_template('remove.html')


@app.route('/shopping/remove', methods=['GET', 'POST'])
def shoppingRemove(): #This name here is what 'url_for' is using.

    shoppingItems = Grocery.query.all()
    # form = ItemForm()
    # session['itemToRemove'] = form.item.data
    
    if request.method == 'POST':
        removeItems = request.form.getlist('removeItem')

        # removeItems = session.get('itemToRemove') # This comes from the class's variable name - look for %-%
        for item in removeItems:
            print(f'Remove: {item}')
            itemToRemoveSQLQUERY = Grocery.query.filter_by(itemName=item).first()
            if itemToRemoveSQLQUERY:

                db.session.delete(itemToRemoveSQLQUERY)            
                session['failState'] = False
                session['successState'] = True
                 
            else:
                session['failState'] = True
                session['successState'] = False
                
        db.session.commit()
        if len(removeItems) > 1:
            itemString = ', '.join(removeItems)
            session['removedItem'] = itemString
        else:
            session['removedItem'] = removeItems[0]
        # session['itemToAdd'] = form.itemToAdd.data
        return redirect(url_for('shoppingRemove'))


    return render_template('remove.html', items=shoppingItems, fail=session.get('failState', False), success=session.get('successState', False), removedItems=session.get('removedItem', False))

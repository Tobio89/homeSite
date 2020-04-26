import os

from flask import Flask, render_template, session, redirect, url_for, request, flash

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message


from wtforms import StringField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional

import setENV

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# SQL APP CONFIGURATIONS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# MAIL APP CONFIGURATIONS

# The gmail settings are cut-and-paste
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['MAIL_SUBJECT_PREFIX'] = '[Homesite]'
app.config['MAIL_SENDER'] = 'From homeSite <homesite1004@gmail.com>'



# APP INITIALISATIONS
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
mail = Mail(app)



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



# Functions

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    # msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)




# FLASK ROUTES / SITE PAGES

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/schedule')
def schedule():
   
    return render_template('schedule.html')

@app.route('/schedule/edit')
def editSchedule():
   
    return render_template('editschedule.html')

@app.route('/shopping', methods=['GET', 'POST'])
def shopping():
    
    shoppingItems = Grocery.query.all()

    recipientEmailAddress = None
    if request.method == 'POST':
        recipient = request.form.get('emailRecipient')
        if recipient == 'Toby':
            recipientEmailAddress = os.environ.get('TOBY_ADDRESS')
        elif recipient == 'Eileen':
            recipientEmailAddress = os.environ.get('EILEEN_ADDRESS')
        
        if recipientEmailAddress:
            send_email(recipientEmailAddress, 'Your Shopping List', 'shoppingMail', items=shoppingItems)
            print(f'Email sent to {recipientEmailAddress}')
            flash(f'Your shopping list was mailed to {recipient}')
        



    return render_template('shopping.html', items=shoppingItems)
    
@app.route('/shopping/add', methods=['GET', 'POST'])
def shoppingAdd():

    # Clear the shopping states


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
                
                 
            else:
                session['failState'] = True
                
                
        db.session.commit()
        if len(removeItems) > 1:
            itemString = ', '.join(removeItems)
            flash(f'The following items were removed: {itemString}')
        else:
            flash(f'The item: {removeItems[0]} was removed.')
        # session['itemToAdd'] = form.itemToAdd.data
        return redirect(url_for('shoppingRemove'))


    return render_template('remove.html', items=shoppingItems, fail=session.get('failState', False))

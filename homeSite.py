import os, random
from datetime import datetime

from flask import Flask, render_template, session, redirect, url_for, request, flash

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_migrate import Migrate

from wtforms import StringField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional

from parcelChecker import getCJParcelStatus, getHanJinParcelStatus, getLotteParcelStatus
from tasks import recurringTask, oneTimeTask, getTimelessDate

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
migrate = Migrate(app, db)
# moment = Moment(app)


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

class Schedule(db.Model): # This DB 'table' will only contain one cell. :D
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    stringSchedule = db.Column(db.String(64))

class ParcelInfo(db.Model): # Store Parcel Information
    __tablename__ = 'parcelInfo'
    id = db.Column(db.Integer, primary_key=True)
    trackingNumber = db.Column(db.String(64))
    company = db.Column(db.String(64))
    description = db.Column(db.String(64))
    delivered = db.Column(db.Boolean(), default=False) #Store simple bool for is delivered - use for CSS styling
    status = db.Column(db.String(64)) #Store short parcel status note
    timestamp = db.Column(db.DateTime()) #Store last update's timestamp
    location = db.Column(db.String(64)) #Store last update's location 
    extraNotes = db.Column(db.String(64)) #Store extra notes if given

class Tasks(db.Model): # Keep task object information
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    isSingleUse = db.Column(db.Boolean(), default=False)
    createdDate = db.Column(db.DateTime())
    interval = db.Column(db.Integer())
    delay = db.Column(db.Integer(), default=0)
    completedDate = db.Column(db.DateTime()) #No date = not completed. Save date, and when this date is past, task can be removed automatically.


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

def getWisdom():
    wisPath = './wisdomSlices'
    pearls = [txtFile for txtFile in os.listdir(wisPath) if txtFile.endswith('.txt')]
    randomPearl = random.choice(pearls)

    with open(os.path.join(wisPath, randomPearl),  'r') as pearlFile:
        pearlText = pearlFile.read()
    return pearlText

# Constant Variables

timeList = [f'{num}'.zfill(2) for num in range(0, 24)]
parcelProviders = ['HanJin', 'CJ', 'Lotte']


# FLASK ROUTES / SITE PAGES

@app.route('/')
def index():
    content = getWisdom()
    return render_template('index.html', textContent=content)

@app.route('/schedule',  methods=['GET', 'POST'])
def schedule():
    

    scheduleString = Schedule.query.first().stringSchedule

    if not scheduleString:
        scheduleString = 'EEEEEEEETTTTTBEETTTEEETT'

    scheduleList = [letter for letter in scheduleString]

    

    combined_schedule = []
    for i in range(len(timeList)):
        combined_schedule.append(
            {
                'hour' : timeList[i],
                'sched': scheduleList[i]
            }
        )

    
    currentHour = datetime.now().hour

    if request.method == 'POST':

        
        if 'submitEdit' in request.form:
            newSchedule = request.form.getlist('newSchedule')
            newSchedule_joined = ''.join(newSchedule)
            print(newSchedule_joined)

            if newSchedule_joined == scheduleString:
                flash(f' No changes detected', 'info')
                print('Requested schedule is the same as old schedule - no changes made')

            else:
                schedule_loaded_from_database = Schedule.query.first()
                schedule_loaded_from_database.stringSchedule = newSchedule_joined
                db.session.commit()
                print(f'Edited to: {newSchedule_joined}')
                flash('Schedule updated', 'success')
                return redirect(url_for('schedule'))
            

            

    
   
    return render_template('schedule.html', schedule=combined_schedule, currentHour=str(currentHour))

@app.route('/schedule/edit', methods=['GET', 'POST'])
def editSchedule():

    scheduleString = Schedule.query.first().stringSchedule
    scheduleList = [letter for letter in scheduleString]

    # tableList = zip(timeList, scheduleList)

    if request.method == 'POST':
        print('Schedule edit request')
        newSchedule = request.form.getlist('newSchedule')
        newSchedule_joined = ''.join(newSchedule)

        if newSchedule == scheduleList:
            print('Schedule is the same - no change made')
            flash(f' No changes detected')

        else:
            schedule_loaded_from_database = Schedule.query.first()
            schedule_loaded_from_database.stringSchedule = newSchedule_joined
            db.session.commit()
            print(f'Edited to: {newSchedule_joined}')
            return redirect(url_for('schedule'))

   
    return render_template('editschedule.html', timeTitle=timeList, schedule=scheduleList,)

@app.route('/shopping', methods=['GET', 'POST'])
def shopping():
    
    
    shoppingItems = Grocery.query.all()

    recipientEmailAddress = None
    if request.method == 'POST':

        if 'remove' in request.form:
            itemsToRemove = request.form.getlist('itemToRemove')
            print(itemsToRemove)
            if itemsToRemove:

                for item in itemsToRemove:
                    itemToRemoveSQLQUERY = Grocery.query.filter_by(itemName=item).first()
                    db.session.delete(itemToRemoveSQLQUERY)


                db.session.commit()

                if len(itemsToRemove) > 1:

                    flash(f"Items {', '.join(itemsToRemove)} removed from list", 'success')
                else:
                    flash(f'Item {itemsToRemove[0]} removed from list', 'success')

                return redirect(url_for('shopping'))


            else:
                flash('No items selected to remove', 'danger')
        elif 'eileen' in request.form:

            recipientEmailAddress = os.environ.get('EILEEN_ADDRESS')

            send_email(recipientEmailAddress, 'Your Shopping List', 'shoppingMail', items=shoppingItems)
            print(f'Email sent to {recipientEmailAddress}')
            flash(f'The shopping list was mailed to Eileen', 'success')


        elif 'toby' in request.form:

            recipientEmailAddress = os.environ.get('TOBY_ADDRESS')
            
            send_email(recipientEmailAddress, 'Your Shopping List', 'shoppingMail', items=shoppingItems)
            print(f'Email sent to {recipientEmailAddress}')
            flash(f'The shopping list was mailed to Toby', 'success')
        
        elif 'addItem' in request.form:

            newItem_name = request.form.get('itemName')
            newItem_quantity = request.form.get('itemQuant')

            if newItem_name[0].islower():
                newItem_name = newItem_name.capitalize()

            if newItem_quantity:
                if int(newItem_quantity) < 2: #Most items are 1 so there's no need to display it.
                    newItem_quantity = None
                else:
                    newItem_quantity = int(newItem_quantity) #Int-ifty the number.

            db.session.add(Grocery(itemName=newItem_name, quantity=newItem_quantity))

            db.session.commit()

            flash(f'Added new item: {newItem_name} {newItem_quantity}', 'success' )

            return redirect(url_for('shopping'))




    return render_template('shopping.html', items=shoppingItems)
    
@app.route('/shipping', methods=['GET', 'POST'])
def shipping():

    parcelsCurrentlyTracked = ParcelInfo.query.all()

    if request.method == 'POST':
        
        if 'addParcelInfo' in request.form:

            newItem_deliveryCompany = request.form.get('selectedParcelProvider')
            newItem_parcelNumber = request.form.get('parcelNumber')
            newItem_description = request.form.get('parcelDescription')

            db.session.add(ParcelInfo(trackingNumber=newItem_parcelNumber, company=newItem_deliveryCompany, description=newItem_description, delivered=False))

            print(f"Add parcel {newItem_parcelNumber} delivered by {newItem_deliveryCompany}. It's a {newItem_description}")
            db.session.commit()

            flash('Parcel added', 'info')

            return redirect(url_for('shipping'))
        
        elif "update" in request.form:

            print('Requested update tracking information')

            
            requestedParcel = request.form.get('parcelToUpdate')

            if requestedParcel:

                print(requestedParcel)

                queriedParcel = ParcelInfo.query.filter_by(id=requestedParcel).first()

                timestamp_whenLastChecked = queriedParcel.timestamp

                if queriedParcel.company == "CJ":
                    print('Initialising CJ Tracking check')
                    tracking_results = getCJParcelStatus(queriedParcel.trackingNumber)
                
                elif queriedParcel.company == "Lotte":
                    print('Initialising Lotte Tracking check')
                    tracking_results = getLotteParcelStatus(queriedParcel.trackingNumber)

                elif queriedParcel.company == "HanJin":
                    print('Initialising HanJin Tracking check')
                    tracking_results = getHanJinParcelStatus(queriedParcel.trackingNumber)

                if tracking_results:

                    timestamp_whenCheckedThisTime = tracking_results['dateTime']

                    if timestamp_whenCheckedThisTime == timestamp_whenLastChecked: #Check to see if anything has changed
                        #If not, show this nessage
                        flash("There is no new information - your parcel's status hasn't changed.", 'info')
                    
                    else:
                        #Else, update the info in the DB - now that it's worth doing.
                        trackingError = tracking_results['error']
                        queriedParcel.status = tracking_results['status']
                        queriedParcel.location = tracking_results['location']
                        queriedParcel.timestamp = tracking_results['dateTime']
                        queriedParcel.extraNotes = tracking_results['extra']

                        if tracking_results['status'] == '배달완료':
                            queriedParcel.delivered = True
                    
                        db.session.commit()

                        if trackingError:
                            flash(f'Tracking Number / Company error:\nCheck Number and Company and try again.', 'danger')
                        else:

                            flash(f'Collected tracking info for {queriedParcel.trackingNumber}', 'success')

                        return redirect(url_for('shipping'))
                
                else:

                    flash('Failed to collect tracking info', 'danger')
            else:
                
                flash("No parcel selected to update: can't update", 'info')
        
        elif "remove" in request.form:
            print('Requested remove parcel')

            requestedParcel = request.form.get('parcelToUpdate')

            if requestedParcel:

                queriedParcel = ParcelInfo.query.filter_by(id=requestedParcel).first()

                db.session.delete(queriedParcel)

                db.session.commit()

                flash(f'Successfully deleted parcel: {queriedParcel.description}', 'info')

                return redirect(url_for('shipping'))

            else:

                flash("No parcel selected: can't delete.", 'info')


    return render_template('shipping.html', companies=parcelProviders, parcels=parcelsCurrentlyTracked)


@app.route('/tasks', methods=['GET', 'POST'])
def tasks():

    loadedTasks = Tasks.query.all()

    loadedTasks_taskObjects = []
    for task in loadedTasks:
        if task.isSingleUse:
            print(f'Task {task.name} is one-time')

            if task.createdDate < getTimelessDate(datetime.today()):

                print("Scheduled one-time task was scheduled for before today :S")
                db.session.delete(task)
                db.session.commit()


            # Check if the task has a completed date allocated
            elif task.completedDate:
                
                #If that date was yesterday, get rid
                if getTimelessDate(task.completedDate) < getTimelessDate(datetime.today()):

                    print("It's old and will be removed")
                    db.session.delete(task)
                    db.session.commit()
                    
                else: #Tasks here are complete, but they were completed today.
                    taskObject = oneTimeTask(name=task.name, scheduledDate=task.createdDate, delayedDays=task.delay, completedDate=task.completedDate)
                    loadedTasks_taskObjects.append(taskObject)


            else: #Tasks that get here have no completed date, i.e they are still to be done.
                taskObject = oneTimeTask(name=task.name, scheduledDate=task.createdDate, delayedDays=task.delay)
                loadedTasks_taskObjects.append(taskObject)


        # Tasks that get to this else are recurring tasks. Their completed date is less important.
        else:
            completedDate = task.completedDate
            if completedDate:
                print(f'{task.name} has been completed before')
                if task.completedDate < getTimelessDate(datetime.today()): #To reset completion if it's old, so that it shows up due next time.
                    print('It was completed before today')
                    completedDate = None
                
            
            taskObject = recurringTask(name=task.name, createdDate=task.createdDate, interval=task.interval, delayedDays=task.delay, completedDate=completedDate)
                    
            loadedTasks_taskObjects.append(taskObject)



    dueToday = [task for task in loadedTasks_taskObjects if task.isDue(datetime.today())]
    otherTasks = [task for task in loadedTasks_taskObjects if not task.isDue(datetime.today())]


    if request.method == 'POST':

        if 'remove' in request.form:

            taskToRemove = request.form.get('taskToUpdate')

            if taskToRemove:
                print('remove')
                queriedTask = Tasks.query.filter_by(name=taskToRemove).first()
                db.session.delete(queriedTask)
                db.session.commit()

                flash(f"Task '{queriedTask.name}' removed", 'success')

                return redirect(url_for('tasks'))

            else:
                flash('No task selected to remove', 'danger')

        elif 'delay' in request.form:

            taskToDelay = request.form.get('taskToUpdate')

            if taskToDelay:
                print('delay')
                queriedTask = queriedTask = Tasks.query.filter_by(name=taskToDelay).first()
                queriedTask.delay += 1

                db.session.commit()

                flash(f"Task '{queriedTask.name}' delayed by one day", 'success')

                return redirect(url_for('tasks'))
            else:
                flash('No task selected to delay', 'danger')
            
        elif 'complete' in request.form:

            taskToMarkCompleted = request.form.get('taskToUpdate')

            if taskToMarkCompleted:
                print('complete')
                queriedTask = Tasks.query.filter_by(name=taskToMarkCompleted).first()
                queriedTask.completedDate = getTimelessDate(datetime.today())

                db.session.commit()

                flash(f"Task '{queriedTask.name}' marked as completed", 'success')

                return redirect(url_for('tasks'))

            else:
                flash('No task selected to mark as completed', 'danger')


        elif 'addTask' in request.form:

            newTaskIsRecurring = request.form.get('isRecurring')
            print(newTaskIsRecurring)
            newTaskDescription = request.form.get('taskDescription')
            newTaskStartingDate = datetime.strptime(request.form.get('taskDate'), '%Y-%m-%d')

            # Is the task going to recurr...
            if newTaskIsRecurring:
                newTaskStartingInterval = int(request.form.get('taskInterval'))

                if newTaskStartingInterval > 0: #To handle an interval of 0

                    print('Add recurring task')
                    print(newTaskDescription)

                    db.session.add(Tasks(name=newTaskDescription, createdDate=newTaskStartingDate, interval=newTaskStartingInterval))
                    db.session.commit()

                    flash(f"Recurring Task '{newTaskDescription}' added", 'success')

                    return redirect(url_for('tasks'))
                else:
                    #Warn user that the interval was 0, which doesn't make sense
                    flash("Oops - The interval can't be zero.", "danger")
            
            #...Or is it a one-time thing
            else:
                print('Add one-time task')

                db.session.add(Tasks(name=newTaskDescription, createdDate=newTaskStartingDate, isSingleUse=True))
                db.session.commit()

                flash(f"One-Time Task '{newTaskDescription}' added", 'success')

                return redirect(url_for('tasks'))


        elif 'removeOther' in request.form:

            
            taskToRemove = request.form.get('undueTaskToRemove')

            if taskToRemove:

                print('remove')
                queriedTask = Tasks.query.filter_by(name=taskToRemove).first()
                db.session.delete(queriedTask)
                db.session.commit()

                flash(f"Task '{queriedTask.name}' removed", 'success')

                return redirect(url_for('tasks'))
            else:
                flash('No task selected to remove', 'danger')

            



            




    return render_template('tasks.html', todayTasks=dueToday, otherTasks=otherTasks)
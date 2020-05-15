from . import db



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


from datetime import datetime, timedelta




def getTimelessDate(dateObject):
    if dateObject:    
        return datetime(dateObject.year, dateObject.month, dateObject.day)
    else:
        return None


class recurringTask():
    def __init__(self, name, createdDate, interval, delayedDays=0, completedDate=None):
        self.name = name
        self.taskType = 'recurring'
        self.createdDate = getTimelessDate(createdDate)
        self.interval = timedelta(days=interval)
        self.completedDate = getTimelessDate(completedDate)

        self.__delay = timedelta(days=delayedDays)


    @property
    def delay(self):
        return self.__delay
    
    @delay.setter
    def delay(self, setDelay):
        setDelta = timedelta(days=setDelay)
        self.__delay = setDelta

    def isDue(self, queryDate):

        timeLessQueryDate = getTimelessDate(queryDate)

        dateDifference = timeLessQueryDate - (self.createdDate + self.delay)

        if dateDifference == timedelta(0):

            return True 
        
        elif dateDifference % self.interval == timedelta(0):

            return True
        
        return False
    
class oneTimeTask():
    def __init__(self, name, scheduledDate, delayedDays=0, completedDate=None):
        self.name = name
        self.taskType = 'single'
        self.scheduledDate = getTimelessDate(scheduledDate)
        self.completedDate = getTimelessDate(completedDate)
        
        self.__delay = timedelta(days=delayedDays)

    @property
    def delay(self):
        return self.__delay
    
    @delay.setter
    def delay(self, setDelay):
        setDelta = timedelta(days=setDelay)
        self.__delay = setDelta

    def isDue(self, queryDate):

        timeLessQueryDate = getTimelessDate(queryDate)

        dateDifference = timeLessQueryDate - (self.scheduledDate + self.delay)

        if dateDifference == timedelta(0):

            return True 
        
               
        return False

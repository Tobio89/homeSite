from datetime import datetime, timedelta




def getTimelessDate(dateObject):
    
    return datetime(dateObject.year, dateObject.month, dateObject.day)


class recurringTask():
    def __init__(self, name, createdDate, interval, delayedDays=0):
        self.name = name
        self.createdDate = getTimelessDate(createdDate)
        self.interval = timedelta(days=interval)
        
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
        print(dateDifference)


        if dateDifference == timedelta(0):

            return True 
        
        elif dateDifference % self.interval == timedelta(0):

            return True
        
        return False
    

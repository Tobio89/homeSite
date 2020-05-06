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
            print('Due today')
            return True 
        
        elif dateDifference % self.interval == timedelta(0):
            print('Scheduled day is today - due')
            return True
        
        
        print('Not due')
        return False
    


todayDate = getTimelessDate(datetime.today())
threeDaysLater = todayDate + timedelta(days=9)

task1 = recurringTask('Wipe cabinet', todayDate, 3)

task1.delay = 0

print(task1.isDue(threeDaysLater))
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
    def dueDate(self):
        timelessToday = getTimelessDate(datetime.today())
        adjustedCreatedDate = (self.createdDate + self.delay)
        if adjustedCreatedDate > timelessToday: #Catch possibility of created/scheduled date being after than today
            print(f'Task {self.name} is first due later than today')
            daysLater = (adjustedCreatedDate - timelessToday).days
            if daysLater == 1:
                print(f'Task {self.name} is due tomorrow\n')
                return 'Due tomorrow'
            else:
                print(f'Task {self.name} is due {daysLater} days later\n')
                return f'Due in {daysLater} days'
        else:
            print(f'Task {self.name} was first due {self.createdDate}')
            howLongAgo = timelessToday - adjustedCreatedDate

            if howLongAgo < self.interval: #If the task was made less than self.inverval days ago
                print(f'Task {self.name} was first due not that long ago\n')
                nextDue = self.interval - howLongAgo
                if nextDue.days == 1:
                    return 'Due tomorrow'
                else:
                    return f'Due in {nextDue.days} days'
            else:
                print(f'Task {self.name} was first due a while ago')
                adjustedLongAgo = (howLongAgo % self.interval)
                print(f'It has completed {howLongAgo // self.interval} cycle(s)')
                print(f'It was last due {adjustedLongAgo} days ago')
                adjustedDue = (timelessToday - adjustedLongAgo) + self.interval

                nextDue = adjustedDue - timelessToday

                print(f'It should be due on {adjustedDue}')
                print(f'Which is {nextDue.days} days from now\n')
                if nextDue.days == 1:
                    return 'Due tomorrow'
                else:
                    return f'Due in {nextDue.days} days'


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
    def dueDate(self):
        howLongTilDue = (self.scheduledDate - getTimelessDate(datetime.today())).days

        if howLongTilDue == 1:
            return 'Due tomorrow'
        else:
            return f'Due in {howLongTilDue} days'

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

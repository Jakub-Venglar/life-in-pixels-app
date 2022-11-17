#! python3
import calendar
import datetime
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivy.factory import Factory # because we need popup

superColor= ()
goodColor=()
averageColor=()
badColor=()

keepResults={}


class LifeLayout(MDWidget):
    #create calendar view - default is current date and set a list of field ids
    def make_Cal(self,now=False, year=2020, month=6):        
        c = calendar.Calendar(0)
        calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]

        #this creates list of date objects
        if now==True:
            currentCal = c.monthdatescalendar(datetime.datetime.now().year, datetime.datetime.now().month)
            monthToShow = datetime.datetime.now().strftime("%B")
        else:
            currentCal = c.monthdatescalendar(year, month)
            myDate = datetime.date(year, month, 7)
            monthToShow = myDate.strftime("%B")
        #iterate through crated calendar and set a day number for every field
        #also sed date id for every field
        for weeknum, week in enumerate(calList):
            for daynum, day in enumerate(week):
                id = calList[weeknum][daynum]
                setDate = currentCal[weeknum][daynum]
                self.ids[id].text = str(setDate.day)
                self.ids.CurrentMonth_label.text = str(monthToShow)
                self.ids[id].date_id = str(setDate)

                #make current day more visible

                if setDate == datetime.datetime.date(datetime.datetime.now()):
                    self.ids[id].newsize=50
                    self.ids[id].newOutWidth=1.2
                    self.ids[id].newTextColor= (.8,.8,.8,1)

    
    #open popup and handle variables

    def cal_click(self, date_id, my_id):
        popup = Factory.MoodPopup()
        popup.open()
        self.date_id = date_id
        self.my_id = my_id
        
    def pop_click(self,value):
        print(self.date_id)
        print(self.my_id)
        self.ids[self.my_id].text = str(value)
        keepResults[self.date_id] = value
        print(keepResults)
    
    def move_month(self,direction):
        pass

    def move_year(self,direction):
        pass

#TODO: save selected to clicked button as color --> cuurently used words
#TODO: add option to change months
#TODO: save everything to database or file
#TODO: add comment, which can be opened
#TODO: add picture

# run app and construct calendar

class LifePixels(MDApp):
    def build(self):
        return LifeLayout()
    def on_start(self):
        self.root.make_Cal()

if __name__ == "__main__":

    LifePixels().run()

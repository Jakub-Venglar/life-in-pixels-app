#! python3
import calendar
from datetime import datetime
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivy.factory import Factory # because we need popup

superColor= ()
goodColor=()
averageColor=()
badColor=()


class LifeLayout(MDWidget):
    #create calendar view - default is current date and set a list of field ids
    def make_Cal(self):
        global keepResults
        keepResults={}
        c = calendar.Calendar(0)
        calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]

        #this creates list of date objects
        currentCal = c.monthdatescalendar(datetime.now().year, datetime.now().month)

        #iterate through crated calendar and set a day number for every field
        #also sed date id for every field
        for weeknum, week in enumerate(calList):
            for daynum, day in enumerate(week):
                id = calList[weeknum][daynum]
                setDate = currentCal[weeknum][daynum]
                self.ids[id].text = str(setDate.day)
                self.ids[id].date_id = str(setDate)
                if setDate == datetime.date(datetime.now()):
                    self.ids[id].newsize=50
                    self.ids[id].newOutWidth=1.2
                    self.ids[id].newTextColor= (.8,.8,.8,1)

    
    #open popup and handle variables

    def cal_click(self, date_id, my_id):
        popup = Factory.MoodPopup()
        popup.open()
        """
        global id_var
        global date_var
        id_var = my_id
        date_var = date_id
        print(id_var)
        print(date_var)"""
        return date_id, my_id
    
    def pop_click(self,value):
        global id_var
        global date_var
        keepResults
        self.ids[id_var].text = str(value)
        keepResults[date_var] = value
        id_var=''
        date_var = ''
        print(keepResults)


#TODO: save selected to clicked button as color --> cuurently used words
#TODO: add option to change months
#TODO: save everything to database or file

# run app and construct calendar

class LifePixels(MDApp):
    def build(self):
        return LifeLayout()
    def on_start(self):
        self.root.make_Cal()

if __name__ == "__main__":

    LifePixels().run()

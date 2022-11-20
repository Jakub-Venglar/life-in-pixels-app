#! python3
import calendar, datetime, os, sys, json
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivy.factory import Factory # because we need popup

superColor= (.2,.3,.6,1)
goodColor=(0,.5,1,1)
averageColor=(.9,0,1,1)
badColor=(.1,.1,.1,1)

"""dateData = {
    "2022-11-09": "bad",
    "2022-11-15": "good",
    "2022-11-18": "good",
    "2022-11-24": "good",
    "2022-11-10": "super",
    "2022-11-17": "good",
    "2022-11-22": "bad",
    "2022-11-25": "good",
    "2022-11-26": "super",
    "2022-11-08": "bad",
    "2022-11-14": "good"
}"""

class LifeLayout(MDWidget):

    def create_user_directory(self):
        #make sure working directory is set the same as file directory
        os.chdir(os.path.dirname(sys.argv[0]))
        #create directory if not existing
        try:
            os.mkdir('./userdata/')
        except FileExistsError:
            pass

    def pass_data(self):        
            try:   
                with open('./userdata/caldata.json', 'r', encoding='utf-8') as file:
                    return eval(file.read())
            except FileNotFoundError: 
                with open('./userdata/caldata.json', 'w', encoding='utf-8') as file:
                    file.write('{}')
                    return {}

    def save_data(self, newData):
        with open('./userdata/caldata.json', 'w', encoding='utf-8') as file:
            json.dump(newData, file, indent = 4)
    
    def delete_data(self):
        with open('./userdata/caldata.json', 'w', encoding='utf-8') as file:
            file.write('{}')
        self.make_Cal()

    #create calendar view

    def make_Cal(self,now=True, year=2020, month=6):
        dateData = self.pass_data()
        c = calendar.Calendar(0)
        calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]

        #this creates list of date objects for current month at program start or home press

        if now==True:
            currentCal = c.monthdatescalendar(datetime.datetime.now().year, datetime.datetime.now().month)
            monthLabel = datetime.datetime.now().strftime("%B %Y")
            self.monthID = str(datetime.datetime.now().month)
            self.yearID = str(datetime.datetime.now().year)

        #this will create list of date objects for given year and month
        else:
            currentCal = c.monthdatescalendar(year, month)
            newDate = datetime.date(year, month, 7)
            monthLabel = newDate.strftime("%B %Y")
            self.monthID = str(month)
            self.yearID = str(year)

        #iterate through crated calendar and set a day number for every field
        #also sed date id for every field
        
        for weeknum, week in enumerate(calList):
            for daynum, day in enumerate(week):
                id = calList[weeknum][daynum]
                setDate = currentCal[weeknum][daynum]
                self.ids[id].text = str(setDate.day)
                self.ids.month_Label.text = str(monthLabel)
                self.ids[id].date_id = str(setDate)

                #make current day more visible

                if setDate == datetime.datetime.date(datetime.datetime.now()):
                    #self.ids[id].newsize=50
                    #self.ids[id].newOutWidth=1.2
                    #self.ids[id].newTextColor= (.8,.8,.8,1)
                    self.ids[id].text = '[b]>' + self.ids[id].text + '<[/b]'
                
                # if mood for date already set then render it

                if self.ids[id].date_id in dateData:
                    self.ids[id].background_color = self.choose_color(dateData[self.ids[id].date_id])

    # next or previous month after click

    def move_month(self,direction):
        if direction == 'forward':
            month = int(self.monthID)
            month +=1
            if month > 12:
                year = int(self.yearID) + 1
                month = 1
            else:
                year = int(self.yearID)
        else:
            month = int(self.monthID)
            month -=1
            if month < 1:
                year= int(self.yearID) - 1
                month = 12
            else:
                year = int(self.yearID)

        self.make_Cal(now=False, year=year, month=month)

    def move_year(self,direction):
        month = int(self.monthID)
        if direction == 'forward':
            year = int(self.yearID) + 1
        else: 
            year= int(self.yearID) - 1
        self.make_Cal(now=False, year=year, month=month)
    
    def present_click(self):
        self.make_Cal(now=True)


    #open popup and handle variables
    def choose_color(self, value):
        if value == 'super':
            return superColor
        if value == 'good':
            return goodColor
        if value == 'average':
            return averageColor
        if value == 'bad':
            return badColor

    #click on any date, call popup 

    def cal_click(self, date_id, my_id):
        popup = Factory.MoodPopup()
        popup.open()
        self.date_id = date_id
        self.my_id = my_id
    
    #click at pop pop up write values into calendar

    def pop_click(self,value):
        dateData = self.pass_data()
        print(self.date_id)
        print(self.my_id)
        self.ids[self.my_id].background_color = self.choose_color(value)
        dateData[self.date_id] = value
        self.save_data(dateData)
        print(dateData)
        #with open('./userdata/caldata.txt', 'w', encoding='utf-8') as file:
        #    file.write(dateData)

#TODO: improve pop up - vertical layout AND label with date and description
#TODO: improve colors and overal layout
#TODO: save everything to database or file
#TODO: add comment, which can be opened
#TODO: add picture

# run app and construct calendar

class LifePixels(MDApp):
    def build(self):
        return LifeLayout()
    def on_start(self):
        self.root.create_user_directory()
        self.root.make_Cal()

if __name__ == "__main__":

    LifePixels().run()

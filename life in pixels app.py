#! python3
# Life in pixels project
import calendar, datetime, os, sys, json, random
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder
from kivy.clock import Clock
from functools import partial
from sortedcontainers import SortedDict
from kivy.graphics import Rectangle
from babel.dates import format_date

#TODO: learn how to properly comment and add comments and docstrings
#TODO: add loading screen and wait until calendar and widow are constructed
#TODO: add habits/activities, render them if accomplished on the main calendar - possibility to track them (show how many or just checkbox if accomplished)
#TODO: ask for name at the begining and personalize saved files (because of possible multiuser in future)
#TODO: finish tutorials so I have better idea what I am doing :)
#TODO: use sorted dict, avoid loading everything (one year should be enough) - one file for every year
#TODO: solve how to show habit labels
#TODO: add option for set your own colors
#TODO: choice from default pictures or your own as BG
#TODO: add, picture of the day, copy to dedicated folder and name it, backup
#TODO: make printable page, with summary of the year/month
#TODO: sync between computer and mobile app - at PC you can see better bigger picture
#TODO: backup possibilities
# maybe todo: add location on the map, later show pins on the map


if platform == 'android':
    from android.storage import app_storage_path
    settings_path = app_storage_path()

    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()

    from android.storage import secondary_external_storage_path
    secondary_ext_storage = secondary_external_storage_path()

    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

if platform == 'win':
    Window.size = (400*1.5, 712*1.5)
    Window.top = 50
    Window.left = 50

test= SortedDict({'uh':'oh','ahoj':'none'})

emptyDayData = {'mood':'','comment':''}
fsDivider = 35

superColor= (255/255,232/255,28/255,.8) #(227/255,65/255,25/255,.8)
goodColor=(43/255,168/255,8/255,.8)
averageColor=(138/255,153/255,184/255,.8)
badColor= (117/255,32/255,16/255,.8) #(150/255,39/255,20/255,.8)
terribleColor=(28/255,49/255,36/255,.8)
clearColor = (.5,.5,.5,.45)

today = (12/255,84/255,179/255,.8)
notToday = (12/255,84/255,179/255,0)

calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]
class YearObject():
    def __init__(self, year, data):
        self.year = year
        self.data = data


#define screens
class CalendarWindow(MDScreen):
        # construct labels for cal buttons
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize = self.labelSize)


    def labelSize(self,x=1,y=1,z=1,clocktime=0):
        self.manager.get_screen('CalLabels').fs = z/fsDivider

    def create_user_directory(self):
        if platform == 'android':
            path = os.path.join(settings_path, 'userdata')
            try:
                os.mkdir(path)
                os.chdir(path)
            except FileExistsError:
                os.chdir(path)

        else:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'userdata')
            #create directory if not existing
            try:
                os.mkdir(path)
                os.chdir(path)
            except FileExistsError:
                os.chdir(path)
    
    def switch_to_ext_storage(self):
        pass
    
    def pass_data(self,date_id):
        year = str(date_id)[:4]
        if year != self.currentYear:
            self.currentYear = year
            try:   
                with open(f'caldata-{year}.json', 'r', encoding='utf-8') as file:
                    yearData =  eval(file.read())
            except FileNotFoundError: 
                with open(f'caldata-{year}.json', 'w', encoding='utf-8') as file:
                    file.write('{}')
                    yearData =  {}
            self.yearData = yearData
            #thisYear = YearObject(year,yearData)
        return self.yearData

    def save_data(self, newData, date_id):
        year = str(date_id)[:4]
        with open(f'caldata-{year}.json', 'w', encoding='utf-8') as file:
            json.dump(newData, file, indent = 4)
    
    def delete_data(self,date_id):
        year = str(date_id)[:4]
        with open(f'caldata-{year}.json', 'w', encoding='utf-8') as file:
            file.write('{}')
        self.make_Cal(now=True)
        self.make_Cal(now=True) # clock is not working but this yes....

    #create calendar view

    def make_Cal(self,now=True, year=2020, month=6):
        self.manager.get_screen('CalLabels').fs = Window.size[1]/fsDivider
        c = calendar.Calendar(0)

        #this creates list of date objects for current month at program start or home press

        if now==True:
            currentCal = c.monthdatescalendar(datetime.datetime.now().year, datetime.datetime.now().month)
            now = datetime.datetime.now()
            monthLabel = format_date(datetime.datetime.now(),"LLLL y", locale='cs_CZ').capitalize() #now.strftime("%B %Y").capitalize()
            self.monthID = str(datetime.datetime.now().month)
            self.yearID = str(datetime.datetime.now().year)
            #self.dateToShow = datetime.datetime.now().("%B")

        #this will create list of date objects for given year and month
        else:
            currentCal = c.monthdatescalendar(year, month)
            newDate = datetime.date(year, month, 7)
            monthLabel = format_date(newDate,"LLLL y", locale='cs_CZ').capitalize()
            self.monthID = str(month)
            self.yearID = str(year)
            #self.dateToShow = format_date(newDate,format='long', locale='cs')

        #iterate through crated calendar and set a day number for every field
        #also sed date id for every field
        
        for weeknum, week in enumerate(calList):
            for daynum, day in enumerate(week):
                id = calList[weeknum][daynum]
                setDate = currentCal[weeknum][daynum]
                self.ids[id].text = str(setDate.day)
                self.ids.month_Label.text = str(monthLabel)
                self.ids[id].date_id = setDate
                self.ids[id].clear_widgets()
                self.ids[id].today = notToday

                #make current day more visible
                if setDate == datetime.datetime.date(datetime.datetime.now()):
                    self.ids[id].today = today
                
                # if mood for date already set then render it, otherwise make field clear
                Clock.schedule_once(partial(self.colorize,id,self.ids[id].date_id))
        
        self.ids['delete'].date_id = self.ids['3-3'].date_id #set id for deleting whole calendar

    def colorize(self,my_id,date_id,clocktime=0):
        call = self.manager.get_screen('Calendar')
        calLabels = self.manager.get_screen('CalLabels')
        dateData = call.pass_data(date_id)
        dateKey = str(date_id)
        calLabels.ids[my_id+'a'].text= ''
        calLabels.ids[my_id+'b'].text= ''
        calLabels.ids[my_id+'c'].text= ''
        calLabels.ids[my_id+'d'].text= ''
        try:
            if dateData[dateKey]['comment'] != '':
                calLabels.ids[my_id+'a'].text= 'T'
        except KeyError:
            pass
        if dateKey in dateData:
            call.ids[my_id].background_color = call.choose_color(dateData[str(self.ids[my_id].date_id)]['mood'])
        else: call.ids[my_id].background_color = clearColor
        Clock.schedule_once(partial(self.create_labels,my_id,dateData,dateKey))
        
    def create_labels(self,my_id,dateData, dateKey, clocktime=0):
        '''creates labels on canvas of calendar buttons with defined symbols'''
        call = self.manager.get_screen('Calendar')
        calLabels = self.manager.get_screen('CalLabels')
        labelIDa = calLabels.ids[my_id+'a']
        labelIDb = calLabels.ids[my_id+'b']
        labelIDc = calLabels.ids[my_id+'c']
        labelIDd = calLabels.ids[my_id+'d']
        calButtonID = call.ids[my_id]
        if dateKey in dateData:
            if dateData[dateKey]['comment'] != '':
                calLabels.ids[my_id+'a'].text= 'T'
            else: 
                calLabels.ids[my_id+'a'].text= ''
        calLabels.ids[my_id+'b'].text= ''
        calLabels.ids[my_id+'c'].text= ''
        calLabels.ids[my_id+'d'].text= ''
        call.ids[my_id].canvas.after.clear()
        with call.ids[my_id].canvas.after:
            Rectangle(size=labelIDa.texture_size, pos=(calButtonID.x, calButtonID.top-labelIDa.texture_size[1]), texture=labelIDa.texture)
            Rectangle(size=labelIDb.texture_size, pos=(calButtonID.right-labelIDb.texture_size[0], calButtonID.top-labelIDb.texture_size[1]), texture=labelIDb.texture)
            Rectangle(size=labelIDc.texture_size, pos=(calButtonID.right-labelIDc.texture_size[0], calButtonID.y), texture=labelIDc.texture)
            Rectangle(size=labelIDd.texture_size, pos=calButtonID.pos, texture=labelIDd.texture)

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
    
    def present_click(self, clocktime=0):
        self.make_Cal(now=True)

    # make colors
    
    def choose_color(cls, value):
        if value == 'super':
            return superColor
        if value == 'good':
            return goodColor
        if value == 'average':
            return averageColor
        if value == 'bad':
            return badColor
        if value == 'terrible':
            return terribleColor
        else:
            return clearColor
    
    #click on any date, call popup 

    def cal_click(self, date_id, my_id):
        self.manager.transition.direction = 'left'
        self.manager.current = 'DayMood'
        daySetting = self.manager.current_screen
        dateKey = str(date_id)
        dateData = self.pass_data(date_id)
        daySetting.date_id = date_id
        daySetting.my_id = my_id
        daySetting.current_date = format_date(date_id,"long", locale='cs_CZ')
        daySetting.ids.terrible.background_color = terribleColor
        daySetting.ids.bad.background_color = badColor
        daySetting.ids.average.background_color = averageColor
        daySetting.ids.good.background_color = goodColor
        daySetting.ids.super.background_color = superColor
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        daySetting.ids.question.bg = self.choose_color(dateData[dateKey]['mood'] )
        daySetting.ids.comment.text = dateData[dateKey]['comment']    

class DayWindow(MDScreen):
    #click at pop pop up write values into calendar

    def mood_click(self,value, text):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        dateData[dateKey]['mood'] =  value
        dateData[dateKey]['comment'] = text
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)

    
    def save_text(self, text):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        dateData[dateKey]['comment'] = text
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)

    def delete_day(self):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = emptyDayData.copy()
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)
        self.ids.comment.text= ''


class HabitsWindow(MDScreen):
    def load_habit_list(self):
        try:   
            with open('habits.json', 'r', encoding='utf-8') as file:
                return eval(file.read())
        except FileNotFoundError: 
            with open('habits.json', 'w', encoding='utf-8') as file:
                file.write('{}')
                return eval(file.read())

    def save_habit_list(self,to_save):
        with open('habits.json', 'w', encoding='utf-8') as file:
            file.write(to_save)
            return eval(file.read())

class SettingsWindow(MDScreen):
    def load_settings(self):
        try:   
            with open('settings.json', 'r', encoding='utf-8') as file:
                return eval(file.read())
        except FileNotFoundError: 
            with open('settings.json', 'w', encoding='utf-8') as file:
                file.write('{}')
                return eval(file.read())

    def save_settings(self,to_save):
        with open('settings.json', 'w', encoding='utf-8') as file:
            file.write(to_save)
            return eval(file.read())

class WindowManager(ScreenManager):
    pass

class CalendarLabels(MDScreen):
    pass

class ButtonLabel(Label):
    pass
    #def __init__(self, **kwargs):
    #    super(Explay, self).__init__(**kwargs)

# run app and construct calendar

class LifePixels(MDApp):
    def build(self):
        Builder.load_file('lifepixels.kv')
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(CalendarWindow(name='Calendar'))
        sm.add_widget(DayWindow(name='DayMood'))
        sm.add_widget(HabitsWindow(name='Habits'))
        sm.add_widget(SettingsWindow(name='Settings'))
        sm.add_widget(CalendarLabels(name='CalLabels'))
        sm.current = 'Calendar'
        return sm
        '''
    title = 'Life in pixels'
    def build(self):
        return CalendarWindow()'''
    def on_start(self):
        #self.root.create_user_directory()
        #self.root.make_Cal()
        #self.root.get_screen('Calendar').create_user_directory()
        self.root.current_screen.create_user_directory()
        self.root.current_screen.make_Cal()



if __name__ == "__main__":

    LifePixels().run()

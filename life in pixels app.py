#! python3
# Life in pixels project
import calendar, datetime, os, sys, json, time
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.widget import MDWidget
from kivy.factory import Factory #popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder
from babel.dates import format_date, format_datetime, format_time

#TODO: learn how to properly comment and add comments and docstrings
#TODO: ask for name at the begining and personalize saved files (because of possible multiuser in future)
#TODO: finish tutorials so I have better idea what I am doing :)
#TODO: make function for coloring calendar and writing labels
#TODO: circle around today
#TODO: add 5th mood
#TODO: improve pop up - colorize label according to set mood color
#TODO: improve colors and overal layout
#TODO: add option for set your own colors
#TODO: choice from default pictures or your own as BG
#TODO: add habits/activities, render them if accomplished on the main calendar - possibility to track them (show how many or just checkbox if accomplished)
#TODO: picture of the day
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
    
superColor= (227/255,65/255,25/255,.8)
goodColor=(43/255,168/255,8/255,.8)
averageColor=(138/255,153/255,184/255,.8)
badColor=(56/255,56/255,56/255,.8)
clearColor = (.5,.5,.5,.35)

calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]

#define screens
class CalendarWindow(Screen):
        # construct labels for cal buttons
    
    def __init__(self, **kwargs):
        super(CalendarWindow, self).__init__(**kwargs)
        Window.bind(on_resize = self.labelSize)

    def labelSize(self,x,y,z):
        self.fs = z/35

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


    def pass_data(self):        
            try:   
                with open('caldata.json', 'r', encoding='utf-8') as file:
                    return eval(file.read())
            except FileNotFoundError: 
                with open('caldata.json', 'w', encoding='utf-8') as file:
                    file.write('{}')
                    return {}

    def save_data(self, newData):
        with open('caldata.json', 'w', encoding='utf-8') as file:
            json.dump(newData, file, indent = 4)
    
    def delete_data(self):
        with open('caldata.json', 'w', encoding='utf-8') as file:
            file.write('{}')
        self.make_Cal()

    #create calendar view

    def make_Cal(self,now=True, year=2020, month=6):
        self.fs = Window.size[1]/35
        dateData = self.pass_data()
        c = calendar.Calendar(0)

        #this creates list of date objects for current month at program start or home press

        if now==True:
            currentCal = c.monthdatescalendar(datetime.datetime.now().year, datetime.datetime.now().month)
            monthLabel = format_date(datetime.datetime.now(),"LLLL y", locale='cs').capitalize()
            self.monthID = str(datetime.datetime.now().month)
            self.yearID = str(datetime.datetime.now().year)
            self.dateToShow = format_date(datetime.datetime.now(), format='long', locale='cs')

        #this will create list of date objects for given year and month
        else:
            currentCal = c.monthdatescalendar(year, month)
            newDate = datetime.date(year, month, 7)
            monthLabel = format_date(newDate,"LLLL y", locale='cs').capitalize()
            self.monthID = str(month)
            self.yearID = str(year)
            self.dateToShow = format_date(newDate,format='long', locale='cs')

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
                self.ids[id].add_widget(ButtonLabel())
                self.ids[id].add_widget(ButtonLabel(valign = 'top', halign ='right'))
                self.ids[id].add_widget(ButtonLabel(valign = 'bottom', halign ='right'))
                self.ids[id].add_widget(ButtonLabel(valign = 'bottom'))

                #make current day more visible

                if setDate == datetime.datetime.date(datetime.datetime.now()):
                    #self.ids[id].font_size=50
                    #self.ids[id].outline_width=1.2
                    #self.ids[id].color= (.8,.8,.8,1)
                    #self.ids[id].pict_source= 'pict/norsko.jpg'
                    self.ids[id].text = '[b]>' + self.ids[id].text + '<[/b]'
                
                # if mood for date already set then render it, otherwise make field clear
                
                # make function of this later

                dateKey = str(self.ids[id].date_id)
                if dateKey in dateData:
                    self.ids[id].background_color = self.choose_color(dateData[str(self.ids[id].date_id)]['mood'])
                    if dateData[dateKey]['comment'] != '':
                        self.ids[id].children[3].label='T'
                else: self.ids[id].background_color = clearColor


        #self.ids['1-1'].children[0].text = 'sadsa'

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

    # make colors

    def choose_color(self, value):
        if value == 'super':
            return superColor
        if value == 'good':
            return goodColor
        if value == 'average':
            return averageColor
        if value == 'bad':
            return badColor
        if value == '':
            return clearColor
    
    #click on any date, call popup 

    def cal_click(self, date_id, my_id):
        self.manager.transition.direction = 'left'
        self.manager.current = 'DayMood'
        daySetting = self.manager.current_screen
        """popup = Factory.MoodPopup()
        popup.open()"""
        dateKey = str(date_id)
        daySetting.date_id = date_id
        daySetting.my_id = my_id
        daySetting.current_date = format_date(date_id,format='long', locale='cs')
        daySetting.ids.bad.background_color = badColor
        daySetting.ids.average.background_color = averageColor
        daySetting.ids.good.background_color = goodColor
        daySetting.ids.super.background_color = superColor
        dateData = self.pass_data()
        dateData[dateKey] = dateData.setdefault(dateKey, {'mood':'average','comment': ''})
        daySetting.ids.comment.text = dateData[dateKey]['comment']
        print(self.ids['1-1'].children[0].parent.pos)
    

class DayWindow(Screen):
    #click at pop pop up write values into calendar

    def mood_click(self,value, text):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data()
        dateKey = str(self.date_id)
        call.ids[self.my_id].background_color = call.choose_color(value)
        dateData[dateKey] = dateData.setdefault(dateKey, {'mood':'average','comment':''})
        dateData[dateKey]['mood'] =  value
        dateData[dateKey]['comment'] = text
        call.save_data(dateData)

    
    def save_text(self, text):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data()
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, {'mood':'average','comment':''})
        dateData[dateKey]['comment'] = text
        call.save_data(dateData)

    def delete_day(self):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data()
        dateKey = str(self.date_id)
        dateData[dateKey] = {'mood':'','comment':''}
        call.save_data(dateData)
        call.ids[self.my_id].background_color = call.choose_color('')
        self.ids.comment.text= ''


class WindowManager(ScreenManager):
    pass

class ButtonLabel(Label):
    pass
    #def __init__(self, **kwargs):
    #    super(Explay, self).__init__(**kwargs)

# run app and construct calendar

class LifePixels(MDApp):
    def build(self):
        #Builder.load_file('lifepixkv.kv')
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(CalendarWindow(name='Calendar'))
        sm.add_widget(DayWindow(name='DayMood'))
        #sm.current = 'Calendar'
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

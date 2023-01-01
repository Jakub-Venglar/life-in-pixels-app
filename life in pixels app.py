#! python3
# Life in pixels project
import calendar, datetime, os, sys, json, hashlib, httplib2, time
from dateutil import parser
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.config import Config
from kivy import platform
from kivy.lang import Builder
from kivy.clock import Clock
from functools import partial
from sortedcontainers import SortedDict
from kivy.graphics import Rectangle, Color, Line
from babel.dates import format_date
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


#TODO: make menu screen
#TODO: make popup function/class
#TODO: create graph view for healt
#TODO: create year stats for mood and health - make it separate screen
#TODO: create and show hint for physical health status

#TODO: show physical health status as bar??

#TODO: @solve how to show habit labels

#TODO: learn how to properly comment and add comments and docstrings
#TODO: add loading screen and wait until calendar and widow are constructed
#TODO: add habits/activities, render them if accomplished on the main calendar - possibility to track them (show how many or just checkbox if accomplished)
#TODO: finish tutorials so I have better idea what I am doing :)

#TODO: add option for set your own colors
#TODO: choice from default pictures or your own as BG
#TODO: add, picture of the day, copy to dedicated folder and name it, backup
#TODO: make printable page, with summary of the year/month
# maybe todo: add location on the map, later show pins on the map


if platform == 'android':
    
    from android.storage import app_storage_path
    settings_path = app_storage_path()

    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()

    from android.storage import secondary_external_storage_path
    secondary_ext_storage = secondary_external_storage_path()

if platform == 'win':
    Window.size = (400*1.5, 712*1.5)
    Window.top = 50
    Window.left = 50

Config.set('kivy', 'exit_on_escape', '0')

emptyDayData = {'mood':'','mood2':'','doubleMood': False, 'comment':'','health': None}
fsDivider = 35

superColor= (242/255,85/255,12/255,.8)#(227/255,65/255,25/255,.8) #(255/255,232/255,28/255,.8)
goodColor=(43/255,168/255,8/255,.8)
averageColor= (68/255,121/255,207/255,.8) #(138/255,153/255,184/255,.8)
badColor= (28/255,49/255,36/255,.8) #(117/255,32/255,16/255,.8) #(150/255,39/255,20/255,.8)
terribleColor=(28/255,49/255,36/255,.8)
clearColor = (.5,.5,.5,.45)
noColor = (0,0,0,0)

today = (48/255,60/255,133/255,.9) #(12/255,84/255,179/255,.8)
notToday = (12/255,84/255,179/255,0)

calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]

#experimental class / probably no need for using it

class YearObject():
    def __init__(self, year, data):
        self.year = year
        self.data = data


#define screens
class CalendarWindow(MDScreen):
        # construct label sizes for cal buttons
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize = self.labelSize)

    def labelSize(self,x=1,y=1,z=1,clocktime=0):
        self.manager.get_screen('CalLabels').fs = z/fsDivider

#create directory if not existing for both platfoms and change working directory to it
#os.makedirs

    def create_userdata_directory(self):
        if platform == 'android':
            path = os.path.join(settings_path, 'userdata')
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
        else:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'userdata')
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
    
    def switch_to_ext_storage(self):
        pass
    
    def pass_data(self,date_id):
        year = str(date_id)[:4]
        userdata = self.get_userdata()
        if year != self.currentYear:
            self.currentYear = year
            try:   
                with open(f'{userdata}/caldata-{year}.json', 'r', encoding='utf-8') as file:
                    yearData =  json.loads(file.read())
            except FileNotFoundError:
                    yearData =  {}
            self.yearData = yearData
            #thisYear = YearObject(year,yearData)
        return self.yearData

    def save_data(self, newData, date_id):
        year = str(date_id)[:4]
        userdata = self.get_userdata()
        filename = f'{userdata}/caldata-{year}.json'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('{}')
            json.dump(SortedDict(newData), file, indent = 4)
    
    def delete_data(self,date_id):
        year = str(date_id)[:4]
        userdata = self.get_userdata()
        with open(f'{userdata}/caldata-{year}.json', 'w', encoding='utf-8') as file:
            file.write('{}')
        self.make_Cal(now=True)
        self.make_Cal(now=True) # clock is not working but this yes....
    
    def get_self_directory(self):
        if platform == 'android':
            path = os.path.join(MDApp.get_running_app().user_data_dir, 'app/')
        else:
            path = os.path.dirname(sys.argv[0])
        return path

    def get_userdata(self):
        if platform == 'android':
            path = os.path.join(settings_path, 'userdata')
        else:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'userdata')
        return path

    def sync_data(self,clocktime=0):
        try:
            secrets_path = os.path.join(self.get_self_directory(), 'drivelogin/', 'client_secrets.json')
            credentials_path = os.path.join(self.get_self_directory(), 'drivelogin/', 'credentials.json')
            # authenticate to google drive (needs my client secrets)
            # google auth settings.yaml is set
            settings={'client_config_file': secrets_path,
                        'save_credentials': True,
                        'save_credentials_backend': 'file',
                        'save_credentials_file': credentials_path,
                        'get_refresh_token': True}
            gauth = GoogleAuth(settings=settings)
            # Create local webserver and auto handles authentication.
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)
            os.chdir(self.get_userdata())
            local_file_list = os.listdir()
            local_file_meta = {}
            drive_file_list = drive.ListFile({'q': "('1QRcc1s1xZQz5fWlMjut8chLO8hsTit8Y' in parents) and (trashed=false) and (mimeType != 'application/vnd.google-apps.folder')"}).GetList()
            drive_file_meta = {}
            for file in local_file_list:
                with open(file,'rb') as f:
                    data = f.read()
                    md5checksum = hashlib.md5(data).hexdigest()
                local_file_meta[file] = {'checksum': md5checksum, 'modifiedDate': os.path.getmtime(file),'dtobject': datetime.datetime.fromtimestamp(os.path.getmtime(file))} #datetime.datetime.fromtimestamp
            for file in drive_file_list:
                drive_file_meta[file['title']] = {'id': file['id'],'checksum': file['md5Checksum'], 'modifiedDate': datetime.datetime.timestamp(parser.parse(file['modifiedDate'])), 'dtobject': parser.parse(file['modifiedDate'])}

            try:
                self.syncMessage = ''

                if len(local_file_list)<1:
                    for filename in drive_file_meta:
                        new_file = drive.CreateFile({'parents': [{'id': '1QRcc1s1xZQz5fWlMjut8chLO8hsTit8Y'}],'title':filename, 'id': drive_file_meta[filename]['id']})
                        new_file.GetContentFile(filename)
                        self.syncMessage = 'V datech nic nebylo, soubory z drive stazeny'

                elif len(local_file_list)<1 and len(drive_file_list)<1:
                    self.syncMessage = 'Nikde nic, zaciname od nuly'
                else: 
                    pass

                for filename in local_file_list:
                    if filename in drive_file_meta:
                        #self.syncMessage = self.syncMessage + '\n' + filename + ' nalezeno na drive' + '\n'
                        if local_file_meta[filename]['modifiedDate'] > drive_file_meta[filename]['modifiedDate'] and local_file_meta[filename]['checksum'] != drive_file_meta[filename]['checksum']:
                            new_file = drive.CreateFile({'parents': [{'id': '1QRcc1s1xZQz5fWlMjut8chLO8hsTit8Y'}],'title': filename, 'id': drive_file_meta[filename]['id']})
                            new_file.SetContentFile(filename)
                            new_file.Upload()
                            self.syncMessage = self.syncMessage + '\n' + filename + ' - lokální soubor je novější - nahráno na drive' + '\n'
                        elif (local_file_meta[filename]['modifiedDate'] < drive_file_meta[filename]['modifiedDate']) and (local_file_meta[filename]['checksum'] != drive_file_meta[filename]['checksum']):
                            new_file = drive.CreateFile({'parents': [{'id': '1QRcc1s1xZQz5fWlMjut8chLO8hsTit8Y'}],'title':filename, 'id': drive_file_meta[filename]['id']})
                            new_file.GetContentFile(filename)
                            self.syncMessage = self.syncMessage + '\n' + filename + ' - soubor na drive je novější - staženo' + '\n'
                        else:
                            pass
                            #self.syncMessage = self.syncMessage + '\n' + filename + ' má stejné datum nebo checsksum, nic se neděje' + '\n'
                    else:
                        new_file = drive.CreateFile({'parents': [{'id': '1QRcc1s1xZQz5fWlMjut8chLO8hsTit8Y'}],'title':filename, 'mimeType':'application/json'})
                        # Read file and set it as a content of this instance.
                        new_file.SetContentFile(filename)
                        new_file.Upload() # Upload the file.
                        self.syncMessage = self.syncMessage + '\n' + filename +' - nově nahráno' + '\n'
                
                if self.syncMessage == '':
                    pass #popupMessage = 'Nic nebylo potřeba synchronizovat'
                else:
                    popupMessage = self.syncMessage
                    popup = Popup(title='Výsledek synchronizace', content = 
                    Label(text=popupMessage, 
                    font_size= 15,
                    halign= 'center',
                    valign= 'middle',
                    size=(Window.size[0]*0.6,Window.size[1]*0.7),
                    text_size=(Window.size[0]*0.5,Window.size[1]*0.7)), 
                    size_hint=(.6, .7))
                    popup.bind(on_touch_down=popup.dismiss)
                    popup.open()

                
            except Exception as e: print(e)
        except httplib2.error.ServerNotFoundError:
            popup = Popup(title='Není připojení k internetu', content = 
            Label(text='Nemůžu se připojit k internetu. \n Zapni wifi nebo data. \n Klikni kamkoliv pro zavření tohoto okna.', 
            font_size= 20,
            halign= 'center',
            valign= 'middle',
            size=(Window.size[0]*0.6,Window.size[1]*0.7),
            text_size=(Window.size[0]*0.5,Window.size[1]*0.7)), 
            size_hint=(.6, .7))
            popup.bind(on_touch_down=popup.dismiss)
            popup.open()
        self.make_Cal(now=True)
        os.chdir(self.get_self_directory())

    #create calendar view
    def show_popup(self, title='Titulek', content="Zde muze byt cokoliv", button='Zavřít'):
        pass


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
                self.ids[id].colorset = noColor
                self.ids[id].colorset2 = noColor
                
                #make current day more visible
                if setDate == datetime.datetime.date(datetime.datetime.now()):
                    self.ids[id].isToday = True
                else:
                    self.ids[id].isToday = False

                # if mood for date already set then render it, otherwise make field clear
                Clock.schedule_once(partial(self.colorize,id,self.ids[id].date_id))
        
        self.ids['delete'].date_id = self.ids['3-3'].date_id #set id for deleting whole calendar

    def colorize(self,my_id,date_id,clocktime=0):
        call = self.manager.get_screen('Calendar')
        calLabels = self.manager.get_screen('CalLabels')
        call.ids[my_id].canvas.after.clear()
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
        try:
            if dateData[dateKey]['health']:
                calLabels.ids[my_id+'d'].text = str(int(dateData[dateKey]['health']))
        except KeyError:
            pass
        if dateKey in dateData:
            #check for double mood - if yes, set it and clear background
            if dateData[dateKey]['doubleMood'] == True:
                mood1 = call.choose_color(dateData[str(self.ids[my_id].date_id)]['mood'])
                mood2 = call.choose_color(dateData[str(self.ids[my_id].date_id)]['mood2'])
                call.ids[my_id].background_color = noColor
                call.ids[my_id].doublemood = True
                call.ids[my_id].colorset = (mood1[0],mood1[1],mood1[2],mood1[3]-.2)
                call.ids[my_id].colorset2 = (mood2[0],mood2[1],mood2[2],mood1[3]-.2) #call.choose_color(dateData[str(self.ids[my_id].date_id)]['mood'])
            else:
                call.ids[my_id].background_color = call.choose_color(dateData[str(self.ids[my_id].date_id)]['mood'])
        else: 
            call.ids[my_id].background_color = clearColor
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
        with call.ids[my_id].canvas.after:
            if call.ids[my_id].isToday == True:
                Color(rgba = today)
                Line(width = 3, circle= (call.ids[my_id].center_x, call.ids[my_id].center_y,call.ids[my_id].width/2.5))
            Color(rgba = (1,1,1,1))
            # comment label
            Rectangle(size=labelIDa.texture_size, pos=(calButtonID.x+calButtonID.width/20, calButtonID.top-labelIDa.texture_size[1]), texture=labelIDa.texture)
            Rectangle(size=labelIDb.texture_size, pos=(calButtonID.right-labelIDb.texture_size[0], calButtonID.top-labelIDb.texture_size[1]), texture=labelIDb.texture)
            Rectangle(size=labelIDc.texture_size, pos=(calButtonID.right-labelIDc.texture_size[0], calButtonID.y), texture=labelIDc.texture)
            # health label with heart icon
            Rectangle(size=labelIDd.texture_size, pos=(calButtonID.x+calButtonID.width/3.4,calButtonID.y), texture=labelIDd.texture)
            if labelIDd.texture_size[0] > 0:
                path = os.path.join(self.get_self_directory(), 'pict/', 'heart.png')
                Rectangle(source = path, size=(calButtonID.width/4.5,calButtonID.width/4.5), pos=(calButtonID.x+calButtonID.width/20,calButtonID.y+calButtonID.height/15))

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
        daySetting.current_date = format_date(date_id,"full", locale='cs_CZ').capitalize()
        #daySetting.ids.terrible.background_color = terribleColor
        daySetting.ids.bad.background_color = badColor
        daySetting.ids.average.background_color = averageColor
        daySetting.ids.good.background_color = goodColor
        daySetting.ids.super.background_color = superColor
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        try: 
            if dateData[dateKey]['health']:
                daySetting.ids.health.value = dateData[dateKey]['health']
                daySetting.ids.healthLabel.questionMark = False
            else:
                daySetting.ids.health.value = 10
                daySetting.ids.healthLabel.questionMark = True
        except KeyError:
            daySetting.ids.health.value = 10
        daySetting.ids.doubleMoodCheck.active = dateData[dateKey]['doubleMood']
        daySetting.ids.question.bg1 = self.choose_color(dateData[dateKey]['mood'] )
        if daySetting.ids.doubleMoodCheck.active == True:
            daySetting.ids.question.bg2 = self.choose_color(dateData[dateKey]['mood2'] )
        else:
            daySetting.ids.question.bg2 = self.choose_color(dateData[dateKey]['mood'] )
        daySetting.ids.comment.text = dateData[dateKey]['comment']

class DayWindow(MDScreen):

    def on_enter(self):
        Window.bind(on_keyboard=self.back_click)

    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.back_click)

    def back_click(self,window, key, keycode, *largs):
        #print('key ' + str(key) + '----' + 'keycode ' + str(keycode))
        if key == 27:
            self.manager.transition.direction = 'right'
            self.manager.current = 'Calendar'
        #if key == 13: do stuff for enter

    def mood_click(self,value, text):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        if self.ids.doubleMoodCheck.active == True:
            if self.setMoodNum == 1:
                dateData[dateKey]['mood'] =  value
                self.setMoodNum = 2
            elif  self.setMoodNum == 2:
                dateData[dateKey]['mood2'] = value
                self.setMoodNum = 1
        else:
            dateData[dateKey]['mood'] =  value
        dateData[dateKey]['comment'] = text
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)
        self.ids.question.bg1 = call.choose_color(dateData[dateKey]['mood'] )
        if self.ids.doubleMoodCheck.active == True:
            self.ids.question.bg2 = call.choose_color(dateData[dateKey]['mood2'] )
        else:
            self.ids.question.bg2 = call.choose_color(dateData[dateKey]['mood'] )

    def double_mood (self, value):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        if self.ids.doubleMoodCheck.active == True:
            dateData[dateKey]['doubleMood'] = True
        else:
            dateData[dateKey]['doubleMood'] = False
        call.save_data(dateData,self.date_id)
        call.ids[self.my_id].colorset = noColor
        call.ids[self.my_id].colorset2 = noColor
        self.ids.question.bg1 = call.choose_color(dateData[dateKey]['mood'] )
        if self.ids.doubleMoodCheck.active == True:
            self.ids.question.bg2 = call.choose_color(dateData[dateKey]['mood2'] )
        else:
            self.ids.question.bg2 = call.choose_color(dateData[dateKey]['mood'] )
        call.colorize(self.my_id,self.date_id)

    def save_text(self, text):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        dateData[dateKey]['comment'] = text
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)
    
    def save_health(self, value):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = dateData.setdefault(dateKey, emptyDayData.copy())
        dateData[dateKey]['health'] = value
        self.ids.healthLabel.questionMark = False
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)


    def delete_day(self):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = emptyDayData.copy()
        self.ids.comment.text= ''
        self.ids.health.value = 10
        self.ids.healthLabel.questionMark = True
        self.ids.doubleMoodCheck.active = False
        call.save_data(dateData,self.date_id)
        call.colorize(self.my_id,self.date_id)
    
    def close(self):
        pass
        

class HabitsWindow(MDScreen):

    def on_enter(self):
        Window.bind(on_keyboard=self.back_click)

    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.back_click)

    def back_click(self,window, key, keycode, *largs):
        if key == 27:
            self.manager.transition.direction = 'right'
            self.manager.current = 'Calendar'

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

    def on_enter(self):
        Window.bind(on_keyboard=self.back_click)

    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.back_click)

    def back_click(self,window, key, keycode, *largs):
        if key == 27:
            self.manager.transition.direction = 'right'
            self.manager.current = 'Calendar'

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

# run app and construct calendar

class LifePixels(MDApp):
    title = 'Life in Pixels'
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

    def on_start(self):
        #self.root.get_screen('Calendar').create_userdata_directory()
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE, Permission.INTERNET])
        cwdpath = os.getcwd()
        print('zacinam v' + str(cwdpath))
        self.root.current_screen.create_userdata_directory()
        self.root.current_screen.make_Cal()
        Clock.schedule_once(self.root.current_screen.sync_data)
    
    def on_resume(self):
        self.root.get_screen('Calendar').sync_data()



if __name__ == "__main__":

    LifePixels().run()

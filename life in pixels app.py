#! python3
# Life in pixels project
import calendar, datetime, os, sys, json, hashlib, httplib2, shutil, time
'''
#profiling
import cProfile
import pstats
from pstats import SortKey
'''
from threading import Thread
from dateutil import parser
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog.dialog import MDDialog
from kivymd.uix.button.button import MDFlatButton
from kivymd.toast import toast
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.config import Config
from kivy import platform
from kivy.lang import Builder
from kivy.clock import Clock
from functools import partial
#from sortedcontainers import SortedDict
from kivy.graphics import Rectangle, Color, Line
from babel.dates import format_date, format_datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from plyer import filechooser



#TODO: # handling pict of the day, sync and load it - zaklady hotovy
# zapojit i porovnani s cal daty / mohl sem obrazek smazat, ale on na drive zustane a stahne se znovu

#TODO:  pop up kde si můžu vybrat, jak s nimi naložím (co smazat, co nechat - ukaze mi co kde nasel a ja si vyberu jak s tim nalozim)
# mit zaskrtnuty nahrany rok - smazat(lokalne) nebo stahnout(lokalne)

#TODO:  poladit vykon

# upravit velikosti okna, viz screeny v mobilu

# na mobilu ani nenacetl ten bg co uz byl z minula ?? jeste otestovat
# pokud najde bg image zapis ho do settings

#TODO: uzaviram - konec se vola dvakrat
#TODO: vymyslet jak nezapisovat prazdne dny (momentalne se ulozi)
#TODO: zapsat nekam posledni sync

#TODO: better view of day color
#TODO bg image / choose if mine or random +/- 1 month

#TODO: see text comment on long press in calendar / not working on mobile

#TODO: make menu screen
#TODO: create graph view for healt
#TODO: create year stats for mood and health - make it separate screen
#TODO: create and show hint for physical health status, create comment field for health

#TODO: @solve how to show habit labels

#TODO: learn how to properly comment and add comments and docstrings
#TODO: add loading screen and wait until calendar and widow are constructed
#TODO: add habits/activities, render them if accomplished on the main calendar - possibility to track them (show how many or just checkbox if accomplished)
#TODO: finish tutorials so I have better idea what I am doing :)

#TODO: add option for set your own colors
#TODO: aktualne sync slozek vytvori na disku vsechny slozky, ktere najde na drive (naplni ale jen jednu), coz je malinko prasarna

#TODO: make printable page, with summary of the year/month
# maybe todo: add location on the map, later show pins on the map


if platform == 'android':

    from jnius import cast
    from jnius import autoclass
    from android import mActivity, api_version

    from androidstorage4kivy import Chooser, SharedStorage
    #from kvdroid.tools.network import network_status, wifi_status, mobile_status / not working on android, cant import jnius
    
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

emptyDayData = {'mood':'','mood2':'','doubleMood': False, 'comment':'','health': None, 'healthComment': '', 'dayImage': ''}
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

cal_data_drive_folder = '1QRcc1s1xZQz5fWlMjut8chLO8hsTit8Y'
BG_drive_folder = '1vZCpinF7V4NT8AiDA3Hbwe3T2DRAvlBH'
dayPictures_drive_folder = '18vtSYlwb2IrMJ8Hr8JCc6yXBcjdUfOwz'

calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]
listOfMyIds = []
for week in calList:
    for day in week:
        listOfMyIds.append(day)

def open_confirmation_popup(self, function_to_pass = None , title='Potvrzení', text='pop up text', button1='Ano', button2='Ne'):
    if function_to_pass == None:
        function_to_pass = self.empty_function
    box = BoxLayout(orientation = 'vertical', padding=(10,50))
    box.add_widget(Label(text=text, 
        font_size= 30,
        halign= 'center',
        valign= 'middle',
        size=(Window.size[0]*0.6,Window.size[1]*0.7),
        text_size=(Window.size[0]*0.5,Window.size[1]*0.7)),
    )
    
    popup = Popup(title=title, content = box, size_hint=(.8,.8))
    box.add_widget(Button(text = button1, size_hint=(.9,.3), padding_y= 300, pos_hint={'center_x': .5 }, on_press = function_to_pass, on_release=popup.dismiss))
    box.add_widget(Button(text = button2, size_hint=(.9,.3), pos_hint={'center_x': .5 }, on_release=popup.dismiss))
    #popup.bind(on_touch_down=popup.dismiss)
    popup.open()

def empty_function(self, obj):
    pass

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

    def on_enter(self):
        Window.bind(on_key_up=self.key_click)

    def on_pre_leave(self):
        Window.unbind(on_key_up=self.key_click)

    def key_click(self,window, key, keycode, *largs):
        #print('key ' + str(key) + '----' + 'keycode ' + str(keycode))
        if key == 27:
            print('ESCAPING')
            MDApp.get_running_app().stop()
            Window.close()

#create directories if not existing for both platfoms

    def create_userdata_directories(self, permissions = [], grant_results = [] ):
        if platform == 'android':
            path = os.path.join(settings_path, 'userdata')
            
            if not os.path.exists(path):
                os.mkdir(path)

            path = os.path.join(primary_ext_storage, 'Pictures', 'lifepixels', 'user_pictures', 'BG')
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

        else:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'userdata')
            
            if not os.path.exists(path):
                os.mkdir(path)

            path = os.path.join(os.path.dirname(sys.argv[0]), 'user_pictures', 'BG')
            
            if not os.path.exists(path):
                os.mkdir(path)
    
    def pass_data(self,date_id):
        year = str(date_id.year)
        userdata = self.get_userdata()
        #if year != self.currentYear: protože to pak neprojde, když se nemění rok a nereloaduje kalendář
            #self.currentYear = year
        try:   
            with open(f'{userdata}/caldata-{year}.json', 'r', encoding='utf-8') as file:
                yearData =  json.loads(file.read())
        except FileNotFoundError:
                yearData =  {}
        self.yearData = yearData
            #thisYear = YearObject(year,yearData)
        return self.yearData

    def save_data(self, newData, date_id):
        year = str(date_id.year)
        userdata = self.get_userdata()
        filename = f'{userdata}/caldata-{year}.json'

        try:

            with open(filename, 'r', encoding='utf-8') as file: #readfile first and compare
                oldata = json.loads(file.read())
            
            if oldata != newData:

                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(newData, file, indent = 4, sort_keys=True)
                
                print('NOVE, UKLADAM')
            
            else:
                print('STEJNE NEUKLADAM')
        
        except FileNotFoundError:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(newData, file, indent = 4, sort_keys=True)

    
    def delete_data(self,date_id):
        year = str(date_id.year)
        userdata = self.get_userdata()
        with open(f'{userdata}/caldata-{year}.json', 'w', encoding='utf-8') as file:
            file.write('{}')
        self.make_Cal(now=True)
        self.make_Cal(now=True) # clock is not working but this yes....
    
    def get_self_directory(self):
        if platform == 'android':
            path = os.path.join(MDApp.get_running_app().user_data_dir, 'app')
        else:
            path = os.path.dirname(sys.argv[0])
        return path

    def get_userdata(self):
        if platform == 'android':
            path = os.path.join(settings_path, 'userdata')
        else:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'userdata')
        return path

    def get_user_pictures(self):
        if platform == 'android':
            path = os.path.join(primary_ext_storage, 'Pictures', 'lifepixels', 'user_pictures')
        else:
            path = os.path.join(os.path.dirname(sys.argv[0]), 'user_pictures')
        return path
    
    def authenticate(self):
        secrets_path = os.path.join(self.get_self_directory(), 'drivelogin', 'client_secrets.json')
        credentials_path = os.path.join(self.get_self_directory(), 'drivelogin', 'credentials.json')
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
        return gauth
    
    syncText = {'caldata': '', 'settings': ''}
    noInternet = 'Nemůžu se připojit k internetu. \n Zapni wifi nebo data.'

    def sync_day_pictures(self, date_id):
        
        try:

        #prepare calendar data

        #load folders and find the correct one

            drive = GoogleDrive(self.authenticate())

            dayPictID = dayPictures_drive_folder

            os.chdir(self.get_user_pictures())
            local_file_list = os.listdir()
            local_file_meta = {}
            drive_file_list = drive.ListFile({'q': f"( '{dayPictID}' in parents) and (trashed=false) and (mimeType = 'application/vnd.google-apps.folder')"}).GetList()
            drive_file_meta = {}


            for file in local_file_list:
                local_file_meta[file] = {'checksum': None, 'modifiedDate': os.path.getmtime(file),'dtobject': datetime.datetime.fromtimestamp(os.path.getmtime(file))} #datetime.datetime.fromtimestamp

            for file in drive_file_list:
                drive_file_meta[file['title']] = {'id': file['id'],'checksum': None, 'modifiedDate': datetime.datetime.timestamp(parser.parse(file['modifiedDate'])), 'dtobject': parser.parse(file['modifiedDate'])}
                
                if not os.path.exists(file['title']):
                    os.mkdir(file['title'])

            try:
                del local_file_meta['BG']
            except KeyError:
                pass

            MIMEtype = 'application/vnd.google-apps.folder'

            parentID = dayPictures_drive_folder

            self.sync_data(drive, parentID, MIMEtype, local_file_list,local_file_meta,drive_file_list,drive_file_meta,'folders')


            # switch to current (shown) year folder and make sync
            
            year = str(date_id.year)

            drive_file_list = drive.ListFile({'q': f"( '{dayPictID}' in parents) and (trashed=false) and (mimeType = 'application/vnd.google-apps.folder')"}).GetList()
            drive_file_meta = {}

            for file in drive_file_list:
                drive_file_meta[file['title']] = {'id': file['id'],'checksum': None, 'modifiedDate': datetime.datetime.timestamp(parser.parse(file['modifiedDate'])), 'dtobject': parser.parse(file['modifiedDate'])}

            yearFolderID = drive_file_meta[year]['id']

            os.chdir(os.path.join(self.get_user_pictures(),year))
            local_file_list = os.listdir()
            local_file_meta = {}
            drive_file_list = drive.ListFile({'q': f"( '{yearFolderID}' in parents) and (trashed=false) and (mimeType != 'application/vnd.google-apps.folder')"}).GetList()
            drive_file_meta = {}

            for file in local_file_list:
                with open(file,'rb') as f:
                    data = f.read()
                    md5checksum = hashlib.md5(data).hexdigest()
                local_file_meta[file] = {'checksum': md5checksum, 'modifiedDate': os.path.getmtime(file),'dtobject': datetime.datetime.fromtimestamp(os.path.getmtime(file))} #datetime.datetime.fromtimestamp

            for file in drive_file_list:
                drive_file_meta[file['title']] = {'id': file['id'],'checksum': file['md5Checksum'], 'modifiedDate': datetime.datetime.timestamp(parser.parse(file['modifiedDate'])), 'dtobject': parser.parse(file['modifiedDate'])}

            #print(local_file_list)
            #print(local_file_meta)
            #print(drive_file_list)
            #print(drive_file_meta)

            MIMEtype = 'image/*'
        
            self.sync_data(drive, yearFolderID, MIMEtype, local_file_list,local_file_meta,drive_file_list,drive_file_meta,'dayPictures')
    
        except httplib2.error.ServerNotFoundError:
            self.syncText['message'] = self.noInternet
            #self.open_popup(title='Není připojení k internetu', text='Nemůžu se připojit k internetu. \n Zapni wifi nebo data.', button='Zavřít')
        
        os.chdir(self.get_self_directory())

    def sync_data_thread(self):
        
        toast('Provádím synchronizaci', duration = 1.5)
        Clock.schedule_once(self.thread_handle,.5)
 
    def thread_handle(self, clocktime=0):
        t = Thread(target=self.sync_data_prep)
        t.start()
        t.join()

        text = self.syncText['caldata'] + '\n' + self.syncText['settings']

        Clock.schedule_once(partial(self.make_Cal, True))
        Clock.schedule_once(self.manager.get_screen('Settings').load_settings)
        Clock.schedule_once(self.manager.get_screen('Settings').imageRefresh)

        #if text != '':
            

        if text == '\n':
            toast('Nic nebylo potřeba synchronizovat')
        elif text == self.noInternet:
            toast(self.noInternet)
        else:
            toast('Synchronizace dokončena \nDetaily najdeš v nastavení')
        
        self.manager.get_screen('Settings').ids.sync_info.text = 'Naposledy synchronizovano: ' + format_datetime(datetime.datetime.now(),"d.L. yyyy -- HH:mm:ss ", locale='cs_CZ') + '\n' + text

    def sync_data_prep(self,clocktime=0):
        try:

            # first prepare calendar data

            drive = GoogleDrive(self.authenticate())

            parentID = cal_data_drive_folder

            os.chdir(self.get_userdata())
            local_file_list = os.listdir()
            local_file_meta = {}
            drive_file_list = drive.ListFile({'q': f"( '{parentID}' in parents) and (trashed=false) and (mimeType != 'application/vnd.google-apps.folder')"}).GetList()
            drive_file_meta = {}


            for file in local_file_list:
                with open(file,'rb') as f:
                    data = f.read()
                    md5checksum = hashlib.md5(data).hexdigest()
                local_file_meta[file] = {'checksum': md5checksum, 'modifiedDate': os.path.getmtime(file),'dtobject': datetime.datetime.fromtimestamp(os.path.getmtime(file))} #datetime.datetime.fromtimestamp
            for file in drive_file_list:
                drive_file_meta[file['title']] = {'id': file['id'],'checksum': file['md5Checksum'], 'modifiedDate': datetime.datetime.timestamp(parser.parse(file['modifiedDate'])), 'dtobject': parser.parse(file['modifiedDate'])}

            MIMEtype = 'application/json'
        
            self.sync_data(drive, parentID, MIMEtype, local_file_list,local_file_meta,drive_file_list,drive_file_meta,'caldata')

            # then BG picture

            parentID = BG_drive_folder 
            
            os.chdir(os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), 'BG'))
            local_file_list = os.listdir()
            local_file_meta = {}
            drive_file_list = drive.ListFile({'q': f"( '{parentID}' in parents) and (trashed=false) and (mimeType != 'application/vnd.google-apps.folder')"}).GetList()
            drive_file_meta = {}


            for file in local_file_list:
                with open(file,'rb') as f:
                    data = f.read()
                    md5checksum = hashlib.md5(data).hexdigest()
                local_file_meta[file] = {'checksum': md5checksum, 'modifiedDate': os.path.getmtime(file),'dtobject': datetime.datetime.fromtimestamp(os.path.getmtime(file))} #datetime.datetime.fromtimestamp
            for file in drive_file_list:
                drive_file_meta[file['title']] = {'id': file['id'],'checksum': file['md5Checksum'], 'modifiedDate': datetime.datetime.timestamp(parser.parse(file['modifiedDate'])), 'dtobject': parser.parse(file['modifiedDate'])}

            MIMEtype = 'image/*'

            self.sync_data(drive, parentID, MIMEtype, local_file_list,local_file_meta,drive_file_list,drive_file_meta,'settings')

        except httplib2.error.ServerNotFoundError:
            self.syncText['message'] = self.noInternet
            #self.open_popup(title='Není připojení k internetu', text='Nemůžu se připojit k internetu. \n Zapni wifi nebo data.', button='Zavřít')
        
        os.chdir(self.get_self_directory())

    
    def sync_data(self, drive, parentID, MIMEtype, local_file_list, local_file_meta, drive_file_list, drive_file_meta, what_syncing):
        print(1)
        try:
            syncMessage = ''

            if len(local_file_list)<1:
                for filename in drive_file_meta:
                    new_file = drive.CreateFile({'parents': [{'id': parentID }],'title':filename, 'id': drive_file_meta[filename]['id'], 'mimeType': MIMEtype})
                    new_file.GetContentFile(filename)
                    syncMessage = 'V datech nic nebylo, soubory z drive stazeny'
                print(2)
            elif len(local_file_list)<1 and len(drive_file_list)<1:
                syncMessage = 'Nikde nic, zaciname od nuly'
            else: 
                pass

            for filename in local_file_meta:
                print(3)
                if filename in drive_file_meta:
                    #self.syncMessage = self.syncMessage + '\n' + filename + ' nalezeno na drive' + '\n'
                    
                    if local_file_meta[filename]['modifiedDate'] > drive_file_meta[filename]['modifiedDate'] and local_file_meta[filename]['checksum'] != drive_file_meta[filename]['checksum']:
                        new_file = drive.CreateFile({'parents': [{'id': parentID }],'title': filename, 'id': drive_file_meta[filename]['id'], 'mimeType': MIMEtype})
                        if os.path.isfile(filename):
                            new_file.SetContentFile(filename)
                        new_file.Upload()
                        syncMessage = syncMessage + '\n' + filename + ' - lokální soubor je novější - nahráno na drive' + '\n'
                    
                    elif (local_file_meta[filename]['modifiedDate'] < drive_file_meta[filename]['modifiedDate']) and (local_file_meta[filename]['checksum'] != drive_file_meta[filename]['checksum']):
                        new_file = drive.CreateFile({'parents': [{'id': parentID }],'title':filename, 'id': drive_file_meta[filename]['id'], 'mimeType': MIMEtype})
                        new_file.GetContentFile(filename)
                        syncMessage = syncMessage + '\n' + filename + ' - soubor na drive je novější - staženo' + '\n'
                    
                    else:
                        pass
                        #self.syncMessage = self.syncMessage + '\n' + filename + ' má stejné datum nebo checsksum, nic se neděje' + '\n'
                else:
                    print(4)
                    new_file = drive.CreateFile({'parents': [{'id': parentID }],'title':filename, 'mimeType': MIMEtype})
                    # Read file and set it as a content of this instance.
                    if os.path.isfile(filename):
                        new_file.SetContentFile(filename)
                    new_file.Upload() # Upload the file.
                    syncMessage = syncMessage + '\n' + filename +' - nově nahráno' + '\n'
            
            for filename in drive_file_meta:
                if filename not in local_file_meta:
                    new_file = drive.CreateFile({'parents': [{'id': parentID }],'title':filename, 'id': drive_file_meta[filename]['id'], 'mimeType': MIMEtype})
                    new_file.GetContentFile(filename)
                    syncMessage = syncMessage + '\n' + filename + ' - soubor na drive neexistoval na lokálním disku - staženo' + '\n'

            print(5)
            self.syncText[what_syncing] = syncMessage
                
        except Exception as e: print(e)

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
                self.ids[id].colorset = noColor
                self.ids[id].colorset2 = noColor
                
                #make current day more visible
                if setDate == datetime.datetime.date(datetime.datetime.now()):
                    self.ids[id].isToday = True
                else:
                    self.ids[id].isToday = False

                # if mood for date already set then render it, otherwise make field clear
                Clock.schedule_once(partial(self.colorize,id,self.ids[id].date_id))
        
        self.ids['syncPictures'].date_id = self.ids['3-3'].date_id #set id for deleting whole calendar or handling sync of pictures

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
                call.ids[my_id].colorset = (mood1[0],mood1[1],mood1[2],mood1[3])
                call.ids[my_id].colorset2 = (mood2[0],mood2[1],mood2[2],mood1[3])
            else:
                call.ids[my_id].background_color = call.choose_color(dateData[str(self.ids[my_id].date_id)]['mood'])
        else: 
            call.ids[my_id].background_color = clearColor
        Clock.schedule_once(partial(self.create_labels,my_id,dateData,dateKey,date_id))
        
    def create_labels(self,my_id, dateData, dateKey, date_id, clocktime=0):
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
            #Rectangle(size=labelIDb.texture_size, pos=(calButtonID.right-labelIDb.texture_size[0], calButtonID.top-labelIDb.texture_size[1]), texture=labelIDb.texture)
            
            # add small image if is present as Day image
            try:
                if dateData[dateKey]['dayImage'] != '':
                    img_source = os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), str(date_id.year),dateData[dateKey]['dayImage'])
                    img = Image(img_source) # because direct source is cached
                    img.remove_from_cache()
                    Rectangle(texture=img.texture, size=(calButtonID.width/3.2,calButtonID.width/3.2), pos=(calButtonID.right-calButtonID.width/3.2,calButtonID.top-calButtonID.width/3.2))
                    call.ids[my_id].canvas.ask_update()
            except KeyError:
                pass

            Rectangle(size=labelIDc.texture_size, pos=(calButtonID.right-labelIDc.texture_size[0], calButtonID.y), texture=labelIDc.texture)
            # health label with heart icon
            Rectangle(size=labelIDd.texture_size, pos=(calButtonID.x+calButtonID.width/3.4,calButtonID.y), texture=labelIDd.texture)
            if labelIDd.texture_size[0] > 0:
                path = os.path.join(self.get_self_directory(), 'pict', 'heart.png')
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
        daySetting.date_id = date_id
        daySetting.my_id = my_id
        daySetting.load_day(date_id)


    def schedule_long_cal_click(self,date_id, my_id):
        self.open = True
        self.event = Clock.schedule_once(partial(self.show_text, date_id, my_id), 0.3)
        #self.close = True

    def ulp_call_cal_click(self,date_id, my_id):
        self.event.cancel()
        if self.open == True:
            self.cal_click(date_id, my_id)

    def show_text(self, date_id, my_id, clocktime=0):
        self.open = False
        dateData = self.pass_data(date_id)
        dateKey = str(date_id)
        toast(dateData[dateKey]['comment'], duration=5)
        

    def textuj(self, touch):
        print('neco')

class DayWindow(MDScreen):

    def on_pre_enter(self):
        pass

    def on_enter(self):
        print('NAJIZDI DAY WINDOW')
        Window.bind(on_key_up=self.key_click)
        self.ids.comment.bind(focus=self.focus_change)
        self.ids.healthComment.bind(focus=self.focus_change)

    def on_pre_leave(self):
        self.manager.get_screen('Calendar').save_data(self.dateData,self.date_id)
        Window.unbind(on_key_up=self.key_click)
    
    def load_day(self, date_id, clocktime=0):
        self.dateData = self.manager.get_screen('Calendar').pass_data(self.date_id)
        call = self.manager.get_screen('Calendar')
        dateKey = str(date_id)

        self.current_date = format_date(self.date_id,"full", locale='cs_CZ').capitalize()
        #self.ids.terrible.background_color = terribleColor
        self.ids.bad.background_color = badColor
        self.ids.average.background_color = averageColor
        self.ids.good.background_color = goodColor
        self.ids.super.background_color = superColor
        self.dateData[dateKey] = self.dateData.setdefault(dateKey, {})
        self.dateData[dateKey] = self.dateData.setdefault(dateKey, self.set_default_values(self.dateData[dateKey]))
        try: 
            if self.dateData[dateKey]['health']:
                self.ids.health.value = self.dateData[dateKey]['health']
                self.ids.healthLabelValue.questionMark = False
            else:
                self.ids.health.value = 5
                self.ids.healthLabelValue.questionMark = True
        except KeyError:
            self.ids.health.value = 5

        self.ids.doubleMoodCheck.active = self.dateData[dateKey]['doubleMood']
        self.ids.question.bg1 = call.choose_color(self.dateData[dateKey]['mood'] )
        if self.ids.doubleMoodCheck.active == True:
            self.ids.question.bg2 = call.choose_color(self.dateData[dateKey]['mood2'] )
        else:
            self.ids.question.bg2 = call.choose_color(self.dateData[dateKey]['mood'] )
        
        self.ids.comment.text = self.dateData[dateKey]['comment']
        self.ids.healthComment.text = self.dateData[dateKey]['healthComment']
        
        with self.ids.dayImage.canvas.after:
            self.ids.dayImage.canvas.after.clear()

        if self.dateData[dateKey]['dayImage'] != '':
            self.ids.dayImage.image_source = os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), str(self.date_id.year),self.dateData[dateKey]['dayImage'])
            self.ids.dayImage.color = [1,1,1,1]
            self.ids.dayImage.reload()

        else:
            self.ids.dayImage.image_source = self.bgsource
            self.ids.dayImage.color = [.6,.6,.6,.6]
            Clock.schedule_once(self.add_text_on_image)
        

    def add_text_on_image(self, clocktime=0):

        with self.ids.dayImage.canvas.after:

            textonImage = self.manager.get_screen('CalLabels').ids.textOnImage
            Color(rgba = (.95,.95,.95,.95))
            Rectangle( size = textonImage.texture_size, pos=(self.ids.dayImage.center_x-(textonImage.texture_size[0]/2), self.ids.dayImage.center_y), texture=self.manager.get_screen('CalLabels').ids.textOnImage.texture)
        
        #self.ids.dayImage.canvas.ask_update()

    def set_default_values(self, dayDict):
        for key, value in emptyDayData.items():
            dayDict.setdefault(key, value)
        return dayDict

    def focus_change(self, object, state):
        if state == False: 
            self.store_text(object)
        
    def key_click(self,window, key, keycode, *largs):
        print('key ' + str(key) + '----' + 'keycode ' + str(keycode))
        if key == 27:
            self.close_day(self.date_id)
        
        if (self.ids.comment.focus or self.ids.healthComment.focus) == False:
                
            if key == 275: # right arrow
                self.move_day('forward', self.date_id, self.my_id)
            if key == 276: # left arrow
                self.move_day('backward', self.date_id, self.my_id)
        
        #if key == 13: do stuff for enter
    
    # move day

    def move_day(self, direction, date_id, my_id):
        print('MOOOVING')

        self.manager.get_screen('Calendar').save_data(self.dateData, date_id)

        index = listOfMyIds.index(my_id)
        if direction == 'backward':
            date_id = date_id - datetime.timedelta(days=1)
            my_id = listOfMyIds[(index-1) % len(listOfMyIds)]
            
        if direction == 'forward':
            date_id = date_id + datetime.timedelta(days=1)
            my_id = listOfMyIds[(index+1) % len(listOfMyIds)]

        self.my_id = my_id
        self.date_id = date_id
        #self.dateData = self.manager.get_screen('Calendar').pass_data(self.date_id)
        self.manager.get_screen('Calendar').cal_click(date_id, my_id)

    def close_day (self, date_id):
        self.manager.transition.direction = 'right'
        self.manager.current = 'Calendar'
        self.manager.get_screen('Calendar').make_Cal(now=False, year = date_id.year, month = date_id.month)

    def mood_click(self,value, text):
        call = self.manager.get_screen('Calendar')
        dateKey = str(self.date_id)
        if self.ids.doubleMoodCheck.active == True:
            if self.setMoodNum == 1:
                self.dateData[dateKey]['mood'] =  value
                self.setMoodNum = 2
            elif  self.setMoodNum == 2:
                self.dateData[dateKey]['mood2'] = value
                self.setMoodNum = 1
        else:
            self.dateData[dateKey]['mood'] =  value
        self.ids.question.bg1 = call.choose_color(self.dateData[dateKey]['mood'] )
        if self.ids.doubleMoodCheck.active == True:
            self.ids.question.bg2 = call.choose_color(self.dateData[dateKey]['mood2'] )
        else:
            self.ids.question.bg2 = call.choose_color(self.dateData[dateKey]['mood'] )

    def double_mood (self, value):
        call = self.manager.get_screen('Calendar')
        dateKey = str(self.date_id)
        if self.ids.doubleMoodCheck.active == True:
            self.dateData[dateKey]['doubleMood'] = True
        else:
            self.dateData[dateKey]['doubleMood'] = False
        call.ids[self.my_id].colorset = noColor
        call.ids[self.my_id].colorset2 = noColor
        self.ids.question.bg1 = call.choose_color(self.dateData[dateKey]['mood'] )
        if self.ids.doubleMoodCheck.active == True:
            self.ids.question.bg2 = call.choose_color(self.dateData[dateKey]['mood2'] )
        else:
            self.ids.question.bg2 = call.choose_color(self.dateData[dateKey]['mood'] )

    def store_text(self, object):
        dateKey = str(self.date_id)
        if object == self.ids.comment:
            self.dateData[dateKey]['comment'] = self.ids.comment.text

        if object == self.ids.healthComment:
            self.dateData[dateKey]['healthComment'] = self.ids.healthComment.text

    def store_health(self, value):
        
        dateKey = str(self.date_id)
        self.dateData[dateKey]['health'] = value
        self.ids.healthLabelValue.questionMark = False

    #trick with long press button / schedule event on press and cancel it on release

    def schedule_delete_day(self):
        self.event = Clock.schedule_once(self.delete_day,0.3)
        self.close = True

    def unschedule_delete(self):
        self.event.cancel()
        if self.close == True:
            self.close_day(self.date_id)

    def delete_day(self, clocktime=0):
        self.close = False
        open_confirmation_popup(self, text = 'Chceš vymazat celý den?', function_to_pass=self.delete_day_func)
    
    def delete_day_func(self, obj):
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        dateData[dateKey] = emptyDayData.copy()
        call.save_data(dateData,self.date_id)
        self.load_day(self.date_id)

    def open_filemanager(self):
        
        if platform == 'android':
            self.chooser = Chooser(self.choose_day_image)
            self.chooser.choose_content()

        else:
            #openPath = '/'
            filechooser.open_file(path=self.manager.get_screen('Calendar').get_self_directory(), on_selection=self.choose_day_image)
        

    def choose_day_image(self, opened):
        
        call = self.manager.get_screen('Calendar')
        dateData = call.pass_data(self.date_id)
        dateKey = str(self.date_id)
        
        try:

            if platform == 'android':
                ss = SharedStorage()
                path = ss.copy_from_shared(opened[0])

                print('CESTA VYBRANEHO')
                print(path)
                
            else:
                path = opened[0]
            
            try:
                
                if os.path.isfile(path): #because it can be directory
                    
                    #oldpath = dateData[dateKey]['dayImage']
                    #if os.path.exists(oldpath):
                    #    os.remove(oldpath)

                    newFilename = dateKey + os.path.splitext(path)[1]

                    dest_folder = os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), str(self.date_id.year))
                    try:
                        os.makedirs(dest_folder)
                    except FileExistsError:
                        pass
                    
                    destination = os.path.join(dest_folder, newFilename)
                    
                    print('ORIGINAL')
                    print(os.path.getmtime(path))
                    
                    shutil.copy2(path, destination)
                    
                    now = datetime.datetime.now().timestamp()
                    print('NOW')
                    print(now)

                    os.utime(destination,(now,now))

                    print('RESULT')
                    print(os.path.getmtime(destination))

                    dateData[dateKey]['dayImage'] = newFilename
                    call.save_data(dateData,self.date_id)

                    #print('ratio ' + str(self.ids.dayImage.image_ratio)) #landscape is more than 1
                    
                    Clock.schedule_once(partial(self.load_day, self.date_id))

            except Exception as e:
                print(e)

        except Exception as e:
            print(e)
    
    #def insert_refresh_image(self, dest_folder, newFilename, clocktime=0):
    #    #self.ids.dayImage.image_source = os.path.join(dest_folder, newFilename)
#
    #    print('RELOADED')
    
    def on_touch_down(self, touch):

        self.op_fi = False

        if self.ids.dayImage.collide_point(*touch.pos):
            
            self.event = Clock.schedule_once(self.delete_image, 0.3)           
            self.op_fi = True

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        
        if self.op_fi == True:
            self.event.cancel()
            self.open_filemanager()

        return super().on_touch_up(touch)

    def delete_image(self, clocktime=0):
        self.op_fi = False
        open_confirmation_popup(self, text = 'Chceš smazat obrázek?', function_to_pass=self.delete_image_func)

    def delete_image_func(self, obj):
        dateKey = str(self.date_id)
        self.dateData[dateKey]['dayImage'] = ''
        self.manager.get_screen('Calendar').save_data(self.dateData,self.date_id)
        self.load_day(self.date_id)


    def on_touch_move(self, touch):
        print(touch.ox - touch.x)
        return super().on_touch_move(touch)

class HabitsWindow(MDScreen):

    def on_enter(self):
        Window.bind(on_key_up=self.back_click)

    def on_pre_leave(self):
        Window.unbind(on_key_up=self.back_click)

    def back_click(self,window, key, keycode, *largs):
        if key == 27:
            print('backbackback')
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

    def on_pre_enter(self):
        Window.bind(on_key_up=self.back_click)

        #if os.path.exists(self.settings['bgPicture']) == False:
        #    self.settings['bgPicture'] = 'pict/default.jpg'
        #    self.bgsource = self.settings['bgPicture']

    def on_pre_leave(self):
        Window.unbind(on_key_up=self.back_click)

    def back_click(self,window, key, keycode, *largs):
        if key == 27:
            self.manager.transition.direction = 'right'
            self.manager.current = 'Calendar'
        
        #print(key)

    def open_filemanager(self):
        if platform == 'android':
            self.chooser = Chooser(self.choose_BG_img)
            self.chooser.choose_content()

        else:
            #openPath = '/'
            filechooser.open_file(path=self.manager.get_screen('Calendar').get_self_directory(), on_selection=self.choose_BG_img)
        

    def choose_BG_img(self, opened):

        daySetting = self.manager.get_screen('DayMood')
        
        try:

            if platform == 'android':
                ss = SharedStorage()
                path = ss.copy_from_shared(opened[0])
                
            else:
                path = opened[0]
            
            try:
                
                if os.path.isfile(path): #because it can be directory
                    
                    newFilename = 'BG_' + os.path.splitext(path)[1]

                    destination = os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), 'BG', newFilename)
                    print('ORIGINAL')
                    print(os.path.getmtime(path))
                    
                    
                    shutil.copy2(path, destination)
                    now = datetime.datetime.now().timestamp()
                    print('NOW')
                    print(now)

                    os.utime(destination,(now,now))

                    print('RESULT')
                    print(os.path.getmtime(destination))
                    
                    self.settings['bgPicture'] = newFilename
                    Clock.schedule_once(partial(self.insert_image, destination))

            except Exception as e:
                print(e)

        except Exception as e:
            print(e)

    def insert_image(self, destination, clocktime=0):
        for screen in self.manager.screens:
            screen.bgsource = destination
            self.imageRefresh()

    def imageRefresh(self, clocktime=0):
        for screen in self.manager.screens:
            for ID in screen.ids:
                if 'bgImage' in ID:
                    screen.ids[ID].reload()


    def set_default_settings(self, clocktime=0):
        self.settings.setdefault('bgPicture', 'default.jpg')

    def load_settings(self, clocktime=0):

        daySetting = self.manager.get_screen('DayMood')
        
        userdata = self.manager.get_screen('Calendar').get_userdata()
        filename = f'{userdata}/settings.json'
        
        try:   
            with open(filename, 'r', encoding='utf-8') as file:
                self.settings =  json.loads(file.read())
                self.set_default_settings()

        except FileNotFoundError:
            self.set_default_settings()
            with open(filename, 'w', encoding='utf-8') as file:
                file.write('')
                json.dump(self.settings, file, indent = 4) 

        # check if there is something set
        #if not default? but if there is file, use it

        if self.settings['bgPicture'] == 'default.jpg':
            
            BG_path = os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), 'BG')
            bg_check = os.listdir(BG_path)
            print(bg_check)

            try:

                destination = os.path.join(BG_path, bg_check[0])

                for screen in self.manager.screens:
                    screen.bgsource = destination

            except Exception as e:
                print('EXCEPTION ON SETTING BG')
                print(e)
                for screen in self.manager.screens:
                    screen.bgsource = 'pict/default.jpg'
        
        else:
            destination = os.path.join(self.manager.get_screen('Calendar').get_user_pictures(), 'BG', self.settings['bgPicture'])
            for screen in self.manager.screens:
                screen.bgsource = destination

        print('Vsechna aktualni nastaveni: ' + str(self.settings))

    def save_settings(self):
        userdata = self.manager.get_screen('Calendar').get_userdata()
        filename = f'{userdata}/settings.json'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('')
            json.dump(self.settings, file, indent = 4)
        self.load_settings()
        

class WindowManager(ScreenManager):
    pass

class CalendarLabels(MDScreen):
    pass

# run app and construct calendar

class LifePixels(MDApp):
    title = 'Life in Pixels'
    def build(self):

        Builder.load_file('lifepixelskv.kv') #same name for kv file causes some events fired twice
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(CalendarWindow(name='Calendar'))
        sm.add_widget(DayWindow(name='DayMood'))
        sm.add_widget(HabitsWindow(name='Habits'))
        sm.add_widget(SettingsWindow(name='Settings'))
        sm.add_widget(CalendarLabels(name='CalLabels'))
        sm.current = 'Calendar'
        return sm

    
    def permissions_external_storage(self, *args):                  
        if platform == "android":
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Environment = autoclass("android.os.Environment")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            if api_version > 29:
                # If you have access to the external storage, do whatever you need
                if Environment.isExternalStorageManager():

                    # If you don't have access, launch a new activity to show the user the system's dialog
                    # to allow access to the external storage
                    pass
                else:
                    try:
                        activity = mActivity.getApplicationContext()
                        uri = Uri.parse("package:" + activity.getPackageName())
                        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                        currentActivity = cast(
                        "android.app.Activity", PythonActivity.mActivity
                        )
                        currentActivity.startActivityForResult(intent, 101)
                    except:
                        intent = Intent()
                        intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                        currentActivity = cast(
                        "android.app.Activity", PythonActivity.mActivity
                        )
                        currentActivity.startActivityForResult(intent, 101)
                    self.show_permission_popup.dismiss()

    def _show_validation_dialog(self):
        if platform == "android":
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                self.show_permission_popup = MDDialog(
                    title="Alert",
                    text="Permission to access your device's internal storage and files..",
                    size_hint=(0.6, 0.5),
                    buttons=[
                        MDFlatButton(
                            text="Allow", on_press=self.permissions_external_storage
                        ),
                        MDFlatButton(
                            text="Decline",
                            on_release=self._close_validation_dialog,
                        ),
                    ],
                )
                self.show_permission_popup.open()

    def _close_validation_dialog(self, widget):
        """Close input fields validation dialog"""
        self.show_permission_popup.dismiss()
    
    #def check_permissions(self, clocktime=0):
    #    if platform == 'android':
    #        from android.permissions import request_permissions, Permission, check_permission
    #        permission_statusREAD = check_permission(Permission.READ_EXTERNAL_STORAGE)
    #        print('READ:')
    #        print(permission_statusREAD)
    #        #permission_status = check_permission(Permission.READ_EXTERNAL_STORAGE)
    #        #permission_statusWRITE = check_permission(Permission.WRITE_EXTERNAL_STORAGE,)
    #        #print('WRITE:')
    #        #print(permission_statusWRITE)
    #        return permission_statusREAD

    def on_start(self):
        #self.profile = cProfile.Profile()
        #self.profile.enable()


        
        #if platform == 'android':
            #from android.permissions import request_permissions, Permission
            
            #if self.check_permissions() != True:
            #    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.INTERNET])
            #    Clock.schedule_once(self.root.current_screen.create_userdata_directories)
            #    #Clock.schedule_once(self.root.current_screen.sync_data,4)

        if platform == 'android':
            self._show_validation_dialog()
        
        self.root.current_screen.create_userdata_directories()

        Clock.schedule_once(self.root.get_screen('Settings').load_settings)
        self.root.current_screen.make_Cal() #- done on the end of sync - maybe after on pause true not needed

    def on_pause(self):
        DayWin = self.root.get_screen('DayMood')
        if self.root.current_screen == DayWin:
            self.root.get_screen('Calendar').save_data(DayWin.dateData,DayWin.date_id)
            print('SAVE ON STOP')
        return True #because othervise it is stopping 

    def on_resume(self):
        pass

    def stop(self):

        #self.profile.disable()
        #p = pstats.Stats(self.profile)
        #p.sort_stats(SortKey.CUMULATIVE).print_stats(20)
        #p.strip_dirs().sort_stats(-1).print_stats()
        #self.profile.dump_stats('myapp.profile')

        DayWin = self.root.get_screen('DayMood')

        if self.root.current_screen == DayWin:
            self.root.get_screen('Calendar').save_data(DayWin.dateData,DayWin.date_id)
            print('SAVE ON THE END')
        print('uzaviram')

if __name__ == "__main__":
    LifePixels().run()
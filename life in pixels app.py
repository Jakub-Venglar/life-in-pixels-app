#! python3
import calendar
from datetime import datetime
from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget

class LifeLayout(MDWidget):
    def makeCal(self):
        c = calendar.Calendar(0)
        calList = [['1-1','1-2','1-3','1-4','1-5','1-6','1-7'],
                    ['2-1','2-2','2-3','2-4','2-5','2-6','2-7'],
                    ['3-1','3-2','3-3','3-4','3-5','3-6','3-7'],
                    ['4-1','4-2','4-3','4-4','4-5','4-6','4-7'],
                    ['5-1','5-2','5-3','5-4','5-5','5-6','5-7']]
        currentCal = c.monthdatescalendar(datetime.now().year, datetime.now().month)
        for weeknum, week in enumerate(calList):
            for daynum, day in enumerate(week):
                id = calList[weeknum][daynum]
                self.ids[id].text = str(currentCal[weeknum][daynum].day)


        #print(currentCal[0][0].day)

class LifePixels(MDApp):
    def build(self):
        return LifeLayout()
    def on_start(self):
        self.root.makeCal()

if __name__ == "__main__":

    LifePixels().run()

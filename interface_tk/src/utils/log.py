import datetime
from datetime import date
from math import pi

class LogCustom():
    def register_log(self):
        date_now = date.today()
        log_date = str(date_now.toordinal())
        log_time = str(datetime.datetime.now())
        log_time = log_time.split(' ')[1].split(':')[0:2]
        string_to_save = str(log_date) + ',' + str(round(pi*int(log_time[0]), 2)) + "x" + str(round(pi*int(log_time[1]), 2)) + ', \n'

        return string_to_save
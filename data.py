#! /usr/bin/python
import os, sys, datetime, glob, time

# settings file: /home/username/.config/daily_settings
#   format is -    minutes_per_day:begin_valid_hour_of_login:end_valid_hour_of_login
# time add file: /tmp/username.time_add
#   single line containing number of minutes to add for today

# common procedure call to signal to user logout is happening
def logout(user, text):
  os.system("zenity --warning --title Notice --text \"%s\" --timeout=10" % text)
  os.system("skill -kill -u %s" %user)
  sys.exit()

# dump minutes left to a file
def write_time(fname, time):
  f = open(fname, "w")
  f.write(str(time))
  f.close()

def read_settings(fname):
  f = open(fname)
  time = int(f.read())
  f.close()
  return time
  
# read minutes from a file
def read_time(fname):
  f = open(fname)
  time = int(f.read())
  f.close()
  return time

today=datetime.date.today()
current_hour = time.localtime()[3]
user=os.getlogin()
settings_filename = "/home/%s/.config/daily_settings" % user
time_balance_filename="/home/%s/.config/%s.bal" % (user, today)
time_add_filename="/tmp/%s.time_add"

# check for settings file. 
if os.path.exists(settings_filename):
  settings_file = open(settings_filename)
  time_left, start, end = settings_file.read().rstrip().split(":")
  settings_file.close()
  # if outside configured hours, logout
  if current_hour < start or current_hour > end:
    logout(user, "Outside valid computer time.")
else:
  # without a settings file, logout
  logout(user, "No time permitted.")

# if a time balance file exists, use the minutes contained in it for the time_left
if os.path.exists(time_balance_filename):
  time_left = read_time(time_balance_filename)

# find balance files older than today and delete them
for old_f in glob.glob("/home/%s/.config/*.bal" % user):
  # retrieves the stats for the current jpeg image file
  # the tuple element at index 8 is the last-modified-date
  stats = os.stat(old_f)
  # put the two dates into matching format    
  lastmodDate = time.localtime(stats[8])
  if time.strptime(str(today), '%Y-%m-%d') > lastmodDate:
     os.remove(old_f)

# if a time add file exists, add it to current time_left
if os.path.exists(time_add_filename):
  time_left += read_time(time_add_filename)
  os.remove(time_add_filename)

# no time or time expired
if time_left <= 0:
  logout(user, "No time left today.")

# Give a nice welcome message to user
os.system("zenity --info --title \"Welcome\" --text \"You have %d minutes left.\" --timeout=10" % time_left)

# loop until time expires
while time_left > 0:
  # Warn user @ 5 minutes
  if time_left == 5:
    os.system("zenity --warning --title \"WARNING\" --text \"You have 5 minutes left util autologout.\" --timeout=10")
  # Warn again @ 2 minutes
  elif time_left == 2:
    os.system("zenity --warning --title \"WARNING\" --text \"You have 2 minutes left util autologout.\" --timeout=10")

  # check for time_add_filename. If found, read minutes from that file and add to time_left
  if os.path.exists(time_add_filename):
    time_left += read_time(time_add_filename)
    os.remove(time_add_filename)

  # record current time left
  write_time(time_balance_filename, time_left)  
  time.sleep(60)
  time_left -= 1

# time expired. Write 0 to time file for today and logout
write_time(time_balance_filename, 0)
logout(user, "Time expired")





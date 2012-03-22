#!/usr/bin/env python 

import subprocess
from twill import get_browser
from twill.commands import *

#subprocess.call("python restFrontEnd.py \&\> cherry.log \&",shell=True)
#print "Press Enter to continue"
#subprocess.call("read line",shell=True)


get_browser()


#----------------- USER HISTORY --------------------------
print "USER HISTORY:  <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/histuser')
formclear('1')
fv("1", "userId", "mike")
showforms()
submit('0')




#------------------ USER ADD --------------------
print "USER ADD: user input  no input <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/useradd')
formclear('1')
fv("1", "userId", "")
showforms()
submit('0')

print "USER ADD: admin input <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/useradd')
formclear('1')
fv("1", "userId", "adminUser")
showforms()
submit('0')



#------------------ USER LIST --------------------------
print "USER LIST: user input  no input <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/userlist')
show()


#------------------  USER DEL --------------------------

print "USER DEL: <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/userdel')
formclear('1')
fv("1", "userId", "huy")
submit('0')

#------------------  USER QUOTA --------------------------

print "SET QUOTA: <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/setUserQuota')
formclear('1')
fv("1", "userId", "mike")
fv("1", "quota", "3054")
submit('0')
show()

#------------------  USER ROLE --------------------------

print "USER ROLE: <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/setuserrole')
formclear('1')
fv("1", "userId", "mike")
fv("1", "role", "role configuration")
submit('0')
show()


#------------------  USER STATUS --------------------------

print "SET USER STATUS: <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/setuserstatus')
formclear('1')
fv("1", "userId", "mike")
fv("1", "status", "active")
submit('0')








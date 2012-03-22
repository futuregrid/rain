#!/usr/bin/env python 

import subprocess
from twill import get_browser
from twill.commands import *





#subprocess.call("python restFrontEnd.py \&\> cherry.log \&",shell=True)
#print "Press Enter to continue"
#subprocess.call("read line",shell=True)




get_browser()

#----------------- LIST --------------------------
print "LIST:  <enter> "
subprocess.call("read line", shell = True)
get_browser()
go('http://localhost:8080/list')
showforms()
formclear('1')
fv("1", "queryString", "Some query String")
showforms()
submit('0')

#----------------- GET --------------------------
print "GET:  <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/get')
formclear('1')
fv("1", "imageFileName", "/tmp/myfile")
fv("1", "imageId", "4dd3657bc61d5c08f6000000")
showforms()
submit('0')


#---------------- PUT COMMAND ----------------
#print "To execute the put command hit ennter"
#subprocess.call("read line",shell=True)
#go('http://localhost:8080/put')
#formclear('1')
#formfile("1","imageFileName","/Users/mlewis/Downloads/ttylinux/ttylinux.img" )
#fv("1","userId","huy")
#fv("1","attributeString","newAttributeString")
#showforms()
#submit('0')

#----------------- MODIFY --------------------------
print "MODIFY:  <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/modify')
formclear('1')
fv("1", "imageId", "4dd3657bc61d5c08f6000000")
fv("1", "attributeString", "Some Modify Attribute String")
showforms()
submit('0')

#----------------- REMOVE --------------------------
print "REMOVE:  <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/remove')
formclear('1')
fv("1", "imageId", "4dd3657bc61d5c08f6000000")
showforms()
submit('0')

#----------------- IMAGE HISTORY --------------------------
print "IMAGE HISTORY :  <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/histimg')
formclear('1')
fv("1", "imageId", "4dd3657bc61d5c08f6000000")
showforms()
submit('0')


#------------------ USER ADD --------------------
print "USER add: user input  no input <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/useradd')
formclear('1')
fv("1", "userId", "")
showforms()
submit('0')

print "USER add: user input  no input <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/useradd')
formclear('1')
fv("1", "userId", "adminUser")
showforms()
submit('0')



#------------------ USER LIST --------------------------
print "USER add: user input  no input <enter> "
subprocess.call("read line", shell = True)
go('http://localhost:8080/userlist')




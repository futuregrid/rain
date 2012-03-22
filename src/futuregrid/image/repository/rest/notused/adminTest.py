#!/usr/bin/env python 

import subprocess
from twill import get_browser
from twill.commands import *





#subprocess.call("python restFrontEnd.py \&\> cherry.log \&",shell=True)
#print "Press Enter to continue"
#subprocess.call("read line",shell=True)




get_browser()


#----------------- GET --------------------------
print "GET:  <enter> "
subprocess.call("read line", shell = True)
go('https://localhost:8443/adminRest/get')
formclear('1')
fv("1", "imgId", "4dd3657bc61d5c08f6000000")
fv("1", "option", "img")
showforms()
submit('0')


#---------------- PUT COMMAND ----------------
print "To execute the put command hit ennter"
subprocess.call("read line", shell = True)
go('https://localhost:8443/adminRest/put')
formclear('1')
formfile("1", "imageFileName", "/Users/mlewis/downloads/ttylinux/ttylinux.img")
fv("1", "userId", "mlewis")
fv("1", "attributeString", "newAttributeString")
showforms()
submit('0')

#----------------- MODIFY --------------------------
print "MODIFY:  <enter> "
subprocess.call("read line", shell = True)
go('https://localhost:8443/adminRest/modify')
formclear('1')
fv("1", "imgId", "4dd3657bc61d5c08f6000000")
fv("1", "attributeString", "Some Modify Attribute String")
showforms()
submit('0')
show()

#----------------- REMOVE --------------------------
print "REMOVE:  <enter> "
subprocess.call("read line", shell = True)
go('https://localhost:8443/adminRest/remove')
formclear('1')
fv("1", "imgId", "4dd3657bc61d5c08f6000000")
showforms()
submit('0')

#----------------- IMAGE HISTORY --------------------------
print "IMAGE HISTORY :  <enter> "
subprocess.call("read line", shell = True)
go('https://localhost:8443/adminRest/histimage')
formclear('1')
fv("1", "imgId", "4dd3657bc61d5c08f6000000")
showforms()
submit('0')
show()

#----------------- SETPERMISSION --------------------------
print "SET PERMISSION :  <enter> "
subprocess.call("read line", shell = True)
go('https://localhost:8443/adminRest/setpermission')
formclear('1')
fv("1", "imgId", "4dd3657bc61d5c08f6000000")
fv("1", "permissionString", "permissions")
showforms()
submit('0')
show()





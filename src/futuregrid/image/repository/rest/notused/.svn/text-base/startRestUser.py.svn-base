"""
@author Michael Lewis
"""
import ConfigParser
import cherrypy
from cherrypy import _cpserver
from cherrypy import _cpwsgi_server
import os, sys
import cherrypy.lib.sessions
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../server/')
from IRService import IRService
from cherrypy.lib.static import serve_file

localDir = os.path.abspath(os.path.dirname(__file__))

httpconfig = os.path.join(localDir, 'httpconfig.conf')
httpUserConfig = os.path.join(localDir, 'httpUserConfig.conf')
userconfig = os.path.join(localDir, 'userConfig.conf')
httpsconfig = os.path.join(localDir, 'httpsconfig.conf')
certificate = os.path.join(localDir, 'server.crt')
privateKey = os.path.join(localDir, 'server.key')
userName = None
config = None


class UserRestService :
    msg = None
    writeMethodsExposed = True

    def results(self) :
        # adds the ending html tags and possible footer here                                      
        self.msg += "<br> <br> <a href = \"index\"> Return to the main page </a> "
        self.msg += "</body> </html>"
        return self.msg
    results.exposed = True

    def setMessage(self, message) :
        if self.msg == None :
            self.msg = "<html> <body> %s " % message
        else :
            self.msg += message
        return

    def index(self) :
        self.msg = None
        message = "<b> User Commands </b><br> "
        message += "<a href=\"help\"> Get help information </a> <br>"
        message += "<a href=\"list\"> Get list of images that meet the criteria </a> <br>"
        message += "<a href=\"get\"> Retrieve image or URI </a> <br>"
        message += "<a href=\"put\"> Upload/register an image </a> <br>"
        message += "<a href=\"modify\"> Modify an image </a> <br>"
        message += "<a href=\"remove\">  Remove an image from the repository </a> <br>"
        message += "<a href=\"histimg\"> Usage info of an image </a> <br>"
        message += "<a href=\"histuser\">  Usage info of a user </a> <br>"
        self.setMessage(message)
        raise cherrypy.HTTPRedirect("results")
    index.exposed = True;

    def help (self) :
        self.msg = None
        message = " help: get help information. <br>"
        message += " list queryString: get list of images that meet the criteria<br>"
        message += " get img/uri imgId: get a image or only the URI by id<br>"
        message += " put imgFile attributeString: upload/register an image<br>"
        message += " modify imgId attributeString: update information<br>"
        message += " remove imgId: remove an image from the repository<br>"
        message += " histimg imgId: get usage info of an image <br>"
        message += " histuser userId: get usage info of a user <br>"
        self.setMessage(message)
        raise cherrypy.HTTPRedirect("results")
    help.exposed = True;


    def actionList (self, queryString) :
        service = IRService()
        if (len(queryString) == 0):
            imgsList = service.query(userName, "*")
        else:
            imgsList = service.query(userName, queryString)

        if(len(imgsList) > 0):
            try:
                    self.msg = str(imgsList)
            except:
                self.msg = "list: Error:" + str(sys.exc_info()[0]) + "</br>"
                self._log.error("list: Error interpreting the list of images from Image Repository" + str(sys.exc_info()[0]))
        else:
            self.msg = "No list of images returned"
        raise cherrypy.HTTPRedirect("results")
    actionList.exposed = True

    def list (self) :
        self.msg = """ <form method=get action=actionList>                                                                                                      Query string: <input type=string name=queryString> <br>                                                                                        <input type=submit> </form> """
        return self.msg;
    list.exposed = True

    def actionGet(self, option, imgId):
        self.msg = None
        if (len(imgId) > 0 and len(option) > 0):
            service = IRService()
            print("User name %s " % userName)
            filepath = service.get(userName, option, imgId)
            if (filepath == None) :
                self.setMessage("No public images in the repository and/or no images owned by user")
                raise cherrypy.HTTPRedirect("results")
            if (len(imgId) > 0) :
                self.setMessage("Downloading img to %s " % filepath.__str__())
                print("Downloading img to %s " % filepath.__str__())
            else :
                self.setMessage("URL:  %s " % filepath.__str__())
        else :
            self.setMessage("The image Id or option is empty! Please input both the image Id and option")
            raise cherrypy.HTTPRedirect("results")

        serve_file(filepath, "application/x-download", "attachment")

        raise cherrypy.HTTPRedirect("results")

    actionGet.exposed = True

    def get (self):
        return """                                                                                                                                           <html><body>                                                                                                                                      <form method=get action=actionGet>                                                                                                                    Image Id: <input type=string name=imgId> <br>                              
                                         Option ('img' or 'uri'): <input type=string name=option> <br>                                                                   <input type=submit>
                                       </form>
                         </body></html>         
       """
    get.exposed = True;

    def actionPut (self, userId = None, imageFileName = None, attributeString = None) :
        # retrieve the data                                                                                                                       
        size = 0
        self.fromSite = "actionPut"
        self.msg = None
        self.msg = "Uploaded fileName: %s " % imageFileName.__str__()
        while 1:
            data = imageFileName.file.read(1024 * 8) # Read blocks of 8KB at a time                                                               
            size += len(data)
            if not data: break

        print("Image size %s " % size)
        self.msg += " Image size %s " % size
        service = IRService()
        print type(imageFileName)
        imageId = service.put(userName, userId, imageFileName, attributeString, size)
        raise cherrypy.HTTPRedirect("results")
    actionPut.exposed = True

    def put (self) :
       return """                                                                                                                                             <html><body>                                                                                                                                      <form method=post action=actionPut enctype="multipart/form-data">                                                                                     Upload a file: <input type=file name=imageFileName><br>                                                                                           User Id: <input type=string name=userId> <br>                                                                         attributeString: <input type=string name=attributeString> <br>                                                          <input type=submit>             
                                        </form> 
                          </body></html>
        """
    put.exposed = True;


    def actionModify (self, imgId = None, attributeString = None):
        fname = sys._getframe().f_code.co_name
        self.msg = None
        if(len(imgId) > 0):
            service = IRService()
            success = service.updateItem(userName, imgId, attributeString)
        if (success):
            self.msg = "The image %s was successfully updated" % imgId
            self.msg += " User name: < %s > " % userName
        else:
            self.msg = "Error in the update.<br>Please verify that you are the owner or that you introduced the correct arguments"
        raise cherrypy.HTTPRedirect("results")
    actionModify.exposed = writeMethodsExposed;

    def modify (self, imgId = None, attributeString = None):
        self.msg = """ <form method=get action=actionModify>                                                                                                      Image Id: <input type=string name=imgId> <br>                                                                                                     Atribute String: <input type=string name=attributeString> <br>                                                                                   <input type=submit> </form> """
        return self.msg;
    modify.exposed = writeMethodsExposed;


    def actionRemove (self, imgId = None):
        fname = sys._getframe().f_code.co_name
        service = IRService()
        status = service.remove(userName, imgId)
        self.msg = None
        if (status == True):
            self.msg = "The image with imgId=" + imgId + " has been removed"
        else:
            self.msg = "The image with imgId=" + imgId + " has NOT been removed.</br>Please verify the imgId and if you are the image owner"
            raise cherrypy.HTTPRedirect("results")
    actionRemove.exposed = True;

    def remove (self):
        self.msg = """ <form method=get action=actionRemove>                                                                                                      Image Id: <input type=string name=imgId> <br>                                                                                                     <input type=submit> </form> """
        return self.msg
    remove.exposed = True

    def actionHistImage (self, imgId):
        service = IRService()
        fname = sys._getframe().f_code.co_name
        self.msg = None
        if(len(imgId) > 0):
            imgsList = service.histImg(userName, imgId)
        else:
            imgsList = service.histImg(userName, "None")

        try:
            imgs = service.printHistImg(imgsList)
            self.msg = imgs['head']
            for key in imgs.keys():
                if key != 'head':
                    self.msg = self.msg + imgs[key] + "\n"
        except:
            self.msg = "histimg: Error:" + str(sys.exc_info()[0]) + "\n"
            self._log.error("histimg: Error interpreting the list of images from Image Repository" + str(sys.exc_info()[0]))
        raise cherrypy.HTTPRedirect("results")
    actionHistImage.exposed = True;

    def histimg (self):
        self.msg = """ <form method=get action=actionHistImage>                                                                                                   Image Id: <input type=string name=imgId> <br>                                                                                                     <input type=submit> </form> """
        return self.msg;
    histimg.exposed = True;



    def actionHistUser (self, userId):
        fname = sys._getframe().f_code.co_name
        service = IRService()
        self.msg = None
        if (len(userId) > 0):
            userList = service.histUser(userName, userId)
        else:
            userList = service.histUser(userName, "None")

        try:
            users = userList
            self.msg = users['head']
            self.msg = "<br>"
            for key in users.keys():
                if key != 'head':
                    self.msg = self.msg + users[key]
        except:
            self.msg = "histuser: Error:" + str(sys.exc_info()[0]) + "\n"
            self._log.error("histuser: Error interpreting the list of users from Image Repository" + str(sys.exc_info()[0]))
        raise cherrypy.HTTPRedirect("results")
    actionHistUser.exposed = True;

    def histuser (self) :
        self.msg = """ <form method=get action=actionHistUser>                                                                                                     User Id: <input type=string name=userId> <br>                                                                                                     <input type=submit> </form> """
        return self.msg
    histuser.exposed = True;

if __name__ == '__main__':


    # Site configuration
    cherrypy.config.update(httpsconfig)
    ip = cherrypy.config.get("server.socket_host")
    port = cherrypy.config.get("server.socket_port1")
    cherrypy.tree.mount(UserRestService(), '/userRest', config = userconfig)
    cherrypy.config.update(userconfig)
    userName = cherrypy.config.get("user_name")
    print("user name : %s " % userName)


    secure_server = _cpwsgi_server.CPWSGIServer()
    secure_server.bind_addr = (ip, port)
    secure_server.ssl_certificate = certificate
    secure_server.ssl_private_key = privateKey

    adapter = _cpserver.ServerAdapter(cherrypy.engine, secure_server, secure_server.bind_addr)
    adapter.subscribe()
    cherrypy.quickstart(UserRestService(), config = httpUserConfig)


else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(AdminRestService, config = configurationFile)

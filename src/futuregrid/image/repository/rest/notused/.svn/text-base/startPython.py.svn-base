#! /bin/sh                                                                                                 

######################################################################                                     
## WAIT FOR INPUT                                                                                          
function wait() {
    echo "Press ENTER to continue"
    read line
}
######################################################################   

source ~/ .bashrc

echo "######################################################################"
echo "Starting mongod"
echo "######################################################################"
mongod - -port 23000 &
mongoPID = $ !
sleep 1

lsof - i tcp:23000

wait



echo "######################################################################"
echo "Put service"
echo "######################################################################"

python restFrontEnd.py &> cherry.log &
serverPID = $ !
sleep 1

lsof - i tcp:8080
lsof - i tcp:23000



#open http://localhost:8080/list
#open http://localhost:8080/put?userId=mlewis&imageFileName=/Users/mlewis/downloads/imageFile.tar.gz&attributeString=JustATest

wait


echo "Enter return to kill mongod and cherrypy server"
read line

kill - 9 ${serverPID}
kill - 9 ${mongoPID}


rm / data / db / mongod.lock

lsof - i tcp:8080
lsof - i tcp:23000


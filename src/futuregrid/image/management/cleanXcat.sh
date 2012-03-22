#!/bin/bash
##call this using while read line; do ./cleanXcat.sh $line; done < images;
##images has imagename arch in each line
if [ $# -ne 2 ]
then
  echo "Usage: `basename $0 ` {imagename arch}"
  exit $E_BADARGS
else
  echo "clean xCAT"
  todel="/install/netboot/$1"
  if [ $todel != "/install/netboot/" ]
  then
      echo "rm -rf $todel"
      #rm -rf $todel
  fi
  todel="/tftpboot/xcat/$1"
  if [ $todel != "/tftpboot/xcat/" ]
  then
      echo "rm -rf $todel"
      #rm -rf $todel
  fi
  todel="/tftpboot/xcat/netboot/$1"
  if [ $todel != "/tftpboot/xcat/netboot/" ]
  then
      echo "rm -rf $todel"
      #rm -rf $todel
  fi
  echo "tabch -d osvers=$1 osimage"
  #tabch -d osvers=$1 osimage
  echo "tabch -d imagename=$1-$2-statelite-compute linuximage"
  #tabch -d imagename=$1-$2-statelite-compute linuximage

  echo "tabch -d bprofile=$1 boottarget"
  #tabch -d osvers=$1 osimage
  
  #this last one is for moab
  echo "clean Moab"
  echo "sed -i \"/^$1/d\" /opt/moab/tools/msm/images.txt" 
  #sed -i "/^$1/d" 
fi

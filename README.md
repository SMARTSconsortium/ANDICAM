# ANDICAM
all the programs that are used to process, distribute, download, archive ANDICAM data

ANDICAM is a dual Optical IR imager, mounted on the SMARTS 1.3-m Telescope in C.T.I.O. Chile.
Each night, observations for various science projects are made by telescope operators in Chile.
The following morning, the data are downloaded to Yale, where they are processed, under go pre-processing, and are distributed to SMARTS PI's via an FTP site. The data are the archieved to external disk in the afternoon.


Copying Over Data
-----------------------
the shell script autoarchive in this repository lives on the yale astro machine thuban in the directory /data/yalo180/yalo/SMARTS13m. every morning, a cron daemon executes this script. It creates a date directory, which has sub directories for optical data, ir data and ir calibration frames.

Reducing Data
------------------------
the python  module acamred.py contains several functions to reduce optical data, and stage the optical data and ir data so it can be uploaded to the smarts ftp site. to run the reduction, first switch users to yalo. then at your shell prompt, type pyraf to begin a pyraf session. Once the pyraf prompt come up, follow the instructions below

1) import the reduction module
''''-->import acamred''''

2) change directories to the reduced sub directory for the date you are interested in
''''--> cd /data/yalo180/yalo/SMARTS13m/YYYYMMDD/ccd/reduced''''

3) if biases, optical domes, or skyflats were taken that night but need to be combined, use the acamred module
''''--> acamred.optdomecomb(YYMMDD)''''
''''--> acamred.skyflat(YYMMDD)''''

4) if you need to copy over old domes or skyflats from a previous night, do it now

5) once everything is in place, execute the reduction pipeline
''''--> acamred.reduceall()''''

the reduceall function will also call shell scripts that upload the data to the ftp site, discussed below in greater detail

Uploading Data
-----------------------
the modules IRsort() and CCDsort() in acamred.py create owners.lis files, which list the SMARTS plans for which observations were made in the night that was being reduced. the owners.lis files are used as input for the shell scripts ftpupload.sh, and uploads the data for these observing plans to the ftp site, where SMARTS PIs may retrieve them. the ftpupload.sh scripts reside under /data/yalo180/yalo/SMARTS13m/CCD and /data/yalo180/yalo/SMARTS13m/IR.

Archiving Data
----------------------
the shell script autoarchive2 is called by a cron daemon every day at 3pm. this script lives under the directory /data/yalo180/yalo/SMARTS13m/. it gets a listing of all the date directories and data that lies there under, and rsyncs over any data that is not also on the external hard drive 'SMARTS3'

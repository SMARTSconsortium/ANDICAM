# ANDICAM
all the programs that are used to process, distribute, download, archive ANDICAM data

ANDICAM is a dual Optical IR imager, mounted on the SMARTS 1.3-m Telescope in C.T.I.O. Chile.
Each night, observations for various science projects are made by telescope operators in Chile.
The following morning, the data are downloaded to Yale, where they are processed, under go pre-processing, and are distributed to SMARTS PI's via an FTP site. The data are the archieved to external disk in the afternoon.


Copying Over Data From CTIO
-----------------------
the shell script autodates in this repository lives on the yale astro machine thuban in the directory /data/yalo180/yalo/SMARTS13m. every morning, a cron daemon executes this script. It creates a date directory, which has sub directories for optical data, ir data and ir calibration frames.

if you need to, you can execute this by hand
```shell
cd /data/yalo180/yalo/SMARTS13m
./autodates
```

Reducing Data
------------------------
the python  module acamred.py contains several functions to reduce optical data, and stage the optical data and ir data so it can be uploaded to the smarts ftp site. to run the reduction, first switch users to yalo. then at your shell prompt, type pyraf to begin a pyraf session. Once the pyraf prompt come up, follow the instructions below

1) import the reduction module
```python
-->import acamred
```

2) change directories to the reduced sub directory for the date you are interested in
```
--> cd /data/yalo180/yalo/SMARTS13m/YYYYMMDD/ccd/reduced
```

3) if biases, optical domes, or skyflats were taken that night but need to be combined, use the acamred module
```python
--> acamred.optdomecomb(YYMMDD)
--> acamred.skyflat(YYMMDD)
```

4) if you need to copy over old optical domes or skyflats from a previous night, you can us cpCals. For example, to copy all domes and skyflats from a previous date,
```python
-->acamred.cpCals(20150801)
```
to copy particular flats over from a previous date
```
-->acamred.cpCals(20150801,['sky','V',I'])
```
will copy over anyfiles with 'V','sky', or 'I' in the filename. You can refer to the source code for more details on using cpCals. Note that this only works for optical calibrtions, and does not look for biases by default.

5) once everything is in place, execute the reduction pipeline
```python
--> acamred.reduceall()
```

the reduceall function will also call shell scripts that upload the data to the ftp site, discussed below in greater detail

Uploading Data
-----------------------
the modules IRsort() and CCDsort() in acamred.py create owners.lis files, which list the SMARTS plans for which observations were made in the night that was being reduced. the owners.lis files are used as input for the shell scripts ftpupload.sh, and uploads the data for these observing plans to the ftp site, where SMARTS PIs may retrieve them. the ftpupload.sh scripts reside under /data/yalo180/yalo/SMARTS13m/CCD and /data/yalo180/yalo/SMARTS13m/IR.

if the data are already reduced but you need to distribute them again, you can use the acamred modules and ftpupload scripts by had

1) switch users to yalo, start up a pyraf session, and imort the acamred modue (see above)

2) navigate to the copies directory for the optical data you want to distribute, and use CCDsort(). This will make the file /data/yalo180/yalo/SMARTS13m/CCD/owners.lis, which is used by ftpupload
```python
--> cd /data/yalo180/yalo/SMARTS13m/YYYYMMDD/ccd/processed/copies/
--> acamred.CCDsort()
```

3) do the analogous steps for the IR data. This will make /data/yalo180/yalo/SMARTS13m/IR/owners.lis
```python
--> cd /data/yalo180/yalo/SMARTS13m/YYYYMMDD/ir/copies/
--> acamred.IRsort()
```

4) use the ftp upload scripts
```
--> cd /data/yalo180/yalo/SMARTS13m/CCD
--> !./ftpupload.sh
--> /data/yalo180/yalo/SMARTS13m/IR
--> !./ftpupload.sh
```

Archiving Data
----------------------
the shell script autoarchive2 is called by a cron daemon every day at 3pm. this script lives under the directory /data/yalo180/yalo/SMARTS13m/. it gets a listing of all the date directories and data that lies there under, and rsyncs over any data that is not also on the external hard drive 'SMARTS3'

if you need to, you can execute this by hand
```shell
cd /data/yalo180/yalo/SMARTS13m
./autoarchive2
```

Setting Up The Crontab
-----------------------
the cron daemons are listed in a crontab for the user yalo on the machine thuban. if you ever need to reinstall the crontab, follow the instructions below

1) as the user yalo, at the shell prompt type
```shell
crontab -e
```
this will open up the crontab in the text editor vi for editing, or create a new one for editing if there is no crontab

2) press 'I' on your keyboard so you can insert text, and insert the following:
```shell
SHELL=/bin/bash
MAILTO=imran.hasan@yale.edu,emily.machpherson@yale.edu
0 7 * * * /data/yalo180/yalo/SMARTS13m/autodates
0 15 * * * /data/yalo180/yalo/SMARTS13m/autoarchive2
```
the first line sets the shell enviornment to bash. this important because yalo's default shell is tcsh, but the scripts are written for bash.
the second line sets the mailto variable. this is the email address(s) that any output-including error messages-is sent to. you can put as many as you want, so long as they are seperated by a comma
the last two lines are instructions, at 7AM and 3PM of every day of every week of every month, execute the listed programs.

3) once you are finished inputting all of that, on you keyboard hit 'escape', and the ':w return' to save the changes, and ':q return' to quit.


Suggested Improvements
----------------------
1. occasionally autodates will fail if there is poor connection to CTIO, if there was no data taken the previous night, if the observer did not stage the data correctly, or if the observer did stage the data correctly but only after the crondaemon called autodates. it would be nice if autodates was able to deal with these intelligently
2. turn autodates into a function that accepts the date as input. that way you can rsync data over from previous nights
3. the autoarchive2 script will fail if the external hard drive is not mounted to thuban. it would be helpful if it had a small routine that checked if it was mounted, and mounted it if need be
4. the acamred module has no way of dealing with ircalibration frames. i looked at the user defined iraf task domecombineir that suzanne and michelle wrote, but i was too scared of it to translate it to PyRAF for the pipeline. so i left it for someone else to do :trollface:
5. often you have to copy optical calibrations over from previous nights to reduce a particular night. it would be nice if there was a routine that did this for you

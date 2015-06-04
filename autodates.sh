#
#creates directory for a specific date, and subdirectories
#for ccd raw and processed data, and ir data
#before you use this, make sure you are in a bash terminal. the default 
#terminal for yalo is tcsh, which doesnt know how to use some 
#commands in this script. to switch to a bash terminal, simply type 'bash' 
#and hit return. this will be temporary, and the yalo terminal will go back 
#to its default setting after the session
#
#Emily added a line! 130429 copies binned ir data into /copies folder


yalodate=$(date -d 'yesterday' '+%Y%m%d')
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate/ccd
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate/ccd/raw
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate/ccd/processed
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate/ccd/processed/copies
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate/ir
mkdir /data/yalo180/yalo/SMARTS13m/$yalodate/ir/copies
acamdate=$(expr $yalodate - 20000000)
rsync observer@andicam.ctio.noao.edu:/data/observer/$acamdate/irbinned/binir*fits /data/yalo180/yalo/SMARTS13m/$yalodate/ir/
cp /data/yalo180/yalo/SMARTS13m/$yalodate/ir/bin* /data/yalo180/yalo/SMARTS13m/$yalodate/ir/copies/
rsync observer@andicam.ctio.noao.edu:/data/observer/$acamdate/ccd*fits /data/yalo180/yalo/SMARTS13m/$yalodate/ccd/raw/
cp /data/yalo180/yalo/SMARTS13m/$yalodate/ccd/raw/ccd* /data/yalo180/yalo/SMARTS13m/$yalodate/ccd/processed
rsync -r observer@andicam.ctio.noao.edu:/data/observer/$acamdate/irbinned/ircalibs /data/yalo180/yalo/SMARTS13m/$yalodate/ir/

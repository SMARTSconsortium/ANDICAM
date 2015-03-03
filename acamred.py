#!/scisoft/bin/python
#pyraf equivalents of speedup.cl, processccd.cl, combflat.cl, CCDsort.cl, and IRsort.cl
#these functions mirror their iraf counterparts pretty closesly, and function in the same way
#the pyraf wrapper prevents caching problems and lets us easily change directories, execute functions etc
#some projects have special places to pick up data, like the blazar group
#the photometric standards, xrb group, and bethany. specific checks are made for those data
import pyfits
import os
import fnmatch
import glob
from pyraf import iraf
iraf.prcacheOff()

#dont use this, its still under construction
def domecalibs(band):
	bandcomb=iraf.ls("*.dome"+band+".fits", Stdout=1)
	if len(bandframes) == 1:
		return
	elif len(bandframes) == 0:
		banduncomb=iraf.ls("dome"+band+".*.fits", Stdout=1)
		if len(banduncomb) != 10:
			oldband=iraf.ls("/data/yalo180/yalo/SMARTS13m/PROCESSEDCALS/ccd*.dome"+band+".fits", Stdout=1)
			iraf.imcopy(oldband[-1], output='.')
		return

#make a combined b skyflat. 
#Requires: a bias image in same directory to do the bias subtraction
#	skyflats must be offset and have appropriate count number
#input: the date the skyflats were observed YYMMDD
#output: flat.B, a text file that lists the names of the skyflat fits files
#	ccdYYMMDD.skyflatB.fits, the combined skyflat
def skyflat(date, low=15000, high=22000, numimages=5):
	#check if biases are in this directory
	if len(glob.glob('*.bias.*')) < 1:
		print "no combined bias found, exiting"
		return
	#get image name and mean pixel value for all skyflat images
	stats=iraf.imstat('*sky*',format=False,fields='image,mean',Stdout=1)
	pairs=[i.split() for i in stats]

	#write the names of the skyflats w right ammount of counts to file
	#keep track of how many good ones there are
	goodCount=0
	with open("flat.B",'w') as FB:
		for i in pairs:
			if float(i[1]) > low and float(i[1]) < high:
				FB.write(i[0]+'\n')
				goodCount+=1

	if goodCount < numimages:
		print "only "+str(goodCount)+" skyflats have counts between "+str(low)+" and "+str(high)
		print "no combined skyflat made"
		return
	else:
		iraf.ccdproc(images="@flat.B",output=" ",fixpix="no",overscan="yes",trim="no",zerocor="yes",darkcor="no",flatcor="no",illumcor="no",fringecor="no",readcor="no",scancor="no",readaxis="line",biassec="[3:14,1:1024]",zero="*.bias.fits",interactive="no",functio="spline3",order=11)
		iraf.flatcombine("@flat.B",output="FLAT",combine="median",reject="minmax",process="no",scale="mode",ccdtype="")
		os.system("mv FLAT.fits ccd"+str(date)+".skyflatB.fits")
		print ("made combined skyflat ccd"+str(date)+".skyflatB.fits")
	return

#combine biases and optical domes
#Requires: the uncombined fits images
#	if you are combining a dome, you must have a bias from the same night as the dome to preform appropriate bias subtraction
#Input: the date the domes were observed YYMMDD, and fwheel, a list that contains the filters of the domes to be combined
#Outupt: combined dome fits frame for each color where uncombined frames are in the directory 
def optdomecomb(date, fwheel=['bias','B','V','R','I']):
	#convert date to string incase it was entered as an int of float
	date=str(date)
	if len(glob.glob('*bias*')) < 1:
		print "no biases found, exiting"
		return
	else:
		for color in fwheel:
			if color=='bias':
				biaslist=glob.glob('*bias.[0-9]*')
				if len(biaslist) > 10:
					print "only "+str(len(biaslist))+" biases found. you need at least 10"
				else:
					with open("bias.list",'w') as BILIS:
						for i in biaslist:
							BILIS.write(i+'\n')
					iraf.zerocombine("@bias.list",output="ccd"+str(date)+".bias.fits",combine="average",reject="minmax",scale="none",ccdtype="",process="no",delete="no",clobber="no",nlow=1,nhigh=1,nkeep=1)
					print "created ccd"+str(date)+".bias.fits"
					os.system('rm bias.list')

			elif color in ['B','V','R','I']:
				domelist=glob.glob('*dome'+color+'.[0-9]*')
				if len(domelist) < 1:
					print 'no '+color+' domes found'
				elif len(domelist) > 10:
					print 'only '+str(len(domelist))+' domes found. you need at least 10'
				else:
					with open('flat'+color+'.list', 'w') as flist:
						for i in domelist:
							flist.write(i+'\n')
					iraf.ccdproc("@flat"+color+".list", output="z@flat"+color+".list",ccdtype=" ",noproc="no", fixpix="no",overscan="yes", trim="no", zerocor="yes",darkcor="no",flatcor="no", illumcor="no", fringec="no", readcor="no", scancor="no", readaxis="line", biassec="[3:14,1:1024]", zero="ccd"+str(date)+".bias.fits", interactive="no", functio="spline3", order=11)
					iraf.flatcombine("z@flat"+color+".list", output="ccd"+str(date)+".dome"+color+".fits",combine="average", reject="crreject", ccdtype="", process="no", subsets="no", delete="no", clobber="no", scale="mode", rdnoise=6.5, gain=2.3)
					os.system('rm z*dome'+color+'*fits')
					print "created ccd"+str(date)+".dome"+color+".fits"
					os.system('rm flat'+color+'.list')

			else:
				print "your input for the filter was not recognized. Please use either 'bias', 'B', 'V', 'R', or 'I' and try again"
		return

#prepares optical images for reduction
#requires: skyflatB, ccd domes, ccd bias, ccd data, in directory when function is run
#input: none
#output: in.{B,V,R,I}, are txt files which list images observed in b,v,r, and i filters
def speedup():
	#the observer may have forgotten to delete focus, trim, and junk frames
	if len(glob.glob('*junk*')) > 0:
		os.system('rm *junk*')
	if len(glob.glob('*foco*')) > 0:
		os.system('rm *foco*')
	if len(glob.glob('*trim*')) > 0:
		os.system("rm *trim*")
	
	os.system("mkdir calibs")
	os.system("mv *bias* calibs")
	os.system("mv *ky* calibs")
	os.system("mv *dome* calibs")
	
	rawimages=glob.glob('ccd*.fits')
	#open in files for writting
	B = open("in.B",'w')
	V = open("in.V",'w')
	R = open("in.R",'w')
	I = open("in.I",'w')

	for im in rawimages:
		hdulist=pyfits.open(im)
		filt=hdulist[0].header['CCDFLTID']
		hdulist.close()
		if filt=='B':
			B.write(im+'\n')
		elif filt=='V' or filt=='V+ND4':
			V.write(im+'\n')
		elif filt=='R':
			R.write(im+'\n')
		elif filt=='I' or filt=='I+ND4':
			I.write(im+'\n')
		else:
			print "filter for "+im+" is listed as "+filt+" and is not recognized"
			print im+" will not be reduced"

	#close in files
	B.close()
	V.close()
	R.close()
	I.close()

	os.chdir("calibs")			#os.system("cd wherever") doesnt work o_O
	if len(glob.glob("*dome*.0*")) > 0:
		os.system("rm *dome*.0*")
	if len(glob.glob('*domeB*')) > 0:
		os.system("rm *domeB*")
	if len(glob.glob("*bias.0*")) > 0:
		os.system("rm *bias.0*")
	iraf.hselect(images="*",fields="$I,date-obs,time-obs,ccdfltid,exptime",expr="yes")
	print ("------------------------------")
	print ("hsel *ky* $I,ra,dec,ccdfltid,exptime")
	iraf.hselect(images="*ky*",field="$I,ra,dec,ccdfltid,exptime", expr="yes")
	print ("------------------------------")
	os.system("mv * ../")
	os.chdir("../")		#new to this version, go back one directory to processed/ level
	return

#reduces optical andicam data
#required: combined optical biases and flats, unreduced data need to be in working directory
#			also in.{B,V,R,I} and out.{B,V,R,I}, which are text files that list data taken w respective filters
#input: fwheel is a python list that holds the names of the filters for which you want to reduce
#output: rccd versions of ccd*.fits images which are bias and flat corrected are output in working directory
def optreduce(fwheel):
	#make sure we have a bias so we can bias subtract the data
	if len(glob.glob('*.bias*')) < 1:
		print "no combined bias found, exiting. Please place a combined bias in this directory and try agian"
		return
	else:
		for color in fwheel:
			#check that all necessary files exist for reduction, in.color, out.color
			if len(glob.glob('in.'+color)) < 1:
				print "in."+color+" not found. "+color+" data will not be reduced. Please create file and try again"
			#elif len(glob.glob('out.'+color)) < 1:
			#	print "out."+color+" not found. "+color+" data will not be reduced. Please create file and try again"
			else:
				#B data uses the skyflat
				if color=='B':
					if len(glob.glob('*.skyflatB*')) < 1:
						print "no combined B skyflat found. B data will not be reduced. Please create combined B skyflat and try again"
					else:
						with open("in.B") as f:
							num_images=sum(1 for line in f)
						if num_images > 1:
							print str(num_images)+" B images found. Reducing ..."
							iraf.ccdproc(images="@in.B",output="r@in.B",overscan="yes",trim="yes",zerocor="yes",darkcor="no",flatcor="yes",readaxis="line",biassec="[2:16,3:1026]",trimsec="[17:1040,3:1026]",zero="*.bias.fits",flat="*.skyflatB.fits",interactive="no",function="spline3",order="11")
						else:
							print "No B images found"
				#all other data uses domes
				elif color in ['V','R','I']:
					if len(glob.glob('*.dome'+color+'.fits')) < 1:
						print "no combined "+color+" dome found. "+color+" data will not be reduced. Please create combined "+color+" dome and try again"
					else:
						with open("in."+color) as f:
							num_images=sum(1 for line in f)
						if num_images > 1:
							print str(num_images)+" "+color+" images found. Reducing ..."
							iraf.ccdproc(images="@in."+color,output="r@in."+color,overscan="yes",trim="yes",zerocor="yes",darkcor="no",flatcor="yes",readaxis="line",biassec="[2:16,3:1026]",trimsec="[17:1040,3:1026]",zero="*.bias.fits",flat="*.dome"+color+".fits",interactive="no",function="spline3",order="11")
						else:
							print "No "+color+" images found."
				else:
					print color+" is not recognized as a filter. Please use 'B', 'V', 'R', or I"
		return

#bias and flat correct all the optical data taken
#required: in.{B,V,R,I}, out.{B,V,R,I}, ccd*fits, dome{V,R,I}, skyflatB, bias
#input: none
#output: reduced images, with naming scheme rccd*fits. These are copied to the 'copies' subdirectory
def ccdproc(fwheel=['B','V','R','I']):
	#bias subtract and flat field correct optical images
	optreduce(fwheel)

	#clean up all the left over crap and backup the calibrtion files
	os.system("rm ccd*.[0-9]*.fits")	
	os.system("cp rccd*fits copies/")
	os.system("cp *.dome{R,V,I}.fits /data/yalo180/yalo/SMARTS13m/PROCESSEDCALS")
	os.system("cp *.skyflatB.* /data/yalo180/yalo/SMARTS13m/PROCESSEDCALS")
	os.system("cp *.bias.fits /data/yalo180/yalo/SMARTS13m/PROCESSEDCALS")
	return

#move the reduced ccd data to the appropriate project directory under /data/yalo180/yalo/SMARTS13m/CCD
#required: the data you want to copy
#input: none
#output: owners.lis, a txt file that lists the project owners for the fits files in this directory
#	owners.lis is needed for the ftp upload shell scripts
def CCDsort():
	#os.remove('/data/yalo180/yalo/SMARTS13m/CCD/owners.lis')
	fitsimages=fnmatch.filter(os.listdir('.'),'r*.fits')
	owners=set([pyfits.open(i)[0].header['owner'] for i in fitsimages])
	f=open('/data/yalo180/yalo/SMARTS13m/CCD/owners.lis','w')
	for i in owners:
		#we need the xrb data in the owners file for Dipankar now (ih 140826)
		if (str(i) != 'YALE-08A-0001' and str(i) != 'ALL'):
		#if (str(i) != 'YALE-03A-0001' and str(i) != 'YALE-08A-0001'):
			f.write(str(i)+'\n')
	f.close()
	for i in fitsimages:
		owner=pyfits.open(i)[0].header['owner']
		if owner=='YALE-08A-0001':
			os.system("mv "+ i +" /net/glast/ccd")
		elif owner=='YALE-03A-0001':
			os.system("cp "+ i +' /data/yalo180/yalo/SMARTS13m/CCD/ccddm/')
			os.system("mv "+ i +' /net/xrb/ccd/')
		elif owner=='STANDARD' or owner=='STANDARDFIELD':
			os.system("mv "+ i +' /data/yalo180/yalo/SMARTS13m/CCD/ccdstandards/')
		elif owner=='YALE-03A-0009':
			os.system("mv "+ i +' /data/yalo180/yalo/SMARTS13m/ccdNOAO-08B-0001')
		elif owner!='ALL':
			os.system("mv -v "+ i +" /data/yalo180/yalo/SMARTS13m/CCD/ccd"+owner)
	#iraf.imdelete(images='rccd*fits')		
	return

#move the reduced ir data to the appropriate project directory under /data/yalo180/yalo/SMARTS13m/IR
#required: the data you want to copy
#input: none
#output: owners.lis, a txt file that lists the project owners for the fits files in this directory
#	owners.lis is needed for the ftp upload shell scripts
def IRsort():
	#os.remove('/data/yalo180/yalo/SMARTS13m/CCD/owners.lis')
	fitsimages=fnmatch.filter(os.listdir('.'),'binir*.fits')
	owners=set([pyfits.open(i)[0].header['owner'] for i in fitsimages])
	f=open('/data/yalo180/yalo/SMARTS13m/IR/owners.lis','w')
	for i in owners:
		#we need the xrb data in the owners file for Dipankar now (ih 140826)
		if (str(i) != 'YALE-08A-0001' and str(i) != 'ALL'):
		#if (str(i) != 'YALE-03A-0001' and str(i) != 'YALE-08A-0001'):
			f.write(str(i)+'\n')
	f.close()
	for i in fitsimages:
		owner=pyfits.open(i)[0].header['owner']
		if owner=='YALE-08A-0001':
			os.system("mv -v "+ i +" /net/glast/ir/")
		elif owner=='YALE-03A-0001':
			os.system("cp -v "+ i +" /data/yalo180/yalo/SMARTS13m/IR/irdm/")
			os.system("mv -v "+ i +' /net/xrb/ir/')
		elif owner=='STANDARD' or owner=='STANDARDFIELD':
			os.system("mv -v "+ i +' /data/yalo180/yalo/SMARTS13m/IR/irstandards/')
		elif owner=='YALE-03A-0009':
			os.system("mv -v "+ i +' /data/yalo180/yalo/SMARTS13m/irNOAO-08B-0001')
		elif owner!='ALL':
			os.system("mv -v "+ i +" /data/yalo180/yalo/SMARTS13m/IR/ir"+owner)
	#iraf.imdelete(images='rccd*fits')		
	return

def compare(ims):
    for i in ims:
       hdun=pyfits.open(i)
       datan=hdun[0].data
       hdun.close()
       hduo=pyfits.open('../processed/'+i)
       datao=hduo[0].data
       hduo.close()
       print (datan - datao).sum()

#this function calls the others above and changes directories when needed, to preform the entire reduction process
#required: start in the YYMMDD/ccd/processed direcotry for the date you want to reduce
#	either move calibration frames into this directory, or create new ones using combflat and optdomecomb (above)
#	execute function and everything will (hopefully) work
#input:none
#output:none
def reduceall():
	#filterwheel=['V','R','I']
	#for f in filterwheel:
	#	sort.domecalibs(f)
	speedup()
	ccdproc()
	os.chdir("copies/")
	#os.system("ls")
	CCDsort()
	os.chdir("../../../ir/copies")
	IRsort()
	os.chdir("../../../CCD")
	os.system("./ftpupload.sh")
	os.chdir("../IR")
	os.system("./ftpupload.sh")
	os.chdir("../")
	return

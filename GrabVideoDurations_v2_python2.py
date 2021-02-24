# quick function to make a table of video durations in frames

import imgstore
import cv2
import numpy as np
import csv
from sys import argv
from glob import glob
from os import path
from datetime import datetime

# ====================================

def find_vid_durationFrames(bdir):
   frate = 60
   msg = "Processing video %s" % bdir
   print msg
   
   try:
      store = imgstore.new_for_filename(bdir + 'metadata.yaml')
   except:
      msg = "could not read store " + bdir + ", skipping"
      print msg
      info_frames = []
   else:      
      nframes = store.frame_count
      store.close()
      
      # return outputs
      return nframes
      

# ====================================

def main(imgstoreDir):
    # give some info
    msg = "Processing imgstores located in directory " + imgstoreDir
    print msg
	
    # check the directory exists
    if path.isdir(imgstoreDir) == False:
      print "ERROR: The input directory does NOT exist"
    else:
      # prepare the output table
      oCSV = imgstoreDir + "playbackVideoDurationsFr_" + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + ".csv" 
      with open(oCSV,'w') as csvfile:
         fwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
         # header, yuk
         fwriter.writerow(["videoName", "nFrames"])
         
         filePaths = glob(path.join(imgstoreDir, '*.22105721*/')) # finds all matching paths, this is the side camera
         #filePaths = glob(path.join(imgstoreDir, '*.22098636/')) # finds all matching paths, this is the top camera
         fp2 = sorted(filePaths)
         for fp in fp2: # sorted(filePaths):
           nframes = find_vid_durationFrames(fp) 
           blah = path.split(fp) # these two steps are neeeded because imgstore is a directory
           fname = path.basename(blah[0])
           row = [fname] + [nframes]
           print row
           fwriter.writerow(row)
           print "processed [%s]"%(fp)
         csvfile.close()
      print "All %i files are processed."%( len(filePaths) )

if __name__ == "__main__":
		imgstoreDir = argv[1]
		main(imgstoreDir)		

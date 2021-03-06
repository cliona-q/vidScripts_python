# UPDATES: dec 2019
# 1: use last frame instead of first frame as comparison
# 2: reduced area of analysis even further
# 3: for vids with >16 detections, ignore the extra ones as these are prob long vids


import imgstore
import cv2
import numpy as np
import csv
from sys import argv
from glob import glob
from os import path
from datetime import datetime

# ====================================

def find_PB_onsets(bdir):
   msg = "Processing video %s" % bdir
   print msg
   # params:
   thresh_diff = 20 # for difference between current and first frame
   thresh_on = 20 # for evaluating whether a summed frame difference (npix diff) is meaningful or not
   thresh_off = 5
   x1 = 900 #700 # ROI of screen to  (I hope) reduce computing overhead
   x2 = 1200 #1400
   y1 = 500 #400
   y2 = 800 #900
   nPB = 16 # expected lengths of on/off frame lists
   
   try:
      store = imgstore.new_for_filename(bdir + 'metadata.yaml')
   except:
      msg = "could not read store " + bdir + ", skipping"
      print msg
      on_frames = []
      off_frames = []
   else:      
      md = store.get_frame_metadata()
      fn = md['frame_number']
      
      on_frames = [] # store candidate frame numbers in here
      off_frames = []
      
      # first frame
      img0, (frame_number, frame_timestamp) = store.get_image(fn[-1])
      # convert to grayscale
      img0 = cv2.cvtColor(img0,cv2.COLOR_RGB2GRAY)
      # crop
      img0 = img0[y1:y2, x1:x2]
      
      onSeeker = True
      for fr in fn:  # do for all frames including first (zero diff) 
         # current frame
         img, (frame_number, frame_timestamp) = store.get_image(fr)
         img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
         img = img[y1:y2, x1:x2]
         
         # difference
         diff = cv2.absdiff(img,img0)
         ted = cv2.threshold(diff,thresh_diff,1,cv2.THRESH_BINARY)[1] # first output is threshold
         pix_over_thresh = np.sum(ted)
         
         if onSeeker:
            if pix_over_thresh>thresh_on:
               msg = "on frame %d had %d pixs" % (fr, pix_over_thresh)
               print msg
               on_frames.append(frame_number) # this is the frame in which the movie is turned on
               onSeeker = False
         else: # looking for off
            if pix_over_thresh<thresh_off:
               msg = "off frame %d had %d pixs" % (fr, pix_over_thresh)
               print msg
               off_frames.append(frame_number) # this is the first frame for which the movie is off
               onSeeker = True

      store.close()
      # check lengths of lists:
      if len(on_frames) > nPB:
         "too many on_frames: %d, disregarding extras" % len(on_frames)
         on_frames = on_frames[0:nPB]
      if len(on_frames) < nPB:
         "too few on_frames: %d, ignoring video" % len(on_frames)
         on_frames = [-1] * nPB
      if len(off_frames) > nPB:
         "too many off_frames: %d, disregarding extras" % len(off_frames)
         off_frames = off_frames[0:nPB]
      if len(off_frames) < nPB:
         "too few off_frames: %d, ignoring video" % len(off_frames)
         off_frames = [-1] * nPB
      
      # return outputs
      return dict(on_frames=on_frames, off_frames=off_frames)
      

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
      oCSV = imgstoreDir + "playbackTimingInfo_" + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + ".csv" 
      with open(oCSV,'w') as csvfile:
         fwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
         # header, yuk
         fwriter.writerow(["videoName", "onFrame01", "onFrame02", "onFrame03", "onFrame04", \
         "onFrame05", "onFrame06", "onFrame07", "onFrame08", "onFrame09", "onFrame10", "onFrame11", "onFrame12", \
         "onFrame13", "onFrame14", "onFrame15", "onFrame16","offFrame01", "offFrame02", "offFrame03", "offFrame04", \
         "offFrame05", "offFrame06", "offFrame07", "offFrame08", "offFrame09", "offFrame10", "offFrame11", "offFrame12", \
         "offFrame13", "offFrame14", "offFrame15", "offFrame16"])
         
         filePaths = glob(path.join(imgstoreDir, '*.22098636*/')) # finds all matching paths, this is the camera index number we are interested in
         blah = sorted(filePaths)
         fp2 = blah  # [:-5] # last ones are test vids
         for fp in fp2: # sorted(filePaths):
           ret = find_PB_onsets(fp) 
           print ret
           blah = path.split(fp) # these two steps are neeeded because imgstore is a directory
           fname = path.basename(blah[0])
           row = [fname] + ret["on_frames"] + ret["off_frames"]
           print row
           fwriter.writerow(row)
           print "processed [%s]"%(fp)
         csvfile.close()
      print "All %i files are processed."%( len(filePaths) )

if __name__ == "__main__":
		imgstoreDir = argv[1]
		main(imgstoreDir)		

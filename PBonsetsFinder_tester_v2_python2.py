import imgstore
import cv2
import numpy as np
import csv
import matplotlib.pyplot as plt
from sys import argv
from glob import glob
from os import path
from datetime import datetime

store = imgstore.new_for_filename(tdir + 'metadata.yaml')
md = store.get_frame_metadata()     
fn = md['frame_number']      

# 10, 4000, 200  ; ok
# 5, 10000, 1000 ; not good for off
# 9, 4000, 100; great for A condition
thresh_diff = 9 
thresh_on =  4000
thresh_off = 100
on_frames = []
off_frames = []
onSeeker = True

x1 = 800 #900 #700 # ROI of screen to  (I hope) reduce computing overhead
x2 = 1300 #1200 #1400
y1 = 400 # 200 #500 #400
y2 = 1200 #1200 #800 #900
nPB = 50 #16 # expected lengths of on/off frame lists
   

#img0, (frame_number, frame_timestamp) = store.get_image(fn[-1]) # last frame instead of first?

img0, (frame_number, frame_timestamp) = store.get_image(fn[0]) # first frame
img0 = cv2.cvtColor(img0,cv2.COLOR_RGB2GRAY)
img0 = img0[y1:y2, x1:x2]
for fr in fn:  # do for all frames including first (zero diff) 
    #if fr%1000==0:
    #   raw_input("press enter to continue")  # only use input for py 3+
       
    # current frame
    img, (frame_number, frame_timestamp) = store.get_image(fr)
    img = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    img = img[y1:y2, x1:x2]
    
    # difference
    diff = cv2.absdiff(img,img0)
    ted = cv2.threshold(diff,thresh_diff,1,cv2.THRESH_BINARY)[1] # first output is threshold
    pix_over_thresh = np.sum(ted)
    
    #msg = "frame %d, %d pix over thresh" % (fr, pix_over_thresh)
    #print msg
    
       
    
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
          
          
          
for fr in on_frames: # range(3000,3005): # fn:  # off_frames: #
   img, (frame_number, frame_timestamp) = store.get_image(fr)
   cv2.rectangle(img,(x1,y1),(x2,y2),(0,0,255),1)
   # show the frame
   cv2.imshow('frame',img)
   k = cv2.waitKey(0) & 0xFF # will wait for keyboard input
   # & 0xFF is needed because this is a 64 bit machine!

   if k == ord('q'):
      break
   #else:
      # nothing?

cv2.destroyAllWindows()          

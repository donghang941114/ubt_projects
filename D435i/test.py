import numpy as np
import cv2
import itertools
from itertools import groupby
import time
import math
from collections import deque

a = np.zeros((240,640))
print(a.shape)





def compute_distance(locate_list):
  if len(list_locx) > 30 and locate_list[0]>300:
    locate_listx,locate_listy = locate_list[0],locate_list[1]
    depth_value = depth_image[locate_listx,locate_listy]
    distance = depth_value/math.cos(45)
  return distance


def compute_distance(canny):
  canny = np.array(canny)
  number_list = []
  locate_list = []
  for i in range(160,480):
    ylist = canny[:,i]
    number = 0
    for j in range(len(ylist)):
      if ylist[j] == 255:
        number += 1
    number_list.append(number)
  b = [i for i,x in enumerate(number_list) if x==1]
  c = np.split(b, np.where(np.diff(b) != 1)[0] + 1)
  list_locx = max(c,key=len)
  list_locx = list_locx + 160

  for m in list_locx:
    ylist = canny[:,m]
    n = [i for i,x in enumerate(ylist) if x==255]
    n = int(n[0])
    locate=[n,m]
    #print(locate)
    locate_list.append(locate)
  locate_list = np.array(locate_list)
  try:
    locate_list = ((max(locate_list[:,0])+min(locate_list[:,0]))/2,(max(locate_list[:,1])+min(locate_list[:,1]))/2)
  except:
    pass
  locate_list = [int(i) for i in locate_list]
  return number_list,list_locx, locate_list
        
  

def show_stairs(list_locx,locate_list,run_time):
  if len(list_locx) > 320 and locate_list[0]>300:
    now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    print(" {} ---- Stairs! Danger! The location is {} Compute time: {}".format(now_time,locate_list,run_time))
    with open("./videodata/savefig/log.txt","a") as f:
      f.write(" {} ---- Stairs! Danger! The location is {} Compute time: {}".format(now_time,locate_list,run_time))



#canny = cv2.imread('/home/nvidia/projects/D435i/mydata7/savefig1/stack/stack_00000.png')
#print(canny.shape)
#cv2.imshow("rgb",canny[320:480,:640])
#key = cv2.waitKey(0)


  


#number_list,list_locx,locate_list =  compute_distance(canny)
##print(number_list)
##print(list_locx)
#print(locate_list)
##time0, time_med, time255 = pix_judment(number_list)
##print(time255)
##show_stairs(time255)


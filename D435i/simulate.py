import pyrealsense2 as rs
import numpy as np
import os
import cv2
import time
import math
from collections import deque

ctx = rs.context()
if len(ctx.devices) > 0:
    for d in ctx.devices:
        print('Found device: ',
              d.get_info(rs.camera_info.name), ' ',
              d.get_info(rs.camera_info.serial_number))
else:
    print("No Intel Device connected")

def compute_distance(locate_list):
  global distance
  if len(list_locx) > 120 and locate_list[0]>240:
    locate_listx,locate_listy = locate_list[0],locate_list[1]
    depth_value = depth_image[locate_listx,locate_listy]
    distance = depth_value * math.sin(math.radians(45))
    return distance


def compute_line(canny):
  canny = np.array(canny)
  number_list = []
  locate_list = []
  for i in range(0,640):
    ylist = canny[:,i]
    number = 0
    for j in range(len(ylist)):
      if ylist[j] == 255:
        number += 1
    number_list.append(number)
  b = [i for i,x in enumerate(number_list) if x==1]
  c = np.split(b, np.where(np.diff(b) != 1)[0] + 1)
  list_locx = max(c,key=len)
  list_locx = list_locx

  for m in list_locx:
    ylist = canny[:,m]
    n = [i for i,x in enumerate(ylist) if x==255]
    n = int(n[0])
    locate=[n,m]
    locate_list.append(locate)
  locate_list = np.array(locate_list)
  try:
    locate_list = (np.mean(locate_list[:,0]),np.mean(locate_list[:,1]))
  except:
    pass
  locate_list = [int(i) for i in locate_list]
  return number_list,list_locx, locate_list
        
  
def cordinate(color_intrin_part,list_locx,locate_list,aligned_depth_frame,depth_intrin):
  ppx = color_intrin_part[0]
  ppy = color_intrin_part[1]
  fx = color_intrin_part[2]
  fy = color_intrin_part[3]
  if len(list_locx) > 120 and locate_list[0]>240:
    locate_pixelx,locate_pixely = locate_list[1],locate_list[0]
    depth_value = depth_image[locate_pixely,locate_pixelx]
    depth_point = rs.rs2_deproject_pixel_to_point(depth_intrin, [locate_pixelx,locate_pixely], depth_value)
    text = "%.5lf, %.5lf, %.5lf\n" % (depth_point[0], depth_point[1], depth_point[2])
    return text


def show_stairs(list_locx,locate_list,run_time,distance,text,mid_point):
  now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
  print(" {} ---- Stairs! Danger! The location is {} Compute time: {} Distance {} 3D cordinate: {}\n".format(now_time,mid_point,run_time,distance,text))
  with open("./videodata/savefig/log.txt","a") as f:
    f.write(" {} ---- Stairs! Danger! The location is {} Compute time: {} Distance: {} 3D cordinate: {} \n".format(now_time,mid_point,run_time,distance,text))



cap = cv2.VideoCapture("/home/nvidia/projects/D435i/videodata/data/stack.avi")


# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
 
# Start streaming
profile=pipeline.start(config)


# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: " , depth_scale)

align_to = rs.stream.color
align = rs.align(align_to)

num1 = 0   
q = deque(maxlen=3)
q1 = deque(maxlen=3)
q2 = deque(maxlen=3)
num2 = 0

try:
    while True:
        ret, frame = cap.read()
        color_image = frame[:480,:640]
        depth_ret = frame[:480, 640:]


#        # Wait for a coherent pair of frames: depth and color
#        frames = pipeline.wait_for_frames()
#        aligned_frames = align.process(frames) 
#        aligned_depth_frame = aligned_frames.get_depth_frame()
#        color_frame =aligned_frames.get_color_frame()

#        if not aligned_depth_frame or not color_frame:
#            continue
# 

#        # Intrinsics & Extrinsics
#        # Depth camera Internal reference matrix
#        depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
#        # RGB camera Internal reference matrix
#        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
#        color_intrin_part = [color_intrin.ppx, color_intrin.ppy, color_intrin.fx, color_intrin.fy]
#        #print(color_intrin_part)
#        #[319.0599060058594, 237.28564453125, 616.4171142578125, 616.5468139648438]
#  
#        # Depth image-> color image external reference RT
#        depth_to_color_extrin = aligned_depth_frame.profile.get_extrinsics_to(
#            color_frame.profile)
#        #print(depth_intrin)

# 
#        #dis = aligned_depth_frame.get_distance(x,y)


#        # Convert images to numpy arrays
#        depth_image = np.asanyarray(aligned_depth_frame.get_data())

#        #print(depth_image.shape) #(480,640) H,W
#        color_image = np.asanyarray(color_frame.get_data())

#        depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
#        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

# 
#        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
#        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
# 
#        
#        #Stairs image deal
#        start = time.time()
#        depth_ret = np.array(depth_image)
#        depth_ret=(depth_ret-np.min(depth_ret))/(np.max(depth_ret)-np.min(depth_ret))*255
#        depth_ret = depth_ret.astype('uint8')
#        #cv2.imshow('depth_image',depth_ret) 

        start = time.time()

        depth_ret = depth_ret *float(4)
        depth_ret[depth_ret>127]=255
        depth_ret[depth_ret<127]=0
        depth_ret = np.round(depth_ret)
        depth_ret = depth_ret.astype('uint8')
        depth_contrast = depth_ret 
        #cv2.imshow('depth_contrast',depth_contrast) 

        kernel = np.ones((5,5), np.uint8)
        dilation = cv2.dilate(depth_contrast,kernel,iterations = 2)
        canny = cv2.Canny(dilation.astype('uint8'),50,150)
        #cv2.imshow('depth_canny',canny)
        

        #Detect stairs
        number_list,list_locx, locate_list =  compute_line(canny)
        distance = compute_distance(locate_list) 
        #text = cordinate(color_intrin_part,list_locx,locate_list,aligned_depth_frame,depth_intrin)


        #Stairs_midpoint detection
        mid_point = None
        if len(list_locx) > 120 and locate_list[0] > 240:
          q.append(locate_list)
          q1.append(num1)
          q2.append(color_image)
          if len(q) >= 2:
            if q[1][0]-q[0][0] > 30 or q1[1]- q1[0] > 1:
              q.popleft()
              q1.popleft()
              q2.popleft()
          if len(q) == 3:
            if q[0][0]<q[1][0]<q[2][0] and max(q[0][1],q[1][1],q[2][1])-min(q[0][1],q[1][1],q[2][1])<50 :
              mid_point = q[1]
              mid_color_image = q2[1]
              #Paint red circle
              point_size = 10
              thickness = -4 
              cv2.circle(mid_color_image, (int(mid_point[0]),int(mid_point[1])), point_size, (0, 0, 255), thickness)


        end = time.time()
        run_time = str(end-start)

        if mid_point is not None:
          show_stairs(list_locx,locate_list,run_time,distance,text,mid_point)
          #Paint red circle
          point_size = 10
          thickness = -4 
          cv2.circle(color_image, (int(mid_point[0]),int(mid_point[1])), point_size, (0, 0, 255), thickness)

        # Stack both images horizontally
#        images1 = np.hstack((color_image, depth_colormap))
#        images2 = np.hstack((depth_contrast, canny))    
        canny = np.stack((canny,)*3,axis = -1)
        images3 = np.hstack((color_image,canny))



        # Show images
#        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
#        cv2.imshow('RealSense', images1)
#        cv2.namedWindow('RealSense2', cv2.WINDOW_AUTOSIZE)
#        cv2.imshow('RealSense2', images2)
        cv2.namedWindow('RealSense3', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense3', images3)
        cv2.setWindowTitle('RealSense3', "RealSense3 {}s ({}.3fms) Distance {}".format(
        "compute time" ,(end-start)*1000,distance))
 

        #imwrite
#        cv2.imwrite('./videodata/savefig/rgb/image_r_{}.png'.format(str(num1).zfill(5)), color_image)
#        cv2.imwrite('./videodata/savefig/midrgb/midimage_r_{}.png'.format(str(num1).zfill(5)), mid_color_image)
#        cv2.imwrite('./videodata/savefig/depth/image_d_{}.png'.format(str(num1).zfill(5)), depth_colormap)
#        cv2.imwrite('./videodata/savefig/canny_image/canny_image_{}.png'.format(str(num1).zfill(5)), canny)
#        #np.savetxt('./videodata/savefig/canny_csv/canny_image_{}.csv'.format(str(num1).zfill(5)),canny,fmt="%d",delimiter=",")
#        cv2.imwrite('./videodata/savefig/stack/stack_{}.png'.format(str(num1).zfill(5)), images3)
#        num1 += 1

 
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break

finally:
 
    # Stop streaming
    pipeline.stop()


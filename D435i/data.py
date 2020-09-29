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
 
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames) 
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame =aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            continue
 
        # Depth camera Internal reference matrix
        depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
        # RGB camera Internal reference matrix
        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
        color_intrin_part = [color_intrin.ppx, color_intrin.ppy, color_intrin.fx, color_intrin.fy]

  
        # Depth image-> color image external reference RT
        depth_to_color_extrin = aligned_depth_frame.profile.get_extrinsics_to(
            color_frame.profile)

        # Convert images to numpy arrays
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        depth_ret = np.array(depth_image)
        depth_ret=(depth_ret-np.min(depth_ret))/(np.max(depth_ret)-np.min(depth_ret))*255
        depth_ret = depth_ret.astype('uint8')

        depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
         
        # Stack both images horizontally
        #images1 = np.hstack((color_image, depth_colormap))
        depth_ret = np.stack((depth_ret,)*3,axis = -1)
        images2 = np.hstack((color_image , depth_ret))  
  

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', depth_colormap)
        cv2.namedWindow('RealSense2', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense2', images2)

        #imwrite
        cv2.imwrite('./videodata/data/depth_colormap/depth_colormap_{}.png'.format(str(num1).zfill(5)), depth_colormap)
        cv2.imwrite('./videodata/data/stack/stack_{}.png'.format(str(num1).zfill(5)), images2)
        num1 += 1
 
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break

finally:
 
    # Stop streaming
    pipeline.stop()

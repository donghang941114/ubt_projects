from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths

import pyrealsense2 as rs
import numpy as np
import gol

import os
import cv2

from opts import opts
from detectors.detector_factory import detector_factory

image_ext = ['jpg', 'jpeg', 'png', 'webp']
video_ext = ['mp4', 'mov', 'avi', 'mkv']
time_stats = ['tot', 'load', 'pre', 'net', 'dec', 'post', 'merge']


def demo(opt):
  os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpus_str
  opt.debug = max(opt.debug, 1)
  Detector = detector_factory[opt.task]
  detector = Detector(opt)

  if opt.demo == 'webcam' or \
    opt.demo[opt.demo.rfind('.') + 1:].lower() in video_ext:
    cam = cv2.VideoCapture(0 if opt.demo == 'webcam' else opt.demo)
    detector.pause = False
    while True:
        _, img = cam.read()
        #print(img.shape)
        #cv2.imshow('input', img)
        ret = detector.run(img)
        time_str = ''
        for stat in time_stats:
          time_str = time_str + '{} {:.3f}s |'.format(stat, ret[stat])
        print(time_str)
        if cv2.waitKey(1) == 27:
            return   

  elif opt.demo== '435':
 
    # Configure depth and color streams
    pipeline = rs.pipeline()
    # 创建 config 对象：
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    # Start streaming
    profile=pipeline.start(config)

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    print("Depth Scale is: " , depth_scale)

    # We will be removing the background of objects more than        
    #  clipping_distance_in_meters meters away
    clipping_distance_in_meters = 1    #meters
    clipping_distance = clipping_distance_in_meters / depth_scale

    align_to = rs.stream.color
    align = rs.align(align_to)
    
    i=0
    timeF=30
    while True:
        # Wait for a coherent pair of frames（一对连贯的帧）: depth and color
        frames = pipeline.wait_for_frames()

        aligned_frames = align.process(frames) 

        aligned_depth_frame = aligned_frames.get_depth_frame()
        gol.set_value('aligned_depth_frame',aligned_depth_frame)  #定义跨模块全局变量
        color_frame = aligned_frames.get_color_frame()


#        # Intrinsics & Extrinsics
#        #深度相机内参矩阵
#        depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
#        #RGB相机内参矩阵
#        color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
#        # 外参矩阵-深度图相对于彩色图像的外参RT
#        depth_to_color_extrin = aligned_depth_frame.profile.get_extrinsics_to(color_frame.profile)
#        print("内参 ppx,ppy",depth_intrin.ppx, ':', depth_intrin.ppy)
#        print("内参矩阵",depth_intrin)

        if not aligned_depth_frame or not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        #global depth_image
        depth_image = np.asanyarray(aligned_depth_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        images = np.hstack((bg_removed, depth_colormap))

#        #imwrite depth_image color_iamge
#        if i%timeF==0:
#          cv2.imwrite('./mydata/savefig/rgb/image_r_{}.png'.format(str(i).zfill(5)), color_image)
#          cv2.imwrite('./mydata/savefig/depth/image_d_{}.png'.format(str(i).zfill(5)), depth_colormap)
#          cv2.imwrite('./mydata/savefig/depth/images_stack_{}.png'.format(str(i).zfill(5)), images)
#          np.savetxt("./mydata/savefig/depth_csv/depth_image_{}.csv".format(str(i).zfill(5)),depth_image,fmt="%d",delimiter=",")
#          i+=30
#      
        #Show images
        cv2.namedWindow('Remove Background', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Remove Background', images)

        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image) 

#        # 通过对齐后的深度图,对齐原始RGB：color_frame，保存彩色点云
#        pc = rs.pointcloud()
#        pc.map_to(color_frame)
#        points = pc.calculate(aligned_depth_frame)
#        points.export_to_ply('./out.ply', color_frame)
#        #pcd = read_point_cloud(file_path)
#        # Visualize PLY
#        #draw_geometries([pcd])


        ret = detector.run(color_image)
        time_str = ''  
        for stat in time_stats:
          time_str = time_str + '{} {:.3f}s |'.format(stat, ret[stat])
        print(time_str)
        if cv2.waitKey(1) & 0xff == ord('q'):
            return 


  else:
    if os.path.isdir(opt.demo):
      image_names = []
      ls = os.listdir(opt.demo)
      for file_name in sorted(ls):
          ext = file_name[file_name.rfind('.') + 1:].lower()
          if ext in image_ext:
              image_names.append(os.path.join(opt.demo, file_name))
    else:
      image_names = [opt.demo]
    
    for (image_name) in image_names:
      ret = detector.run(image_name)
      time_str = ''
      for stat in time_stats:
        time_str = time_str + '{} {:.3f}s |'.format(stat, ret[stat])
      print(time_str)

if __name__ == '__main__':

  gol._init()#先必须在主模块初始化（只在Main模块需要一次即可）
#  gol.set_value('depth_image',depth_image)  #定义跨模块全局变量
  opt = opts().init()
  demo(opt)

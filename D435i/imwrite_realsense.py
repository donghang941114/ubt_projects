import pyrealsense2 as rs
import numpy as np
import cv2
 
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

i=0
timeF=300    

try:
    while True:
 
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames) 
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame =aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            continue
 
        #print(aligned_depth_frame )
        # Convert images to numpy arrays
        depth_image = np.asanyarray(aligned_depth_frame.get_data())

#       print(depth_image.shape) #(480,640)
        color_image = np.asanyarray(color_frame.get_data())
 
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
 
        # Stack both images horizontally
        images = np.hstack((color_image, depth_colormap))

        #imwrite depth_image color_iamge
        if i%timeF==0:
          cv2.imwrite('./mydata/savefig/rgb/image_r_{}.png'.format(str(i).zfill(5)), color_image)
          cv2.imwrite('./mydata/savefig/depth/image_d_{}.png'.format(str(i).zfill(5)), depth_colormap)
          cv2.imwrite('./mydata/savefig/stack/images_stack_{}.png'.format(str(i).zfill(5)), images)
          np.savetxt("./mydata/savefig/depth_csv/depth_image_{}.csv".format(str(i).zfill(5)),depth_image,fmt="%d",delimiter=",")
        i+=1
 
        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
 
 
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
 
 
finally:
 
    # Stop streaming
    pipeline.stop()

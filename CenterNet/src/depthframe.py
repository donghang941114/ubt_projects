import pyrealsense2 as rs
import numpy as np
import cv2


class realsense_im(object):
    def __init__(self,image_size=(640,480)):
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.depth, image_size[0], image_size[1], rs.format.z16, 30)
        config.enable_stream(rs.stream.color, image_size[0], image_size[1], rs.format.bgr8, 30)
        self.profile = self.pipeline.start(config)

    def __get_depth_scale(self):
        depth_sensor = self.profile.get_device().first_depth_sensor()

        depth_scale = depth_sensor.get_depth_scale()

        return depth_scale

    def get_image(self):

        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        depth_image = np.asarray(depth_frame.get_data(), dtype=np.float32)
        color_image = np.asarray(color_frame.get_data(), dtype=np.uint8)
        color_image_pad = np.pad(color_image, ((20, 0), (0, 0), (0, 0)), "edge")
        depth_map_end = depth_image * self.__get_depth_scale() * 1000
        return depth_map_end,color_image

    def process_end(self):
        self.pipeline.stop()

rs_t=realsense_im()

i=0
try:
    while True:

        depth_map,rgb_map=rs_t.get_image()
        print(rgb_map.shape)
#        cv2.imwrite('./mydata/savefig/rgb/image_r_{}.png'.format(str(i).zfill(5)), rgb_map)
#        cv2.imwrite('./mydata/savefig/depth/image_d_{}.png'.format(str(i).zfill(5)), np.asarray(depth_map,np.uint16))

        i+=1

        cv2.namedWindow('RGB Example', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RGB Example', rgb_map)

        key = cv2.waitKey(1)

        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break

finally:
    pass



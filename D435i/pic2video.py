# -*- coding: UTF-8 -*-
import os
import cv2
import time
import glob

#方式一
def pic2video(pic_path,video_path,size):
    filelist = os.listdir(pic_path) #获取该目录下的所有文件名
    fps = 25
    file_path = video_path + ".avi"#导出路径
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')#不同视频编码对应不同视频格式
    video = cv2.VideoWriter( file_path, fourcc, fps, size )

    filelist = os.listdir(pic_path) 
    #filelist.sort(key=lambda x : int(x.split('.')[0].split('_')[2] ))
    filelist.sort(key=lambda x : int(x.split('.')[0].split('_')[1] ))
 
    for item in filelist:
        if item.endswith('.png'):   #判断图片后缀是否是.png
            item = pic_path + '/' + item 
            img = cv2.imread(item)  #使用opencv读取图像，直接返回numpy.ndarray 对象，通道顺序为BGR ，注意是BGR，通道值默认范围0-255。
            video.write(img)        #把图片写进视频
 
    video.release() #释放

#方式二（调整大小）
def resize(img_array, align_mode):
    _height = len(img_array[0])
    _width = len(img_array[0][0])
    for i in range(1, len(img_array)):
        img = img_array[i]
        height = len(img)
        width = len(img[0])
        if align_mode == 'smallest':
            if height < _height:
                _height = height
            if width < _width:
                _width = width
        else:
            if height > _height:
                _height = height
            if width > _width:
                _width = width
 
    for i in range(0, len(img_array)):
        img1 = cv2.resize(img_array[i], (_width, _height), interpolation=cv2.INTER_CUBIC)
        img_array[i] = img1
 
    return img_array, (_width, _height)
 
def images_to_video(path,video_path):
    img_array = []
 
    for filename in glob.glob(path+'/*.png'):
        img = cv2.imread(filename)
        if img is None:
            print(filename + " is error!")
            continue
        img_array.append(img)
 
    # 图片的大小需要一致
    img_array, size = resize(img_array, 'largest')
    fps = 1
    file_path = video_path + 'demo.avi'
    out = cv2.VideoWriter(file_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
 
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

if __name__ == '__main__':
  pic_path = '/home/nvidia/projects/D435i/videodata/data/stack/'
  video_path = '/home/nvidia/projects/D435i/videodata/data/stack'
  size = (1280,480)
  pic2video(pic_path,video_path,size)
  #images_to_video(pic_path,video_path)

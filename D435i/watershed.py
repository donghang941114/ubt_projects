# -*- coding: utf-8 -*-
import numpy as np
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from PIL import ImageEnhance
import glob
import os
import re

path = '/home/nvidia/projects/D435i/mydata1/savefig0/depth_csv/'
paths = glob.glob(os.path.join(path, '*.csv'))
paths.sort()
for path in paths:
  file_name = path.split('/')
  regex = re.compile(r'\d+')
  file_number = regex.findall(file_name[-1])
  file_number = np.array(file_number)
  ret = pd.read_csv(path)
  depth_ret = np.array(ret)
  depth_ret=(depth_ret-np.min(depth_ret))/(np.max(depth_ret)-np.min(depth_ret))*255
  depth_ret = depth_ret.astype('uint8')
  #cv2.imshow('depth_image_{}'.format(file_number[0]),depth_ret) 

  depth_ret = depth_ret *float(4)
  depth_ret[depth_ret>127]=255
  depth_ret[depth_ret<127]=0
  depth_ret = np.round(depth_ret)
  depth_ret = depth_ret.astype('uint8')
  depth_contrast = depth_ret 
  #cv2.imshow('depth_contrast_{}'.format(file_number[0]),depth_contrast) 

  kernel = np.ones((5,5), np.uint8)
  dilation = cv2.dilate(depth_contrast,kernel,iterations = 2)
  canny = cv2.Canny(dilation.astype('uint8'),50,150)
  cv2.imwrite("/home/nvidia/projects/D435i/mydata1/savefig0/depth_canny_image/depth_canny_{}.png".format(file_number[0]),canny)
  np.savetxt("/home/nvidia/projects/D435i/mydata1/savefig0/canny_csv/depth_canny_{}.csv".format(file_number[0]),canny,fmt="%d",delimiter=",")
  #cv2.imshow('depth_canny_{}'.format(file_number[0]),canny)

#  cv2.waitKey(0)
#  cv2.destroyAllWindows()





####第一版
#number=str(0)+str(0)+str(150)
#ret = pd.read_csv('/home/nvidia/projects/D435i/mydata1/savefig0/depth_csv/depth_image_{}.csv'.format(number))
#depth_ret = np.array(ret)


#depth_ret=(depth_ret-np.min(depth_ret))/(np.max(depth_ret)-np.min(depth_ret))*255
#depth_ret = depth_ret.astype('uint8')
#cv2.imshow('depth_image',depth_ret) 


#depth_ret = depth_ret *float(4)
#depth_ret[depth_ret>127]=255
#depth_ret[depth_ret<127]=0
#depth_ret = np.round(depth_ret)
#depth_ret = depth_ret.astype('uint8')
#depth_contrast = depth_ret 
#cv2.imshow('depth_contrast',depth_contrast) 


#kernel = np.ones((5,5), np.uint8)
#dilation = cv2.dilate(depth_contrast,kernel,iterations = 2)
#canny = cv2.Canny(dilation.astype('uint8'),50,150)
#cv2.imwrite("/home/nvidia/projects/D435i/mydata1/savefig0/depth_canny_image/depth_canny_{}.png".format(number),canny)
#np.savetxt("/home/nvidia/projects/D435i/mydata1/savefig0/canny_csv/depth_canny_{}.csv".format(number),canny,fmt="%d",delimiter=",")
#cv2.imshow('depth_canny_{}'.format(number),canny)

#cv2.waitKey(0)
#cv2.destroyAllWindows()


#读入图片/CSV文件
#img = cv2.imread('/home/nvidia/projects/D435i/mydata1/savefig0/rgb/image_r_01650.png')
#img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#def compute(depth_ret):
#  result = []
#  x = depth_ret[:,0][::-1]
#  for i in range(478):
#    result.append((x[i+1]-x[i])/x[i])
#  return result

#result = compute(depth_ret)
#print(np.array(result).size)
#x = np.arange(0,478)
#plt.title("gradient_plot") 
#plt.xlabel("x ") 
#plt.ylabel("y ") 
#plt.plot(x,result,linewidth=1)
#plt.show()


##CSV列数据可视化
#x_axis = np.linspace(0, depth_ret.shape[0],479)
#y_axis = depth_ret[:,320][::-1]
##x_axis_new = np.linspace(min(depth_ret[:,0]), max(depth_ret[:,0]),479)
##y_smooth = spline(x_axis,y_axis,x_axis_new)
#plt.plot(x_axis,y_axis,linewidth=1)
##plt.plot(x_axis_new,y_smooth)
#plt.legend()
#plt.title("depth_data_plot", fontsize=14)
#plt.xlabel("X", fontsize=10)
#plt.ylabel("Y", fontsize=10)
#plt.tick_params(axis='both', labelsize=14)
#plt.savefig("/home/nvidia/projects/D435i/mydata1/savefig0/depth_csv/csv_plot/depth_csv_data_plot_{}.png".format(number))
#plt.show()


  
#阈值处理
#ret, th = cv2.threshold(depth_ret.astype('uint8'), 0, 255, cv2.THRESH_OTSU)
#th2 = cv2.adaptiveThreshold(
#    depth_ret.astype('uint8'), 255,  cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 1)
#ret,th3 = cv2.threshold(depth_ret.astype('uint8'),27,255,cv2.THRESH_BINARY)
#np.savetxt("/home/nvidia/projects/D435i/depth_threshold_{}.csv".format(number),depth_ret.astype('uint8'),fmt="%d",delimiter=",")
#cv2.imshow('depth_image_threshold',th2)
#cv2.imshow('depth_image',depth_ret.astype('uint8'))
#cv2.waitKey(0)


#模糊处理
#depth_img = cv2.Sobel(depth_img,cv2.CV_16S, 1, 1, ksize=1)
#depth_img = cv2.convertScaleAbs(depth_img)
#depth_img = cv2.blur(depth_img,(3,3))
#depth_img = cv2.boxFilter(depth_img,-1,(3,3))
#depth_img = cv2.GaussianBlur(depth_img,(3,3),1.5)
#depth_img = cv2.medianBlur(depth_img,3)


#Canny边缘检测
#canny = cv2.Canny(depth_ret.astype('uint8'),50,150)
#cv2.imshow('depth_canny_{}'.format(number),canny)
#cv2.imwrite('/home/nvidia/projects/D435i/mydata1/savefig0/depth_canny_image/depth_canny_image_{}.png'.format(number),canny)
#print(canny.shape)
#np.savetxt("/home/nvidia/projects/D435i/mydata1/savefig0/canny_csv/depth_canny_{}.csv".format(number),canny,fmt="%d",delimiter=",")


#腐蚀膨胀
#kernel = np.uint8(np.zeros((3，3)))
#for i in range(3):
#  kernel[1, i] = 1
#  kernel[i, 1] = 1

#kernel = np.uint8(np.array([[0,1,0],
#                            [1,1,1],
#                            [0,1,0]]))

#方案一
#kernel0 = np.uint8(np.array([[1,1,1,1,1]
#                            ]))
#kernel1 = np.uint8(np.array([[1,0,1],
#                            [0,0,0],
#                            [1,0,1]]))
##kernel1 = np.uint8(np.zeros((5,5)))
##for i in range(5):
##  kernel1[2, i] = 1
##  kernel1[i, 2] = 1
##  kernel1[2,2] = 0
##print(kernel1)
#kernel2 = np.ones((3,3),np.uint8)
#kernel = np.ones((15,15),np.uint8)
#erosion = cv2.erode(canny,kernel0,iterations = 1)
##closing = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, kernel3)
##opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel3) 
#cv2.imshow('depth_er_{}'.format(number),erosion)
#dilation = cv2.dilate(erosion,kernel0,iterations = 3)
#cv2.imshow('depth_erdi_{}'.format(number),dilation)
#方案二
#kernel3 = np.ones((15,15),np.uint8)
#dilation = cv2.dilate(canny,kernel,iterations = 1) #9,9
#closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
#closing = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel3)  #27,27
#erosion = cv2.erode(closing,kernel3,iterations = 1)
##opening = cv2.morphologyEx(canny, cv2.MORPH_OPEN, kernel)  
#cv2.imshow('depth_erdi_{}'.format(number),closing)



##显著性区域检测
#def diag_sym_matrix(k=256):
#    base_matrix = np.zeros((k,k))
#    base_line = np.array(range(k))
#    base_matrix[0] = base_line
#    for i in range(1,k):
#        base_matrix[i] = np.roll(base_line,i)
#    base_matrix_triu = np.triu(base_matrix)
#    return base_matrix_triu + base_matrix_triu.T

#def cal_dist(hist):
#    Diag_sym = diag_sym_matrix(k=256)
#    hist_reshape = hist.reshape(1,-1)
#    hist_reshape = np.tile(hist_reshape, (256, 1))
#    return np.sum(Diag_sym*hist_reshape,axis=1)

#def LC(image_gray):
#    image_height,image_width = image_gray.shape[:2]
#    hist_array = cv2.calcHist([image_gray], [0], None, [256], [0.0, 256.0])
#    gray_dist = cal_dist(hist_array)

#    image_gray_value = image_gray.reshape(1,-1)[0]
#    image_gray_copy = [(lambda x: gray_dist[x]) (x)  for x in image_gray_value]
#    image_gray_copy = np.array(image_gray_copy).reshape(image_height,image_width)
#    image_gray_copy = (image_gray_copy-np.min(image_gray_copy))/(np.max(image_gray_copy)-np.min(image_gray_copy))
#    return image_gray_copy
#canny = cv2.blur(canny,(3,3))
#saliency_image = LC(canny.astype('uint8'))
#cv2.imshow("gray saliency image",saliency_image)




##聚类图像
##获取图像高度、宽度
#rows, cols = canny.shape[:]
##图像二维像素转换为一维
#data = canny.reshape((rows * cols, 1))
#data = np.float32(data)
##定义中心 (type,max_iter,epsilon)
#criteria = (cv2.TERM_CRITERIA_EPS +
#            cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
##设置标签
#flags = cv2.KMEANS_RANDOM_CENTERS
##K-Means聚类 聚集成4类
#compactness, labels, centers = cv2.kmeans(data, 2, None, criteria, 10, flags)
##生成最终图像
#dst = labels.reshape((canny.shape[0], canny.shape[1]))
##用来正常显示中文标签
#plt.rcParams['font.sans-serif']=['SimHei']
##显示图像
#titles = [u'原始图像', u'聚类图像']  
#images = [canny, dst]  
#for i in range(2):  
#   plt.subplot(1,2,i+1), plt.imshow(images[i], 'gray'), 
#   plt.title(titles[i])  
#   plt.xticks([]),plt.yticks([])  
#plt.show()


#Hough直线检测#标准霍夫线变换
#lines = cv2.HoughLines(canny,1,np.pi/180,180)
#result = canny.copy()
#for line in lines:
#	rho = line[0][0]  #第一个元素是距离rho
#	theta= line[0][1] #第二个元素是角度theta
#	if  (theta < (np.pi/4. )) or (theta > (3.*np.pi/4.0)): #垂直直线
#		pt1 = (int(rho/np.cos(theta)),0)               #该直线与第一行的交点
#		#该直线与最后一行的焦点
#		pt2 = (int((rho-result.shape[0]*np.sin(theta))/np.cos(theta)),result.shape[0])
#		cv2.line( result, pt1, pt2, (0,255,0))            
#	else:                                                  #水平直线
#		pt1 = (0,int(rho/np.sin(theta)))               # 该直线与第一列的交点
#		#该直线与最后一列的交点
#		pt2 = (result.shape[1], int((rho-result.shape[1]*np.cos(theta))/np.sin(theta)))
#		cv2.line(result, pt1, pt2, (0,0,255), 1) 
          
#for line in lines:
#  rho,theta = line[0]
#  a = np.cos(theta)
#  b = np.sin(theta)
#  x0 = a * rho
#  y0 = b * rho
#  x1 = int(x0 + 1000*(-b))
#  y1 = int(y0 + 1000*(a))
#  x2 = int(x0 - 1000 * (-b))
#  y2 = int(y0 - 1000 * (a))
#  cv2.line(result,(x1,y1),(x2,y2),(0,0,255),2)
#cv2.imshow('Result', result)

##统计概率霍夫线变换
##经验参数
#result_p = canny.copy()
#minLineLength = 60  #最低线段的长度，小于这个值的线段被抛弃
#maxLineGap = 20  #线段中点与点之间连接起来的最大距离，在此范围内才被认为是单行
#lines = cv2.HoughLinesP(canny,1,np.pi/180,50,minLineLength,maxLineGap)
#for x1,y1,x2,y2 in lines[0]:
#	cv2.line(canny,(x1,y1),(x2,y2),(0,0,255),1)
#cv2.imshow('Result_P', canny)


##转换为灰度图片
#gray_img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

##canny边缘检测 函数返回一副二值图，其中包含检测出的边缘。
#canny = cv2.Canny(gray_img,80,150)
#cv2.imshow('Canny',canny)


##寻找图像轮廓 返回修改后的图像 图像的轮廓  以及它们的层次
#canny,contours,hierarchy = cv2.findContours(canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
##32位有符号整数类型，
#marks = np.zeros(img.shape[:2],np.int32)
##findContours检测到的轮廓
#imageContours = np.zeros(img.shape[:2],np.uint8)

##轮廓颜色
#compCount = 0
#index = 0
##绘制每一个轮廓
#for index in range(len(contours)):
#    #对marks进行标记，对不同区域的轮廓使用不同的亮度绘制，相当于设置注水点，有多少个轮廓，就有多少个轮廓
#    #图像上不同线条的灰度值是不同的，底部略暗，越往上灰度越高
#    marks = cv2.drawContours(marks,contours,index,(index,index,index),1,8,hierarchy)
#    #绘制轮廓，亮度一样
#    imageContours = cv2.drawContours(imageContours,contours,index,(255,255,255),1,8,hierarchy)
#    
##查看 使用线性变换转换输入数组元素成8位无符号整型。
#markerShows = cv2.convertScaleAbs(marks)    
#cv2.imshow('markerShows',markerShows)
##cv2.imshow('imageContours',imageContours)

##使用分水岭算法
#marks = cv2.watershed(img,marks)
#afterWatershed = cv2.convertScaleAbs(marks)  
#cv2.imshow('afterWatershed',afterWatershed)

##生成随机颜色
#colorTab = np.zeros((np.max(marks)+1,3))
##生成0~255之间的随机数
#for i in range(len(colorTab)):
#    aa = np.random.uniform(0,255)
#    bb = np.random.uniform(0,255)
#    cc = np.random.uniform(0,255)
#    colorTab[i] = np.array([aa,bb,cc],np.uint8)
#    
#bgrImage = np.zeros(img.shape,np.uint8)

##遍历marks每一个元素值，对每一个区域进行颜色填充
#for i in range(marks.shape[0]):
#    for j in range(marks.shape[1]):
#        #index值一样的像素表示在一个区域
#        index = marks[i][j]
#        #判断是不是区域与区域之间的分界,如果是边界(-1)，则使用白色显示
#        if index == -1:
#            bgrImage[i][j] = np.array([255,255,255])
#        else:                        
#            bgrImage[i][j]  = colorTab[index]
#cv2.imshow('After ColorFill',bgrImage)            

##填充后与原始图像融合
#result = cv2.addWeighted(img,0.6,bgrImage,0.4,0)
#cv2.imshow('addWeighted',result)     

#cv2.waitKey(0)
#cv2.destroyAllWindows()

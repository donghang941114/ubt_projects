# -*- coding: utf-8 -*-
from __future__ import print_function
import numpy as np
import pcl 
import pcl.pcl_visualization as viewer  



def main():
    #通过pcl.load加载pcd文件
    cloud2 = pcl.load("/home/nvidia/projects/D435i/nanshan.pcd")
    cloud1 = pcl.load("/home/nvidia/projects/D435i/nanshan.pcd")
    cloud2=np.array(cloud2)#这里转换成数组是为了进行一个平移，能够看出来两个点云的差异
    print(cloud2.shape)
   
    for x in range(cloud2.shape[0]):
        cloud2[x]=cloud2[x]+2

    cloud1 = np.array(cloud1)
   
    #如何将数组类型转换成点云所需要的数据类型
    cloud2=pcl.PointCloud(cloud2)
    cloud1=pcl.PointCloud(cloud1)

   
    visualcolor1 = pcl.pcl_visualization.PointCloudColorHandleringCustom(cloud2, 0, 255, 0)
    visualcolor2=pcl.pcl_visualization.PointCloudColorHandleringCustom(cloud1,255,0,0)
    vs=pcl.pcl_visualization.PCLVisualizering
    vss1=pcl.pcl_visualization.PCLVisualizering()#初始化一个对象，这里是很重要的一步
    vs.AddPointCloud_ColorHandler(vss1, cloud1, visualcolor2, id=b'cloud', viewport=0)
    vs.AddPointCloud_ColorHandler(vss1,cloud2,visualcolor1,id=b'cloud1',viewport=0)
    v = True
    while not vs.WasStopped(vss1):
       vs.Spin(vss1)


if __name__ == "__main__":
    main()

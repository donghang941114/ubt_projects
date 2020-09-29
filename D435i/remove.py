import cv2
import os
import glob
 
path=["/home/nvidia/projects/D435i/mydata/savefig/depth",
"/home/nvidia/projects/D435i/mydata/savefig/rgb", 
"/home/nvidia/projects/D435i/mydata/savefig/stack",
"/home/nvidia/projects/D435i/mydata/savefig/depth_csv"]



def get_file(file_name):
    filelist = []
    for parent, dirnames, filenames in os.walk(file_name):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg','.csv')):
                filelist.append(os.path.join(parent, filename))
        return filelist



if __name__=='__main__':
  for file_name in path:  
    filelist=get_file(file_name)
    for pathi in filelist:
      os.remove(pathi)
  os.remove('/home/nvidia/projects/D435i/videodata/savefig/log.txt')
  print("All files clear !")
   


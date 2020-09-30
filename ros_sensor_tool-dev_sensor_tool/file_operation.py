#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
LOGGER = logging.getLogger('main')
senser_file_path_name=["senser_data\\ultrasonic_1.json",\
                       "senser_data\\ir_wall_1.json",\
                       "senser_data\\ir_top_tof_1.json",\
                       "senser_data\\ir_charge_1.json",\
                       "senser_data\\geomagnetism_1.json",\
                        "senser_data\\lidar_1.json",
                       ]

class file_op(object):
    def setup_file_op(self, MainWindow):
        pass
    def file_save_deal(self):
        try:
            for i,j in enumerate(senser_file_path_name):
                if (self.tabWidget_all.currentIndex() == 0 and i<5 and self.checkBox_15.checkState()) or (self.tabWidget_all.currentIndex() == 2 and i==5 and self.checkBox_19.checkState()):
                    senser_file_path_name[i] = self.check_file_size(j)
                    # if not os.path.exists(os.path.split(j)[0]):
                    #     os.makedirs(os.path.split(j)[0])
                    self.senser_file[i] = open(senser_file_path_name[i], 'a')#'w'
                # self.senser_file[i].write(json.dumps(dic)+"\n")
                elif (self.tabWidget_all.currentIndex() == 0 and i<5 and not self.checkBox_15.checkState()) or (self.tabWidget_all.currentIndex() == 2 and i==5 and not self.checkBox_19.checkState()):
                    self.senser_file[i].close()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def check_file_size(self,name):
        try:
            if not os.path.exists(os.path.split(name)[0]):
                os.makedirs(os.path.split(name)[0])
            if not os.path.isfile(name):
                with open(name, 'x') as fd:
                    pass
            if os.path.getsize(name)/1024/1024 > 30:#
                tmp =[item[::-1] for item in name[::-1].split('_', 1)][::-1]
                # tmp=re.split('[_.]', name)
                tmp2=tmp[1].split('.', 1)
                tmp2[0]=str(int(tmp2[0])+1)
                name= tmp[0]+"_"+tmp2[0]+"."+tmp2[1]
                if not os.path.isfile(name):#os.path.exists(os.path.split(name)[0])
                    with open(name, 'x') as fd:#os.mknod(name)#创建空文件os.makedirs(os.path.split(name)[0])
                        pass
                name=self.check_file_size(name)
            return name
        except Exception as e:
          LOGGER.exception("Exception Logged")
    def run_check_file_size(self,name,i):
        try:
            new_name=self.check_file_size(name)
            if new_name!= name:
                self.senser_file[i].close()
                self.senser_file[i] = open(new_name, 'a')
        except Exception as e:
          LOGGER.exception("Exception Logged")
if __name__ == "__main__":

    pass
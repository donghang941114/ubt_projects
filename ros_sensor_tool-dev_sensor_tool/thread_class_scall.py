#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QThread, pyqtSignal#, QDateTime
import os,time
from ssh_class import ssh_connection
# import traceback
import random
import logging
import json
from roslibpy import ServiceRequest
from ftplib import FTP
import hashlib
soft_first_start=True
LOGGER = logging.getLogger('main')
tool_info_str=''
client_call=None
ros_client=None
call_uws_server_type=None#False  None
class ssh_log_thread_class(QThread):
    signal = pyqtSignal(list)  # 括号里填写信号传递的参数

    def __init__(self):
        super().__init__()
        self.cmd=[]
        self.arg=[]
        self.ssh_arg = []
        self.ssh=None

    def setVal(self, cmd,arg,ssh_arg):
        self.ssh_arg=ssh_arg
        self.cmd = cmd  # int(val)
        self.arg=arg
        self.cnt=0


    def __del__(self):
        # self.wait()
        # self.quit()
        try:
            if self.ssh:
                self.ssh.close()
                self.ssh=None
            self.terminate()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def cmd_call_service(self,data):
        try:
            timeout_arg=2.5 if data=='date' else 36000
            dt=data+'ukey'
            result = client_call.call(ServiceRequest({'cmd': data,'md5':hashlib.md5(dt.encode(encoding='utf8')).hexdigest()}),timeout=timeout_arg)#'s'.encode(encoding='GTK')
            tmp_result=json.loads(result['result'])
            if len(tmp_result['stdout'])>0:
                return tmp_result['stdout']
            if len(tmp_result['stderr'])>0:
                return ["error", tmp_result['stderr']]
            # result = result['result'].split('\n')
            return tmp_result['stdout']
        except Exception as e:
            # if e.args[0] =='No service response received':
            #     return ["error", 'No service response received']
            LOGGER.info("password login ...")
    def find_ros_node_type(self,data):
        gs=False
        sl=False
        for j in data:
            for i in j:
                if i.find("/navigation_behaviour_gs_http") >= 0:
                    gs = True  # self.label_118.setText("高仙")
                if i.find("/navigation_behaviour_node") >= 0:
                    sl = True  # self.label_118.setText("思岚")
        return [gs,sl]
    def cmd_deal(self,cmd,*args):
        output = []
        for i in cmd:
            if call_uws_server_type == False:
                try:
                    tmp =self.ssh.exec_command(i.replace('/ftpDownload/log_tmp_copy','/log_tmp_copy')).decode()
                except:
                    tmp=''
            else:
                tmp = self.cmd_call_service(i)#self.ssh.exec_command(i)  # list.index(i)
            if not tmp:
                # if self.arg[0] == 1:
                #     out.append(["none_file"])
                continue
            if tmp[0] == "error":# file changed as we read it
                self.signal.emit([-10,tmp[1]])
                continue
            if not args or args[0]!='no_split':
                tmp = tmp.replace("\r", "").split('\n')
                while '' in tmp:
                    tmp.remove('')
            # print("ssh_log ok1:" + tmp)replace("[sudo] password for cruiser: ","")
            if tmp and tmp[0] != "error":
                if len(tmp) >= 2 and tmp[1].find("[sudo] password for") >= 0:
                    output.append(tmp[2:])
                elif tmp[0].find("[sudo] password for") >= 0:
                    output.append(tmp[1:])
                else:
                    output.append(tmp)
            else:
                LOGGER.warning("ssh cmd read NULL/error")
        return output
    def ftp_download(self,remote_file,localpath):
        try:
            if call_uws_server_type == False:
                self.ssh.ssh_download_files(["/home/cruiser/" + remote_file[0]],localpath)  # "ros_logs"
            else:
                if not os.path.exists(localpath):
                    os.makedirs(localpath)
                buf_size = 1024#1024 8192
                myftp = FTP()
                # myftp.encoding = 'gbk'
                myftp.connect(self.ssh_arg[0], 21)
                myftp.login('anonymous', '')
                for file in remote_file:
                    with open(localpath+'/%s'%os.path.basename(file), 'wb') as fp:
                        myftp.retrbinary('RETR %s' % file, fp.write, buf_size)
                myftp.quit()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def run(self):
        # 进行任务操作
        # out = []
        global call_uws_server_type
        while True:
            try:
                if call_uws_server_type == False and  not self.ssh and (self.arg[0]!=100 or (self.arg[0]==100 and self.cnt>80)):
                    self.ssh = ssh_connection(self.ssh_arg[0], 22, 'cruiser', self.ssh_arg[1])
            except Exception as e:
                LOGGER.exception("Exception Logged")#print(traceback.print_exc())
                self.signal.emit([-1, "ssh connect exception:"+str(e)])  # 发射信号
                call_uws_server_type=None
                return
                # if mode[0]:
                #     QMessageBox.critical(self, 'error', 'log_ssh连接失败')
            try:
                if ((call_uws_server_type == False and self.ssh) or call_uws_server_type != False)  and  self.arg:#and (self.arg[0]==1 or self.arg[0]==2)
                    try:
                        # for i in range(len(list)):
                        # list[i]
                        out=self.cmd_deal(self.cmd)
                            # err = stderr.read().decode()
                            # if err!="":
                            #     print("ssh_log connect err :" + err)
                        if self.arg[0]==1:#查找地图map json
                            # map_json_list = []
                            try:
                                map_json_data = self.cmd_deal(["find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/map/ -maxdepth 2 -name '*.json' | xargs -i cat {} " ],'no_split')
                                if map_json_data[0].find('}{')>=0:
                                    map_json_data = map_json_data[0].split('}{')
                            except Exception as e:
                                pass
                            try:
                                for dt in (map_json_data):
                                    try:
                                        if dt[0]!='{':dt='{'+dt
                                        if dt[-1] != '}':dt =dt+'}'
                                        out.append(json.loads(dt))
                                    except Exception as e:
                                        pass
                            except Exception as e:
                                pass
                            self.signal.emit([1, out])  # 发射信号
                        elif self.arg[0]==2:#下载
                            ros_node_type=self.find_ros_node_type(out)
                            self.signal.emit([6, ros_node_type])  # 发射信号
                            try:
                                tmp = self.cmd_deal(["rm -rf /home/cruiser/ftpDownload/log_tmp_copy"])
                            except Exception as e:
                                pass
                            ros_time = self.cmd_deal(["date +%s"])[0][0]#.replace("\n","")
                            systime=int(time.time())-int(ros_time)
                            tmp=self.cmd_deal(["mkdir -p /home/cruiser/ftpDownload/log_tmp_copy/conv_map"])
                            str_time_offset='P'+str(systime)+'s' if systime>=0 else 'R'+str(-systime)+'s'
                            LOGGER.debug("rostime:%s"%ros_time)
                            ros_time_last_second = int(int(ros_time) - self.arg[1])  # utcfromtimestamp(ros_time_last_second+8*60*60)
                            cmds = ["find /home/cruiser/ros_ws/upgrade_manager/ -name 'ubtrosUpgrade.log'"]
                            targzfind = []
                            if self.arg[4] =='all':
                                if (ros_node_type[0] and ros_node_type[1]) or (not ros_node_type[0] and not ros_node_type[1]):
                                    if self.arg[6]:
                                        cmds.append("find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/bag -name '*.bag*'")
                                    if self.arg[8]:
                                        cmds.append("find /home/cruiser/logs/ -name 'slamwared.sle*'")
                                elif ros_node_type[0]:
                                    if self.arg[6]:
                                        cmds.append("find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/bag -name '*.bag*'")
                                else:
                                    if self.arg[8]:
                                        cmds.append("find /home/cruiser/logs/ -name 'slamwared.sle*'")
                                if self.arg[7]:
                                    cmds.append("find /home/cruiser/logs/ -name 'rosout.log' -o -name '*.tar.gz'")
                            else:
                                f_min=int(self.arg[4])
                                offset_min=self.arg[9]
                                extra_offset_min_start=offset_min - 30 if offset_min>30 else 0 #默认多拷贝往后30分日志
                                if (ros_node_type[0] and ros_node_type[1]) or (not ros_node_type[0] and not ros_node_type[1]):#高仙 思岚
                                    if self.arg[6]:
                                        cmds.append("find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/bag -name '*.bag*' -mmin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))#m ->a
                                        cmds.append("find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/bag -name '*.bag*' -amin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                                    if self.arg[8]:
                                        cmds.append("find /home/cruiser/logs/ -name 'slamwared.sle*'")
                                elif ros_node_type[0]:#offset_min + f_min时间在前
                                    if self.arg[6]:
                                        cmds.append("find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/bag -name '*.bag*' -mmin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                                        cmds.append("find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/bag -name '*.bag*' -amin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                                else:
                                    if self.arg[8]:
                                        cmds.append("find /home/cruiser/logs/ -name 'slamwared.sle*'")
                                if self.arg[7]:
                                    try:
                                        targz = self.cmd_deal(["ls /home/cruiser/logs/ | grep '.tar.gz'"])[0]
                                        print(targz)
                                        if targz[-1]=='':
                                            targz.pop(-1)
                                        targz_timestamp=[]
                                        for i in targz:
                                            try:
                                                targz_timestamp.append(i.split('.tar.gz')[0].split('_')[1])
                                            except Exception as e:
                                                pass
                                        start_time=ros_time_last_second-f_min*60

                                        for i,value in enumerate(targz_timestamp):
                                            if int(value)>=start_time:
                                                targzfind.append(' /home/cruiser/logs/'+targz[i])
                                        targzfindstr=''.join(targzfind)#兼容ros日志压缩targz

                                        tmp = self.cmd_deal(["for tar in %s; do tar xf $tar -C /home/cruiser/ftpDownload/log_tmp_copy; done "%targzfindstr])
                                        cmds.append("find /home/cruiser/ftpDownload/log_tmp_copy/ -name 'rosout.log' -mmin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                                        cmds.append("find /home/cruiser/ftpDownload/log_tmp_copy/ -name 'rosout.log' -amin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                                    except Exception as e:
                                        LOGGER.info("Exception Logged")
                                    cmds.append("find /home/cruiser/logs/ -name 'rosout.log' -mmin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                                    cmds.append("find /home/cruiser/logs/ -name 'rosout.log' -amin +%d -a -mmin -%d" % (extra_offset_min_start, offset_min + f_min))
                            out = self.cmd_deal(cmds)
                            if self.arg[2]!='':
                                if self.arg[2].find('#dircopy#')<0:
                                    out.append([self.arg[2]])
                                else:
                                    try:#转换地图成PC识别格式
                                        path_name=self.arg[2].split('#dircopy#')
                                        cmd2 = ["cp -ar %s/* /home/cruiser/ftpDownload/log_tmp_copy/conv_map;cd /home/cruiser/ftpDownload/log_tmp_copy/conv_map; /home/cruiser/ros_ws/install/share/gs_console/tools/ubtech_map_converter > %s.map;\
                                                cp map.png %s.map ..;mv ../map.png ../%s.png;tar czf ../%s.tar.gz ."%(path_name[0],path_name[1],path_name[1],path_name[1],path_name[1])]
                                        tmp = self.cmd_deal(cmd2)
                                        if tmp and tmp[0] == "error":
                                            self.signal.emit([-10, tmp[1]])
                                        out.append(['/home/cruiser/ftpDownload/log_tmp_copy/%s%s'%(path_name[1],i) for i in ['.map','.png','.tar.gz']])
                                    except Exception as e:
                                        LOGGER.exception("Exception Logged")  # print(traceback.print_exc())
                            if self.arg[8]:#计算console时间
                                if self.arg[4]=="all" or int(self.arg[4])>=6*60*24:
                                    cmd3=["sudo -S find /root/.ros/ -name 'console*.log' -o -name 'move_base_node*.log'"]
                                else:
                                    # ros_time_last_wk = int(time.strftime("%w", time.localtime(ros_time_last_second)))
                                    # ros_time_start_wk = int(time.strftime("%w", time.localtime(ros_time_last_second - int(self.arg[4]) * 60)))
                                    ros_time_last_wk = int(time.strftime("%w", time.gmtime(ros_time_last_second+8*60*60)))#东八区
                                    ros_time_start_wk = int(time.strftime("%w", time.gmtime(ros_time_last_second+8*60*60 - int(self.arg[4]) * 60)))
                                    tmp_name="sudo -S find /root/.ros/ "
                                    # tmp_str=['console','move_base_node','adapter','gmapping','gs_checker','joystick_control','localization','op_node','scan_to_scan_filter_chain']
                                    if ros_time_last_wk>ros_time_start_wk:
                                        for i in range(ros_time_start_wk,ros_time_last_wk):
                                            tmp_name = tmp_name + "-name '*[a-zA-Z]-%d[.-]*log' -o " % (i)
                                            # for k in tmp_str:
                                            #     tmp_name = tmp_name + "-name '%s-%d[.-]*log' -o " % (k,i)
                                            # tmp_name=tmp_name+"-name 'console-%d.log' -o "%i
                                            # tmp_name = tmp_name + "-name 'move_base_node-%d-*.log' -o " % i
                                    elif ros_time_last_wk<ros_time_start_wk:
                                        for i in range(ros_time_start_wk, 7):
                                            tmp_name = tmp_name + "-name '*[a-zA-Z]-%d[.-]*log' -o " % (i)
                                            # for k in tmp_str:
                                            #     tmp_name = tmp_name + "-name '%s-%d[.-]*log' -o " % (k, i)
                                        for i in range(0,ros_time_last_wk):
                                            tmp_name = tmp_name + "-name '*[a-zA-Z]-%d[.-]*log' -o " % (i)
                                            # for k in tmp_str:
                                            #     tmp_name = tmp_name + "-name '%s-%d[.-]*log' -o " % (k, i)
                                    # tmp_name=tmp_name + "-name 'console-%d.log' -o "%ros_time_last_wk
                                    # tmp_name = tmp_name + "-name 'move_base_node-%d-*.log'" % ros_time_last_wk
                                    # for k in tmp_str:
                                    #     tmp_name = tmp_name + "-name '%s-%d[.-]*log' -o " % (k, ros_time_last_wk)
                                    tmp_name = tmp_name + "-name '*[a-zA-Z]-%d[.-]*log'" % (ros_time_last_wk)
                                    # tmp_name= tmp_name.rstrip(" -o ")
                                    cmd3 = [tmp_name]
                                out=out+self.cmd_deal(cmd3)
                            if len(self.arg[10])>0:
                                out.append(self.arg[10])
                            str_name=""
                            # for i in out:
                            #     for j in i:
                            #         str += " "+j
                            filter_out=[]
                            for i in range(len(out)):
                                for j in range(len(out[i])):
                                    if out[i][j] not in  filter_out:
                                        filter_out.append(out[i][j])
                                        if out[i][j].find("rosout.log")>=0:
                                            if out[i][j].find("log_tmp_copy")>=0:#添加压缩解压后的ros文件，直接重原来地方copy
                                                for k in targzfind :
                                                    if os.path.basename(os.path.dirname(out[i][j])) in k:
                                                        str_name += ' '+k
                                                        break
                                            else:
                                                str_name += " "+os.path.dirname(out[i][j])
                                        else:
                                            str_name += " "+out[i][j]
                                        # self.plainTextEdit.appendPlainText("符合的文件："+out[i][j])
                                        self.signal.emit([2, ["符合的文件："+out[i][j]]])  # 发射信号
                            # file_name=[]
                            file_name=self.arg[3].replace(" ","_").replace(":","-")+"_"+self.arg[4]+"-"+str_time_offset+'_'+str(random.randint(0,10000))#self.lineEdit_10.text()
                            # self.plainTextEdit.appendPlainText("打包名字：" + file_name)
                            #转义
                            time.sleep(0.12)
                            tmp=self.cmd_deal(['touch /home/cruiser/ftpDownload/log_tmp_copy/bug_description.log /home/cruiser/ftpDownload/log_tmp_copy/tool_info.log;\
                                           echo "%s" > /home/cruiser/ftpDownload/log_tmp_copy/bug_description.log;echo "%s" > /home/cruiser/ftpDownload/log_tmp_copy/tool_info.log'%(self.arg[11][1],tool_info_str)])
                            str_name += ' /home/cruiser/ftpDownload/log_tmp_copy/bug_description.log'+' /home/cruiser/ftpDownload/log_tmp_copy/tool_info.log'
                            LOGGER.debug("file:%s %s"%(file_name,str_name))
                            self.signal.emit([3, []])  # 发射信号

                            tmp =self.cmd_deal([" sudo -S tar -czPf /home/cruiser/ftpDownload/log_tmp_copy/%s\(%s\).tar.gz %s"%(file_name,self.arg[11][0],str_name)])
                            file_size = self.cmd_deal(["ls -l /home/cruiser/ftpDownload/log_tmp_copy/%s\(%s\).tar.gz | awk '{print $5}'" % (file_name,self.arg[11][0])])
                            # return "/home/cruiser/ftpDownload/log_tmp_copy/"+file_name
                            self.signal.emit([4, [file_size[0][0],self.arg[5]+'/'+file_name+"(%s).tar.gz"%(self.arg[11][0])]])  # 发射信号
                            self.ftp_download(["log_tmp_copy/"+file_name+"(%s).tar.gz"%(self.arg[11][0])],self.arg[5])#"ros_logs"
                            cmd2 = ["rm -rf /home/cruiser/ftpDownload/log_tmp_copy"]
                            self.signal.emit([5, [cmd2]])  # 发射信号
                            tmp = self.cmd_deal(cmd2)
                        elif self.arg[0] == 3:
                            self.signal.emit([102, "ros connect close"])  # 发射信号
                        elif self.arg[0]==100:
                            # self.signal.emit([101, "ros server ok"])  # 发射信号
                            self.cnt=0
                            while self.cnt<70:
                                self.cnt += 1
                                time.sleep(0.1)
                                if ros_client and ros_client.is_connected or out:
                                    self.signal.emit([100, "ros connect ok"])  # 发射信号
                                    if call_uws_server_type != False:
                                        call_uws_server_type = True
                                    return
                                if call_uws_server_type != False:
                                    break
                            if call_uws_server_type != False:
                                call_uws_server_type = False
                            self.signal.emit([-100, "ROS服务连接超时，请再试一次",self.arg[4]])  # 发射信号
                        return
                    except Exception as e:
                        self.signal.emit([-2, "ssh cmd exception:"+str(e)])  # 发射信号
                        LOGGER.exception("Exception Logged")#print(traceback.print_exc())
                    finally:
                        # if close_mode==0:
                        # self.ssh.close()pass
                        self.ssh=None
                        return
                elif self.arg[0]==100:
                    global soft_first_start
                    if self.cnt>20 and soft_first_start:
                        soft_first_start=False
                        self.cnt=81
                    else:
                        self.cnt+=1
                        time.sleep(0.1)
                    if ros_client and ros_client.is_connected:
                        if call_uws_server_type != False:
                            call_uws_server_type=True
                        self.signal.emit([100, "ros connect ok"])  # 发射信号
                        soft_first_start = False
                        return
            except Exception as e:
                self.signal.emit([-3, "ssh cmd exception:" + str(e)])  # 发射信号
                LOGGER.exception("Exception Logged")
                return
if __name__ == "__main__":

    pass

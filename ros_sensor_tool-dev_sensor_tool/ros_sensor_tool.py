#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ros_qt2_new import Ui_MainWindow
from PyQt5 import QtCore,QtWidgets,QtGui
from PyQt5.QtWidgets import QMessageBox,QFileDialog,QAction, QListWidget, QListWidgetItem, QCheckBox
from password_class import PasswordWindow
from file_operation import file_op,senser_file_path_name
# from __future__ import print_function
# import paramiko
#import roslibpy
from roslibpy import  Ros, Topic,Service#Message,
import os
# import threading
import time
from PyQt5.QtCore import QTimer#,QThread, pyqtSignal#, QDateTime
import pyqtgraph as pg
import numpy as np
# import pyqtgraph.examples as pge
# pge.run()
# import traceback
# import matplotlib
# matplotlib.use('Qt5Agg')
# from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
# import matplotlib.pyplot as plt
# import numpy as np
import array
import json
import signal
from ini_operation import ini_file_operator
import datetime
import math
# from ssh_class import ssh_connection
import thread_class_scall# from thread_class import ssh_log_thread_class

from log import config_logging
import logging
from zipfile import ZipFile
import re
# Ctrl + Numpad+/-   展开/折叠代码块（当前位置的：函数，注释等）
# Ctrl + shift + Numpad+/-   展开/折叠所有代码
#不支持宏定义，可改成全局变量 或者特殊字符后面替换也可以
#控件太多，不一一重命名，需要根据QT界面查找即可
NUM_POINT=1000
#ult wallir toptof chargeir imu lidar batt floorir
rostopic_num=8

sensor_name=['超声波','墙检红外','头部TOF红外','回充红外','地检红外']
sensor_index=[8,6,1,2,1]
sensor_data=[[] for _ in range(sum(sensor_index))]
sensor_data_min_max_value=[-5000 if i > sum(sensor_index) else 5000 for i in range(sum(sensor_index*2))]

# str_ip="192.168.100.10"
str_ip="192.168.100.10"#"192.168.11.123"#"10.10.61.156"#"192.168.100.10"
reconnect_cnt=0
reconnect_fail_cnt=0
global ssh_mode_state,down_flie_info,robot_type,lidar_radius_data
lidar_radius_data=[]
lidar_radius_angle=[0,360]
ssh_mode_state=0
down_flie_info = [0,""]
robot_type="Cruzr1S"
reconnect_topic_cnt=0
reconnect_topic_cnt_bak=0
lidar_test_para={'time':0,'dis':0,'sa':0,'ea':0}
lidar_sun,lidar_err =1,0
password_ui=None
lidar_filter='/scan'
log_read_all=False
def config_log_level():
    try:
        ini_dt = ini_file_operator('./config.ini')
        s = ini_dt.get_ini_val('setting', 'log_level')
        if s: config_logging(file_name="log.log", log_level=s)  # NOSET INFO
        s = ini_dt.get_ini_val('setting', 'robot_model')
        global str_ip
        if s and s=="Cruzr1S": str_ip="192.168.11.123"#
        s = ini_dt.get_ini_val('setting', 'lidar_filter')
        global lidar_filter
        if s and s=="YES": lidar_filter='/scan_filtered'
        s = ini_dt.get_ini_val('setting', 'read_log_all')
        global log_read_all
        if s and s == "YES": log_read_all = True
    except Exception as e:
        print(str(e))

config_log_level()
LOGGER = logging.getLogger('main')
VERSION=1.1
# ros_rosbridge_server_connect_again=False
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow,file_op):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
#初始化
        # self.label_70.setText("V1.0.0")
        self.setWindowTitle('UBTECH-Cruzr V%0.1f '%VERSION)
        thread_class_scall.ros_client = None
        self.label_118.setText("未检测")
        # self.checkBox_21.setVisible(False)
        self.setFixedSize(self.width(), self.height())#self.showFullScreen()
        self.comboBox_2.addItem(robot_type)
        self.comboBox_2.addItem("Cruzr1")
        self.comboBox_2.currentIndexChanged.connect(self.comboBox_robot_type_select)
        self.save_map_path=[]
        self.save_manual_bag_path = []
        self.real_password = 'aa'#self.lineEdit_88.text()
        # text
        self.pushButton_open_close.setText("查看传感器")
    # 按钮
        self.pushButton_11.setText("暂停显示曲线")
        self.pushButton_11.clicked.connect(self.start_pause_display)
        self.pushButton_open_close.clicked.connect(self.open_close_ros)
        self.toolBox.currentChanged.connect(self.toolBox_change_deal)  #
        self.pushButton_12.clicked.connect(self.download_ros_log)
        self.pushButton_18.setText("暂停显示曲线")
        self.pushButton_18.clicked.connect(self.start_pause_display)
        self.pushButton_17.clicked.connect(self.query_ros_map)
        #ult
        # self.pushButton.clicked.connect(self.button_plot_check_select)
        # self.pushButton_2.clicked.connect(self.button_plot_check_select)
        # self.pushButton_3.clicked.connect(self.button_plot_check_select)
        self.pushButton_4.clicked.connect(self.clear_edit_data_display)
       #ir_wall
        # self.pushButton_5.clicked.connect(self.button_plot_check_select)
        # self.pushButton_6.clicked.connect(self.button_plot_check_select)
        # self.pushButton_7.clicked.connect(self.button_plot_check_select)
        #
        # 获取到text光标
        # textCursor = self.textEdit.textCursor()
        # # 滚动到底部
        # textCursor.movePosition(textCursor.End)
        # # 设置光标到text中去
        # self.textEdit.setTextCursor(textCursor)
    #event
        self.checkBox_15.stateChanged.connect(self.file_save_deal)
        self.checkBox_19.stateChanged.connect(self.file_save_deal)
        self.checkBox_20.stateChanged.connect(self.ros_log_time_set)
        self.checkBox_15.setVisible(False)
        self.checkBox_19.setVisible(False)
    #tab toolBox.setCurrentIndex (0) # 选项卡
        self.groupBox_ult_check.setVisible(True)
        self.groupBox_ult_data.setVisible(True)
        # self.toolBox.addItem(QtWidgets.QPushButton("Tab Content 1"),"超声波1")
        # self.pushButton.setText("全选")
        # self.pushButton_2.setText("全不选")
        # self.pushButton_3.setText("反选")
        self.checkBox.setText("超声波1")
        self.checkBox_2.setText("超声波2")
        self.checkBox_3.setText("超声波3")
        self.checkBox_4.setText("超声波4")
        self.checkBox_5.setText("超声波5")
        self.checkBox_6.setText("超声波6")
        self.checkBox_7.setText("超声波7")
        self.checkBox_8.setText("超声波8")
        self.checkBox.setChecked(True)
        self.checkBox_2.setChecked(True)
        self.checkBox_3.setChecked(True)
        self.checkBox_4.setChecked(True)
        self.checkBox_5.setChecked(True)
        # self.checkBox_6.setChecked(True)
        self.checkBox_7.setChecked(True)
        # self.checkBox_8.setChecked(True)
        self.label_4.setText("超声波1")
        self.label_5.setText("超声波2")
        self.label_13.setText("超声波3")
        self.label_21.setText("超声波4")
        self.label_22.setText("超声波5")
        self.label_23.setText("超声波6")
        self.label_24.setText("超声波7")
        self.label_25.setText("超声波8")
        self.label.setText("实时值")
        self.label_2.setText("最大值")
        self.label_3.setText("最小值")
        self.pushButton_4.setText("清除数据")
        #wall_ir
        #wall_ir
        self.label_42.setText("ROS IP：")
        self.lineEdit_52.setText(str_ip)
        # self.lineEdit_88.setText("aa")
        self.lineEdit_11.setText("60")

        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.display_plot)
        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.general_timer_deal)
        self.timer2.start(1000)
        self.timer_lidar_test = QTimer(self)
        self.timer_lidar_test.timeout.connect(self.lidar_test_timeout)
#data val
        self.pointcnt_frequency=[[0,0,0] for i in range(rostopic_num)]#总数 频率 累加计数
        self.ssh_connect_cnt = 0

        self.ult_file=None
        self.ir_wall_file = None
        self.ir_top_tof_file = None
        self.ir_charge_file = None
        self.senser_file = [None]*rostopic_num
        self.listener_untrasonic=None
        self.listener_sensor_tof_ir=None
        self.listener_wall_check_ir=None
        self.listener_charge_ir=None
        self.listener_geomagnetism=None
        # self.listener_battery=None
        self.listener_lidar=None
        self.listener_floor_ir=None
        self.label_7.setPixmap(QtGui.QPixmap(':c1s/c1s.png'))
        self.label_7.setScaledContents(True)
        # self.label_7.setPixmap(QPixmap(""))  # 移除label上的图片
        # self.label_7.setObjectName("ss")
        self.setWindowIcon(QtGui.QIcon(':c1s/c1s.ico'))
        self.plt_disp_data=[None for _ in range(sum(sensor_index))]
        self.graph_sensor_init()
        self.sensor_lable_index = [self.label_75, self.label_72, self.label_77, self.label_79, self.label_81, self.label_84,self.label_83, self.label_92,\
                             self.label_100,self.label_86,self.label_99,self.label_88,self.label_98,self.label_94,\
                             self.label_97,\
                             self.label_111,self.label_112,\
                             self.label_114]
        self.sensor_lineedit_index=[self.lineEdit,self.lineEdit_9,self.lineEdit_38,\
                                    self.lineEdit_2,self.lineEdit_19,self.lineEdit_39,\
                                    self.lineEdit_3,self.lineEdit_20,self.lineEdit_40,\
                                    self.lineEdit_4,self.lineEdit_21,self.lineEdit_41,\
                                    self.lineEdit_5,self.lineEdit_34,self.lineEdit_42,\
                                    self.lineEdit_6,self.lineEdit_35,self.lineEdit_43,\
                                    self.lineEdit_7,self.lineEdit_36,self.lineEdit_44,\
                                    self.lineEdit_8,self.lineEdit_37,self.lineEdit_45]
        self.sensor_checkbox_index=[self.checkBox,self.checkBox_2,self.checkBox_3,self.checkBox_4,self.checkBox_5,self.checkBox_6,self.checkBox_7,self.checkBox_8]
        self.sensor_lable_value_name=[self.label_4,self.label_5,self.label_13,self.label_21,self.label_22,self.label_23,self.label_24,self.label_25]

        self.tabWidget_all.currentChanged.connect(self.tabWidget_all_change_deal)
        self.toolBox.setCurrentIndex(1)
        self.toolBox_change_deal()
        self.tabWidget_all.setCurrentIndex(0)

        self.tabWidget_all.setTabEnabled(1,False)
        self.ssh_ros_thread = thread_class_scall.ssh_log_thread_class()
        self.ssh_ros_thread.signal.connect(self.ssh_thread_ros_callback)
    # ros_log日志
        self.label_15.setText("需要获取时间：")
        # self.lineEdit_10.setText(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.pushButton_20.clicked.connect(self.timestamp_time)
        self.pushButton_21.clicked.connect(self.timestamp_time)
        self.ssh_log_thread=thread_class_scall.ssh_log_thread_class()
        self.ssh_log_thread.signal.connect(self.ssh_thread_log_callback)
        self.progressBar.setVisible(False)
        self.label_69.setVisible(False)
        self.pushButton_19.clicked.connect(self.clear_plainedit_display)
        # self.ssh_log_thread.setVal()
        self.graph_lidar_win=None
        self.comboBox_3.addItems(["无","虚线","实线"])
        self.comboBox_3.setCurrentIndex(1)
        self.comboBox_3.currentIndexChanged.connect(self.lidar_polar_round_select)
        self.polar_lidar_round = []
        # self.robot_type_init()
        self.label_103.setText("")
        self.label_105.setText("")
        self.pushButton_22.clicked.connect(self.clear_lidar_point_edit_display)
        # self.label_71.setGeometry(QtCore.QRect(10, 20, 54, 12))
        if str_ip == "192.168.100.10":
            self.comboBox_2.setCurrentIndex(1)
        else:
            self.comboBox_2.setCurrentIndex(0)
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())#str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

        exitAct = QAction(QtGui.QIcon(':c1s/c1s.ico'),'输入ROS密码..', self)  # exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.triggered.connect(self.ui_set_password)
        fileMenu = self.menuBar.addMenu('设置')
        fileMenu.addAction(exitAct)

        exitAct = QAction(QtGui.QIcon(':c1s/c1s.ico'),'关于..', self)  # exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.triggered.connect(self.show_about)
        fileMenu = self.menuBar.addMenu('帮助')
        fileMenu.addAction(exitAct)

        self.listWidget = QListWidget()
        # self.listWidget.itemClicked.connect(self.listWidget_Clicked)
        self.verticalLayout_22.addWidget(self.listWidget)
        self.pushButton_25.clicked.connect(self.lidar_error_test)
        self.label_46.setVisible(False)
        self.label_45.setVisible(False)
        self.label_20.setVisible(False)
        self.label_58.setVisible(False)

        self.timer_lidar_ts = QTimer(self)
        self.timer_lidar_ts.timeout.connect(self.lidar_avg_test)
        self.timer_lidar_ts.start(10000)
        self.tmp_angle_avg_data=0
        self.tmp_angle_avg_data_bak = 0
        if not log_read_all:
            self.checkBox_20.setDisabled(True)
        self.robot_type_init()
    def show_about(self):
        QMessageBox.about(self, "关于", "传感器显示及日志下载功能\n------V%0.1f 修改记录------\n"
                                      "1、修复默认无密码模式，压缩时间过长导致超时退出\n"
                                      "2、修复默认无密码模式，雷达点云显示卡顿问题"%VERSION
                                        )
#之前为了兼容Cruzr1添加显示，后面发现Cruzr1无法无法获取传感器数据暂保留
    def ui_set_password(self):
        self.display_password_ui(self.sender())
    def robot_type_init(self):
        try:
            self.graph_lidar_init()
            if robot_type=="Cruzr1S":
                self.label_75.setText("")
                self.label_72.setText("")
                self.label_77.setText("")
                self.label_79.setText("")
                self.label_81.setText("")
                self.label_84.setText("")
                self.label_83.setText("")
                self.label_92.setText("")

                self.label_100.setText("")
                self.label_86.setText("")
                self.label_99.setText("")
                self.label_88.setText("")
                self.label_98.setText("")
                self.label_94.setText("")
                self.label_97.setText("")
                self.label_111.setText("")
                self.label_112.setText("")
                self.label_114.setText("")
                self.label_101.setVisible(True)
                self.label_97.setVisible(True)
                self.label_82.setVisible(True)
                self.label_83.setVisible(True)
                self.label_90.setVisible(True)
                self.label_92.setVisible(True)
                self.label_95.setVisible(True)#ir6-4
                self.label_94.setVisible(True)
                self.label_96.setVisible(True)
                self.label_98.setVisible(True)
                self.label_89.setVisible(True)
                self.label_88.setVisible(True)
                self.label_85.setGeometry(QtCore.QRect(1356, 389, 31, 16))#self.label_85.setGeometry(QtCore.QRect(1344, 379, 31, 16))
                self.label_84.setGeometry(QtCore.QRect(1365, 400, 21, 20))# self.label_84.setGeometry(QtCore.QRect(1350, 390, 21, 20))
                self.label_80.setGeometry(QtCore.QRect(1252, 499, 41, 16))
                self.label_81.setGeometry(QtCore.QRect(1250, 516, 21, 20))
                self.label_78.setGeometry(QtCore.QRect(1280, 503, 41, 16))
                self.label_79.setGeometry(QtCore.QRect(1280, 518, 21, 20))
                self.label_76.setGeometry(QtCore.QRect(1318, 503, 41, 16))
                self.label_77.setGeometry(QtCore.QRect(1320, 519, 21, 20))
                self.label_73.setGeometry(QtCore.QRect(1353, 503, 41, 16))
                self.label_72.setGeometry(QtCore.QRect(1350, 518, 21, 20))
                self.label_74.setGeometry(QtCore.QRect(1380, 499, 41, 16))
                self.label_75.setGeometry(QtCore.QRect(1380, 515, 21, 20))
                self.label_95.setGeometry(QtCore.QRect(1261, 571, 28, 16))#ir6-1
                self.label_94.setGeometry(QtCore.QRect(1261, 581, 16, 16))
                self.label_96.setGeometry(QtCore.QRect(1281, 531, 28, 16))
                self.label_98.setGeometry(QtCore.QRect(1281, 541, 16, 16))
                self.label_89.setGeometry(QtCore.QRect(1309, 571, 28, 16))
                self.label_88.setGeometry(QtCore.QRect(1309, 581, 16, 16))
                self.label_91.setGeometry(QtCore.QRect(1326, 531, 28, 16))
                self.label_99.setGeometry(QtCore.QRect(1326, 541, 16, 16))
                self.label_87.setGeometry(QtCore.QRect(1358, 571, 28, 16))
                self.label_86.setGeometry(QtCore.QRect(1358, 581, 16, 16))
                self.label_93.setGeometry(QtCore.QRect(1371, 531, 28, 16))
                self.label_100.setGeometry(QtCore.QRect(1371, 541, 16, 16))
            else:
                self.label_101.setVisible(False)#tof ult8-7
                self.label_97.setVisible(False)
                self.label_82.setVisible(False)
                self.label_83.setVisible(False)
                self.label_90.setVisible(False)
                self.label_92.setVisible(False)
                self.label_85.setGeometry(QtCore.QRect(1231, 521, 28, 16))
                self.label_84.setGeometry(QtCore.QRect(1231, 531, 21, 16))
                self.label_80.setGeometry(QtCore.QRect(1265, 521, 28, 16))
                self.label_81.setGeometry(QtCore.QRect(1265, 531, 21, 16))
                self.label_78.setGeometry(QtCore.QRect(1299, 521, 28, 16))
                self.label_79.setGeometry(QtCore.QRect(1299, 531, 21, 16))
                self.label_76.setGeometry(QtCore.QRect(1333, 521, 28, 16))
                self.label_77.setGeometry(QtCore.QRect(1333, 531, 21, 16))
                self.label_73.setGeometry(QtCore.QRect(1368, 521, 28, 16))
                self.label_72.setGeometry(QtCore.QRect(1368, 531, 21, 16))
                self.label_74.setGeometry(QtCore.QRect(1402, 521, 28, 16))
                self.label_75.setGeometry(QtCore.QRect(1402, 531, 21, 16))
                self.label_95.setVisible(False)#ir6-4
                self.label_94.setVisible(False)
                self.label_96.setVisible(False)
                self.label_98.setVisible(False)
                self.label_89.setVisible(False)
                self.label_88.setVisible(False)
                self.label_93.setGeometry(QtCore.QRect(1380, 560, 28, 16))
                self.label_100.setGeometry(QtCore.QRect(1380, 570, 16, 16))
                self.label_87.setGeometry(QtCore.QRect(1320, 570, 28, 16))
                self.label_86.setGeometry(QtCore.QRect(1320, 580, 16, 16))
                self.label_91.setGeometry(QtCore.QRect(1260, 560, 28, 16))
                self.label_99.setGeometry(QtCore.QRect(1260, 570, 16, 16))
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def lidar_avg_test(self):
        try:
            if self.tabWidget_all.currentIndex() == 2 :#and len(self.label_105.text())>0:
                self.tmp_angle_avg_data_bak=self.tmp_angle_avg_data
                self.tmp_angle_avg_data=0
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def graph_sensor_init(self):
        # 建立窗体：1
        # self.plt = pg.PlotWidget(title="超声波1")#addWidget(plt)
        # pg.setConfigOption('background', 'w')
        # self.plt_ult1 = self.plt.plot(pen="r", name="超声波1")
        # self.verticalLayout.addWidget(self.plt)
        # 建立窗体：2
        try:
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
            win = pg.GraphicsWindow()  # title="超声波1"GraphicsWindow
            win.resize(1, 1)

            self.verticalLayout.addWidget(win)
            # self.plt = win.addPlot(title="动态波形图")
            # self.plt_ult1 = self.plt.plot(pen="r", name="超声波1")
            self.plt = win.addPlot()  # title="动态波形图"

            self.plt.showGrid(x=True, y=True)
            self.plt.setLabel(axis="left", text="distance")
            self.plt.setLabel(axis="bottom", text="point")
            self.plt.setTitle("超声波 cm")
            self.plt.addLegend()
            # self.plt.addLegend(size=(10, 10))
            # c1 = plt.plot([1, 3, 2, 4], pen='r', symbol='o', symbolPen='r', symbolBrush=0.5, name='red plot')
            # c2 = plt.plot([2, 1, 4, 3], pen='g', fillLevel=0, fillBrush=(255, 255, 255, 30), name='green plot')
            self.plt_disp_data[0] = self.plt.plot(pen="r", symbol='o', symbolPen='r', symbolSize=3, name="超声波1")
            self.plt_disp_data[1]  = self.plt.plot(pen="g", symbol='t', symbolPen='g', symbolSize=3, name="超声波2")
            self.plt_disp_data[2]  = self.plt.plot(pen="b", symbol='t1', symbolPen='b', symbolSize=3, name="超声波3")
            self.plt_disp_data[3]  = self.plt.plot(pen="c", symbol='t2', symbolPen='c', symbolSize=3, name="超声波4")
            self.plt_disp_data[4]  = self.plt.plot(pen="m", symbol='d', symbolPen='m', symbolSize=3, name="超声波5")
            self.plt_disp_data[5]  = self.plt.plot(pen="y", symbol='s', symbolPen='y', symbolSize=3, name="超声波6")
            self.plt_disp_data[6]  = self.plt.plot(pen=(100, 100, 150), symbol='p', symbolPen='g', symbolSize=3,
                                          name="超声波7")  # 255 白色 (100, 100, 150)
            self.plt_disp_data[7]  = self.plt.plot(pen=(200, 150, 150), symbol='t', symbolPen='w', symbolSize=3, name="超声波8")
            # self.verticalLayout.addWidget(self.plt)

            self.plt.setXRange(0, NUM_POINT)
            self.plt.setYRange(0, 160)
            # self.plt.enableAutoRange('x', False)
            # self.plt.setAutoPan(True,True)
            # self.plt.setAutoPan(y=True)
            # pyqtgraph.setConfigOption('leftButtonPan' ， False)
            self.plt_label = pg.TextItem()  # plotItem.clear() # 清空绘图部件中的项textEdit.
            self.plt_label.setColor("b")
            self.plt.addItem(self.plt_label)
            self.plt_label_data=[]
            for i in range(8):
                self.plt_label_data.append(pg.TextItem())
                self.plt_label_data[-1].setColor("b")
                self.plt.addItem(self.plt_label_data[-1])

            # wall ir
            self.plt_disp_data[sum(sensor_index[0:1])+0]  = self.plt.plot(pen="r", symbol='o', symbolPen='r', symbolSize=3, name="墙检红外1")
            self.plt_disp_data[sum(sensor_index[0:1])+1] = self.plt.plot(pen="g", symbol='t', symbolPen='g', symbolSize=3, name="墙检红外2")
            self.plt_disp_data[sum(sensor_index[0:1])+2] = self.plt.plot(pen="b", symbol='t1', symbolPen='b', symbolSize=3, name="墙检红外3")
            self.plt_disp_data[sum(sensor_index[0:1])+3] = self.plt.plot(pen="c", symbol='t2', symbolPen='c', symbolSize=3, name="墙检红外4")
            self.plt_disp_data[sum(sensor_index[0:1])+4] = self.plt.plot(pen="m", symbol='d', symbolPen='m', symbolSize=3, name="墙检红外5")
            self.plt_disp_data[sum(sensor_index[0:1])+5] = self.plt.plot(pen="y", symbol='s', symbolPen='y', symbolSize=3, name="墙检红外6")
            self.plt.legend.removeItem("墙检红外1")
            self.plt.legend.removeItem("墙检红外2")
            self.plt.legend.removeItem("墙检红外3")
            self.plt.legend.removeItem("墙检红外4")
            self.plt.legend.removeItem("墙检红外5")
            self.plt.legend.removeItem("墙检红外6")
            # tof
            self.plt_disp_data[sum(sensor_index[0:2])+0] = self.plt.plot(pen="r", symbol='o', symbolPen='r', symbolSize=3, name="头部TOF红外1")
            self.plt_disp_data[sum(sensor_index[0:3])+0] = self.plt.plot(pen="r", symbol='o', symbolPen='r', symbolSize=3, name="回充红外1")
            self.plt_disp_data[sum(sensor_index[0:3])+1] = self.plt.plot(pen="g", symbol='t', symbolPen='g', symbolSize=3, name="回充红外2")
            self.plt.legend.removeItem("头部TOF红外1")
            self.plt.legend.removeItem("回充红外1")
            self.plt.legend.removeItem("回充红外2")
            #gyro

            # cross hair
            self.vLine = pg.InfiniteLine(angle=90, movable=False)
            self.hLine = pg.InfiniteLine(angle=0, movable=False)
            self.plt.addItem(self.vLine, ignoreBounds=True)
            self.plt.addItem(self.hLine, ignoreBounds=True)
            self.vb = self.plt.vb  # import
            self.plt.proxy = pg.SignalProxy(self.plt.scene().sigMouseMoved, rateLimit=15, slot=self.mouseMoved)#60
            #floor
            self.plt_disp_data[sum(sensor_index[0:4])+0] = self.plt.plot(pen="r", symbol='o', symbolPen='r', symbolSize=3, name="地检红外1")
            # self.plt.scene().sigMouseMoved.connect(self.mouseMoved)
            # self.plt.addLegend(size=(150, 80))
    #
            # val
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def graph_lidar_init(self):
        '''雷达2D初始化'''
        try:
            # if robot_type=="Cruzr1S":
            max_value = 25
            # else:
            #     max_value = 16
            # LOGGER.debug("lidar_polar_start %s"%str(self.graph_lidar_win))
            if  self.graph_lidar_win:
                # self.lidar_polar.
                self.lidar_polar.close()
                self.graph_lidar_win.close()
                # LOGGER.debug("lidar_polar_close")
            # else:
            # LOGGER.debug("lidar_polar_over")
            pg.setConfigOptions(antialias=True)
            self.graph_lidar_win = pg.GraphicsWindow(size=(1,1))
            # self.graph_lidar_win.setWindowTitle('s')
            self.verticalLayout_2.addWidget(self.graph_lidar_win)

            self.lidar_polar = self.graph_lidar_win.addViewBox()
            self.lidar_polar.setAspectLocked()

            self.polar_plt = pg.GraphItem()
            self.lidar_polar.addItem(self.polar_plt)
            self.polar_plt_axis = pg.GraphItem()
            self.lidar_polar.addItem(self.polar_plt_axis)

            lidar_axis_data = np.array([
                [-max_value, 0],
                [max_value, 0],
                [max_value*math.cos(math.radians(180+30)),max_value*math.sin(math.radians(180+30))],
                [max_value * math.cos(math.radians(30)), max_value * math.sin(math.radians(30))],
                [max_value * math.cos(math.radians(180+60)), max_value * math.sin(math.radians(180+60))],
                [max_value * math.cos(math.radians(60)), max_value * math.sin(math.radians(60))],
                [0, -max_value],
                [0, max_value],
                [max_value * math.cos(math.radians(180 + 120)), max_value * math.sin(math.radians(180 + 120))],
                [max_value * math.cos(math.radians(120)), max_value * math.sin(math.radians(120))],
                [max_value * math.cos(math.radians(180 + 150)), max_value * math.sin(math.radians(180 + 150))],
                [max_value * math.cos(math.radians(150)), max_value * math.sin(math.radians(150))],
            ])
            lidar_axis_adj = np.array([[0, 1],[2, 3],[4, 5],[6, 7],[8, 9],[10, 11]])
            # symbols = ['o', 't2', 'o', 't']  # ['o', 's', 't', 't1', 't2', 't3','d', '+', 'x', 'p', 'h', 'star']
            self.polar_plt_axis.setData(pos=lidar_axis_data,size=0.5,adj=lidar_axis_adj)#, symbol=symbols, pxMode=False
            for i in range(int(lidar_axis_data.size/2)):
                polar_y_label=pg.TextItem()
                polar_y_label.setColor("b")
                self.lidar_polar.addItem(polar_y_label)
                polar_y_label.setText("%s°" % (int(i/2) * 30 + (i+1)%2*180))  # Y轴
                polar_y_label.setPos(lidar_axis_data[i][0]*1.1-1.2,lidar_axis_data[i][1]*1.1+0.5)

            polar_plt2_axis = pg.GraphItem()
            self.lidar_polar.addItem(polar_plt2_axis)
            lidar_axis2_data = np.zeros(((max_value)*4, 2))
            tmp=-max_value
            for i in range(max_value*2-1):
                tmp += 1
                lidar_axis2_data[i][1]=tmp
                lidar_axis2_data[i+max_value*2-1][0] = tmp

            polar_plt2_axis.setData(pos=lidar_axis2_data,size=3)#,size=1, symbol=symbols, pxMode=False
            for i in range(max_value):#刻度
                if i*2-max_value == 0:
                    continue
                polar_y_label = pg.TextItem()
                polar_y_label.setColor("b")
                self.lidar_polar.addItem(polar_y_label)
                polar_y_label.setText("%d"%((i*2-max_value)))
                polar_y_label.setPos((i*2-max_value)-0.1, 0)

                polar_y_label = pg.TextItem()
                polar_y_label.setColor("b")
                self.lidar_polar.addItem(polar_y_label)
                polar_y_label.setText("%d"%((i*2-max_value)))
                polar_y_label.setPos(0,(i*2-max_value)+0.1)
            # self.lidar_polar.proxy = pg.SignalProxy(self.lidar_polar.scene().sigMouseMoved, rateLimit=15, slot=self.mouseMoved_lidar_polar)  # 60
            # self.polar_piont_label = pg.TextItem()
            self.polar_plt.scatter.sigClicked.connect(self.lidar_polar_clicked)
            # v.enableAutoRange(x=False, y=False)
            # v.enableAutoRange('xy', False)
            self.set_lidar_polar_round()#画圆
                    # self.lidar_polar.removeItem(polar_lidar_round)
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def set_lidar_polar_round(self):
        try:
            # if robot_type=="Cruzr1S":
            max_value = 25
            # else:
            #     max_value = 16
            self.polar_lidar_round.clear()

            lidar_round_adj = np.zeros((360, 2), dtype=np.int32)
            angle_list = np.arange(0, 360, 1)  # dtype=np.int)#dtype=[('x', 'i4'), ('y', 'i4')
            for j in range(max_value+1):
                if self.comboBox_3.currentText() == "无" and j<max_value:
                    continue
                if j%5!=0 and j<max_value:
                    continue
                lidar_data = np.zeros((360, 2))#放外层的话只有最后一个圈线连接有效
                for i in range(360):
                    lidar_data[i][0] = j * math.cos(math.radians(angle_list[i]))
                    lidar_data[i][1] = j * math.sin(math.radians(angle_list[i]))
                    if self.comboBox_3.currentText()=="虚线" or j<max_value:#and j<max_value
                        if i%2 == 0:
                            continue
                    lidar_round_adj[i][0] = i
                    if i < 359:
                        lidar_round_adj[i][1] = i + 1
                    else:
                        lidar_round_adj[i][1] = 0
                self.polar_lidar_round.append(pg.GraphItem())
                self.lidar_polar.addItem(self.polar_lidar_round[-1])
                self.polar_lidar_round[-1].setData(pos=lidar_data, size=0.1, adj=lidar_round_adj)
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def lidar_polar_round_select(self):
        try:
            for i in self.polar_lidar_round:
                self.lidar_polar.removeItem(i)
            self.set_lidar_polar_round()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def lidar_polar_clicked(self,pts):
        '''鼠标左键点击点触发事件'''
        # print("clicked: %s" % pts)
        try:
            pos=pts.ptsClicked[0]._data
            r=math.sqrt(math.pow(pos[0],2)+math.pow(pos[1],2))
            angle=math.degrees(math.atan2(pos[1],pos[0]))
            # print(str(r),str(angle))
            if angle<0:
                angle+=360
            self.label_103.setText(str(round(r,5)))
            self.label_105.setText(str(round(angle,5)))
            self.tmp_angle_avg_data=0
        except Exception as e:
            LOGGER.exception("Exception Logged")
        # for p in pts:
        #     p.setPen('b', width=2)
        # self.polar_piont_label.setText("长度，角度：%d，%d" %(r,angle))
        # self.plt_label.setPos(mousePoint.x(), y_axis_label)
    def display_polar(self,msg):
        try:
            # msg=[10 for i in range(1440)]#test
            if msg:
                if self.lidar_polar.state['autoRange'][0] is True:
                    self.lidar_polar.enableAutoRange('xy', False)
                lenth = len(msg)
                # if robot_type=="Cruzr1S":#self.comboBox_2.currentText()
                if lidar_radius_angle[1]-lidar_radius_angle[0]==360:
                    tmp_angle = 360
                    angle_radio = tmp_angle / lenth
                    angle_list = np.arange(0, tmp_angle, angle_radio)
                else:
                    tmp_angle= lidar_radius_angle[1]-lidar_radius_angle[0]
                    angle_radio = tmp_angle / lenth
                    angle_list = np.arange(lidar_radius_angle[0], lidar_radius_angle[1], angle_radio)
                # else:
                #     tmp_angle=170
                #     angle_radio = tmp_angle / lenth
                #     angle_list = np.arange(5, tmp_angle+5, angle_radio)
                # tmp_angle= lidar_radius_angle[1]-lidar_radius_angle[0]
                # angle_radio = tmp_angle / lenth
                # angle_list = np.arange(lidar_radius_angle[0], lidar_radius_angle[1], angle_radio)
                lidar_data=np.zeros((lenth, 2))
                for i in range(lenth):
                    # angle_list.append(i*angle_radio)
                    # if msg[i]and msg[i]>25.0:
                    #     pass
                    if msg[i] and math.isinf(msg[i]) == False:
                        x=msg[i]*math.cos(math.radians(angle_list[i]))
                        y=msg[i]*math.sin(math.radians(angle_list[i]))
                    else:
                        x=0
                        y=0

                    lidar_data[i][0] = -x if lidar_radius_angle[1] - lidar_radius_angle[0] == 360 else x
                    lidar_data[i][1] = y
                    # if  msg[i]==None:
                    #     msg[i]=0
                    # if lidar_data[i][0]>25 or lidar_data[i][0]<-25:
                    #     LOGGER.debug("i angle msg x y:%2d,%2d,%2d,%2d,%2d"%(i,angle_list[i],msg[i],lidar_data[i][0],lidar_data[i][1]))
                self.polar_plt.setData(symbolPen="r",pos=lidar_data,size=2.5)  # , size=1, symbol=symbols, pxMode=False
                if self.label_105.text()!='':
                    if lidar_radius_angle[1] - lidar_radius_angle[0] == 360:
                        tmp=msg[int(((180 - float(self.label_105.text())) % 360) / 360 * len(lidar_radius_data)+0.5)]
                        if tmp!=None and math.isinf(tmp) == False:
                            self.tmp_angle_avg_data= tmp if self.tmp_angle_avg_data==0 else (self.tmp_angle_avg_data+tmp)/2
                            self.label_103.setText(str(round(tmp,5))+'#'+str(round(self.tmp_angle_avg_data_bak,5)))
                    else:
                        tmp=msg[int(((45+ float(self.label_105.text())) % 360) / 270 * len(lidar_radius_data)+0.5)]
                        if tmp != None and math.isinf(tmp) == False:
                            self.tmp_angle_avg_data = tmp if self.tmp_angle_avg_data == 0 else (self.tmp_angle_avg_data + tmp) / 2
                            self.label_103.setText(str(round(tmp,5))+'#'+str(round(self.tmp_angle_avg_data_bak,5)))
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def lidar_error_test(self):
        try:
            if self.pushButton_25.text() == '开始':
                global lidar_test_para
                lidar_test_para['time']=int(self.lineEdit_100.text())
                lidar_test_para['dis'] = float(self.lineEdit_10.text())
                lidar_test_para['sa'] = int(self.lineEdit_102.text())
                lidar_test_para['ea'] = int(self.lineEdit_101.text())
                self.timer_lidar_test.start(lidar_test_para['time']*60000)
                global lidar_sun,lidar_err
                lidar_sun=0
                lidar_err=0
                self.pushButton_25.setText('取消')
            else:
                self.pushButton_25.setText('开始')
                if self.timer_lidar_test.isActive():
                    self.timer_lidar_test.stop()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def lidar_test_timeout(self):
        try:
            self.pushButton_25.setText('开始')
            self.timer_lidar_test.stop()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def lidar_error_count(self,dat):
        global lidar_sun,lidar_err
        try:
            data_len=len(dat)
            for i in dat:
                if i!=None and math.isinf(i) == False  and i < lidar_test_para['dis']: #:isinstance(lst, (int, str, list))
                    lidar_err+=1
            lidar_sun+=data_len
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def comboBox_robot_type_select(self):
        global robot_type
        try:
            robot_type=self.comboBox_2.currentText()
            if robot_type == "Cruzr1":
                if self.tabWidget_all.currentIndex() < 3:
                    self.tabWidget_all.setCurrentIndex(3)
                # self.tabWidget_all.setTabEnabled(0, False)
                # self.tabWidget_all.setTabEnabled(2, False)
                # if self.pushButton_open_close.text() != "查看传感器":
                #     self.open_close_ros()
                # self.pushButton_open_close.setDisabled(True)
                if self.lineEdit_52.text() == "192.168.11.123":
                    str_ip = "192.168.100.10"  # "192.168.11.123"
                    self.lineEdit_52.setText(str_ip)
            else:
                self.tabWidget_all.setTabEnabled(0, True)
                # self.tabWidget_all.setTabEnabled(2, True)
                # self.pushButton_open_close.setDisabled(False)
                if self.lineEdit_52.text() == "192.168.100.10":
                    str_ip = "192.168.11.123"
                    self.lineEdit_52.setText(str_ip)
        except Exception as e:
            LOGGER.exception("Exception Logged")
        # self.robot_type_init()
    def auto_detect_robot_type(self):
        # if (self.client and self.client.is_connected) and self.tabWidget_all.currentIndex()!=2 and self.checkBox_21.checkState():
    #         #     self.ros_topic_init("table2")
        pass
    def clear_senser_buffer_data(self):
        self.label_44.setText("")
        self.label_46.setText("")
    def clear_edit_data_display(self):
        try:
            global sensor_data_min_max_value,sensor_data
            for i in range(len(self.sensor_lineedit_index)):
                self.sensor_lineedit_index[i].setText('0')
            last_idx=sum(sensor_index[0:self.toolBox.currentIndex()+1])
            tmp_sum=sum(sensor_index)
            sensor_data_min_max_value[last_idx-sensor_index[self.toolBox.currentIndex()]:last_idx]=[5000 for _ in range(sensor_index[self.toolBox.currentIndex()])]
            sensor_data_min_max_value[last_idx - sensor_index[self.toolBox.currentIndex()]+tmp_sum:last_idx+tmp_sum] = [-5000 for _ in range(sensor_index[self.toolBox.currentIndex()])]
            self.pointcnt_frequency[self.toolBox.currentIndex()][0] = 0
            sensor_data = [[] for _ in range(sum(sensor_index))]
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def picture_label_data_display(self):
        try:
            for i in range(sum(sensor_index)):
                if len(sensor_data[i])>0:
                    self.sensor_lable_index[i].setText(str(sensor_data[i][-1]))
        except Exception as e:
          LOGGER.exception("Exception Logged")
    def point_data_display(self,index):
        try:
            if self.tabWidget_all.currentIndex() == 0:
                self.label_44.setText(str(self.pointcnt_frequency[self.toolBox.currentIndex()][0]))
                tmp = 0 if self.toolBox.currentIndex()==0 else sum(sensor_index[:self.toolBox.currentIndex()])#reduce(lambda x, y: x+y,sensor_index[:self.toolBox.currentIndex()+1])
                tmp_idx=sum(sensor_index)
                if len(sensor_data[tmp])==0:
                    return None
                global sensor_data_min_max_value
                for i in range(8):
                    if i<sensor_index[self.toolBox.currentIndex()]:
                        self.sensor_lineedit_index[i*3].setText(str(sensor_data[tmp+i][-1]))
                        if sensor_data[tmp+i][-1]>sensor_data_min_max_value[tmp_idx+i+tmp]:
                            self.sensor_lineedit_index[i*3+1].setText(str(sensor_data[tmp+i][-1]))
                            sensor_data_min_max_value[tmp_idx + i+tmp]=sensor_data[tmp+i][-1]
                        if sensor_data[tmp+i][-1]<sensor_data_min_max_value[i+tmp]:
                            self.sensor_lineedit_index[i * 3 + 2].setText(str( sensor_data[tmp + i][-1]))
                            sensor_data_min_max_value[i+tmp]=sensor_data[tmp+i][-1]
                    else:
                        self.sensor_lineedit_index[i*3].setText('预留')
                        self.sensor_lineedit_index[i * 3 + 1].setText('预留')
                        self.sensor_lineedit_index[i * 3 + 2].setText('预留')
            # elif self.tabWidget_all.currentIndex() == 1:
            #     self.label_63.setText(str(self.pointcnt_frequency[6][0]))
            #     self.lineEdit_89.setText(str(battery_data[0]))
            #     self.lineEdit_90.setText(str(battery_data[1]))
            #     self.lineEdit_91.setText(str(battery_data[2]))
            elif self.tabWidget_all.currentIndex() == 2:
                self.label_19.setText(str(self.pointcnt_frequency[5][0]))
        except Exception as e:
          LOGGER.exception("Exception Logged")
    def set_validate_ip_password(self,ip_str,password):
        def check_validate_ip(ip_str):
            try:
                sep = ip_str.split('.')
                if len(sep) != 4:
                    return False
                for i, x in enumerate(sep):
                    try:
                        int_x = int(x)
                        if int_x < 0 or int_x > 255:
                            return False
                    except ValueError:
                        return False
                return True
            except Exception as e:
                LOGGER.exception("Exception Logged")
        global  str_ip
        try:
            if check_validate_ip(ip_str):
                str_ip = self.lineEdit_52.text()
                if password.replace(" ","") == "":
                    QMessageBox.critical(self, 'error', '请输入ros密码')
                    return False
                return True
            else:
                QMessageBox.critical(self, 'error', '请输入合法IP')
                return False
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def mouseMoved(self,evt):
        try:
            pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            if evt is None:
                LOGGER.warning("事件为空")
            else:
                if self.plt.sceneBoundingRect().contains(pos):
                    mousePoint = self.vb.mapSceneToView(pos)
                    try:
                        index = int(mousePoint.x())
                    except:
                        index=0
                    # print("mount enter", index,mousePoint.x(),mousePoint.y())
                    cnt=0
                    self.plt_label.setText("采样点：%d" % (index))
                    y_axis_label=mousePoint.y()
                    display_label_gap=(self.plt.viewRange()[1][1]-self.plt.viewRange()[1][0])/25
                    # print("y_axis:",mousePoint.y(),self.plt.viewRange()[1],display_label_gap)
                    if index > 0 :    #len(self.
                        #setHtml style='color:white
                        start_idx = 0 if self.toolBox.currentIndex() == 0 else sum(sensor_index[0:self.toolBox.currentIndex()])
                        if index < len(sensor_data[start_idx]):
                            for i in range(8):
                                if i < sensor_index[self.toolBox.currentIndex()]:
                                    if self.sensor_checkbox_index[i].checkState():
                                        self.plt_label_data[i].setText("%s%d：%d"%(sensor_name[self.toolBox.currentIndex()],i+1,sensor_data[start_idx+i][index]))
                                        cnt += 1
                                        self.plt_label_data[i].setPos(mousePoint.x(), y_axis_label - display_label_gap*cnt)
                                    else:
                                        self.plt_label_data[i].setText("")
                                else:
                                    pass
                        else:
                            for i in range(8):
                                self.plt_label_data[i].setText("")
                            # print("ssssf",widgetRect.x(),widgetRect.y())
                    else:
                        for i in range(8):
                            self.plt_label_data[i].setText("")
                    self.plt_label.setPos(mousePoint.x(),y_axis_label)
                    self.vLine.setPos(mousePoint.x())
                    self.hLine.setPos(mousePoint.y())
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def tabWidget_all_change_deal(self):
        try:
            if (thread_class_scall.ros_client and thread_class_scall.ros_client.is_connected):
                self.unsubscribe_topic("all")  # table2
                if self.tabWidget_all.currentIndex()==0:
                    self.ros_topic_init("table0")
                elif self.tabWidget_all.currentIndex()==1:
                    # self.unsubscribe_topic("all")#table0
                    self.ros_topic_init("table1")
                elif self.tabWidget_all.currentIndex()==2:
                    # self.unsubscribe_topic("all")#table0
                    self.ros_topic_init("table2")
                # elif self.tabWidget_all.currentIndex()==3:
                #     self.unsubscribe_topic("all")#table0
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def toolBox_change_deal(self):
        try:
            self.clear_check_toolBox()
            for i in range(8):
                if i < sensor_index[self.toolBox.currentIndex()]:
                    self.sensor_lable_value_name[i].setText(sensor_name[self.toolBox.currentIndex()]+str(i+1))
                    self.sensor_checkbox_index[i].setText(sensor_name[self.toolBox.currentIndex()].replace("头部",'')+str(i+1))
                else:
                    self.sensor_lable_value_name[i].setText('预留')
                    self.sensor_checkbox_index[i].setText("预留")
            self.groupBox_ult_data.setTitle(sensor_name[self.toolBox.currentIndex()])
            self.groupBox_ult_check.setTitle(sensor_name[self.toolBox.currentIndex()]+'选项卡')
            self.plt.setTitle("%s cm"%sensor_name[self.toolBox.currentIndex()])
            s_idx=0 if self.toolBox.currentIndex()==0 else sum(sensor_index[0:self.toolBox.currentIndex()])
            for i in range(8):
                if i<sensor_index[self.toolBox.currentIndex()]:
                    self.plt.legend.addItem(self.plt_disp_data[s_idx+i], "%s%d"%(sensor_name[self.toolBox.currentIndex()],i+1))

            if self.toolBox.currentIndex() == 0:
                self.plt.setYRange(0, 160)
                # self.ult_plot_flag = [True for i in range(ult_num)]
            elif self.toolBox.currentIndex() == 1:
                self.plt.setYRange(0, 150)

            elif self.toolBox.currentIndex() == 2:
                self.plt.setYRange(600, 1800)

            elif self.toolBox.currentIndex() == 3:
                self.plt.setTitle("回充红外（背对充电桩）")
                self.plt.setYRange(0, 100)

            elif self.toolBox.currentIndex() == 4:
                self.plt.setYRange(40, 70)

        except Exception as e:
            LOGGER.exception("Exception Logged")
    def clear_plot(self):
        try:
            for i in range(len(self.plt_disp_data)):
                self.plt_disp_data[i].clear()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def clear_check_toolBox(self):
        try:
            self.clear_plot()
            for i in range(8):
                self.plt_label_data[i].setText("")
                self.plt.legend.removeItem("超声波%d"%(i+1))
                if i < 6:
                    self.plt.legend.removeItem("墙检红外%d"%(i+1))
            # self.groupBox_ult_check.setVisible(False)
            # self.groupBox_ult_data.setVisible(False)
            # self.plt.legend.removeItem("超声波1")  # setParentItem
            # self.plt.legend.removeItem("墙检红外1")

            self.plt.legend.removeItem("头部TOF红外1")
            self.plt.legend.removeItem("回充红外1")
            self.plt.legend.removeItem("回充红外2")

            self.plt.legend.removeItem("地检红外1")
            self.clear_senser_buffer_data()
        except Exception as e:
            LOGGER.exception("Exception Logged")
        # self.label_44.setText("")
        # self.label_46.setText("")

    def general_timer_deal(self):#count_frequency
        def zip_all_log_file():  # 再次压缩打包3个文件
            try:
                roszip=down_flie_info[1].replace('.tar.gz','') + '(%s)' % self.lineEdit_105.text() + '.zip'
                with ZipFile(roszip, mode='a') as fp:
                    fp.write(down_flie_info[1], os.path.split(down_flie_info[1])[1])
                    self.plainTextEdit.appendPlainText('最后生成文件：%s'%roszip)
                    tmp_log = os.path.dirname(down_flie_info[1]) + '/tool_info.log'
                    with open(tmp_log, 'a', encoding='utf-8')as flog:
                        flog.write(self.plainTextEdit.toPlainText())
                    fp.write(tmp_log, os.path.split(tmp_log)[1])
                    tmp_bug = os.path.dirname(down_flie_info[1]) + '/bug_description.log'
                    with open(tmp_bug, 'a', encoding='utf-8')as flog:
                        flog.write(self.plainTextEdit_2.toPlainText())
                    fp.write(tmp_bug, os.path.split(tmp_bug)[1])
                    os.remove(down_flie_info[1])
                    os.remove(tmp_log)
                    os.remove(tmp_bug)
            except Exception as e:
                LOGGER.exception("Exception Logged")
        try:
            # print(str(self.pointcnt_frequency))
            if self.tabWidget_all.currentIndex() == 0:
                if self.toolBox.currentIndex() == 0:
                    self.label_46.setText(str(self.pointcnt_frequency[0][1]))
                    # print("frequency", self.pointcnt_frequency[0][1])
                    self.pointcnt_frequency[0][1]=0
                    # self.label_44.setText(str(self.pointcnt_frequency[0][0]))
                elif self.toolBox.currentIndex() == 1:
                    self.label_46.setText(str(self.pointcnt_frequency[1][1]))
                    self.pointcnt_frequency[1][1] = 0
                    # self.label_44.setText(str(self.pointcnt_frequency[1][0]))
                elif self.toolBox.currentIndex() == 2:
                    self.label_46.setText(str(self.pointcnt_frequency[2][1]))
                    self.pointcnt_frequency[2][1] = 0
                    # self.label_44.setText(str(self.pointcnt_frequency[2][0]))
                elif self.toolBox.currentIndex() == 3:
                    self.label_46.setText(str(self.pointcnt_frequency[3][1]))
                    self.pointcnt_frequency[3][1] = 0
                elif self.toolBox.currentIndex() == 4:
                    self.label_46.setText(str(self.pointcnt_frequency[4][1]))
                    self.pointcnt_frequency[4][1] = 0
                    # self.label_44.setText(str(self.pointcnt_frequency[3][0]))
                elif self.toolBox.currentIndex() == 10:
                    self.pointcnt_frequency[4][2] += 1
                    if self.pointcnt_frequency[4][2]>=5:
                        self.label_46.setText(str(self.pointcnt_frequency[4][1]/5))
                        self.pointcnt_frequency[4][1] = 0
                        self.pointcnt_frequency[4][2]=0
                    # self.label_44.setText(str(self.pointcnt_frequency[4][0]))
            elif self.tabWidget_all.currentIndex() == 2:
                self.label_20.setText(str(self.pointcnt_frequency[5][1]))
                self.pointcnt_frequency[5][1] = 0
                # self.label_19.setText(str(self.pointcnt_frequency[5][0]))
            elif self.tabWidget_all.currentIndex() == 1:
                self.label_64.setText(str(self.pointcnt_frequency[6][1]))
                self.pointcnt_frequency[6][1] = 0
                # self.label_63.setText(str(self.pointcnt_frequency[6][0]))
            global reconnect_cnt,reconnect_fail_cnt,reconnect_topic_cnt,reconnect_topic_cnt_bak  #重连检查
            if (thread_class_scall.ros_client and not thread_class_scall.ros_client.is_connected) and (self.pushButton_open_close.text() == "关闭连接"):
                if reconnect_cnt>=8:
                    LOGGER.debug("reconnect ros init!")
                    self.ros_topic_init("init")
                    reconnect_cnt=0
                    reconnect_fail_cnt+=1
                    if reconnect_fail_cnt>5:
                        reconnect_fail_cnt=0
                        thread_class_scall.call_uws_server_type = None
                        LOGGER.warning("reconnect_fail close!")
                        self.open_close_ros()
            elif reconnect_fail_cnt:
                reconnect_fail_cnt=0
            if reconnect_cnt<10:
                reconnect_cnt+=1
            if (thread_class_scall.ros_client and thread_class_scall.ros_client.is_connected) and (self.pushButton_open_close.text() == "关闭连接"):
                if self.tabWidget_all.currentIndex() <3:
                    if reconnect_topic_cnt==reconnect_topic_cnt_bak and reconnect_cnt>=7:
                        self.tabWidget_all_change_deal()
                        reconnect_cnt=0
                        LOGGER.debug("topic connect timeout")
                    reconnect_topic_cnt_bak=reconnect_topic_cnt

            global down_flie_info
            if  self.progressBar.isVisible() and self.progressBar.value()<100 and os.path.exists(down_flie_info[1]):
                tmp=None
                if down_flie_info[0]>0:
                    tmp=int(os.path.getsize(down_flie_info[1])/down_flie_info[0]*100)
                    self.progressBar.setValue(tmp)
                else:
                    tmp=100
                if tmp>99:
                    self.label_69.setVisible(False)
                    self.progressBar.setVisible(False)
                    self.pushButton_12.setText("下载")
                    self.pushButton_19.setEnabled(True)
                    self.plainTextEdit.appendPlainText(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + " 文件下载完成")
                    # zip_all_log_file()
                    QMessageBox.information(self, 'ok', '下载完成', QMessageBox.Yes)
            # if 0 and self.comboBox_2.currentText()!=robot_type:
            #     self.comboBox_2.setCurrentText(robot_type)
            if self.pushButton_25.text() != '开始':
                self.lineEdit_103.setText(str(lidar_err))
                self.lineEdit_104.setText(str(round(lidar_err / lidar_sun * 100, 2)) if lidar_sun else '0')
            QtWidgets.QApplication.processEvents()
            # LOGGER.debug("1s:%d"%reconnect_cnt)
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def display_plot(self):
        try:
            global lidar_radius_data
            if self.tabWidget_all.currentIndex()==0:
                if  (self.pushButton_11.text() == "暂停显示曲线"):
                    self.clear_plot()
                # for i in d.keys():
                if (self.pushButton_11.text() == "暂停显示曲线"):
                    start_idx=0 if self.toolBox.currentIndex()==0 else sum(sensor_index[0:self.toolBox.currentIndex()])
                    for i in range(8):
                        if self.sensor_checkbox_index[i].checkState() and i < sensor_index[self.toolBox.currentIndex()]:
                            self.plt_disp_data[i].setData(sensor_data[start_idx+i])
                            # self.plt_label_data[i].update()
            if self.tabWidget_all.currentIndex() == 2:
                # if (self.pushButton_18.text() == "暂停显示曲线"):
                self.display_polar(lidar_radius_data)
        except Exception as e:
          LOGGER.exception("Exception Logged")
    def start_pause_display(self):
        try:
            if self.tabWidget_all.currentIndex() == 0:
                if (self.pushButton_11.text() == "暂停显示曲线"):
                    self.pushButton_11.setText("开启显示曲线")
                else:
                    self.pushButton_11.setText("暂停显示曲线")
            elif self.tabWidget_all.currentIndex() == 2:
                if (self.pushButton_18.text() == "暂停显示曲线"):
                    self.pushButton_18.setText("开启显示曲线")
                else:
                    self.pushButton_18.setText("暂停显示曲线")
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def button_plot_check_select(self):
        try:
            if self.toolBox.currentIndex() == 0:
            # self.ult_plot_flag = [False for i in range(ult_num)]
                if self.sender().text() == "全选":
                    self.checkBox.setChecked(True)
                    self.checkBox_2.setChecked(True)
                    self.checkBox_3.setChecked(True)
                    self.checkBox_4.setChecked(True)
                    self.checkBox_5.setChecked(True)
                    self.checkBox_6.setChecked(True)
                    self.checkBox_7.setChecked(True)
                    self.checkBox_8.setChecked(True)
                elif self.sender().text() == "全不选":
                    self.checkBox.setChecked(False)
                    self.checkBox_2.setChecked(False)
                    self.checkBox_3.setChecked(False)
                    self.checkBox_4.setChecked(False)
                    self.checkBox_5.setChecked(False)
                    self.checkBox_6.setChecked(False)
                    self.checkBox_7.setChecked(False)
                    self.checkBox_8.setChecked(False)
                elif self.sender().text() == "反选":
                    self.checkBox.setChecked(not self.checkBox.checkState())
                    self.checkBox_2.setChecked(not self.checkBox_2.checkState())
                    self.checkBox_3.setChecked(not self.checkBox_3.checkState())
                    self.checkBox_4.setChecked(not self.checkBox_4.checkState())
                    self.checkBox_5.setChecked(not self.checkBox_5.checkState())
                    self.checkBox_6.setChecked(not self.checkBox_6.checkState())
                    self.checkBox_7.setChecked(not self.checkBox_7.checkState())
                    self.checkBox_8.setChecked(not self.checkBox_8.checkState())
            elif self.toolBox.currentIndex() == 1:
                if self.sender().text() == "全选":
                    self.checkBox_9.setChecked(True)
                    self.checkBox_10.setChecked(True)
                    self.checkBox_11.setChecked(True)
                    self.checkBox_12.setChecked(True)
                    self.checkBox_13.setChecked(True)
                    self.checkBox_14.setChecked(True)
                elif self.sender().text() == "全不选":
                    self.checkBox_9.setChecked(False)
                    self.checkBox_10.setChecked(False)
                    self.checkBox_11.setChecked(False)
                    self.checkBox_12.setChecked(False)
                    self.checkBox_13.setChecked(False)
                    self.checkBox_14.setChecked(False)
                elif self.sender().text() == "反选":
                    self.checkBox_9.setChecked(not self.checkBox_9.checkState())
                    self.checkBox_10.setChecked(not self.checkBox_10.checkState())
                    self.checkBox_11.setChecked(not self.checkBox_11.checkState())
                    self.checkBox_12.setChecked(not self.checkBox_12.checkState())
                    self.checkBox_13.setChecked(not self.checkBox_13.checkState())
                    self.checkBox_14.setChecked(not self.checkBox_14.checkState())
            elif self.toolBox.currentIndex() == 10:
                if self.sender().text() == "全选":
                    self.checkBox_17.setChecked(True)
                    self.checkBox_16.setChecked(True)
                    self.checkBox_18.setChecked(True)
                elif self.sender().text() == "全不选":
                    self.checkBox_17.setChecked(False)
                    self.checkBox_16.setChecked(False)
                    self.checkBox_18.setChecked(False)
                elif self.sender().text() == "反选":
                    self.checkBox_17.setChecked(not self.checkBox_17.checkState())
                    self.checkBox_16.setChecked(not self.checkBox_16.checkState())
                    self.checkBox_18.setChecked(not self.checkBox_18.checkState())
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def ssh_thread_ros_callback(self, data):
        try:
            if data:
                if data[0] == 100:  # map
                    LOGGER.info("Tros_ok:%s"%data[1])
                    self.pushButton_open_close.setText("关闭连接")
                    self.timer1.start(100)
                    self.auto_detect_robot_type()
                elif data[0] == 101:
                    LOGGER.info("Tros_init:%s"%data[1])
                    self.ros_topic_init("init")
                elif data[0] == 102:
                    LOGGER.info("Tros_close:%s"%data[1])
                    thread_class_scall.ros_client.is_connected=False
                elif data[0] < 0:#== -100
                    if data[0] == -100 and thread_class_scall.call_uws_server_type == False:
                        if 'Cruzr1' == self.comboBox_2.currentText():
                            self.pushButton_open_close.setText("查看传感器")
                            thread_class_scall.call_uws_server_type=None
                            QMessageBox.information(self, '警告', '通信连接超时，检查是否同个局域网连接/ROS版本是否支持！')
                        else:
                            self.display_password_ui(data[2])
                    else:
                        LOGGER.info("Tros_fail:%s"%data[1])
                        QMessageBox.critical(self, 'error', data[1])
                        if (self.pushButton_open_close.text() != "查看传感器"):
                            self.open_close_ros()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def ros_topic_init(self,mode):
        def set_last_data1(data,message,key):
            try:
                if len(data) < NUM_POINT:
                    try:
                        data.append(message[key])#.get
                    except Exception as e:
                        try:
                            data.append(message[key])#data.append(error_data)#error_data
                        except Exception as e:
                            time.sleep(0.001)
                            data.append(message[key])#data.append(error_data)
                else:
                    data[:-1] = data[1:]
                    try:
                        data[-1] = message[key]
                    except:
                        time.sleep(0.001)
                        data[-1] = message[key]#data[-1] = error_data
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_data_copy(type, message):
            global robot_type,sensor_data
            try:
                if type == 0:
                    set_last_data1(sensor_data[0], message, "distance1")
                    set_last_data1(sensor_data[1], message, "distance2")
                    set_last_data1(sensor_data[2], message, "distance3")
                    set_last_data1(sensor_data[3], message, "distance4")
                    set_last_data1(sensor_data[4], message, "distance5")
                    if 'waist_distance1' in message.keys():
                        # set_last_data1(ult6_data, message, "distance6")
                        set_last_data1(sensor_data[5], message,"waist_distance1")
                        set_last_data1(sensor_data[6], message, "waist_distance2")
                        set_last_data1(sensor_data[7], message, "waist_distance3")
                    else:
                        set_last_data1(sensor_data[5], message, "distance6")
                        sensor_data[6].append(0xff)
                        sensor_data[7].append(0xff)
                    # print("len:",len(ult1_data),len(ult1_data),len(ult2_data),len(ult3_data),len(ult4_data),len(ult5_data),len(ult6_data),len(ult7_data),len(ult8_data))
                elif type == 1:
                    if 1:#robot_type == 'Cruzr1S':
                        for i in range(6):
                            set_last_data1(sensor_data[sum(sensor_index[0:type])+i], message, "dist%d"%(i+1))
                elif type == 2:
                    set_last_data1(sensor_data[sum(sensor_index[0:type])], message, "data")#"cliff2"
                elif type == 3:
                    set_last_data1(sensor_data[sum(sensor_index[0:type])+0], message, "data3")
                    set_last_data1(sensor_data[sum(sensor_index[0:type])+1], message, "data2")
                # elif type == 6:
                #     global battery_data
                #     battery_data[0]=str(message["voltage"])
                #     battery_data[1] = str(message["battery_level"])
                #     battery_data[2] = str(message["temperature"])
                elif type == 4:
                    set_last_data1(sensor_data[sum(sensor_index[0:type])], message, "cliff2")  # "cliff2"
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def start_listening(mode):
            try:
                if self.tabWidget_all.currentIndex() == 0:#if mode == "init" or mode == "table0":
                    self.listener_untrasonic.subscribe(receive_message_untrasonic)
                    self.listener_sensor_tof_ir.subscribe(receive_message_sensor_tof_ir)
                    self.listener_wall_check_ir.subscribe(receive_message_wall_check_ir)
                    self.listener_charge_ir.subscribe(receive_message_charge_ir)
                    # self.listener_geomagnetism.subscribe(receive_message_geomagnetism)
                    self.listener_floor_ir.subscribe(receive_message_floor_ir)
                    # self.listener_battery.subscribe(receive_message_battery)
                elif self.tabWidget_all.currentIndex()==2:
                    self.listener_lidar.subscribe(receive_message_lidar)
                elif self.tabWidget_all.currentIndex() == 1:
                    # self.listener_battery.subscribe(receive_message_battery)
                    pass
                else:#test
                    pass# self.listener_charge_ir.subscribe(receive_message_charge_ir)
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_untrasonic(message):
            # print('receive_message_untrasonic: ' + str(message))
            try:
                global reconnect_topic_cnt
                reconnect_topic_cnt+=1
                if self.pushButton_11.text() == "暂停显示曲线"and(self.pushButton_open_close.text() == "关闭连接"):
                    receive_data_copy(0,message)
                    if self.toolBox.currentIndex() == 0:
                        self.point_data_display(0)#ult1_data
                        for i in range(2):
                            self.pointcnt_frequency[0][i] += 1
                    # self.label_44.setText(str(self.pointcnt_frequency[0][0]))
                # self.display_plot()
                # if self.checkBox_15.checkState():
                #     self.run_check_file_size(senser_file_path_name[0],0)
                #     self.senser_file[0].write(json.dumps(message)+"\n")
                    self.picture_label_data_display()
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_sensor_tof_ir(message):
            # print('receive_message_sensor_tof_ir: ' + str(message))
            try:
                if self.pushButton_11.text() == "暂停显示曲线"and(self.pushButton_open_close.text() == "关闭连接"):
                    receive_data_copy(2, message)
                    # self.display_plot()
                    if self.toolBox.currentIndex() == 2:
                        self.point_data_display(0)
                        for i in range(2):
                            self.pointcnt_frequency[2][i] += 1
                        # self.label_44.setText(str(self.pointcnt_frequency[2][0]))
                    # if self.checkBox_15.checkState():
                    #     self.run_check_file_size(senser_file_path_name[2], 2)
                    #     self.senser_file[2].write(json.dumps(message) + "\n")
                    self.picture_label_data_display()
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_wall_check_ir(message):
            # print('receive_message_wall_check_ir: ' + str(message))
            try:
                if self.pushButton_11.text() == "暂停显示曲线"and(self.pushButton_open_close.text() == "关闭连接"):
                    receive_data_copy(1,message)
                    if self.toolBox.currentIndex() == 1:
                        self.point_data_display(0)
                        for i in range(2):
                            self.pointcnt_frequency[1][i] += 1
                        # self.label_44.setText(str(self.pointcnt_frequency[1][0]))
                    # self.display_plot()
                    # if self.checkBox_15.checkState():
                    #     self.run_check_file_size(senser_file_path_name[1], 1)
                    #     self.senser_file[1].write(json.dumps(message) + "\n")
                    self.picture_label_data_display()
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_charge_ir(message):
            # print('receive_message_charge_ir: ' + str(message))
            try:
                if self.pushButton_11.text() == "暂停显示曲线"and(self.pushButton_open_close.text() == "关闭连接"):
                    receive_data_copy(3,message)
                    # self.display_plot()
                    if self.toolBox.currentIndex() == 3:
                        self.point_data_display(0)
                        for i in range(2):
                            self.pointcnt_frequency[3][i] += 1
                        # self.label_44.setText(str(self.pointcnt_frequency[3][0]))
                    # if self.checkBox_15.checkState():
                    #     self.run_check_file_size(senser_file_path_name[3], 3)
                    #     self.senser_file[3].write(json.dumps(message) + "\n")
                    self.picture_label_data_display()
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_geomagnetism(message):
            # print('receive_message_geomagnetism: ' + str(message))
            try:
                receive_data_copy(4,message)
                # self.display_plot()
                # if self.toolBox.currentIndex() == 10:
                #     self.point_data_display(len(geomagnetism_yaw_data))
                #     for i in range(2):
                #         self.pointcnt_frequency[4][i] += 1
                    # self.label_44.setText(str(self.pointcnt_frequency[4][0]))
                # if self.checkBox_15.checkState() and self.senser_file[5]:
                #     self.run_check_file_size(senser_file_path_name[5], 5)
                #     self.senser_file[5].write(json.dumps(message["ranges"]) + "\n")
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_battery(message):
            try:
                receive_data_copy(6,message)# print('receive_message_battery: ' + str(message))
                for i in range(2):
                    self.pointcnt_frequency[6][i] += 1
                self.point_data_display(0)
            except Exception as e:
                LOGGER.exception("Exception Logged")
            # self.lineEdit_89.setText(str(message["voltage"]))
            # self.lineEdit_90.setText(str(message["battery_level"]))
            # self.lineEdit_91.setText(str(message["temperature"]))
        def receive_message_lidar(message):
            # print('receive_message_lidar: ' + str(message))
            try:
                global reconnect_topic_cnt
                reconnect_topic_cnt+=1
                if self.tabWidget_all.currentIndex()!=2:
                    self.listener_lidar.unsubscribe()
                if (self.pushButton_18.text() == "暂停显示曲线") and (self.pushButton_open_close.text() == "关闭连接"):
                    for i in range(2):
                        self.pointcnt_frequency[5][i] += 1
                    # self.label_19.setText(str(self.pointcnt_frequency[5][0]))
                    global lidar_radius_data,lidar_radius_angle
                    lidar_radius_data = []
                    lidar_radius_data= message["ranges"] #intensities

                    lidar_radius_angle[0] = round(message['angle_min']/math.pi*180+90)
                    lidar_radius_angle[1] = round(message['angle_max']/math.pi*180+90)
                    # print(str(len(lidar_radius_data)) + str(lidar_radius_angle) + str(lidar_radius_data))
                    if self.pushButton_25.text() != '开始':
                        if lidar_radius_angle[1]-lidar_radius_angle[0]==360:
                            sa = int(((180 - lidar_test_para['sa']) % 360) / 360 * len(lidar_radius_data))#180顺时针
                            ea = int(((180 - lidar_test_para['ea']) % 360) / 360 * len(lidar_radius_data))
                            if sa == ea:
                                ea-=1
                            if sa > ea:
                                self.lidar_error_count(lidar_radius_data[ea:sa])
                            else:
                                self.lidar_error_count(lidar_radius_data[ea:] + lidar_radius_data[:sa])
                        else:#sick
                            sa = int(((45+ lidar_test_para['sa']) % 360) / 270 * len(lidar_radius_data))  # 180顺时针
                            ea = int(((45+ lidar_test_para['ea']) % 360) / 270 * len(lidar_radius_data))
                            if sa == ea:
                                ea += 1
                            if sa <= ea:
                                self.lidar_error_count(lidar_radius_data[sa:ea])
                            else:
                                self.lidar_error_count(lidar_radius_data[sa:] + lidar_radius_data[:ea])
                    self.point_data_display(0)

                    # self.display_polar(message["intensities"])
                    # if self.checkBox_19.checkState():
                    #     self.run_check_file_size(senser_file_path_name[5], 5)
                    #     self.senser_file[5].write(json.dumps(message) + "\n")
            except Exception as e:
                LOGGER.exception("Exception Logged")
        def receive_message_floor_ir(message):
            # print('receive_message_charge_ir: ' + str(message))
            try:
                if self.pushButton_11.text() == "暂停显示曲线":
                    receive_data_copy(4,message)
                    # self.display_plot()
                    if self.toolBox.currentIndex() == 4:
                        self.point_data_display(0)
                        for i in range(2):
                            self.pointcnt_frequency[4][i] += 1
                        # self.label_44.setText(str(self.pointcnt_frequency[3][0]))
                    # if self.checkBox_15.checkState():
                    #     self.run_check_file_size(senser_file_path_name[3], 3)
                    #     self.senser_file[3].write(json.dumps(message) + "\n")
                    self.picture_label_data_display()
            except Exception as e:
                LOGGER.exception("Exception Logged")
        try:
            if mode == "init" or (thread_class_scall.ros_client and not thread_class_scall.ros_client.is_connected):
                if thread_class_scall.ros_client:
                    thread_class_scall.ros_client.close()
                LOGGER.info("ros_topic_init")
                if thread_class_scall.call_uws_server_type == False:
                    thread_class_scall.ros_client = Ros(host=str_ip, port=9090)
                else:
                    thread_class_scall.ros_client = Ros(host=str_ip, port=3011)  #9090 p_dt["ip_addr"] 改实际ip'localhost' '192.168.11.123'  '10.10.63.209'
                # client.run()cruiser_msgs/cruiserSensorAltrasonic
                self.listener_untrasonic = Topic(thread_class_scall.ros_client, '/sensor_untrasonic', 'cruiser_msgs/cruiserSensorAltrasonic',throttle_rate=100,queue_size=1)
                self.listener_sensor_tof_ir = Topic(thread_class_scall.ros_client, '/sensor_tof_ir', 'std_msgs/Int32',throttle_rate=100,queue_size=1)#
                self.listener_wall_check_ir = Topic(thread_class_scall.ros_client, '/sensor_wall_check_ir', 'cruiser_msgs/cruiserSensorWallCheckIr',throttle_rate=100,queue_size=1)
                self.listener_charge_ir = Topic(thread_class_scall.ros_client, '/sensor_charge_ir', 'cruiser_msgs/cruiserSensorChargeIr',throttle_rate=100,queue_size=1)
                # self.listener_geomagnetism = Topic(thread_class_scall.ros_client, '/sensor/geomagnetism', 'cruiser_msgs/geomagnetism')
                # self.listener_battery = Topic(thread_class_scall.ros_client, '/battery_info', 'cruiser_msgs/cruiserBatteryInfo')
                self.listener_lidar = Topic(thread_class_scall.ros_client, lidar_filter, 'sensor_msgs/LaserScan',queue_size=1)#scan_filtered
                self.listener_floor_ir = Topic(thread_class_scall.ros_client, '/sensor_floor_check_ir', 'cruiser_msgs/cruiserSensorFloorCheckIr',throttle_rate=100,queue_size=1)
                # self.listener_slamware_lidar = Topic(thread_class_scall.ros_client, '/slamware_LiDa_scan', 'sensor_msgs/LaserScan')
                thread_class_scall.ros_client.on_ready(start_listening(mode))  # 一次性地设定连接成功后的回调函数，并不会阻塞程序来等待连接
                try:
                    thread_class_scall.ros_client.run(timeout=0.5)  # client.run_forever()#前者新开一个单独的线程来处理事件，而后者会阻塞当前线程
                except Exception as e:
                    LOGGER.info("call_uws_server_type %s"%str(thread_class_scall.call_uws_server_type))
                # ros_client = Ros('192.168.11.123', 3011)
                # ros_client.run()
                thread_class_scall.client_call = Service(thread_class_scall.ros_client,  '/uws_terminal_cmd', 'uws_server/uws_cmd')# service_name = '/uws_terminal_cmd' # service_type = 'uws_server/uws_cmd'
            else:
                start_listening(mode)
            # QMessageBox.about(self, 'test', 'receive_ok!')
            LOGGER.info('client_connect_state_start:%d,%s,%s'%(thread_class_scall.ros_client.is_connected,mode,str(thread_class_scall.call_uws_server_type)))
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def unsubscribe_topic(self,mode):
        try:
            if mode == "all" and self.listener_untrasonic:
                LOGGER.debug("unsubscribe all")
                self.listener_untrasonic.unsubscribe()
                self.listener_sensor_tof_ir.unsubscribe()
                self.listener_wall_check_ir.unsubscribe()
                self.listener_charge_ir.unsubscribe()
                # self.listener_geomagnetism.unsubscribe()
                # self.listener_battery.unsubscribe()
                self.listener_lidar.unsubscribe()
                self.listener_floor_ir.unsubscribe()
            elif mode == "table0" and self.listener_untrasonic:
                LOGGER.debug("unsubscribe table0")
                self.listener_untrasonic.unsubscribe()
                self.listener_sensor_tof_ir.unsubscribe()
                self.listener_wall_check_ir.unsubscribe()
                self.listener_charge_ir.unsubscribe()
                # self.listener_geomagnetism.unsubscribe()
                self.listener_floor_ir.unsubscribe()
                # self.listener_battery.unsubscribe()
            elif mode == "table2" and self.listener_lidar:
                LOGGER.debug("unsubscribe table2")
                self.listener_lidar.unsubscribe()
            elif mode == "table1" and self.listener_battery:
                LOGGER.debug("unsubscribe table1")
                # self.listener_battery.unsubscribe()
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def get_real_password(self):
        try:
            orign=self.real_password
            def get_num_ops(num,dat):
                pw=0
                time_range = [946684800000, 1893456000000]  # .000 30year
                try:
                    if orign[num] == '0':
                        t = int(dat[num:])
                        if  (time_range[0]<t<time_range[1]):
                            n=t%(num-1)
                            pw=dat[0:n]+dat[n+1:num]
                except Exception as e:
                    pass
                finally:
                    return pw
            if len(orign)>9:#2 6 8
                #try_time1,try_time2,try_time3=0,0,0
                password=get_num_ops(9, orign)
                if password!=0:
                    self.real_password=password
                    return
                password=get_num_ops(7, orign)
                if password!=0:
                    self.real_password=password
                    return
                password=get_num_ops(3, orign)
                if password!=0:
                    self.real_password=password
                    return
                self.real_password = orign
                LOGGER.exception("error password:%s"%orign)
            # else:
            #     self.real_password=orign
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def getDialogSignal(self,dt):
        if dt[0]!='close_event':
            self.real_password=dt[0]
            self.get_real_password()
            if self.pushButton_open_close == dt[1]:
                self.pushButton_open_close.setText("查看传感器")
            elif self.pushButton_17 == dt[1]:
                self.query_ros_map()
            elif (self.pushButton_12 == dt[1]):
                self.download_ros_log()
            else:
                thread_class_scall.call_uws_server_type=False
        else:
            thread_class_scall.call_uws_server_type = None

        if dt[1] == self.pushButton_open_close:
            self.open_close_ros()
        password_ui.close()
    def display_password_ui(self,arg):
        global password_ui
        password_ui = PasswordWindow(self,[self.real_password,arg])
        # 在主窗口中连接信号和槽
        password_ui.mySignal.connect(self.getDialogSignal)
        password_ui.exec_()
    def detection_server_type(self):
        if thread_class_scall.call_uws_server_type == None :#or not thread_class_scall.ros_client.is_connected
            if not self.set_validate_ip_password(self.lineEdit_52.text(), 'test'):
                return
            self.ros_topic_init("init")
            ssh_arg = [str_ip, self.real_password]
            self.ssh_ros_thread.setVal(['date'], [100, thread_class_scall.ros_client, 0, 0,self.sender()], ssh_arg)
            self.ssh_ros_thread.start()
            time.sleep(2)

    def open_close_ros(self):
        try:
            if (self.pushButton_open_close.text() == "查看传感器"):
                global str_ip
                # if(self.timer3.isActive()):
                #     self.timer3.stop()
                # self.ssh_connect_cnt = 0;
                if not self.set_validate_ip_password(self.lineEdit_52.text(),self.real_password):#self.lineEdit_88.text()
                    return
                self.get_real_password()
                self.pushButton_open_close.setText("连接中...")
                self.ros_topic_init("init")
                if not thread_class_scall.ros_client.is_connected:# :#or (not self.t_ssh_server_start.is_alive()):
                    ssh_arg = [str_ip, self.real_password]
                    if thread_class_scall.call_uws_server_type == False:
                        cmd = ["source ~/ros_ws/install/setup.bash;roslaunch rosbridge_server rosbridge_websocket.launch"]
                    else:
                        cmd=['date']# cmd = ["source ~/ros_ws/install/setup.bash;echo $PATH;roslaunch rosbridge_server rosbridge_websocket.launch"]
                    self.ssh_ros_thread.setVal(cmd, [100, thread_class_scall.ros_client, 0, 0,self.sender()], ssh_arg)
                    self.ssh_ros_thread.start()
                    LOGGER.info("ros_thread_start...")
                else:
                    self.timer1.start(100)
                    self.pushButton_open_close.setText("关闭连接")
            else:
                self.ssh_connect_cnt = 0
                if (self.timer1.isActive()):
                    self.timer1.stop()

                self.unsubscribe_topic("all")
                # if self.t_ssh_server_start and self.t_ssh_server_start.is_alive():
                #     os.kill(self.t_ssh_server_start.pid, signal.SIGINT)#self.t_ssh_server_start.process.signal(signal.SIGINT)#self.t_ssh_server_start.terminate()#p.process.signal(signal.SIGINT) p.send_signal(signal.SIGINT)

                self.pushButton_open_close.setText("查看传感器")
                self.clear_senser_buffer_data()
        except Exception as e:
            LOGGER.exception("Exception Logged")
            QMessageBox.critical(self, 'error', str(e))
    def ros_log_time_set(self):
        if self.checkBox_20.checkState():
            self.lineEdit_11.setReadOnly(True)
        else:
            self.lineEdit_11.setReadOnly(False)
    def query_ros_map(self):
        try:
            if (self.pushButton_17.text() == "刷新列表"):
                self.detection_server_type()
                if thread_class_scall.call_uws_server_type == None :
                    return
                cmd = ["find /home/cruiser/ftpDownload/map/ -maxdepth 1 -type f", \
                       # "source ~/ros_ws/install/setup.bash;rosnode list | grep navigation_behaviour_gs_http", \
                       # "source ~/ros_ws/install/setup.bash;rosnode list | grep navigation_behaviour_node", \
                       "find /home/cruiser/ftpDownload/map/GAUSSIAN_RUNTIME_DIR/temp_map/  -name '*.zip'", \
                       "find /home/cruiser/ftpDownload/log/  -name '*.bag*'"
                       ]
                self.comboBox.clear()
                self.save_map_path=[]#清列表
                self.save_manual_bag_path=[]
                self.listWidget.clear()
                # self.label_118.setText("识别中...")
                self.pushButton_17.setText("取消查询")
                self.plainTextEdit.appendPlainText("刷新中...")
                # files = self.ssh_command(cmd, 1)
                ssh_arg = [str_ip, self.real_password]
                self.ssh_log_thread.setVal(cmd, [1,0,0,0], ssh_arg)
                self.ssh_log_thread.start()
            else:
                self.pushButton_17.setText("刷新列表")
                self.ssh_log_thread.__del__()
                self.plainTextEdit.appendPlainText("取消刷新")
        except Exception as e:
            LOGGER.exception("Exception Logged")

    def clear_lidar_point_edit_display(self):
        self.label_103.setText("")
        self.label_105.setText("")
    def timestamp_time(self):
        try:
            if self.sender().text() == ">>":
                self.lineEdit_93.setText(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(self.lineEdit_92.text())))))
                self.plainTextEdit.appendPlainText(str(time.strftime("%w", time.localtime(float(self.lineEdit_92.text())))))
            elif self.sender().text() == "<<":
                self.lineEdit_92.setText(str(time.mktime((datetime.datetime.strptime(self.lineEdit_93.text(), '%Y-%m-%d %H:%M:%S')).timetuple())))
        except Exception as e:
            QMessageBox.critical(self, 'error', '请输入正确格式:'+str(e))
            LOGGER.exception("Exception Logged")#LOGGER.exception("Exception Logged")
    def download_ros_log(self):
        global down_flie_info
        try:
            if (self.pushButton_12.text() == "下载"):
                self.detection_server_type()
                if thread_class_scall.call_uws_server_type == None :
                    return
                try:
                    offset=datetime.datetime.now()-datetime.datetime.strptime(self.dateTimeEdit.text(), '%Y-%m-%d %H:%M')
                    offset_min=int(offset.total_seconds()/60)
                    if offset_min<0:
                        offset_min=0

                    LOGGER.debug("min:%d"%offset_min)
                except Exception as e:
                    LOGGER.exception("Exception Logged")
                    QMessageBox.critical(self, 'error', '请输入时间格式：2019-05-24 17:54 '+str(e))
                    return
                if self.checkBox_22.checkState():
                    if self.comboBox.currentText()=="":
                        QMessageBox.critical(self, 'error', '地图为空，请先刷新并选择地图')
                        return
                    map=self.save_map_path[self.comboBox.currentIndex()]
                else:
                    map=""
                if self.plainTextEdit_2.toPlainText() =='':
                    QMessageBox.critical(self, 'error', '请在上面bug文本框输入bug信息，谢谢！')
                    return
                dir_path = QFileDialog.getExistingDirectory(self, "请选择保存的路径", os.path.dirname(__file__))
                if dir_path=="":
                    return  #dir_path="ros_logs"
                if (self.pushButton_open_close.text() == "查看传感器"):
                    self.ros_topic_init("init")
                down_flie_info[0] = 0
                down_flie_info[1] = ""
                if self.checkBox_20.checkState():
                    f_min="all"
                else:
                    try:
                        if not self.lineEdit_11.text():
                            QMessageBox.critical(self, 'error', '时间范围输入为空！')
                            return
                        tmp=self.lineEdit_11.text().replace(" ","")
                        t=tmp.split('-')
                        if len(t)>5:
                            QMessageBox.critical(self, 'error', '-输入的太多！')
                            return
                        t.reverse()
                        s=[1,60,24*60,24*60*30,24*60*30*365]
                        f_min=0
                        for i,j in enumerate(t):
                            f_min += int(j)*s[i]
                    except Exception as e:
                        LOGGER.exception("Exception Logged")
                        QMessageBox.critical(self, 'error', '请输入往前时间正确格式:'+str(e))
                        return
                manual_bag_select_list = []

                if self.checkBox_28.checkState():
                    for index in range(self.listWidget.count()):
                        check_box = self.listWidget.itemWidget(self.listWidget.item(index))
                        state = check_box.checkState()
                        if state:
                            manual_bag_select_list.append(self.save_manual_bag_path[index])#"/home/cruiser/ftpDownload/log/"+check_box.text()
                    self.plainTextEdit.appendPlainText('已选手动包：%s'%str(manual_bag_select_list))

                # cmd.append("find /home/cruiser/ros_ws/upgrade_manager/ -name 'ubtrosUpgrade.log'")
                cmd=["source /home/cruiser/ros_ws/install/setup.bash;rosnode list|grep -E 'navigation_behaviour_gs_http|navigation_behaviour_node'"]
                # timestamp=int(time.mktime((datetime.datetime.strptime(self.lineEdit_10.text(), '%Y-%m-%d %H:%M:%S')-datetime.timedelta(minutes=f_min)).timetuple()))
                arg=[2,offset_min*60,map,self.dateTimeEdit.text(),str(f_min),dir_path,\
                     self.checkBox_23.checkState(),self.checkBox_26.checkState(),self.checkBox_27.checkState(),offset_min,manual_bag_select_list,\
                     [re.sub(r"[\/\\\:\*\?\"\<\>\|\(\)\&\^\%\$\#\@\!\~]",'',self.lineEdit_105.text()),self.plainTextEdit_2.toPlainText()]]
                # files=self.ssh_command(cmd,arg)
                self.pushButton_12.setText("取消下载")
                ssh_arg=[str_ip,self.real_password]
                self.ssh_log_thread.setVal(cmd,arg,ssh_arg)
                self.ssh_log_thread.start()
                # self.ssh_get_file([files+".tar.gz"])#QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss.zzz ")
                str_check_text=''
                if self.checkBox_27.checkState():str_check_text+=self.checkBox_27.text()+' '
                if self.checkBox_26.checkState(): str_check_text += self.checkBox_26.text()+' '
                if self.checkBox_22.checkState(): str_check_text += self.checkBox_22.text()+' '
                if self.checkBox_28.checkState(): str_check_text += self.checkBox_28.text()+' '
                if self.checkBox_23.checkState(): str_check_text += self.checkBox_23.text()+' '
                self.plainTextEdit.appendPlainText(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+'已选：'+str_check_text+" 开始查找文件...")
                self.pushButton_19.setEnabled(False)
            else:
                self.pushButton_19.setEnabled(True)
                self.pushButton_12.setText("下载")
                self.ssh_log_thread.__del__()
                self.label_69.setVisible(False)
                self.progressBar.setVisible(False)
                self.plainTextEdit.appendPlainText("取消下载")
                # if down_flie_info[1] !="":
                # try:
                #     os.remove(down_flie_info[1])
                # except Exception as e:
                #     LOGGER.exception("Exception Logged")
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def clear_plainedit_display(self):
        self.plainTextEdit.clear()
    def ssh_thread_log_callback(self,data):
        try:
            if not data:
                LOGGER.warning("ssh callback NULL")
                return
            LOGGER.debug("ssh callback:%s"%(str(data)))
            global down_flie_info
            if data:
                if data[0]==1:#map
                    if not data[1]:
                        self.pushButton_17.setText("刷新列表")
                        QMessageBox.critical(self, 'error', "刷新失败！")
                        # self.label_118.setText("未识别")
                        return
                    if len(data[1]) == 0:
                        self.pushButton_17.setText("刷新列表成功 无地图列表")
                        return
                    for val in data[1]:
                        if type(val).__name__ == 'list':
                            for j in val:
                                try:
                                    file = os.path.basename(j)#[1][0][i]
                                    if file.find(".bag")>=0:
                                        item = QListWidgetItem(self.listWidget)
                                        # item.setText("                      fg" + str(i))
                                        ch = QCheckBox()
                                        ch.setText(file)
                                        self.listWidget.setItemWidget(item, ch)# self.listWidget.addItem(item)
                                        self.save_manual_bag_path.append(j)
                                    else:
                                        self.comboBox.addItem(file)
                                        self.save_map_path.append(j)
                                except:
                                    pass
                        else:
                            self.comboBox.addItem('%s(%s)'%(val['name'],val['createdAt']))
                            self.save_map_path.append('ftpDownload/map/GAUSSIAN_RUNTIME_DIR/map/'+val['id']+'#dircopy#'+val['name'])
                    self.pushButton_17.setText("刷新列表")
                    self.plainTextEdit.appendPlainText("刷新成功")
                    thread_class_scall.tool_info_str = 'tool version %s\n'%VERSION+self.plainTextEdit.toPlainText().replace('`','')
                elif data[0] == 2:  # download roslog
                    self.plainTextEdit.appendPlainText(str(data[1]))
                    thread_class_scall.tool_info_str='tool version %s\n'%VERSION+self.plainTextEdit.toPlainText().replace('`','')
                elif data[0] == 3:
                    self.plainTextEdit.appendPlainText("开始压缩文件...")
                    pass
                elif data[0] == 4:
                    try:
                        tmp=data[1][0].replace("\n","")#decode("utf-8")
                        self.progressBar.setValue(0)
                        self.label_69.setVisible(True)
                        self.progressBar.setVisible(True)
                        down_flie_info[0] = int(tmp)
                    except Exception as e:
                        self.plainTextEdit.appendPlainText('%s'%str(data))
                        self.download_ros_log()
                        LOGGER.exception("Exception Logged")
                        QMessageBox.critical(self, 'error', '回调格式错误' + str(e))
                        return
                    down_flie_info[1]=data[1][1]
                    self.plainTextEdit.appendPlainText("文件保存路径："+down_flie_info[1]+" 文件大小byte："+tmp+" 开始下载文件...")
                elif data[0] == 5:
                    self.plainTextEdit.appendPlainText("删除临时文件完成")
                elif data[0] == 6:
                    if len(data)>=2 and len(data[1])>=2:
                        if data[1][0] and data[1][1]:
                            self.plainTextEdit.appendPlainText("查询到两个导航节点为(异常)：高仙 思岚")
                            self.label_118.setText("高仙 思岚")
                        elif data[1][0]:
                            self.plainTextEdit.appendPlainText("当前导航节点为：高仙")
                            self.label_118.setText("高仙")
                        elif data[1][1]:
                            self.plainTextEdit.appendPlainText("当前导航节点为：思岚")
                            self.label_118.setText("思岚")
                        else:
                            self.label_118.setText("未识别")
                            self.plainTextEdit.appendPlainText("未识别当前导航节点")
                    else:
                        self.label_118.setText("未识别")
                        self.plainTextEdit.appendPlainText("未识别当前导航节点")
                elif data[0] <0 :
                    if data[0]== -10:
                        self.plainTextEdit.appendPlainText("警告：" + data[1])
                    else:
                        self.plainTextEdit.appendPlainText("异常退出"+data[1])
                        QMessageBox.critical(self, 'error', data[1])
                        if self.label_118.text()=="识别中...":
                            self.label_118.setText("未识别")
                        if self.pushButton_17.text() != "刷新列表":
                            self.query_ros_map()
                        if self.pushButton_12.text() != "下载":
                            self.download_ros_log()
                textCursor = self.plainTextEdit.textCursor()
                textCursor.movePosition(textCursor.End)
                self.plainTextEdit.setTextCursor(textCursor)
        except Exception as e:
            LOGGER.exception("Exception Logged")
            QMessageBox.critical(self, 'error', '回调格式错误'+str(e))
    def closeEvent(self, e):
        if thread_class_scall.ros_client and thread_class_scall.ros_client.is_connected and thread_class_scall.call_uws_server_type == False:
            cmd=["source /home/cruiser/ros_ws/install/setup.bash;rosnode kill /rosbridge_websocket"]
            # self.ssh_command(cmd,0)
            ssh_arg = [str_ip, self.real_password]
            self.ssh_ros_thread.setVal(cmd, [99,thread_class_scall.ros_client,0,0], ssh_arg)
            self.ssh_ros_thread.start()
            cnt=0
            while thread_class_scall.ros_client.is_connected:
                cnt+=1
                if cnt>20:
                    break
                time.sleep(0.1)
        # sys.exit(app.exec_())
        # os._exit(0)
if __name__ == "__main__":
    import cgitb    #记录异常
    cgitb.enable(format='text')#记录异常
    import sys
    try:
        app = QtWidgets.QApplication(sys.argv)
        fileOpe = MainWindow()
        fileOpe.show()
    # except Exception as e:#QtWidgets.QApplication.processEvents()
    #   LOGGER.exception("Exception Logged")
    except:#记录异常
        LOGGER.exception("Exception Logged")#traceback.print_exc()
        pass
    sys.exit(app.exec_())

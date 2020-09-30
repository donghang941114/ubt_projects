#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    __Author__:lyy
    密码窗口
'''
from password import Ui_Dialog
from PyQt5.QtWidgets import QMessageBox,QDialog
from PyQt5.QtCore import  pyqtSignal

class PasswordWindow(QDialog,Ui_Dialog):
    mySignal = pyqtSignal(list)
    def __init__(self,parent,arg):
        super(PasswordWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.sendEditContent)
        self.pushButton_2.clicked.connect(self.sendEditContent)
        self.lineEdit.setText(arg[0])
        self.send_info=arg[1]
    def sendEditContent(self):
        str=None
        if self.sender().text()=='确定':
            if self.lineEdit.text().replace(" ", "") == "":
                QMessageBox.critical(self, 'error', '请输入ros密码')
                return
            str=self.lineEdit.text()
        else:
            str='close_event'
        self.mySignal.emit([str,self.send_info])  # 发射信号
    # def closeEvent(self, e):
    #     self.mySignal.emit('close_event')  # 发射信号

if __name__ == "__main__":
    pass

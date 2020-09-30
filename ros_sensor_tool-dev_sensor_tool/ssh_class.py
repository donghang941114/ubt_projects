#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko
import os
# import traceback
import logging
LOGGER = logging.getLogger('main')
class ssh_connection(object):
    def __init__(self, host, port, username, password):

        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._transport = None
        self._sftp = None
        self._client = None
        self._connect()  # 建立连接


    def _connect(self):
        transport = paramiko.Transport((self._host, self._port))
        transport.connect(username=self._username, password=self._password)
        self._transport = transport

# 下载
    def download(self, remotepath, localpath):
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self._sftp.get(remotepath, localpath)

# 上传
#     def put(self, localpath, remotepath):
#         if self._sftp is None:
#             self._sftp = paramiko.SFTPClient.from_transport(self._transport)
#             self._sftp.put(localpath, remotepath)

    def ssh_download_files(self,remote_file,localpath):#
        try:
            if remote_file and localpath:
                # tdir = os.path.split(localpath+"\d")[0]
                if not os.path.exists(localpath):
                    os.makedirs(localpath)
            else:
                LOGGER.error("remote_file NULL")
                return None
            for i in remote_file:
                tmp = i.split('\n')
                while '' in tmp:
                    tmp.remove('')
                for j in tmp:
                    file = os.path.basename(j)
                    self.download(j, "%s\\%s" % (localpath, file))  # os.path.join(local_dir,file)
                    LOGGER.debug("get_file:%s"%j)
            LOGGER.info("download ok")
            # QMessageBox.critical(self, 'error', "下载异常")
        except Exception as e:
            LOGGER.exception("Exception Logged")
    # 执行命令
    def exec_command(self, command):
        try:
            if self._client is None:
                self._client = paramiko.SSHClient()
                self._client._transport = self._transport
            if command.find("sudo -S")>=0:
                stdin, stdout, stderr = self._client.exec_command(command,get_pty=True)
                stdin.write(self._password + '\n')
            else:
                stdin, stdout, stderr = self._client.exec_command(command,get_pty=False)#timeout=10
                # stdin.write(self._password + '\n')
            if command.find("rosbridge_server") < 0:
                data = stdout.read()
                if len(data) > 0:
                    LOGGER.info (data.strip())  # 打印正确结果
                    return data
                err = stderr.read()
                if len(err) > 0:
                    LOGGER.warning (err.strip())  # 输出错误结果
                    return ["error",err]
        except Exception as e:
            LOGGER.exception("Exception Logged")
    def close(self):
        try:
            if self._transport:
                self._transport.close()
            if self._client:
                self._client.close()
        except Exception as e:
            LOGGER.exception("Exception Logged")
if __name__ == "__main__":
    # conn = SSHConnection('ip', port, 'username', 'password')
    # conn.exec_command('ls -l')
    pass


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from configobj import ConfigObj

# import configParser #import ConfigParser
# import string
from configobj import ConfigObj
import logging
LOGGER = logging.getLogger('main')
class ini_file_operator:
    def __init__(self,inifile):
        try:
            self.inifile = inifile#"config.ini"
            self.config = ConfigObj(self.inifile, encoding='UTF8')
        except Exception as e:
            LOGGER.exception("Exception Logged")

    # 获取ini参数值
    def get_ini_val(self, section, option):
        try:
            if len(self.config)==0:
                return False
            val = self.config[section][option]
            if val != None and val != "":
                return val
            else:
                return False
        except Exception as e:
            LOGGER.exception("Exception Logged")
            return False
    '''
    # 获取ini键值
    def get_ini_option(self, section):
        # config = ConfigObj(self.inifile)
        sect = self.config.keys()
        if sect.count(section):
            option = self.config[section]
            return option.keys()
        else:
            return ""

        # 获取ini选项

    def get_ini_section(self):
        # config = ConfigObj(self.inifile)
        section = self.config.keys()
        # print 'sections:', section
        return section

    # 修改ini段值
    def set_ini_section(self, section):

        # config = ConfigObj(self.inifile)
        self.config[section] = {}
        print
        "set ini_section is: ", section
        self.config.write()

    # 修改ini键值
    def set_ini_val(self, section, option, val):

        # config = ConfigObj(self.inifile)
        sect = self.config.keys()
        if sect.count(section):
            self.config[section][option] = val
            print
            "set ini_option is: %s = %s" % (option, val)
        else:
            self.config[section] = {}
            self.config[section][option] = val
            print
            "set ini_option is: %s = %s" % (option, val)
        self.config.write()

    # 删除ini键值
    def del_ini_option(self, section, option):
        # config = ConfigObj(self.inifile)
        sect = self.config[section]
        if sect.keys().count(option):
            del self.config[section][option]
            print
            "delete ini_option is: %s" % option
        self.config.write()
'''
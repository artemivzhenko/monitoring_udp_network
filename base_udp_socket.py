#!/usr/bin/python2
# True Item LLC
# Artem Ivzhenko
# artmeivzhenko@true-item.com
# UDP Monitoring Script

import time
import syslog
import os
from datetime import datetime


class SocketUDP:
    def __init__(self, error_log_file):
        self.error_log_file = error_log_file
        self.__error_logs__ = []
        self.__logs_in_RAM__ = []

    def dump_errors_to_disk_func(self, socket_name):
        while True:
            time.sleep(6)
            tmp_error_logs_len = len(self.__error_logs__)
            tmp_error_logs = self.__error_logs__[:tmp_error_logs_len - 1]
            self.__error_logs__ = self.__error_logs__[tmp_error_logs_len - 1:]
            for error_msg in tmp_error_logs:
                try:
                    os.system("echo '{0}' >> {1}"
                              .format(error_msg, self.error_log_file + str(datetime.now().date()) + '.log'))
                except Exception as error:
                    self.__error_logs__.append(str(error.args) + ' | Date=' + str(datetime.now()) +
                                               ' dump errors to disk [echo to {0}]\n'
                                               .format(self.error_log_file + str(datetime.now().date()) + '.log'))
                    syslog.syslog('[+] UDP script dumped {0} errors to disk space with errors'.format(socket_name))
                else:
                    syslog.syslog('[+] UDP script dumped {0} errors to disk space without errors'.format(socket_name))

    def dump_logs_to_disk_func(self, file_for_dump, socket_name):
        while True:
            time.sleep(6)
            tmp_logs_in_ram_len = len(self.__logs_in_RAM__)
            tmp_logs_in_ram = self.__logs_in_RAM__[:tmp_logs_in_ram_len - 1]
            self.__logs_in_RAM__ = self.__logs_in_RAM__[tmp_logs_in_ram_len - 1:]
            for log in tmp_logs_in_ram:
                try:
                    with open(str(file_for_dump + str(datetime.now().date()) + '.log'), 'a') as log_file:
                        log_file.write(log)
                except Exception as error:
                    self.__error_logs__.append(str(error.args) + ' | Date=' + str(datetime.now()) +
                                               ' dump logs to disk {0}.write\n'
                                               .format(file_for_dump + str(datetime.now().date()) + '.log'))
                    syslog.syslog('[+] UDP script dumped {0} RAM logs to disk space with errors'.format(socket_name))
                else:
                    syslog.syslog('[+] UDP script dumped {0} RAM logs to disk space without errors'.format(socket_name))
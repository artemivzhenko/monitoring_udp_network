#!/usr/bin/python2
# True Item LLC
# Artem Ivzhenko
# artmeivzhenko@true-item.com
# UDP Monitoring Script


import threading
from datetime import datetime
import time
import socket
from base_udp_socket import SocketUDP


class ServerUDP(SocketUDP):
    def __init__(self, ip_and_port, log_files, error_log_file):
        SocketUDP.__init__(self, error_log_file)
        self.log_files = log_files
        self.__request_data__ = ''
        self.__request_address__ = ()
        self.__error_logs__ = []
        self.__logs_in_RAM__ = []
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.server.settimeout(5)
            self.server.bind(ip_and_port)
        except socket.error as error:
            print '[-] Can`t create server socket args = ' + \
                  str(error.args) + \
                  str(ip_and_port[0]) + ':' + \
                  str(ip_and_port[1]) + '\n' + \
                  ' | Date={0}\n'.format(datetime.now())
            exit()

    @property
    def error_logs(self):
        return self.__error_logs__

    @property
    def logs_in_ram(self):
        return self.__logs_in_RAM__

    @property
    def request_data(self):
        return self.__request_data__

    @property
    def request_address(self):
        return self.__request_address__

    def server_start(self):
        server_function_thread = threading.Thread(target=self.__server_func__)
        server_function_thread.setDaemon(False)
        server_function_thread.start()
        dump_errors_to_disk_thread = threading.Thread(target=self.dump_errors_to_disk_func,
                                                      args=('server',))
        dump_errors_to_disk_thread.setDaemon(False)
        dump_errors_to_disk_thread.start()
        dump_logs_to_disk_thread = threading.Thread(target=self.dump_logs_to_disk_func,
                                                    args=(self.log_files[0] + 'ram_', 'server',))
        dump_logs_to_disk_thread.setDaemon(False)
        dump_logs_to_disk_thread.start()

    def __server_func__(self):
        while True:
            try:
                data, address = self.server.recvfrom(4096)
                if (data, address) != (self.__request_data__, self.__request_address__):
                    self.__request_data__, self.__request_address__ = data, address
                    get_time, readable_time = int(float(time.time() * 1000)), datetime.now()
                else:
                    continue
            except Exception as error:
                error_msg = str(error.args) + '\n' + str(datetime.now())
                self.__error_logs__.append(error_msg)
                continue
            except KeyboardInterrupt:
                exit()
            else:
                answer = self.__request_data__.decode('utf-8').split(';')
                try:
                    output_line = '{0} ; {1} ; {2} ; {3} ; {4} ; {5} ; {6} ' \
                        .format(answer[0], answer[1], get_time, int(float(time.time() * 1000)),
                                answer[2], readable_time, datetime.now())
                    self.server.sendto(bytes(output_line), self.__request_address__)
                    if write_to_disk:
                        for log_file in self.log_files:
                            try:
                                with open(log_file + str(datetime.now().date()) + '.log', 'a') as lf:
                                    lf.write(output_line + '\n')
                            except Exception as write_error:
                                self.__error_logs__.append(str(write_error.args) + ' | Date=' + str(datetime.now()) +
                                                           ' server function {0}.write\n'.format(log_file))
                    self.__logs_in_RAM__.append(output_line + '\n')
                except IndexError as msg_error:
                    self.__error_logs__.append('Message is unreadable {0} {1}\n'.format(datetime.now(), msg_error.args))

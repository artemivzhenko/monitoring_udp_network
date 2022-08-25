#!/usr/bin/python2
# True Item LLC
# Artem Ivzhenko
# artmeivzhenko@true-item.com
# UDP Monitoring Script


from datetime import datetime
import time
import socket
import threading
from base_udp_socket import SocketUDP


class ClientUDP(SocketUDP):
    def __init__(self, ip_and_port, server_ip_and_port, request_log_files, response_log_files, error_log_file,
                 transaction_label, client_id):
        SocketUDP.__init__(self, error_log_file + str(client_id) + '_')
        self.ip_and_port = ip_and_port
        self.server_ip_and_port = server_ip_and_port
        self.request_log_files = []
        for request_log_file in request_log_files:
            self.request_log_files.append(request_log_file + str(client_id) + '_')
        self.response_log_files = []
        for response_log_file in response_log_files:
            self.response_log_files.append(response_log_file + str(client_id) + '_')
        self.transaction_label = transaction_label
        self.__transaction_id__ = 1
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client.settimeout(5)
            self.client.bind(ip_and_port)
        except socket.error as error:
            print '[-] Can`t create client socket args = ' + \
                  str(error.args) + \
                  str(ip_and_port[0]) + ':' + \
                  str(ip_and_port[1]) + '\n' + \
                  ' | Date={0}\n'.format(datetime.now())
            exit()

    @property
    def error_logs(self):
        return self.__error_logs__

    @property
    def transaction_id(self):
        return self.__transaction_id__

    @transaction_id.setter
    def transaction_id(self, value):
        self.__transaction_id__ += value

    def start_client(self):
        client_function_thread = threading.Thread(target=self.__client_function__)
        client_function_thread.setDaemon(False)
        client_function_thread.start()
        send_message_function_tread = threading.Thread(target=self.__send_message_function__)
        send_message_function_tread.setDaemon(False)
        send_message_function_tread.start()
        dump_errors_to_disk_thread = threading.Thread(target=self.dump_errors_to_disk_func,
                                                      args=('client',))
        dump_errors_to_disk_thread.setDaemon(False)
        dump_errors_to_disk_thread.start()
        dump_logs_to_disk_thread = threading.Thread(target=self.dump_logs_to_disk_func,
                                                    args=(self.response_log_files[0] + 'ram',
                                                          'client'))
        dump_logs_to_disk_thread.setDaemon(True)
        dump_logs_to_disk_thread.start()

    def __send_message_function__(self):
        while True:
            time.sleep(1)
            self.client.sendto(bytes('{0}{1} ; {2} ;{3}'
                                     .format(self.transaction_label,
                                             self.__transaction_id__,
                                             int(float(time.time() * 1000)),
                                             datetime.now())),
                               self.server_ip_and_port)
            if write_to_disk:
                for log_file in self.request_log_files:
                    try:
                        with open(log_file + str(datetime.now().date()) + '.log', 'a') as lf:
                            lf.write('Send {0}{1} {2}\n'.format(self.transaction_label, self.__transaction_id__,
                                                                datetime.now()))
                    except Exception as error:
                        self.__error_logs__.append(str(error.args) + ' | Date=' + str(datetime.now()) +
                                                   ' can`t write to log file: {0}\n'.format(log_file))
            self.__transaction_id__ += 1

    def __client_function__(self):
        while True:
            try:
                response_data, response_address = self.client.recvfrom(4096)
                readable_get_time, response_time = datetime.now(), int(float(time.time() * 1000))
            except socket.error as s_error:
                error_msg = str(s_error.args) + '\n' + str(datetime.now())
                self.__error_logs__.append(error_msg)
                continue
            except KeyboardInterrupt:
                exit()
            else:
                answer = response_data.decode('utf-8').split(';')
                try:
                    output_line = 'Date: {0} Tnx: {1}; ' \
                                  'Request= {2}; ' \
                                  'Response= {3}; ' \
                                  'Client= {4}; Server= {5}; ' \
                                  'Send request time {6}; Get request time {7}; ' \
                                  'Send response time {8}; Get response time {9}\n ' \
                        .format(datetime.now(), answer[0],
                                str((int(answer[2]) - int(answer[1]))) + 'ms',
                                str(response_time - int(answer[3])) + 'ms',
                                self.ip_and_port, response_address,
                                readable_get_time, answer[4],
                                answer[5], answer[6])
                except Exception as error:
                    self.__error_logs__.append(str(error.args) + ' | Date=' + str(datetime.now()) +
                                               ' unreadable message : {0}\n'.format(str(answer)))
                else:
                    if write_to_disk:
                        for log_file in self.response_log_files:
                            try:
                                with open(log_file + str(datetime.now().date()) + '.log', 'a') as lf:
                                    lf.write(output_line)
                            except Exception as error:
                                self.__error_logs__.append(str(error.args) + ' | Date=' + str(datetime.now()) +
                                                           ' can`t write to log file : {0}\n'.format(log_file))
                    self.__logs_in_RAM__.append(output_line)


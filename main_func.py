#!/usr/bin/python2
# True Item LLC
# Artem Ivzhenko
# artmeivzhenko@true-item.com
# UDP Monitoring Script

import random
import string
import optparse
from server_class import ServerUDP
from client_class import ClientUDP


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config_file',
                      help='Configuration file for UDP script')
    parser.add_option('-w', '--write', dest='write_to_disk',
                      help='Write to disk 1 - yes, 0 - no')
    (all_options, arguments) = parser.parse_args()
    return all_options


def get_server_ip_and_port(ip_and_port_line):
    global server_address
    ip_and_port_line = ip_and_port_line.replace('\n', '')
    address = ip_and_port_line.split(':')
    server_address = (address[0], int(address[1]))


def get_server_log_files(server_log_files_line):
    global server_log_files
    server_log_files_line = server_log_files_line.replace('\n', '')
    for server_log_file in server_log_files_line.split(','):
        server_log_files.append(server_log_file)


def get_server_error_file(server_error_file_line):
    global server_error_file
    server_error_file_line = server_error_file_line.replace('\n', '')
    server_error_file = server_error_file_line


def get_client_addresses(ip_and_port_line):
    global client_addresses
    ip_and_port_line = ip_and_port_line.replace('\n', '')
    addresses = ip_and_port_line.split(',')
    for address in addresses:
        ip, port = address.split(':')
        client_addresses.append((ip, int(port)))


def get_client_log_files(client_log_files_line):
    global client_request_log_files
    global client_response_log_files
    client_log_files_line = client_log_files_line.replace('\n', '')
    for client_log_file in client_log_files_line.split(','):
        client_request_log_files.append(client_log_file + 'send_')
        client_response_log_files.append(client_log_file + 'get_')


def get_client_error_file(client_error_file_line):
    global client_error_file
    client_error_file_line = client_error_file_line.replace('\n', '')
    client_error_file = client_error_file_line


if __name__ == '__main__':
    options = get_arguments()
    write_to_disk = bool(int(options.write_to_disk)) if options.write_to_disk else False
    config_file_way = options.config_file if options.config_file else './udp.config'
    server_address = ()
    server_log_files = []
    server_error_file = ''
    client_addresses = []
    client_request_log_files = []
    client_response_log_files = []
    client_error_file = ''
    dictionary_for_parse_config = {'server_ip': get_server_ip_and_port,
                                   'server_log_files': get_server_log_files,
                                   'server_error_file': get_server_error_file,
                                   'clients_ip': get_client_addresses,
                                   'client_log_files': get_client_log_files,
                                   'client_error_file': get_client_error_file}
    try:
        with open(config_file_way, 'r') as config_file:
            for line in config_file:
                split_line = line.split('=')
                dictionary_for_parse_config[split_line[0]](split_line[1])
    except Exception as error:
        print str(error.args) + ' config file = {0}'.format(str(config_file_way))
        exit()
    serverUDP = ServerUDP(server_address, server_log_files, server_error_file)
    serverUDP.server_start()
    index = 1
    for client_address in client_addresses:
        lower_upper_alphabet = string.ascii_letters
        random_letter = random.choice(lower_upper_alphabet)
        clientUDP = ClientUDP(client_address, server_address,
                              client_request_log_files, client_response_log_files, client_error_file,
                              string.upper(random_letter), index)
        clientUDP.start_client()
        index += 1

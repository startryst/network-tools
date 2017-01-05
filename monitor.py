#!/usr/bin/env python


# Environment requirement:
# 1. CentOS 6.8 with network tools 'nc' installed, due to different output of 'nc' in Mac, Mac has some problems
# 2. Python 2.6.6/2.7.10 interpreter
# chmod 755 for this file to run directly

import subprocess
from datetime import datetime
import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


def get_ip_list(filename):
    ip_list = []
    file_to_open = open(filename)
    for line in file_to_open:
        line = line.strip('\n')
        ip_list.append(line.split(','))
    file_to_open.close()
    return ip_list


def nc_test(ip_list, filename):
    for i in ip_list:
        output = subprocess.Popen(['nc', '-w', '2', '-z', i[0], i[1]], stdout=subprocess.PIPE).communicate()[0]
        if output == '':
            result = '|' + str(datetime.now()).ljust(30) + '|' + (i[0] + ':' + i[1]).ljust(20) + '|' + 'FAILED'.ljust(10)
            print '\n' + result
            save_to_file(result, filename)
        else:
            print "*",
            result = '|' + str(datetime.now()).ljust(30) + '|' + (i[0] + ':' + i[1]).ljust(20) + '|' + 'SUCCESS'.ljust(10)
            save_to_file(result, filename)


def save_to_file(result, filename):
    file_to_save = open(filename, "a")
    file_to_save.write('\n' + result)
    file_to_save.close()


def main():
    ip_file_name = raw_input('Please enter the file name to monitor[ip.txt]: ')
    result_file_name = raw_input('Please enter the fine name to save for the monitor result[result.txt]: ')

    if ip_file_name == '':
        ip_file_name = 'ip.txt'
    if result_file_name == '':
        result_file_name = 'result.txt'

    while True:
        nc_test(get_ip_list(ip_file_name), result_file_name)

if __name__ == '__main__':
    main()



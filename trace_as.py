#!/usr/bin/env python3


import subprocess
import re
import urllib.request
import time


def get_ip_list(target):
    ip_list = []
    trace_list = subprocess.check_output(['traceroute', '-nI', '-q', '1', '-w', '1', target]).decode().split('\n')
    for i in trace_list[:-1]:
        if len(i) < 10:
            ip_list.append('*')
        else:
            ip_list.append(re.search(r'(\d+\.\d+\.\d+\.\d+)', i).group(1))
    return ip_list


def search_as_name_merit(ip_list):
    name_list = []
    for i in ip_list:
        if i is '*':
            name_list.append('*')
        else:
            name_raw = subprocess.check_output(['whois', '-h', '198.108.0.18', i]).decode().split('\n')
            if len(name_raw) <= 2:
                name_list.append('Not Found')
            else:
                name = re.match(r'descr:\s+(.+)', name_raw[1]).group(1)
                name_list.append(name)
    return name_list


def search_as_name_cymru(ip_list):
    name_list = []
    for i in ip_list:
        if i is '*':
            name_list.append('*')
        else:
            name_raw = subprocess.check_output(['whois', '-h', 'v4.whois.cymru.com', i]).decode().split('\n')
            name = re.search(r'\d+\.\d+\.\d+\.\d+\s+\|\s(.+)', name_raw[1]).group(1)
            name_list.append(name)
    return name_list


def search_as_name_ipip(ip_list):
    name_list = []
    for i in ip_list:
        if i is '*':
            name_list.append('*')
        else:
            name_raw_str = urllib.request.urlopen("http://freeapi.ipip.net/" + i).read().decode()
            time.sleep(5)
            name_list.append(name_raw_str[1:-1])
    return name_list


def main():
    ip_list = get_ip_list(input("Please enter the target IP address to trace: "))
    name_list_merit = search_as_name_merit(ip_list)
    name_list_cymru = search_as_name_cymru(ip_list)
    name_list_ipip = search_as_name_ipip(ip_list)

    print("Every Hop".ljust(20) + "MeritRADb".ljust(50) + "Team Cymru".ljust(50) + "ipip.net")
    for ip,merit, cymru, ipip in zip(ip_list, name_list_merit, name_list_cymru, name_list_ipip):
        print(ip.ljust(20) + merit.ljust(50) + cymru.ljust(50) + ipip)


if __name__ == '__main__':
    main()




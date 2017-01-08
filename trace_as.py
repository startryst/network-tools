#!/usr/bin/env python3


import subprocess
import re
import urllib.request
import socket
from fast import fast_trace
import time
import netaddr


def merit_filter(item):
    if 'No entries found' in item:
        as_name = 'Not Found'
        asn = 'Not Found'
    else:
        try:
            as_name = re.search(r'descr:\s+(.+)', item).group(1)
            asn = re.search(r'origin:\s+(.+)', item).group(1)

        # if whois server no return or reset the TCP connection
        except AttributeError:
            as_name = 'Timeout'
            asn = 'Timeout'
    return as_name, asn


def cymru_filter(item):
    try:
        as_name = re.search(r'\d+\.\d+\.\d+\.\d+\s+\|\s(.+)', item).group(1)

    # if whois server no return or reset the TCP connection
    except AttributeError:
        as_name = 'Timeout'
    return as_name


def search_as_name_ipip(ip):
    name_raw_str = urllib.request.urlopen("http://freeapi.ipip.net/" + ip).read().decode()

    # ipip.net set con-current connection limit for freeapi, so need to pause for 1 second
    time.sleep(1)
    raw_string = name_raw_str[1:-1].replace('"','')
    raw_list = raw_string.split(',')
    result = raw_list[1] + ':' + raw_list[-1]
    return result


def print_save(hop, asn, merit, cymru, ipip, filename, ip):
    if hop == "IP Address":
        template = hop.ljust(16) + '|' + asn.ljust(9) + '|' + merit.ljust(29) + '|' + cymru.ljust(37) + '|' + ipip
        print('\nTracing to {}: '.format(ip))
        print(template)
        with open(filename, "a") as file_to_save:
            file_to_save.write('\n\n\nTracing to {}: '.format(ip))
    else:
        template = hop.ljust(16) + '|' + asn.ljust(9) + '|' + merit[:28].ljust(29) + '|' + cymru[:36].ljust(37)\
                   + '|' + ipip
        print(template)
    with open(filename, "a") as file_to_save:
        file_to_save.write('\n' + template)


def as_border_check(asn, last_asn, filename):
    if 'AS' in asn and 'AS' in last_asn and asn != last_asn:
        print('======AS BORDER======' * 6)
        with open(filename, "a") as file_to_save:
            file_to_save.write('\n' + '======AS BORDER======' * 6)
        return asn
    elif asn == 'Not Found' or asn == '*' or asn == 'Timeout' or asn == 'Private':
        return last_asn
    else:
        return asn


def main():
    target = input("Please enter the domain name/IP address to trace: ")
    max_ttl = input("Please enter the max hops: ")
    file_name = str(input('Please enter the file name to save for the trace result[asn_trace.txt]: ') or
                    'asn_trace.txt')
    skip_ipip = bool(input("ipip.net has concurrent connection detection, do you want to skip ipip.net?"
                           "[y] or [press enter for n]: "))
    merit_raw = []
    cymru_raw = []
    # last_asn for as border check
    last_asn = ''

    # capture the (ip) address if the target is a domain name
    ip = socket.getaddrinfo(target, None)[0][4][0]

    # print title column
    print_save("IP Address", "ASN", "MeritRADb", "Team Cymru", "ipip.net", file_name, ip)

    # Conduct fast trace to get the full hop ip address list
    trace_list = fast_trace(ip, max_ttl)

    # Concurrent processing of whois for both merit and cymru
    for i in trace_list:
        if i != '*' and netaddr.IPAddress(i).is_private():
            merit_raw.append('Private')
            cymru_raw.append('Private')
        elif i != '*':
            merit_raw.append(subprocess.Popen(['whois', '-m', i], stdout=subprocess.PIPE))
            cymru_raw.append(subprocess.Popen(['whois', '-h', 'v4.whois.cymru.com', i], stdout=subprocess.PIPE))
        else:
            merit_raw.append('*')
            cymru_raw.append('*')

    # Filter output and print result
    for t, m, c in zip(trace_list, merit_raw, cymru_raw):
        if m == 'Private':

            # print & save result
            print_save(t, 'Private', 'Private', 'Private', 'Private', file_name, ip)
        elif m != '*':

            # Due to ipip.net has concurrent limitation restriction, need to avoid con-current processing
            if skip_ipip:
                ipip = "Skipped"
            else:
                ipip = search_as_name_ipip(t)

            merit, asn = merit_filter(m.communicate()[0].decode())
            cymru = cymru_filter(c.communicate()[0].decode())

            # To calculate the cross AS border and print '======AS BORDER======'
            last_asn = as_border_check(asn, last_asn, file_name)

            # print result
            print_save(t, asn, merit, cymru, ipip, file_name, ip)
        else:
            print_save('*', '*', '*', '*', '*', file_name, ip)


if __name__ == '__main__':
    main()




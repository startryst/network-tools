#!/usr/bin/env python3


import subprocess
import re
import urllib.request
import socket
import time
import netaddr


def ping_filter(item):
    if 'Time to live exceeded' in item or '1 packets received' in item:
        output_list = item.split('\n')
        hop = re.search(r'(\d+\.\d+\.\d+\.\d+)', output_list[1]).group(1)
        return hop
    else:
        return '*'


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

    # last_asn for as border check
    last_asn = ''

    # capture the (ip) address if the target is a domain name
    ip = socket.getaddrinfo(target, None)[0][4][0]

    # print title column
    print_save("IP Address", "ASN", "MeritRADb", "Team Cymru", "ipip.net", file_name, ip)

    # Incremental of ttl for each ping, and query whois against merit and cymru, query http API against ipip.net
    for ttl in range(1, int(max_ttl)+1):
        ping_output = subprocess.Popen(['ping', '-c', '1', '-m', str(ttl), '-i', '0.1', '-t', '2', ip],
                                       stdout=subprocess.PIPE).communicate()[0].decode()
        i = ping_filter(ping_output)

        # check to see if the ip address is private IP address
        if i != '*' and netaddr.IPAddress(i).is_private():
            print_save(i, 'Private', 'Private', 'Private', 'Private', file_name, ip)
        elif i != '*':
            merit_raw = subprocess.Popen(['whois', '-m', i], stdout=subprocess.PIPE)
            cymru_raw = subprocess.Popen(['whois', '-h', 'v4.whois.cymru.com', i], stdout=subprocess.PIPE)
            ipip = search_as_name_ipip(i)
            merit, asn = merit_filter(merit_raw.communicate()[0].decode())
            cymru = cymru_filter(cymru_raw.communicate()[0].decode())

            # To calculate the cross AS border and print '======AS BORDER======'
            last_asn = as_border_check(asn, last_asn, file_name)

            # print result
            print_save(i, asn, merit, cymru, ipip, file_name, ip)

        # if no reply received, marked as '*'
        else:
            print_save('*', '*', '*', '*', '*', file_name, ip)

        # if the echo-reply received from the destination, break the loop
        if i == ip:
            print("Trace Done!")
            break
        else:
            pass


if __name__ == '__main__':
    main()




#!/usr/bin/env python3


import subprocess
import re
import urllib.request
import socket
# import time


def search_as_name_merit(ip):
    name_tuple = subprocess.Popen(['whois', '-h', '198.108.0.18', ip], stdout=subprocess.PIPE)
    name_raw = name_tuple.communicate()[0].decode()
    if 'No entries found' in name_raw:
        result = 'Not Found'
        asn = 'Not Found'
    else:
        result = re.search(r'descr:\s+(.+)', name_raw).group(1)
        asn = re.search(r'origin:\s+(.+)', name_raw).group(1)
    return result, asn


def search_as_name_cymru(ip):
    name_tuple = subprocess.Popen(['whois', '-h', 'v4.whois.cymru.com', ip], stdout=subprocess.PIPE)
    name_raw = name_tuple.communicate()[0].decode().split('\n')
    try:
        result = re.search(r'\d+\.\d+\.\d+\.\d+\s+\|\s(.+)', name_raw[1]).group(1)
    except IndexError:
        result = 'Timeout'
    return result


def search_as_name_ipip(ip):
    name_raw_str = urllib.request.urlopen("http://freeapi.ipip.net/" + ip).read().decode()
    # time.sleep(1)
    raw_string = name_raw_str[1:-1].replace('"','')
    raw_list = raw_string.split(',')
    result = raw_list[1] + ':' + raw_list[-1]
    return result


def print_save(hop, asn, merit, cymru, ipip, filename, ip):
    if hop == "IP Address":
        template = hop.ljust(15) + '|' + asn.ljust(9) + '|' + merit.ljust(29) + '|' + cymru.ljust(37) + '|' + ipip
        print('\nTracing to {}: '.format(ip))
        print(template)
        with open(filename, "a") as file_to_save:
            file_to_save.write('\n\n\nTracing to {}: '.format(ip))
    else:
        template = hop.ljust(15) + '|' + asn.ljust(9) + '|' + merit[:28].ljust(29) + '|' + cymru[:36].ljust(37)\
                   + '|' + ipip
        print(template)
    with open(filename, "a") as file_to_save:
        file_to_save.write('\n' + template)


def as_border_check(asn, last_asn):
    if 'AS' in asn and 'AS' in last_asn and asn != last_asn:
        print('======AS BORDER======' * 6)
        return asn
    elif asn == 'Not Found' or asn == '*':
        return last_asn
    else:
        return asn


def main():
    target = input("Please enter the domain name/IP address to trace: ")
    max_ttl = input("Please enter the max hops: ")
    file_name = str(input('Please enter the file name to save for the trace result[asn_trace.txt]: ') or
                    'asn_trace.txt')

    # capture the (ip) address if the target is a domain name
    ip = socket.getaddrinfo(target, None)[0][4][0]

    # print title column
    print_save("IP Address", "ASN", "MeritRADb", "Team Cymru", "ipip.net", file_name, ip)

    # last_asn for as border check
    last_asn = ''
    for i in range(1, int(max_ttl)+1):

        # if time-to-exceed error message or echo-reply message received, the console output on 2nd line(output_list[1])
        # always have IP address of the responding hop
        raw_output = subprocess.Popen(['ping', '-c', '1', '-m', str(i), '-i', '0.1', '-t', '1', ip],
                                      stdout=subprocess.PIPE)
        output = raw_output.communicate()[0].decode()
        output_list = output.split('\n')
        try:

            # capture the IP address of the responding hop by reg
            hop = re.search(r'(\d+\.\d+\.\d+\.\d+)', output_list[1]).group(1)

        # if not replies from certain hop, then output_list[1] doesn't have any ip address to trigger AttributeError
        except AttributeError:
            print_save('*', '*', '*', '*', '*', file_name, ip)

        # To search merit and cymru's whois server, REST API to search ipip's ASN database
        merit, asn = search_as_name_merit(hop)
        cymru = search_as_name_cymru(hop)
        ipip = search_as_name_ipip(hop)

        # To calculate the cross AS border and print '======AS BORDER======'
        last_asn = as_border_check(asn, last_asn)

        # Print the result and cut only the first 30 characters for merit and cymru
        print_save(hop, asn, merit, cymru, ipip, file_name, ip)

        # if echo-reply message received, break out the loop
        if '1 packets received' in output:
            break


if __name__ == '__main__':
    main()




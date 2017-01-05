#!/usr/bin/env python3


import subprocess
import re
import urllib.request
import time


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
    result = re.search(r'\d+\.\d+\.\d+\.\d+\s+\|\s(.+)', name_raw[1]).group(1)
    return result


def search_as_name_ipip(ip):
    name_raw_str = urllib.request.urlopen("http://freeapi.ipip.net/" + ip).read().decode()
    time.sleep(1)
    result = name_raw_str[1:-1]
    return result


def main():
    target = input("Please enter the IP address to trace: ")
    max_ttl = input("Please enter the max hops: ")
    raw_list = []
    last_asn = ''
    print("IP Address".ljust(18) + "ASN".ljust(13) + "MeritRADb".ljust(30) + "Team Cymru".ljust(30) + "ipip.net")

    for i in range(1, int(max_ttl)+1):
        raw_output = subprocess.Popen(['ping', '-c', '1', '-m', str(i), '-i', '0.1', '-t', '1', target],
                                      stdout=subprocess.PIPE)
        output = raw_output.communicate()[0].decode()

        # if mtu expired, the remote end will send our Time to live exceeded ICMP error message, the error message
        # contain the IP address of the responding (hop),also we capture the (ip) address if the target is a domain name
        if 'Time to live exceeded' in output:
            output_list = output.split('\n')
            ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', output_list[0]).group(1)
            hop = re.search(r'(\d+\.\d+\.\d+\.\d+)', output_list[1]).group(1)

            # To search merit's whois server
            merit, asn = search_as_name_merit(hop)

            # To calculate the cross AS border and print '='
            if asn != 'Not Found' and asn != last_asn and last_asn != '':
                print('=' * 130)
                last_asn = asn
            elif asn == 'Not Found' or asn == '*':
                pass
            else:
                last_asn = asn

            # To search Team Cymru's whois server
            cymru = search_as_name_cymru(hop)

            # To search ipip.net's AS info
            ipip = search_as_name_ipip(hop)

            # Print the result and cut only the first 30 characters for merit and cymru
            print(hop.ljust(18) + asn.ljust(13) + merit[:29].ljust(30) + cymru[:29].ljust(30) + ipip)
        elif '1 packets received' in output:
            merit, asn = search_as_name_merit(ip)
            cymru = search_as_name_cymru(ip)
            ipip = search_as_name_ipip(ip)
            print(ip.ljust(18) + asn.ljust(13) + merit.ljust[:29].ljust(30) + cymru[:29].ljust(30) + ipip)
            break
        else:
            print('*'.ljust(18) + '*'.ljust(13) + '*'.ljust(30) + '*'.ljust(30) + '*')


if __name__ == '__main__':
    main()




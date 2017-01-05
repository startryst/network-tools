#!/usr/bin/env python3

import subprocess
import re


def fast_trace(ip, max_ttl):
    raw_list = []
    trace_list = []
    for i in range(1, int(max_ttl)+1):
        raw_list.append(subprocess.Popen(['ping', '-c', '1', '-m', str(i), '-i', '0.1', '-t', '1', ip], stdout=subprocess.PIPE))
    for i in raw_list:
        output = i.communicate()[0].decode()
        if 'Time to live exceeded' in output:
            output_list = output.split('\n')
            hop = re.search(r'(\d+\.\d+\.\d+\.\d+)', output_list[1]).group(1)
            trace_list.append(hop)
        elif '1 packets received' in output:
            trace_list.append(ip)
            break
        else:
            trace_list.append('*')
    return trace_list


def main():
    ip = input("Please enter the IP address to trace: ")
    max_ttl = input("Please enter the max hops to trace: ")
    for i in fast_trace(ip, max_ttl):
        print(i)
    print('End of Trace')

if __name__ == '__main__':
    main()


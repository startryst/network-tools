#!/usr/bin/env python3

import os
import sys
import trace_as
import fast
import routing


def menu():
    print("1) ASN Trace (Trace from your computer to given destination know the AS number for each hop)")
    print("2) Port Monitoring (To monitor a list of IP addresses for their service port reachability)")
    print("3) Routing to China (To add routes from APNIC to your computer for a secondary internet gateway")
    print("4) Fast Trace (To trace a target quickly")
    choice = input("Tools listed as above, please make your choice, [q] to exit: ")
    if choice not in ['1', '2', '3', '4', 'q']:
        os.system('clear')
        print("\nYour input is invalid, please re-enter your choice by number showing above \n")
        menu()
    elif choice is 'q':
        sys.exit()
    else:
        return choice


def main():
    print("\nWelcome to Bright's network tools collection! \n")
    while True:
        choice = menu()
        if choice == '1':
            print("\n")
            trace_as.main()
            print("\n")
        elif choice == '2':
            print("\n")
            print("Only runs under python 2.x")
            print("\n")
        elif choice == '3':
            print("\n")
            routing.main()
            print("\n")
        else:
            print("\n")
            fast.main()
            print("\n")

if __name__ == '__main__':
    main()

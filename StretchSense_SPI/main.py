#!/usr/bin/env python3
from __future__ import print_function
import stretchSenseLibrary


stretchsenseObject = stretchSenseLibrary.StretchSenseAPI()


def main():
    print("Main()")

    stretchsenseObject.spiSetup()
    while(1):
        stretchsenseObject.continuousModeCapacitanceToPrint()
    stretchsenseObject.closeSpi()

if __name__ == "__main__":
    main()
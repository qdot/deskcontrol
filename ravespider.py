#################################################################
# python amBX controller object
# By Kyle Machulis <kyle@nonpolynomial.com>
# http://www.nonpolynomial.com
#
# Distributed as part of the libambx project
#
# Website: http://qdot.github.com/libambx
# Repo: http://www.github.com/qdot/libambx
#
# Licensed under the BSD License, as follows
#
# Copyright (c) 2009, Kyle Machulis/Nonpolynomial Labs
# All rights reserved.
#
# Redistribution and use in source and binary forms, 
# with or without modification, are permitted provided 
# that the following conditions are met:
#
#    * Redistributions of source code must retain the 
#      above copyright notice, this list of conditions 
#      and the following disclaimer.
#    * Redistributions in binary form must reproduce the 
#      above copyright notice, this list of conditions and 
#      the following disclaimer in the documentation and/or 
#      other materials provided with the distribution.
#    * Neither the name of the Nonpolynomial Labs nor the names 
#      of its contributors may be used to endorse or promote 
#      products derived from this software without specific 
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#################################################################

import sys

#Requires PyUSB
#http://pyusb.berlios.de/

import usb

class RaveSpider:
    
    #Device as retreived from the bus listing
    RaveSpiderDevice = None
    #Handle to access the device with
    RaveSpiderHandle = None

    #VID/PID for RaveSpider Controller
    RAVESPIDER_VENDOR_ID = 0x1964
    RAVESPIDER_PRODUCT_ID = 0x0001
    
    #Constructor
    def __init__(self):
        return

    def open(self, index = 0):
        """ Given an index, opens the related ambx device. The index refers
        to the position of the device on the USB bus. Index 0 is default, 
        and will open the first device found.

        Returns True if open successful, False otherwise.
        """
        device_count = 0
        for bus in usb.busses():
            devices = bus.devices
            for dev in devices:
                if dev.idVendor == self.RAVESPIDER_VENDOR_ID and dev.idProduct == self.RAVESPIDER_PRODUCT_ID :
                    if device_count == index:
                        self.RaveSpiderDevice = dev
                        break
                    device_count += 1
        if self.RaveSpiderDevice is None:
            print "Returning!"
            return False
        self.RaveSpiderHandle = self.RaveSpiderDevice.open()
        self.RaveSpiderHandle.setConfiguration(1)
        self.RaveSpiderHandle.claimInterface(0)
        return True

    def close(self):
        """Closes the device currently held by the object, 
        if it is open."""
        if self.RaveSpiderHandle is not None:
            self.RaveSpiderHandle.releaseInterface() 
            self.RaveSpiderHandle = None

    def setSpeed(self, command):
        """Given a list of raw bytes, writes them to the out endpoint of the
        ambx controller.

        Returns total number of bytes written.
        """
        self.RaveSpiderHandle.controlMsg(usb.ENDPOINT_IN | usb.TYPE_VENDOR | usb.RECIP_DEVICE, 5, 0, command, 0, 5000)

def main(argv=None):
    RaveSpiderDevice = RaveSpider()
    RaveSpiderDevice.debug = True
    if RaveSpiderDevice.open() is False:
        print "No ambx device connected"
        return

    #Some things you can do
    RaveSpiderDevice.setSpeed(255)
    RaveSpiderDevice.close()
    
if __name__ == "__main__":
        
    sys.exit(main())

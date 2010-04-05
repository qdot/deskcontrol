import serial
import time
import sys
import usb
import logging

class SimpleFTDI:
    _device = None

    def __init__(self):
        return

    def open(self, vendorId, productId):
        self._device = usb.core.find(idVendor = vendorId, idProduct = productId)
        if self._device is None:
            return False
        self._device.set_configuration(1)
        return True
    
    def close(self):
        return

    def write(self, value):
        self._device.write(0x02, value)
        return

    def read(self, size, value):
        # issue read
        v = self._device.read(0x81, size + 2, 0, 100)
        # strip modem bits
        if len(v) > 2:
            value = v[2:]
        else:
            print "Nothing Read"
    
class StockArduinoFTDI(SimpleFTDI):
    def open(self, vendorId, productId):
        SimpleFTDI.open(self, vendorId, productId)
        # Sleep for 5 seconds while we wait for the firmware to reboot. 
        # I hate you, arduino.
        logging.info("Waiting on arduino to reboot")
        time.sleep(5)

class FTDIDeskLight(StockArduinoFTDI):
    def open(self):
        StockArduinoFTDI.open(self,0x0403, 0x6001)
        
    def setSpeed(self, index, speed):
        command = ''.join([chr(index), chr(speed), chr(0)])
        self.write(command)
        time.sleep(.001)

    def resetCommunication(self):
        self.setSpeed(0xff, 0xff);
        return 
    
def main():
    d = FTDIDeskLight()
    d.open()
    d.setBaudRate(9600)
    d.setSpeed(0, 255)
    d.setSpeed(1, 255)

if __name__ == "__main__":
    sys.exit(main())
    

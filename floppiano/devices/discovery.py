from threading import Thread, Event
import floppiano.bus as bus
from floppiano.devices.drives import DEVICE_TYPE, DEVICE_TYPE_REG

class DeviceDiscovery(Thread):
    """
        A Thread to find drives and the keyboard on the I2C bus
    """

    def __init__(self) -> None:
        Thread.__init__(self)

        self._stop_event = Event()
        self._drive_addresses = []
        self._keyboard_address = None
    
    def run(self) -> None:
        # ping all i2c devices from from 0x8 to 0x77 and get their device type, 
        # if the type is correct add it to the list
        for address in range(0x8, 0x77+1):
            if self._stop_event.is_set(): break
            try:
                response = bus.read(address, DEVICE_TYPE_REG, 1)[0]
                if response == DEVICE_TYPE: 
                    self._drive_addresses.append(address)
                # if response == 55: #TODO fix this to match keyboard 
                #     self._keyboard_address = address
            except Exception:
                # Don't let any exceptions happen. Either due to the bus
                # otherwise.
                pass

    def quit(self):
        self._stop_event.set()

    def get_devices(self) -> tuple[list[int], int]:
        """
            Returns the devices found on the I2C bus
        Raises:
            Exception: If the DeviceDiscovery is still working
        Returns:
            tuple[list[int], int]: A list of drive addresses and the keyboard 
            address
        """
        if self.is_alive():
            raise Exception("DeviceDiscovery not finished")
        
        return (self._drive_addresses, self._keyboard_address)
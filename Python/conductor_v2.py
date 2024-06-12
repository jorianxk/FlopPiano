from mido import Message

class Conductor():

    def __init__(self) -> None:

        
        #Instruments immutable set
        #Active Instruments
        #Available Instruments
        #modulation (amount)= int
        #pitch_bend (amount) = int
        #pitch bend mode
        
        #input_channel int [015]
        #Output mode
        #output_channel int [0-15]
        
        #keyboard = Keyboard object
        #do_keyboard = bool
        #loopback = bool        
        #keyboard octave = int [??-??]

        pass

    def conduct(self, messages:list[Message])->list[Message]:
        pass

    def silence(self):
        pass


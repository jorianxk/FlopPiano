from threading import Thread, Event
from queue import Queue, Empty, Full


from mido.ports import BaseInput, BaseOutput
from mido import Message, MidiFile

from jidi.synths import Synth
from jidi.midi import MIDIParser
import mido
import logging

class SynthService(Thread):

    def __init__(
            self, 
            synth:Synth, 
            incoming_size:int = 100, 
            outgoing_size:int =100):
        Thread.__init__(self)

        #synth to pump
        self._synth = synth
        #stop flag
        self._stop_event = Event()
       
        # outgoing queue -We don't know if the user will consume outgoing 
        # messages but incoming messages we consume as soon as possible.        
        self._incoming_q = Queue(incoming_size)
        self._outgoing_q = Queue(outgoing_size)

    def run(self):
        #do this until stop flag is set
        while not self._stop_event.is_set():
            incoming_messages = []
            try: incoming_messages.extend(self._incoming_q.get_nowait())
            except Empty: pass

            outgoing_messages = self._synth.update(incoming_messages)

            if len(outgoing_messages)>0:
                try:
                    self._outgoing_q.put_nowait(outgoing_messages)
                except Full: pass #if full ignore
        #reset the synth before stopping        
        self._synth.reset()

    def quit(self):
        """_summary_
            Stop the Service Thread
        """
        self._stop_event.set()

    def get(self, **kwargs)->list[Message]:
        return self._outgoing_q.get(**kwargs)

    def put(self, messages:list[Message] ,**kwargs):
        self._incoming_q.put(messages,**kwargs)

class PortService(SynthService):

    def __init__(
            self,
            synth: Synth,
            service_type:str = 'physical', 
            input_hint:str = 'USB', 
            output_hint:str = 'USB', 
            **kwargs):

        # Get the service type
        if service_type != 'physical' and service_type!='virtual':
            raise ValueError("Service type must be 'physical' or 'virtual'")
        #TODO: add virtual support
        if service_type == 'virtual': 
            raise NotImplementedError('virtual service not implemented')

        # Set up ports
        self._inport:BaseInput = mido.open_input(
            PortService._find_port(input_hint, mido.get_input_names()))

        self._outport:BaseOutput = mido.open_output(
            PortService._find_port(output_hint, mido.get_output_names()))
        
        #All above went well, so we're good to start
        
        self._inport_enable = Event()
        self._inport_enable.set()
        self._outport_enable = Event()
        self._outport_enable.set()

        SynthService.__init__(self, synth, **kwargs)


    def run(self):
        self.exc = None
        try:
            #do this until stop flag is set
            while not self._stop_event.is_set():
                incoming_messages:list[Message] = []
                outgoing_messages:list[Message] = []

                #get any incoming messages from the application
                try: incoming_messages.extend(self._incoming_q.get_nowait())
                except Empty: pass

                #TODO exception if the port is closed
                #Get the messages from the input port
                if(not self._inport.closed): 
                    input_msg = self._inport.receive(block=False)
                    #only add them if we are inport is enabled
                    if input_msg is not None and self._inport_enable.is_set():
                        incoming_messages.append(input_msg)

                outgoing_msgs = self._synth.update(incoming_messages)

                if len(outgoing_messages)>0:
                    #try to write the outgoing messages to the output port
                    #TODO exception if the port is closed
                    if (not self._outport.closed) and self._outport_enable.is_set():
                        for msg in outgoing_msgs:
                            self._outport.send(msg)
                    #Return any output messages to the application
                    try:
                        self._outgoing_q.put_nowait(outgoing_messages)
                    except Full: pass #if full ignore
                    
            #Reset the synth before stopping
            self._synth.reset()
        except Exception as e:
            self.exc = e

    def join(self, timeout: float | None = None) -> None:
        super().join(timeout)
        if self.exc:
            raise self.exc

    @property
    def inport_enable(self):
        return self._inport_enable.is_set()

    
    @inport_enable.setter
    def inport_enable(self, enable:bool):
        if enable:
            self._inport_enable.set()
        else:
            self._inport_enable.clear()
    
    @property
    def outport_enable(self):
        return self._outport_enable.is_set()

    @outport_enable.setter
    def outport_enable(self, enable:bool):
        if enable:
            self._outport_enable.set()
        else:
            self._outport_enable.clear()


    @staticmethod
    def _find_port(hint:str, options:list[str])->str:
        for option in options:
            if option.startswith(hint.upper()):
                return option

        raise ValueError(f'Could not find port with hint: {hint.upper()}')
    


class MIDPlayerService(SynthService):

    def __init__(self, port_service:PortService, mid_file:str, transpose:int):
        
        #TODO Validate if file exists
        self._mid_file = mid_file
        self._transpose = transpose


        if not port_service.is_alive():
            raise ValueError("port_service is dead")

        self._port_service = port_service


        #All above went well, so we're good to start
        SynthService.__init__(self, None, 1, 1)
    

    def run(self):
        #only run if the port service is alive
        if self._port_service.is_alive():
            #disable midi inport from the inport 
            self._port_service.inport_enable = False

            for msg in MidiFile(self._mid_file).play():
                #stop if the port service is dead or if told to
                if (self._stop_event.is_set() or 
                    not self._port_service.is_alive()): break
                
                # apply the transpose
                if (msg.type == "note_on" or msg.type =="note_off"):
                    msg.note = msg.note + self._transpose
                
                # redirect all messages with a channel to the synth
                if MIDIParser.has_channel(msg):
                    msg.channel = self._port_service._synth.input_channel
                
                self._port_service.put([msg])
            

            #send a reset
            msg = Message(
                type = 'control_change',
                control = self._port_service._synth.control_change_map.code('reset'),
                value = 0,
                channel = self._port_service._synth.input_channel
            )
            self._port_service.put([msg])

            #re-enable inport
            self._port_service.inport_enable = True

        


# class MIDPlayerService(SynthService):

#     def __init__(self, synth: Synth, mid_file:str, transpose:int, **kwargs):
        
#         #TODO Validate if file exists
#         self._mid_file = mid_file
#         self._transpose = transpose
#         #All above went well, so we're good to start
#         SynthService.__init__(self, synth, **kwargs)

#     def run(self):
#         for msg in MidiFile(self._mid_file).play():
#             #Stop if commanded to
#             if self._stop_event.is_set():break

    
#             incoming_messages:list[Message] = []
#             outgoing_messages:list[Message] = []

#             #get any incoming messages from the application
#             try: incoming_messages.extend(self._incoming_q.get_nowait())
#             except Empty: pass

#             # redirect all messages with a channel to the synth
#             if MIDIParser.has_channel(msg):
#                 msg.channel = self._synth.input_channel

#             # apply the transpose
#             if (msg.type == "note_on" or msg.type =="note_off"):
#                 msg.note = msg.note + self._transpose
            
#             #add the mid file messages to the incoming
#             incoming_messages.append(msg)

#             #let the synth work 
#             outgoing_messages = self._synth.update(incoming_messages)
            
#             #return any messages back to the application
#             if len(outgoing_messages)>0:
#                 try:
#                     self._outgoing_q.put_nowait(outgoing_messages)
#                 except Full: pass #if full ignore

#         #reset the synth before stopping
#         self._synth.reset()


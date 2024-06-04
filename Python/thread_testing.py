from threading import Thread
from queue import Queue, Empty
import time




def player(msg_q_in:Queue, msg_q_out:Queue):

    
    while True:
        value:list = None
        try:
            value = msg_q_in.get(block=False)
        except Empty:
            pass
        
        time.sleep(1.5)

        if value is not None:
            print(f'Player thread in value:{value}')
            out:list = []
            
            for val in value:
                if val%2==0:
                    pass
                else:
                    out.append(val)
            
            out_q.put(out)



in_q = Queue()
out_q = Queue()

playerThread = Thread(target=player, daemon= True, args=(in_q, out_q))
playerThread.start()


while True:

    in_q.put([1,2,3,4,5,6,7,8,9,10])


    time.sleep(1)


    value:list = None
    try:
        value = out_q.get(block=False)
    except Empty:
        pass

    if value is not None:
        print(f'Main got: {value}')
    




#playerThread.join()

#in_q.join()
#out_q.join()
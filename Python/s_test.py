from FlopPiano.Service import Configuration, Service
import logging
import time
#write a config

# config = Configuration.default()
# with open("config.ini", 'w') as configfile:
#     config.write(configfile)

#read a config
#Configuration.read("config.ini")


# class Test():
#     def __init__(self, arg1:int, arg2:str="test") -> None:
#         print(arg1)
#         print(arg2)



# myargs = {"arg1":44, "arg2":"monkeys", "farts":23}


# Test(**myargs)






logging.basicConfig(level=logging.DEBUG)


cs = Service()
cs.start()

try:    

    while True: 
        time.sleep(1)
        print("Main:", "loop")

except KeyboardInterrupt as ke:
    print("Main:"," KeyboardInterrupt doing exit...")
finally:
    print("Main:","Issuing thread quit()")
    cs.quit()
    print("Main","Waiting for thread join()")
    cs.join()


    print("Main","Done.")



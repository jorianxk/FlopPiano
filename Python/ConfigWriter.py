from configparser import ConfigParser


config = ConfigParser()


config['Server'] = {
    'usb_input' : 'some string', # ??
    'usb_output': 'some string', # ??
    'log_file'  : 'some path',   # Any
    'log_level' : 'INFO'         # ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
}

config['Conductor'] = {
    'keyboard_address' : 0x77,      # [0x8-0x77]
    'loopback'         : False,     # [True, False]
    'input_channel'    : -1,        # [0-16]
    'output_channel'   : 0 ,        # [0-15]
    'output_mode'      : 'rollover' # 'rollover', 'keys', 'off'
}


for drive_num in range(1,11):
    config[f'Drive {drive_num}']={
        'address' : drive_num+7,  # [0x8-0x77]
        'tuning'  : '1,2,3,4,5,6' # TODO: depends on how we handle tuning
    }



with open("config.ini", "w") as f:
    config.write(f)


## dump for later


class Config():

    def __init__(self) -> None:
        pass
    
    @classmethod
    def default(cls) ->ConfigParser:
        config = ConfigParser()

        config['Server'] = {
            'usb_input' : 'some string', # ??
            'usb_output': 'some string', # ??
            'log_file'  : 'some path',   # Any
            'log_level' : 'INFO'         # ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        }

        config['Conductor'] = {
            'keyboard_address' : 0x77,      # [0x8-0x77]
            'loopback'         : False,     # [True, False]
            'input_channel'    : -1,        # [0-16]
            'output_channel'   : 0 ,        # [0-15]
            'output_mode'      : 'rollover' # 'rollover', 'keys', 'off'
        }

        for drive_num in range(1,11):
            config[f'Drive {drive_num}']={
                'address' : drive_num+7,  # [0x8-0x77]
                'tuning'  : '1,2,3,4,5,6' # TODO: depends on how we handle tuning
            }

        return config




import sys
from floppiano import FlopPianoGUI, FlopPianoCLI


#TODO read config
if __name__ == '__main__':  
    # Do we have arguments? If so, test if FlopPiano should be started without a 
    # UI
    if len(sys.argv)>1 and sys.argv[1] == "nogui":
        print("FLOPPIANO WITH NO UI")
    else:
        # FlopPiano should be started normally (with the UI)
        #logging.basicConfig(level=logging.DEBUG)
        #TODO add config loading
        FlopPianoGUI(
            theme='default',
            handle_resize=False,
            splash_start=False, 
            screen_timeout=30,
            asset_dir='./assets').run()
    
    
    

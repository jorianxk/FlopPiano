import sys
from floppiano.UI import FlopPianoApp

if __name__ == '__main__':  
    # Do we have arguments? If so, test if FlopPiano should be started without a 
    # UI
    if len(sys.argv)>1 and sys.argv[1] == "noui":
        print("FLOPPIANO WITH NO UI")
    else:
        # FlopPiano should be started normally (with the UI)
        #logging.basicConfig(level=logging.DEBUG)
        #TODO add config loading
        FlopPianoApp(
            theme='default',
            handle_resize=False,
            splash_start=False, 
            screen_timeout=30,
            asset_dir='./assets').run()
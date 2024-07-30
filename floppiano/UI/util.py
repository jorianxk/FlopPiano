from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene
from asciimatics.event import KeyboardEvent, Event

"""
     A collection of helper functions to aid in UI rendering
"""

def time2frames(time:float, frame_rate:int=20) -> int:
    """_summary_
        Converts a time (in seconds) to an integer number of frames
    Args:
        time (float): Time in seconds (or fractions of seconds)
        frame_rate (int, optional): the number of frames per second.
            Defaults to 20.

    Returns:
        int: The number of frames round(frame_rate*time) 
    """
    return int(round(frame_rate*time))


def keyboard_event_draw(screen:Screen, force:bool=False, repeat:bool = False) -> bool:
    """_summary_
        Draws the Screen only on Keyboard events or if forced.
    Args:
        screen (Screen): The Screen to be drawn
        force (bool, optional): If true the screen is forced to draw regardless 
            of keyboard events. Defaults false.
        repeat (bool, optional): If true the Screen will repeat any Scenes after
            they have finished. Defaults to false.

    Returns:
        bool: True if the screen rendered, false otherwise.
    """    
    # Only update/draw on keyboard events or if we force an update
    # bypass effect event handling so that all effects will get events
    #returns true if a draw actually occurred
    try:
  
        scene = screen._scenes[screen._scene_index]
        event = screen.get_event()
        # Only update on keyboard events or if we force an update
        if isinstance(event, KeyboardEvent) or force:
            screen._frame += 1
            # TODO: if forced the event might be none is that ok?
            # We want all effects to get events ..
            scene.process_event(event) 
            for effect in scene.effects:
                # Update the effect and delete if needed.
                effect.update(screen._frame)
                if effect.delete_count is not None:
                    effect.delete_count -= 1
                    if effect.delete_count <= 0:
                        scene.remove_effect(effect)

            screen.refresh()

     
            if 0 < scene.duration <= screen._frame:
                raise NextScene()
            return True
        
        return False
    except NextScene as e:
        # Tidy up the current scene.
        scene.exit()

        # Find the specified next Scene
        if e.name is None:
            # Just allow next iteration of loop
            screen._scene_index += 1
            if screen._scene_index >= len(screen._scenes):
                if repeat:
                    screen._scene_index = 0
                else:
                    raise StopApplication("Repeat disabled") from e
        else:
            # Find the required scene.
            for i, scene in enumerate(screen._scenes):
                if scene.name == e.name:
                    screen._scene_index = i
                    break
            else:
                raise RuntimeError(f"Could not find Scene: '{e.name}'") from e

        # Reset the screen if needed.
        scene = screen._scenes[screen._scene_index]
        scene.reset()
        screen._frame = 0
        screen._idle_frame_count = 0
        if scene.clear:
            screen.clear()

        #force the screen to update
        #TODO make sure there is no infinite recursion
        return keyboard_event_draw(screen, force=True)

from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication, NextScene



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


def event_draw(screen:Screen, event=None, repeat = False):    

    scene = screen._scenes[screen._scene_index]

    #TODO: think about the below
    if screen.has_resized(): 
        raise ResizeScreenError("Screen resized", scene)

    try:
        # Check for an event now and remember for refresh reasons.
        #JORIAN commented out the below line
        #event = screen.get_event()
        
        got_event = False
        if event is not None:
            event = scene.process_event(event)
            got_event = True

        # got_event = event is not None
        # # Now process all the input events
        # while event is not None:
        #     event = scene.process_event(event)
        #     if event is not None and screen._unhandled_input is not None:
        #         screen._unhandled_input(event)
        #     event = screen.get_event()

        # Only bother with a refresh if there was an event to process or
        # we have to refresh due to the refresh limit required for an
        # Effect.

        screen._frame += 1
        screen._idle_frame_count -= 1
        #if got_event or screen._idle_frame_count <= 0 or screen._forced_update:
        screen._forced_update = False
        screen._idle_frame_count = 1000000
        for effect in scene.effects:
            # Update the effect and delete if needed.
            effect.update(screen._frame)
            if effect.delete_count is not None:
                effect.delete_count -= 1
                if effect.delete_count <= 0:
                    scene.remove_effect(effect)

            # Sort out when we next _need_ to do a refresh.
            if effect.frame_update_count > 0:
                screen._idle_frame_count = min(screen._idle_frame_count,
                                                effect.frame_update_count)
        screen.refresh()
        
        if 0 < scene.duration <= screen._frame:
            raise NextScene()
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

        #TODO make sure there is no infinite recursion
        event_draw(screen)


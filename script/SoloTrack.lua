local track_number = 1
local debounce_interval = 0.5 -- Set debounce time in seconds
local last_toggle_time = 0    -- Store the last toggle timestamp

function ToggleSolo()
    local track = reaper.GetTrack(0, track_number - 1) -- Get track 0-based index, from current project

    if track then
        local solo_state = reaper.GetMediaTrackInfo_Value(track, "I_SOLO")
        reaper.SetMediaTrackInfo_Value(track, "I_SOLO", solo_state == 0 and 1 or 0)
    end
end

function KeyCheck()
    local retVal, midi_msg = reaper.MIDI_GetRecentInputEvent(0)

    -- Check if a MIDI message was received
    if retVal then
        local status = midi_msg:byte(1)
        local data1 = midi_msg:byte(2)
        local data2 = midi_msg:byte(3)

        -- Get current time
        local current_time = reaper.time_precise()

        -- Check if the message is a note on message
        if status == 0x90 and data1 == 60 and data2 > 0 then
            -- Check if the debounce interval has passed
            if current_time - last_toggle_time > debounce_interval then
                ToggleSolo()
                last_toggle_time = current_time
            end
        end
    end

    reaper.defer(KeyCheck)
end

-- Start the script
if not reaper.JS_VKeys_GetState then
    reaper.MB("This script requires the SWS/S&M extension. Please install it and try again.", "Error", 0)
    return
end

KeyCheck()

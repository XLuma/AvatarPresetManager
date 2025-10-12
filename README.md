### AvatarPresetManager
This piece of software allows you to create snapshots of your avatar state, and restore it at any moment. It uses VRChat OSC to function.

## TODO
- Figure out a proper way to prevent the data folder from resetting itself when a new executable is generated
- Add rename feature (preset names, avatar id association)
- config generator
- Updater program
- Python code cleanup

## Known issues
- Switching into an avatar only works if that avatar is favorited. [This is due to a VRChat bug](`https://feedback.vrchat.com/avatar-30/p/1626-osc-avatar-change-is-not-working`)
- VRChat discovery, once online, seems to not detect properly if the game is offline
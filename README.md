### AvatarPresetManager
This piece of software allows you to create snapshots of your avatar state, and restore it at any moment. It uses VRChat OSC to function.

## TODO
- Add rename feature

- Make it so port scanning happens at all time, not just program startup (make it so ui loads even without it)
- Start vrchat button (could load preset once the game loads ??)
- config generator ?
- Updater program
- Python code cleanup
- Once cleanup is done, rewrite in nodejs + electron

## Known issues
- Switching into an avatar only works if that avatar is favorited. [This is due to a VRChat bug](`https://feedback.vrchat.com/avatar-30/p/1626-osc-avatar-change-is-not-working`)
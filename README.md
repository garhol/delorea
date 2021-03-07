# Delorea
Python &amp; Pygame racing game launcher


## Initial setup

Install python - https://www.python.org/

Check if you have pip installed

Open a command prompt/terminal and enter
```
python -m pip --version
```

If you don't have pip then grab with 
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```
or download
https://bootstrap.pypa.io/get-pip.py

From the folder where you downloaded get-pip run the following in your terminal
```
python get-pip.py
```

From the delorea folder in your terminal run 
```
pip install -r requirements.txt
```

## Setting up your emulators

Copy the sample-config.py and games.json from the delorea folder.
Drop them both in the config folder and remove the "sample-" from the names

The list of emulators should contain the name of the emulator (currently AM2, AM3 or Mame)
and the name of the binary/executable
```
'AM2': 'EMULATOR.EXE',
```

Each emulator listed should have a corresponding entry in paths with a trailing slash
```
'AM2': 'D:/Games/m2emulator/',
```
*Note: windows users, the `/` character is used and will automatically be converted*
*for your system. If you use `\` then remember that the last `\` must be doubled `\\`*


**Setting up your games and roms**

In games.json follow the examples given:

- **Native PC games**
   ```
	{
	 "name" : "Flatout 2",
	 "system" : "IBM PC",
	 "screenshot" : "flatou2",
	 "working_dir" : "C:/Program Files (x86)/Steam/steamapps/common/FlatOut2/",
	 "binary" : "FlatOut2.exe"
	},
    ```
   *Again, use `/` as separators*

- **AM2/AM3/Mame**
    ```
    {
      "name" : "Daytona USA",
      "system" : "AM2",
      "screenshot" : "daytona",
    },
    ```
    *For Nebula, Supermodel and Mame/Mame64 the screenshot name should the same as the rom name.*

    *Provide a screenshot of the same name in the screens directory or leave blank for the default*

## Controls
The following controls are mapped by default
```
Left arrow- Select previous
Right arrow - Select next game
Enter - Select game
Space - Update quote

Up arrow - display fps ( there you go @craigbutcher )
```

## Configuring joysticks
By default the first joystick is selected
In config.py you can set your joystick buttons or axis (and axis for pretending to drive)
```
controls = {
    'steering': 0,
    'gameup': 10,
    'gamedown': 9,
    'gameselect': 1,
    'quit': 7
}
```
*The default settings are for a G27 wheel with paddles for selecting games and the top thumb buttons for quit(left) and select(right)

**To report the axis and buttons for your joystick run**
```
python joystickConfig.py
```
Press any button or move an axis (beyond about 60%) to display the reported value

## You're done.

```python delorea.py``` or create a symlink

*Issues and bugs can be raised on the project board*


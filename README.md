# Advanced Clash Launcher
A command-line app for various TT:Corporate Clash manipulations.
Launching multiple toons, freezing toons, finding zap combos using screen recognition and more. 

## Installation
* Install TT:Corporate Clash.
* Install python 3.X (I don't know what version is needed, I think 3.7 or higher).
* Clone this project.
* ``pip install -r requirements.txt``

## Configuration
The `config.py` file contains sensible defaults. In particular:
* The launcher is located under `%user%\Appdata\Local\Corporate Clash`
* The account file is located in the project root
* The multicontroller is also located in the project root
* The default district is Seltzer Summit

You likely don't need to change this file.
However, you do need to create an `accounts.yml` file in the project root.
You can edit it with any text editor. The syntax is googlable (YAML format), and
the structure of that file is explained in the provided example file.
The launcher supports any number of accounts.

## Operation
Running `main.py` will launch a cmd-like interface with a bunch of functions:
* `launch` or `lc` starts any number of toons at the same time: `lc alias1 alias2 alias3`
will launch these 3 toons, provided they exist in accounts file. It's smart and won't
let you start the same account multiple times unless you close the old window
(but it will let you start it once if you already started it with other launcher).
The toons all are started in the current district (which is Seltzer Summit by default).
* `district` or `ds` changes the current district. It only affects future toons logging in,
not the ones already started.
* `multicontroller` or `mc` starts the multicontroller, or focuses it if it's already started.
It works with any multicontroller (or even any application - you could set the mc path to notepad
or anything if you wanted to).
* `disconnect` or `dc` disconnects any number of toons, as if you closed the windows.
* `freeze` will *freeze* a toon for a specified time. This is not recommended:
  * Each 30 seconds, the server sends the Heartbeat request. If a toon does not respond
  twice in a row, it will get disconnected. So freezing for more than 30 sec. can
  force a dc.
  * Freezing prevents all damage done to the toon from some sources. The most popular one
  is CFO gears. Mods don't like this and might get you banned if you freeze in a CFO.
  * People don't like waiting for you to unfreeze. There's currently no way to unfreeze other
  than waiting the specified time amount.
  * If the launcher crashes, the toon will remain frozen indefinitely, which will cause a DC.
* You still can use `freeze`, but only at your own risk. Don't report me for adding this
function if you get banned for it or if you dc from a boss or anything.
* `zap` will find a zap combo for a specific set. Each cog can be determined by level or HP.
  * Example of using this: `zap 12e 180 15 212` will show smth like "Tesla Cloud TV Cloud"
  * Experimental feature. DM all bugs to me on Discord.
* `recognize` or `cr`: finds all toons connected which are currently in a battle, and prints
the HP values of each cog in battle using screen recognition.
  * Only works on Full HD, HD and 960x540 window sizes. Might work on others but untested.
  * If you need it to work on small window sizes (HD and below) which aren't implemented,
  you can teach it. The explanation is written below.
  * You don't need to pass any arguments. If you don't (run it like `cr`),
  the raw values from the CR will be returned. If you do (run it like `cr 1`),
  the values from sanitizer will be returned. (For example, if CR returns `(272, 27)`,
  the sanitizer will detect that 27 isn't a valid HP value, and turn it into `(272, 272)`.)
  * In some cases returns wrong values. Report any issues you find.
  Running this command like `cr debug` will enable debug mode - use it for reports
  (this will return the unsanitized values).
* `rcombos` or `rc`: uses screen recognition to get all battles, and finds zap combo for each.
  * Another experimental feature. It seems to mostly work, but report all bugs to me.
  * This is how it looks:
  ![rcombos command](https://media.discordapp.net/attachments/839954064980836382/910484196206739476/unknown.png)

## Future additions
* Improve the calculator to add other kinds of combos.
* Make zap calculator more efficient, and allow it to use lv 1-4 gags.
* An improved multicontroller.
* Improve damaged cog handling.
* An option to automatically use the combos detected.
* Improved quad toon handling, and toon build knowledge.
* Automatic detection of gags used by other toons.

## Advanced usage
### Under the hood
The screen recognition finds green/yellow/red rectangles on the screen. That's the easy part.
Then it tries to read the digits from those rectangles. The hard part.

With large display resolutions (larger than HD), a topological digit detector (TDD) is used.
It mostly looks whether the "white space" is connected or not and how many components it has.
For example, the digit "8" has 3 components (1 outside and 2 inside), and that uniquely determines it.
Applying similar checks to all 10 digits gives the one most likely to be in the image.

With small display resolutions, that doesn't work, unfortunately. (It works fine for HD, but
not great with multiple cogs.) So instead, a comparative digit detector (CDD) is used.
The files under `learning` contain learning data for them, and the closest "image" is used.
Currently, the files with heights 6 (for 960x540) and 9 (for HD) are included.
There's no self-improving unlike neural networks, so all learning has to be done manually.

### Training CDD
To train CDD, run the CR on multiple cogs in debug mode. Every time, a string like this 
is printed:
```
.o.o.
o...o
o...o
o...o
o..o.
.ooo.
```
Some strings will be bugged and not correspond to any digits. Ignore them. Take the ones
that you consider not bugged, and add them to a file in the `learning` directory.
Then add that file to the `code/numbers/similarity.py` file if it's not added yet.
The files in that directory have the following structure:
```
<string_from_debug>
<number> <multiplier?>

<string_from_debug 2>
<number 2> <multiplier 2?>

etc.
```
The `number` is an integer the number which the string should be considered.
The `multiplier` is a floating point number - it's usually not needed and defaults to 1.
When the string's difference to the string in game is found, it's multiplied by that number.
So the higher the multiplier is, the more exact the match must be.

After each record in the file (including the last one), two blank lines must be present.
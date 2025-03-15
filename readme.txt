VARIOUS INFOS

The .exe file doesn't requires Python

If you want to use the Python code, refer to the Python readme.

the .txt in DataDic must be named same as corresponding png, and content follow this format:
TheFingersHex : [(0, 0), (0.5, 0.5)]

You can layer multiples .png for the same item, they will all be applied.

Clashtra is weird, it follows a different naming scheme in game files, stick to it!
Deadlands has a minus L in gamefiles, but capital L in api, stick to Deadlands for naming files, not DeadLands

The APIbased layer can't work if ABLE is not at war, there isn't a proper backup file at the moment

Correction_in_meters.txt must follow this format:
84 : (-5;5), number being the icon number (refer to table)

100m = roughtly 94px (on a 2048x1776px basis)

Application order of layers is :
- Layer specific
- Global
- API based items
- Custom dic based items

You can bundle up map elements in the item_codes.json, so different API element share the same "name" and .png.

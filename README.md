# harmonize-tunnify-inflection
A FontForge plug-in to harmonize or tunnify or add inflection points to the selected parts. 
This is the predecessor to the [Curvatura](https://github.com/linusromer/curvatura) plugin.
I strongly recommend using [Curvatura](https://github.com/linusromer/curvatura) over `harmonize-tunnify-inflection`
because `harmonize-tunnify-inflection` will not be updated.

## Prerequisites
On Linux you must have installed Python along with FontForge. On Windows FontForge embeds an own version of Python. Hence, you do not have to install Python additionaly.

## Installation
According to the documentation of FontForge you have to copy the file harmonize_tunnify_inflection.py to 
`$(PREFIX)/share/fontforge/python` or `~/.FontForge/python` but for me (on Ubuntu) it works at
`~/.config/fontforge/python` and for Windows it might be at
`C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python`.

## New Tools added by harmonize-tunnify-inflection
After installation, FontForge will show in the Tools menu 4 new entries: "Harmonize", "Harmonize handles" ,"Tunnify (balance)", "Add points of inflection". The first three tools are all some kind of smoothing the bezier curves. Their effects are visualized in the following image (you will not see the light blue curvature combs in FontForge, they have been added here for documentation reasons):

<img width="1227" alt="tools for cubic beziers" src="https://user-images.githubusercontent.com/11213578/69705892-bf8e6180-10f6-11ea-8548-98135bf1b28e.png">

The last tool ("Add points of inflection") adds points of inflection (FontForge can natively display them but not natively add them):

<img width="520" alt="inflection point" src="https://user-images.githubusercontent.com/11213578/69705891-bef5cb00-10f6-11ea-9ccd-5f4a0c57fd9f.png">

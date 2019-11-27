# harmonize-tunnify-inflection
A FontForge plug-in to harmonize or tunnify or add inflection points to the selected parts.

## Prerequisites
Under Linux you must have installed Python along with FontForge. Under Windows FontForge embeds an own version of Python. Hence, you do not have to install Python additionaly.

## Installation
According to the documentation of FontForge you have to copy the file harmonize_tunnify_inflection.py to 
`$(PREFIX)/share/fontforge/python` or `~/.FontForge/python` but for me (on Ubuntu) it works at
`~/.config/fontforge/python` and for Windows it might be at
`C:\Users\[YOUR USERNAME HERE]\AppData\Roaming\FontForge\python`.

## New Tools added by harmonize-tunnify-inflection
After installation, FontForge will show in the Tools menu 4 new entries: "Harmonize", "Harmonize handles" ,"Tunnify (balance)", "Add points of inflection". The first three tools are all some kind of smoothing the bezier curves. Their effects are visualized in the following image (you will not see the light blue curvature combs in FontForge, they have been added here for documentation reasons):

![curvature-comb-doc1](https://user-images.githubusercontent.com/11213578/69705892-bf8e6180-10f6-11ea-8548-98135bf1b28e.png)

The last tool ("Add points of inflection") adds points of inflection (FontForge can natively display them but not natively add them):

![curvature-comb-doc2](https://user-images.githubusercontent.com/11213578/69705891-bef5cb00-10f6-11ea-9ccd-5f4a0c57fd9f.png)





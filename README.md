## Voronota version 1.19

You can download the latest archive from the official downloads page: https://bitbucket.org/kliment/voronota/downloads
Voronota is developed by Kliment Olechnovic (kliment@ibt.lt)

## Vcontacts installation guide

```
1) download vcontacts.zip
2) extract vcontacts.zip
3) go to vcontacts directory
4) voronota installation guide is in the voronota1.19 folder
4) After install voronota, set VORONOTA_EXE variable in Server/config.init to realm path to voronota executable 
```
## To run server
You can run it via python interpreter: python /PATH/TO/server.py
Or you can make it executable: chmod +x /PATH/TO/server.py
and run it: ./PATH/TO/server.py

## Vcontacts.py
Type in PyMOL console
```
run PATH/TO/Vcontacts.py
```

Or configurate your pymolrc file

1) On Windows: Start > Run and then paste notepad "%HOMEDRIVE%%HOMEPATH%\pymolrc.pml"

2) On Unix/Linux-type system (including Mac OS X): Open a terminal and type
nano ~/.pymolrc

and paste:
```
run PATH/TO/Vcontacts.py
```

## Help
```
For help type in PyMOL console: help Vcontacts
```

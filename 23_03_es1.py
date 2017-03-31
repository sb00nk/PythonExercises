"""
Esercizio 1: ricerca dei percorsi dei file a partire da una cartella
python3 23_03_es1.py <cartella_di_partenza>
"""
import os
import sys
import pathlib
import stat

def insert_dict(dictlink, key, value):
    """
    Inserisce un nuovo elemento nel dizionario rispettando il default
    """
    if key not in dictlink:
        dictlink[key] = list()
    dictlink[key].append(value)

def main():
    """
    Funzione principale, analizza gli input, calcola gli output, fa tutto lei
    """
    if len(sys.argv) < 2:
        print("Please provide the directory to analyze")
        return
    elif len(sys.argv) > 2:
        print("Too many arguments, please provide only the directory")
        return
    elif not pathlib.Path(sys.argv[1]).is_dir():
        print("Provide a valid path, please")
        return

    rootdir = pathlib.Path(sys.argv[1])
    allfiles = [str(pathfile) for pathfile in rootdir.glob('**/*')]

    dictlinks = dict()
    for pathfile in allfiles:
        inodenum = os.stat(pathfile, follow_symlinks=True)[stat.ST_INO]
        if os.path.islink(pathfile):
            insert_dict(dictlinks, inodenum, "s   " + pathfile)
        else:
            insert_dict(dictlinks, inodenum, "h   " + pathfile)

    for keyval in dictlinks:
        for pathval in sorted(dictlinks[keyval]):
            print(pathval)
        print("##########################")

if __name__ == '__main__':
    main()

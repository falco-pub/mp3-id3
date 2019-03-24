#!/usr/bin/python3

import subprocess, shlex, os, unicodedata, taglib, multiprocessing, argparse
from configparser import ConfigParser

norm = lambda x: unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode().replace("'", " ").replace('"', ' ')
str_to_list = lambda x: [y for y in x.splitlines() if y]


def parse_arg_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inifile", help="config .ini file")
    parser.add_argument("-n", help="dry run", action="store_true")
    parser.add_argument("-w",
                        help="write a sample config file (inifile must not exist)",
                        action="store_true")
    return vars(parser.parse_args())

def parse_inifile(f):
    c = ConfigParser()
    c.read(f)
    cd = c['DEFAULT']
    obj = type("", (), {})()
    obj.titles = str_to_list( cd['titles'] )
    obj.album = cd['album']
    obj.year = cd['year']
    obj.artist = cd['artist']
    obj.offset = int(cd['offset'])
    return obj

def sample_id3():
    d = type("", (), {})()
    d.titles = ["Titre 1", "Titre 2", "Titre 3"]
    d.album = "My album"
    d.year = "1234"
    d.artist = "My artist"
    d.offset = 1
    return d

def w_inifile(id3, path):
    with open(path, 'x') as f:
        c = ConfigParser()
        d = {
            'titles': "\n".join(id3.titles),
            'album' : id3.album,
            'year'  : id3.year,
            'artist': id3.artist,
            'offset': id3.offset,
        }
        c['DEFAULT'] = d
        c.write(f)

def p_id3(id3):
    print("artist = %s\nalbum=%s\nyear=%s\ntitles=\n %s" % (
        id3.artist, id3.album, id3.year, "\n ".join(id3.titles) ) )


def do_cmd(i, o, fmt):
    if os.path.exists(o):
        raise FileExistsError
    if fmt == 'flac':
        cmd = 'flac -s --best "%s" -o "%s"' % (i, o)
    elif fmt == 'mp3':
        cmd = 'lame --quiet --preset 192 "%s" "%s"' % (i, o)
    else:
        raise LookupError
    print("Encoding %s" % o)
    subprocess.run(shlex.split(cmd))

def do_id3(f, _n, id3, title):
    print("ID3 on %s, track %s, title %s" % (f, _n, title))
    s = taglib.File(f)
    s.tags["ALBUM"]  = id3.album
    s.tags["ARTIST"] = id3.artist
    s.tags["DATE"]   = str(id3.year)
    s.tags["TRACKNUMBER"] = '%s/%s' % (_n, len(id3.titles))
    s.tags["TITLE"]  = title
    print("%s --> %s" % (f, s.tags))
    s.save()

def do_file(dirname, fmt, n, id3):
    _n = str(n+id3.offset).zfill(2)
    wavname = "track%s.cdda.wav" % _n
    fname = "%s - %s" % (_n, norm(id3.titles[n]))
    outfile = dirname+"/"+fmt+"/"+fname+"."+fmt
    if not os.path.isfile(wavname):
        raise FileNotFoundError(wavname)
    try:
        do_cmd(wavname, outfile, fmt)
    except FileExistsError:
        print("%s already exists" % outfile)
    do_id3(outfile, _n, id3, id3.titles[n])


def main(id3):

    dirname = norm(id3.album)

    try:
        os.makedirs(dirname+"/mp3")
    except FileExistsError:
        pass
    try:
        os.makedirs(dirname+"/flac")
    except FileExistsError:
        pass

    for n in range(len(id3.titles)):
        p = multiprocessing.Process(target=do_file, args=(dirname, 'mp3', n, id3)).start()
        p = multiprocessing.Process(target=do_file, args=(dirname, 'flac', n, id3)).start()



if __name__ == "__main__" and not __doc__:
    args = parse_arg_main()
    id3 = sample_id3() if args['w'] else parse_inifile(args['inifile'])
    if args['n']:
        p_id3(id3)
    elif args['w']:
        w_inifile(id3, args['inifile'])
    else:
        main(id3)




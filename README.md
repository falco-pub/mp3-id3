Convert WAV files (from cdparanoia) to FLAC and MP3 files, with ID3 tags

### Example usage
    docker run --rm -v "$PWD:/wd" mp3 my_album.ini

```shell
  usage: mp3-id3.py [-h] [-n] [-w] inifile
  
  positional arguments:
    inifile     config .ini file
  
  optional arguments:
    -h, --help  show this help message and exit
    -n          dry run
    -w          write a sample config file (inifile must not exist)
```

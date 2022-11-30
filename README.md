# multithreaded file downloader

Downloads anything with a direct url to a file by splitting up the download into chunks and downloading each chunk with a seperate request to bypass download throttling. Good for those sites that have a download speed limit of 500kb, this should bypass that.

# args:

```
  --url -u <url>                        needs a direct url to a file/video/etc (ex: https://www.example.com/video.mp4)
                                        will try to get a url from your clipboard if this arg isnt passed
  --filename -f <filename>              if not passed, will get a filename from the url
  --save_path -o <path>                 (preset is your downloads folder if arg not passed) (ex: C:/users/administrator/downloads)
  --chunk_size -cs <num>                size of chunk the download will be split up to (num * 1MB) (ex: 0.5 * 1MB = 500kb chunk size)
                                        if not passed, will be 500kb
  --concurrent_downloads -cs <num>      number of concurrent downloads (preset is 20 if arg not passed)
  --verbose -v                          shows debug info
  --uid -uid                            sets the file name to a generated UUIDv4
  --clean -cl                           overwrites old download attempts
```

# example:

```
  dlf.py -u https://www.example.com/video.mp4 -cs 1 -uid -v
```
will result with:
```
  [95.59%]-[65/68]-[bytes=67048704-68096339]
  [97.06%]-[66/68]-[bytes=68096340-69143975]
  [98.53%]-[67/68]-[bytes=69143976-70191611]
  [100.0%]-[68/68]-[bytes=70191612-71239183]
  ============================
  Downloaded 211abc53b51d432f9a8a3e37fe6fc9e7.mp4
  Size 67M | 71239184 bytes
  Time Taken: 3 seconds
  Location: C:\Users\Tzmo\Downloads\dlf\211abc53b51d432f9a8a3e37fe6fc9e7.mp4
  ============================
```

(not the best but wanted to make one myself)

Ultimaker 3 Timelapse Maker
===========================

A script that makes timelapse videos from the onboard camera on your Ultimaker 3.

Usage
-----
```
$ ./timelapse.py HOST DELAY OUTFILE
```

This script requires Python 3.5 or later and [FFmpeg](https://ffmpeg.org/).
Run the script. It will wait for your Ultimaker to begin printing, then it will start taking pictures.
When the print finishes, the script will compile all the snapshots it took into a video.
Video is encoded using H.264 at 30 fps, but you can easily change this by editing `ffmpegcmd` in the script.

| Option  | Description |
| ------- | ----------- |
| HOST    | The IP address of your Ultimaker 3. You can find this through the menu by going to System > Network > Connection Status. |
| DELAY   | The time between snapshots in seconds. You'll probably want to figure this out based on how long your print will take and how long you want the video to be. For example, if I want a 10 second video at 30 fps, that will be 300 frames. If the print will take five hours, then 5 hours / 300 frames = 60 seconds between frames. |
| OUTFILE | This is the name of the video file you want to make. I recommend giving it either a .mkv or .mp4 extension, although you could choose any container format that supports H.264. |

Thanks
------

[Ultimaker 3 API library](https://ultimaker.com/en/community/23329-inside-the-ultimaker-3-day-3-remote-access-part-2) by Daid

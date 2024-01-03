## 3D_Printer_LEDs

5V Neopixels from Adafruit.

Using a RaspberryPi Zero and basic image:

Install: 

```
sudo pip3 install Adafruit-Blinka
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo pip3 install setproctitle
```


### Enable I2C
```
sudo raspi-config nonint do_i2c 0
```

### Enable SPI
```
sudo raspi-config nonint do_spi 0
```

### For VLC Livestreaming
```
cvlc v4l2:///dev/video0:chroma=h264:width=1280:height=720:fps=25 --sout '#standard{access=http,mux=ts,dst=:8080}'
```

### VLC .mp4 Stream
```
cvlc -vvv /path/to/your/video/file --sout '#standard{access=http,mux=ts,dst=:8080}'
```

### Take timelapse video
```
raspistill -o ~/timelapse/image%02d.jpg -tl 5000 -t 120000
```
This will take 1 picture every 5 seconds for 2 minutes (25 jpgs)
Then, convert the images to timelapse:
```
ffmpeg -r 10 -i ~/timelapse/image%02d.jpg -c:v libx264 ~/timelapse/tl.mp4
ffmpeg -framerate 10 -pattern_type glob -i "timelapse/*.jpg" -s:v 800:600 -c:v libx264 -crf 17 time.mp4
```

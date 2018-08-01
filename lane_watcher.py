import picamera
from picamera.array import PiRGBArray
from lane_detect_pi import Lines
import Adafruit_CharLCD as LCD
import time

fps_limit = 0 # 0 means no limit

image_size=(320, 192)
camera = picamera.PiCamera()
camera.resolution = image_size
camera.framerate = 7 
camera.vflip = False
camera.hflip = False 
#camera.exposure_mode='off'
rawCapture = PiRGBArray(camera, size=image_size)

# allow the camera to warmup
time.sleep(0.1)

lcd_rs        = 25
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 18
lcd_d7        = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

lines = Lines()
lines.look_ahead = 10
lines.remove_pixels = 100
lines.enlarge = 2.25


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    start_time = time.time()
    image = frame.array
    
    image = image[lines.remove_pixels:, :]
    
    image = lines.trans_per(image)
    lines.im_shape = image.shape
    lines.get_fit(image)
    
    if lines.detected_first & lines.detected:
        lines.calculate_curvature_offset()
        lcd.clear()
        direction_mark = "     | -->|"
        if lines.offset < 0:
            direction_mark = "     |<-- |"
        offset_text = direction_mark + "\n     " + str(round(abs(lines.offset),2)) + "m"
        lcd.message(offset_text)
    else:
        lcd.clear()
        lcd.message("  Not Detected")
        
    rawCapture.truncate()
    rawCapture.seek(0)
    end_time = time.time()
    if fps_limit != 0:
        fps = 1/(end_time - start_time)
        if fps > fps_limit:
            time.sleep(1/fps_limit - (end_time - start_time))

#!./env/bin/python

import sys

from settings import *

import datetime, time
from time import sleep

import numpy
import matplotlib.pyplot as plt

import PIL, cv2
from PIL import ImageGrab

from pprint import pprint
import asyncio
import threading

from threading import Thread
from asyncio import run

from multiprocessing import Process, Queue

# import easyocr, pytesseract

# reader = easyocr.Reader(['en']) 

KILL_PIXEL_THRESHOLD = 500
print("Loaded screen_capture.py")
SETTINGS = set_settings()
DEBUG = SETTINGS["DEBUG"]
MANUAL_DELAY = SETTINGS["MANUAL_DELAY"]

def epoch():
	return time.time()

# def ocr(img) -> str:
# 	t0 = epoch()
# 	config = "" # "--psm 7"
# 	text = pytesseract.image_to_string(img, config=config)
# 	clean_text = text.replace("\x0c", "").strip()
# 	t1 = epoch()
# 	print(f"PT OCR in {t1-t0}")
# 	return text
# 
# def test_ocr_modes(img):
# 	data = {}
# 	output_file = "./ocr_modes.txt"
# 	for i in range(0,12):
# 		config = f"--psm {i}"
# 		try:
# 			text = str(pytesseract.image_to_string(img, config=config))
# 			clean_text = str(text.replace("\x0c", "").strip())
# 		except:
# 			clean_text = ("Error")
# 		data[i] = "".join(f"{clean_text}")
# 
# for key in data.keys():
# 	text = data[key]
# 	text = "".join(text)
# 	data[key] = text
# with open(output_file, 'w') as file:
# 	pprint(data, stream=file)
# 
# return

def crop(image, p1, p2):
	x, y, c = image.shape
	x1 = round(x * p1[0])
	y1 = round(y * p1[1])
	x2 = round(x * p2[0])
	y2 = round(y * p2[1])
	
	crop = image[x1:x2, y1:y2]
	return crop

def resize(image, scale):
	x1, y1 = image.size
	x2 = x1 * scale
	y2 = y1 * scale
	newsize = (x2,y2)
	image = image.resize(newsize)
	return image

def detect_kills(image) -> str:
	p0 = (0.33, 0.00)
	p1 = (0.66, 0.50)
	image = crop(image, p0, p1)
	image = resize(image, 3)
	image = prepare(image)
	text = ocr(image)
	return (image, text)

def weighted_grayscale(image):
	""" WARNING, TAKES TOO LONG """

	print("Warning, using weighted grayscale, bad performance")

	W = {
		"R": 0.2989,
		"G": 0.5870,
		"B": 0.1140
	}

	rows, cols = image.shape[:2]
	for x in range(rows):
		for y in range(cols):
			r = image[x, y][2] * W["R"]
			g = image[x, y][1] * W["G"]
			b = image[x, y][0] * W["B"]
			v = r + g + b
			image[x, y] = [v, v, v]

	return image

def display(image) -> None:
	cv2.imshow("Displaying Image", image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	return

def grayscale_method(image, mode, A=127, B=255):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	if mode == 0: thresh = gray
	if mode == 1: ret, thresh = cv2.threshold(gray, A, B, cv2.THRESH_TOZERO_INV)
	if mode == 2: ret, thresh = cv2.threshold(gray, A, B, cv2.THRESH_TRUNC)
	if mode == 3: ret, thresh = cv2.threshold(gray, A, B, cv2.THRESH_TOZERO)
	if mode == 4: ret, thresh = cv2.threshold(gray, A, B, cv2.THRESH_BINARY)
	return thresh

def color_histogram(img) -> None:
	# colors for channels
	colors = ('b', 'g', 'r')

	for i, col in enumerate(colors):
			hist = cv2.calcHist([img], [i], None, [256], [0, 256])
			plt.plot(hist, color=col)
			plt.xlim([0, 256])

	plt.title("RGB Color Histogram")
	plt.xlabel("Pixel Intensity")
	plt.ylabel("Frequency")
	plt.show()

def rotate(image, degrees):

	height, width = image.shape[:2]

	# center = (width//2, height//2)
	# rotation = degrees
	# scale = 0.5

	image = numpy.array(rotate(image, degrees), dtype=numpy.uint8)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	return image

def easyocr(image) -> list:
	t0 = epoch()
	result = reader.readtext(filepath)
	t1 = epoch()
	print(f"ran ocr in {t1-t0}s")
	return result

def threshold_red(image):
	# Note: using GBR not RGB
	r = lambda image: image[:,:,2]
	b = lambda image: image[:,:,1]
	g = lambda image: image[:,:,0]

	conditions = [
		lambda image: r(image) <= 240,
		lambda image: r(image) >= 220,
		lambda image: g(image) <= 50,
		lambda image: b(image) <= 50
	]

	matrix = conditions[0](image)
	for condition in conditions[1:]:
		matrix = matrix & condition(image)
	
	image[matrix] = [255,255,255]
	image[numpy.invert(matrix)] = [0,0,0]
	
	pixels = numpy.sum(image[:,:,:] == [255,255,255])
	
	return image, pixels

# def threshold_red_stats(image, thresh) -> int: return thresh_pixels

def get_kills(image):
	image, red_pixels = threshold_red(image)
	if DEBUG: print(f"Pixels = {red_pixels}")
	kills = red_pixels // KILL_PIXEL_THRESHOLD
	return image, kills

def capture_image() -> (PIL.Image, int):
	seconds = time.time()
	image = PIL.ImageGrab.grab(bbox = None)
	return image, seconds

def check_image(image) -> int:
	kills = 0
	image, kills = get_kills(image)
	return (image, kills)

def print_image(dest: str, image) -> None:
	cv2.imwrite(dest, image)
	return

def check_kill(queue = None):
	image, seconds = capture_image()
	image = numpy.array(image)
	image = image[:,:,:3]
	image = image[:, :, ::-1]

	# Crop if 2 Monitors
	MONITOR = SETTINGS["MONITOR"]
	if MONITOR == 0:
		pass
	if MONITOR == 1:
		image = crop(image, (0.00, 0.00), (1.00, 0.50))
	if MONITOR == 2:
		image = crop(image, (0.00, 0.50), (1.00, 1.00))

	if DEBUG:
		print_image("./monitor.jpg", image)

	image = crop(image, (0.25, 0.33), (0.325, 0.66))
	if DEBUG:
		print_image("./crop.jpg", image)

	image, kills = check_image(image)
	seconds_elapsed = time.time() - seconds
	text = f"Kills = {kills}"
	if DEBUG:
		text = text + f", {seconds_elapsed:.2f}s delay"
		print(f"{text}") 
		print_image("./test.jpg", image)
	if queue != None: 
		queue.put_nowait(text)

def check_kill_loop(queue):
	while(True):
		check_kill(queue)
		sleep(MANUAL_DELAY)
	
class Kill_Log:
	queue = None
	process = None
	def __init__(self, Settings: dict, Debug = False):
		global SETTINGS
		global DEBUG
		SETTINGS = Settings
		DEBUG = DEBUG
		print("Creating Kill Logger")
		self.queue = Queue()
		loop = check_kill_loop
		self.process = Process(target=loop, args=(self.queue,))
		self.process.start()
		sleep(.1)
		print("Created Kill Logger")

async def main():
	log = Kill_Log()
	queue = log.queue
	
	while(True):
		x = queue.get()	
		print(x)
		sleep(0.50)

if __name__ == "__main__":
	argv = sys.argv

	if "--debug" in argv: DEBUG = True
	if "--once" in argv: check_kill()

	if "--once" not in argv:
		run(main())

	sys.exit(0)


#!./env/bin/python

import sys
import PIL

import pytesseract

from pprint import pprint
from PIL import (
	Image,
	ImageFilter,
	ImageEnhance
)

print("Loaded screen_capture.py")

def prepare(img):


	mode = "L"
	img = img.convert(mode)
	
	# Apply a median filter to reduce noise
	img = img.filter(ImageFilter.MedianFilter())

	# Enhance the image contrast
	enhancer = ImageEnhance.Contrast(img)
	img = enhancer.enhance(1)

	return img

def ocr(img) -> str:

	# config = "--psm 7"
	text = pytesseract.image_to_string(img)
	clean_text = text.replace("\x0c", "").strip()

	return text

def test_ocr_modes(img):
	data = {}
	output_file = "./ocr_modes.txt"
	for i in range(0,12):
		config = f"--psm {i}"
		try:
			text = str(pytesseract.image_to_string(img, config=config))
			clean_text = str(text.replace("\x0c", "").strip())
		except:
			clean_text = ("Error")
		data[i] = "".join(f"{clean_text}")

	for key in data.keys():
		text = data[key]
		text = "".join(text)
		data[key] = text
	with open(output_file, 'w') as file:
		pprint(data, stream=file)

	return

def crop(img, p1, p2):
	size = img.size
	x, y = size
	x1 = x * p1[0]
	y1 = y * p1[1]
	x2 = x * p2[0]
	y2 = y * p2[1]
	
	img = img.crop((x1,y1,x2,y2))
	return img

def resize(image, scale):
	x1, y1 = image.size
	x2 = x1 * scale
	y2 = y1 * scale
	newsize = (x2,y2)
	image = image.resize(newsize)
	return image

def detect_kills(image) -> str:

	p0 = (.33,0)
	p1 = (.66, .5)
	image = crop(image, p0, p1)
	image = resize(image, 3)
	image = prepare(image)
	text = ocr(image)
	return (image, text)

if __name__ == "__main__":

	filepath = "screenshots/20260616161501_1.jpg"

	if filepath == "": continue

	# image = Image.open(filepath)
	image = cv2.imread(filepath)

	break

	image, text, = detect_kills(image)
	image.show()
	data = test_ocr_modes(image)

	break


	sys.exit(0)

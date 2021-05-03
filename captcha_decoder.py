import cv2
import pytesseract
import imutils 
import glob
import numpy as np
import matplotlib.pyplot as plt


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

# image_files = glob.glob('./captcha/*.png')
# print(image_files)
def decode_captcha(PATH, imshow=False):
    image = cv2.imread(PATH)
    img=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    tessdata_config = r'--psm 7'

    text = pytesseract.image_to_string(img, config=tessdata_config)

    #print(text)
    if imshow:
        plt.imshow(img)
    return text.replace(" ", "")

def extract_letters(PATH):
    image = cv2.imread(PATH)
    cv2.imshow('Original', image)
    cv2.waitkey()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cv2.imshow('Grayscale', gray)
    cv2.waitkey()

    gray = cv2.copyMakeBorder(gray, 8, 8, 8, 8, cv2.BORDER_REPLICATE)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cv2.imshow('Pure Black and White', thresh)
    cv2.waitkey()

# extract_letters('./captcha/captcha.png')
def extract_letters(PATH):
    image = cv2.imread(PATH)
    plt.figure()
    plt.imshow(image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plt.figure()
    plt.imshow(gray)


    gray = cv2.copyMakeBorder(gray, 8, 8, 8, 8, cv2.BORDER_REPLICATE)
    
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    plt.figure()
    plt.imshow(thresh)
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[1] if imutils.is_cv3() else contours[0]
    
    letter_image_regions =[]
    
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        letter_image_regions.append((x, y, w, h))
        
    letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])
    print(letter_image_regions)
    boxed_img = thresh.copy()
    text = []
    for box in letter_image_regions:
        x, y, w, h = box
        sp = (x, y + h)
        ep = (x + w, y)
        boxed_img = cv2.rectangle(boxed_img, sp, ep, (255, 255, 255), 1)
        image_chunk = thresh[y-2:y+h+2, x-2:x+w+2]
        text.append(pytesseract.image_to_string(image_chunk, config=r'--psm 10'))
        plt.figure()
        plt.imshow(image_chunk)
    
    s = ''
    for i in text:
        s += i[0]
    print('Separate Charcters:', s)
    print('Whole:', pytesseract.image_to_string(thresh, config=r'--psm 7'))
    plt.figure()
    plt.imshow(boxed_img)
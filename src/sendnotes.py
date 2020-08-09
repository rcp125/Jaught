import cv2
import os

counter = 0

def main(canvas):
    global counter
    counter = counter + 1
    path = os.path.join(os.path.dirname(os.getcwd()), "saved_notes", str(counter) + '.jpg')
    print(path)
    cv2.imwrite(path, canvas)
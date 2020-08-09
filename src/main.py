import capture
import cv2
import numpy as np

# REGION OF INTEREST
xend = 0.3 #0.5
yend= 0.85 #0.75
resy = 600
resx = 400

full = False

if __name__ == "__main__":
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    bgModel = None
    canvas = 255 * np.ones(shape=[resx, resy, 3], dtype=np.uint8)
    extTop = (0,0)

    while camera.isOpened():
        _, frame = camera.read()
        frame = cv2.flip(frame, 1)
        if not full:
            cv2.rectangle(frame, (int(xend * frame.shape[1]), 0), (frame.shape[1], int(yend * frame.shape[0])), (255, 0, 0), 2)
        else:
            cv2.rectangle(frame, (int(frame.shape[1]), 0), (frame.shape[1], int(frame.shape[0])), (255, 0, 0), 2)
        cv2.imshow('original', frame)

        if bgModel:
            removed = capture.removeBG(frame, bgModel)
            if not full:
                cropped = removed[0:int(yend * frame.shape[0]), int(xend * frame.shape[1]):frame.shape[1]]
            else:
                cropped = removed[0:frame.shape[0], 0:frame.shape[1]]
            cv2.imshow('removed', cropped)

            thres = capture.image_process(cropped)
            contours, _ = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            count, extTop, canvas = capture.find_max_contour(contours, cropped, canvas, extTop)
            # count = contours(thres, cropped)

            cv2.imshow("White Blank", canvas)

        k = cv2.waitKey(10)
        if k == 27:
            camera.release()
            cv2.destroyAllWindows()
            print("Exiting...")
            break
        elif k == ord('b'):
            bgModel = cv2.createBackgroundSubtractorMOG2(0, 50)
            print("Background captured")
        elif k == ord('s') and bgModel:
            print(count)
        elif k == ord('c'):
            canvas = 255 * np.ones(shape=[resx, resy, 3], dtype=np.uint8)
            print("Canvas cleared")

import cv2
import numpy as np
import math
import sendnotes

color = 0
pointsz = 0
resy = 600
resx = 400
slope = 0
slope_save = 0

def image_process(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (35, 35), 0)
    _, thres = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY)
    return thres

def removeBG(frame, bgModel):
    mask = bgModel.apply(frame,learningRate=0)
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.erode(mask, kernel)
    removed = cv2.bitwise_and(frame, frame, mask=mask)
    return removed

def find_max_contour(contours, img, canvas, oldExtTop):
    global slope
    global slope_save
    global color
    global pointsz
    maxArea = 0
    maxIndex = 0
    if len(contours) > 0:
        for i in range(len(contours)):
            curr = contours[i]
            area = cv2.contourArea(curr)
            if area > maxArea:
                maxArea = area
                maxIndex = i

        max_contour = contours[maxIndex]
        hull = cv2.convexHull(max_contour)
        drawing = np.zeros(img.shape, np.uint8)
        cv2.drawContours(drawing, [max_contour], 0, (0, 255, 0), 2)
        cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 3)

        cnt = calculateFingers(max_contour,drawing, img)

        extTop = tuple(max_contour[max_contour[:, :, 1].argmin()][0])
        if(oldExtTop and cnt > 1):
            if(-5 > oldExtTop[0] - extTop[0]  or oldExtTop[0] - extTop[0] > 5):
                slope = slope + 1
                if(slope == 10):
                    canvas = 255 * np.ones(shape=[resx, resy, 3], dtype=np.uint8)
                    print('canvas cleared')
                    slope = 0
            else:
                slope = 0

        if(oldExtTop and cnt > 1):
            if(-5 > oldExtTop[1] - extTop[1]  or oldExtTop[1] - extTop[1] > 5):
                slope_save = slope_save + 1
                if(slope_save == 10):
                    sendnotes.main(canvas)
                    print('canvas saved')
                    slope_save = 0
            else:
                slope_save = 0
        if(cnt == 4):
            color = color + 1
        color = color % 2
        if(color == 0):
            colorval = (255, 0, 0)
        else:
            colorval = (0,255,0)

        if(cnt == 3):
            pointsz = pointsz + 1
        pointsz = pointsz % 2
        if(pointsz == 0):
            sz = 1
        else:
            sz = 2
        if(cnt == 0):
            if(oldExtTop == None):
                cv2.line(canvas, extTop, extTop, colorval, sz)
            else:
                cv2.line(canvas, oldExtTop, extTop, colorval, sz)
            # cv2.circle(canvas, extTop, 1, (0, 255, 0), -1)
        # if(cnt == 4):
        #     canvas = 255 * np.ones(shape=[resx, resy, 3], dtype=np.uint8)

        cv2.imshow('output', drawing)

        

        return cnt, extTop, canvas
    return (None, None, canvas)

def calculateFingers(max_contour,drawing, img):
    hull = cv2.convexHull(max_contour, returnPoints=False)
    if len(hull) > 3:
        defects = cv2.convexityDefects(max_contour, hull)
        if type(defects) != type(None):
            cnt = 0
            for i in range(defects.shape[0]):  # calculate the angle
                s, e, f, _ = defects[i][0]
                start = tuple(max_contour[s][0])
                end = tuple(max_contour[e][0])
                far = tuple(max_contour[f][0])
                angle = calculateAngle(far, start, end)
                
                if angle <= math.pi / 2:
                    cnt += 1
                    cv2.circle(drawing, far, 8, [211, 84, 0], -1)
            return cnt
    return 0

def calculateAngle(far, start, end):
    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))
    return angle

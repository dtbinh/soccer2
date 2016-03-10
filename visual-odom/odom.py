#! /usr/bin/env python

import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt
import video
import time
import math

def featureDetection(im):
    # Initiate FAST object with default values
    # fast = cv2.FastFeatureDetector_create(20,True)
    fast = cv2.FastFeatureDetector_create()

    # find and draw the keypoints
    keypoints = fast.detect(im)
    print 'fast keypoints',len(keypoints)
    # for i in keypoints:
        # print i.pt
    # exit()
    # im2 = cv2.drawKeypoints(im,keypoints,im,color=(255,0,0))
    # cv2.imshow('keypoints',im2)
    # cv2.waitKey(10)

    # convert keypoints
    # keypoints=np.array([[k.pt] for k in keypoints],dtype='f4')
    # print 'fast numpy shape',keypoints.shape
    # print 'fast',keypoints
    # print type(keypoints)
    # print keypoints.dtype
    # if keypoints.shape[0] == 0:
    #     im2 = cv2.drawKeypoints(im,keypoints,im,color=(255,0,0))
    #     cv2.imshow('keypoints',im2)
    #     cv2.waitKey(0)
    # exit()

    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 100,
        qualityLevel = 0.3,
        minDistance = 7,
        blockSize = 7 )
    keypoints = cv2.goodFeaturesToTrack(im, mask = None, **feature_params)
    print 'goodFeaturesToTrack shape',keypoints.shape
    # # print 'good',keypoints
    # print type(keypoints)
    # print keypoints.dtype
    # exit()

    return keypoints

def checkRange(x,max,min):
    # print 'check',x
    if x <= max and x >= min: return True
    else: return False


def featureTrack(new_gray,old_gray,p0):
    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (21,21),
                  maxLevel = 3,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.001))

    # cd=np.array([k.pt for k in keypoints])
    # cd=np.array([[k.pt for k in keypoints]])
    # if p0.shape[0] > 50: cd = p0
    # else:
    #     print '------- reset --------'
    #     p0 = featureDetection(old_gray)
    #     cd = p0
    cd = p0
    # print cd
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, new_gray, cd, None, **lk_params)

    # print 'st',st.shape
    # print 'st',st
    # print 'p0',p0.shape
    # print 'p1',p1.shape
    # exit()

    new = []
    old = []

    # Select good points
    for i in range(0,p1.shape[0]):
        # print 'st',st[i]
        # print 'p1',p1[i]
        if st[i][0] == 1 and p1[i][0][0] >= 0 and p1[i][0][1] >= 0:
            new.append(p1[i][0])
            old.append(p0[i][0])

    good_new = np.array([[k] for k in new],dtype=np.float32)
    good_old = np.array([[k] for k in old],dtype=np.float32)

    # print 'p0',p0.shape
    # print 'p1',p1.shape
    # print 'good_new',good_new.shape
    # print 'good_old',good_old.shape

    # im2 = cv2.drawKeypoints(new_gray,cd,new_gray,color=(255,0,0))
    im2 = im.copy()
    for i in good_new:
        # print i
        cv2.circle(im2,(int(i[0][0]),int(i[0][1])),3,(0,255,0),-1)
    cv2.imshow('keypoints',im2)
    cv2.waitKey(10)

    return good_old, good_new

# plt.ion()
# plt.show()
# plt.title('image'), plt.xticks([]), plt.yticks([])
# plt.axis("off")

def draw(pts):
    x = []
    y = []
    for i in pts:
        x.append(i[0])
        y.append(i[1])
        # print i

    # li.set_ydata(y)
    # li.set_xdata(x)
    # fig.canvas.draw()
    plt.plot(x,y)
    # plt.axis([0, 6, 0, 20])
    plt.grid(True)
    plt.draw()
    plt.pause(5)
    # time.sleep(5)

cam = video.Camera('floor.mp4')
# cam.load('camera_params.npz')
# cameraMat = cam.data['camera_matrix']

# print 'cameraMat',cameraMat

# cv2.IMREAD_GRAYSCALE faster?
ret, old_im = cam.read(True)
ret, im = cam.read(True)

# set ROI
old_im = old_im[0:479,200:639]
im = im[0:479,200:639]

p0 = featureDetection(old_im)
p0, p1 = featureTrack(im,old_im,p0)

pp = (220,240)
focal = 200.0
R_f = np.eye(3,3,dtype=np.float)
t_f = np.array([0,0,1],dtype=np.float)

# print 'wtf???'
# print 'p0',p0.shape
# print 'p1',p1.shape
# E, mask = cv2.findEssentialMat(p0,p1,cameraMat,cv2.FM_RANSAC)
# retval, R, t, mask = cv2.recoverPose(E,p0,p1,cameraMat)
E, mask = cv2.findEssentialMat(p0,p1,focal,pp,cv2.FM_RANSAC)
retval, R, t, mask = cv2.recoverPose(E,p0,p1,R_f,t_f,focal,pp,mask)



print 'ret',ret
print 't',t
print 'R',R
# exit()

R_f = R.copy()
t_f = t.copy()

print 'R:',R_f
print 't:',t_f
save_pts = []
while(cam.isOpened()):
    try:
        ret, im = cam.read(True)

        if not ret:
            print 'video end'
            # draw(save_pts)
            break

        im = im[0:479,200:639]


        if p0.shape[0] < 50:
            print '------- reset --------'
            p0 = featureDetection(old_im)
            if p0.shape[0] == 0:
                print 'bad image'
                continue

        # im = cam.undistort(im)

        # keypoints = featureDetection(im)
        # p0 - old pts
        # p1 - new pts
        p0, p1 = featureTrack(im,old_im,p0)

        # since these are rectified images, fundatmental (F) = essential (E)
        # E, mask = cv2.findEssentialMat(p0,p1,focal,pp,cv2.FM_RANSAC)
        # retval, R, t, mask = cv2.recoverPose(E,p0,p1,R_f,t_f,focal,pp,mask)

        E, mask = cv2.findEssentialMat(p0,p1,focal,pp,cv2.FM_RANSAC)
        retval, R, t, mask = cv2.recoverPose(E,p0,p1,R_f,t_f,focal,pp,mask)
        # print retval,R

        # Now update the previous frame and previous points
        old_im = im.copy()
        # p0 = p1.reshape(-1,1,2)
        p0 = p1

        # print 'p0 size',p0.shape
        # print 'p1 size',p1.shape

        R_f = R.dot(R_f)
        t_f = t_f + R_f.dot(t)

        # num = np.array([t_f[0]/t_f[2],t_f[1]/t_f[2]])
        num = t_f
        # print 'position:', num
        # print 'distance:', np.linalg.norm(num)
        # R_f = R*R_f
        # print 'R:',R_f,'t:',t_f
        # print t_f

        save_pts.append(t_f)

    except KeyboardInterrupt:
        print 'captured interrupt'
        break

cam.release()

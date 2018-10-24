import cv2
import numpy as np

FINPUT = "tlfull"

vidcap = cv2.VideoCapture(FINPUT + ".mp4")

fps = vidcap.get(cv2.CAP_PROP_FPS)
dfps = 60
mfps = int(fps/dfps)
if (mfps < 1):
    mfps = 1
fnum = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
print(fps, fnum, mfps-1)

nfact = 0.8

bt = [0.2, 0.7, 0.1]

rs, frame = vidcap.read()

timelapse = np.array(frame, dtype=np.float64)
max_timelapse= timelapse

#print(image)

#print(np.average([cnv, cnv], axis=0))

count = 1
framecounter = 1
cl = 2000

while rs:
    rs, frame = vidcap.read()
    framecounter+=1
    if (rs):
        # timelapse += (255/(255**nfact))*np.power(np.array(frame, dtype=np.float64), nfact)
        max_timelapse = np.maximum(max_timelapse, np.array(frame, dtype=np.uint64))
        # timelapse += np.array(frame, dtype=np.float64)
        # timelapse += np.power(np.array(frame, dtype=np.float64), 1.23)
        # timelapse += np.clip(np.power(np.array(frame, dtype=np.float64), 1.23), 0, 255)
        # timelapse += np.clip(255*np.power(np.array(frame, dtype=np.float64)/255, 1.2), 0, 255)
        timelapse += np.clip(np.power(np.array(frame, dtype=np.float64), 1.10), 0, 255)
        for i in range(mfps-1):
            rs = vidcap.grab()
            framecounter+=1
        #print('Frame read:', rs)
        count += 1
    if count > cl:
        rs = 0
    if framecounter % 10 == 0:
        print (100 * framecounter / fnum, "%")
print ("100 %")

max_mult_factor = 0.45

timelapse = np.clip(timelapse, 0, 255*count) / count

final = np.clip(timelapse + max_timelapse*max_mult_factor,0,255)

final = np.uint8(final)

#print(timelapse)

cv2.imwrite(FINPUT + ".jpg", final)  # save frame as JPEG file
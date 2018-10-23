import cv2
import numpy as np

FINPUT = "input_video"

vidcap = cv2.VideoCapture(FINPUT + ".mp4")

fps = vidcap.get(cv2.CAP_PROP_FPS)
dfps = 60
mfps = int(fps/dfps)
if (mfps < 1):
    mfps = 1
fnum = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
print(fps, fnum, mfps-1)

nfact = 0.8

rs, frame = vidcap.read()

timelapse = np.array(frame, dtype=np.float64)


#print(image)

#print(np.average([cnv, cnv], axis=0))

count = 1
cl = 1000

while rs:
    rs, frame = vidcap.read()
    if (rs):
        timelapse += (255/(255**nfact))*np.power(np.array(frame, dtype=np.float64), nfact)
        #timelapse = np.maximum(timelapse, np.array(frame, dtype=np.uint64))
        for i in range(mfps-1):
            rs = vidcap.grab()
        #print('Frame read:', rs)
        count += 1
    if count > cl:
        rs = 0
    if count % 100 == 0:
        print (100 * count / fnum, "%")

timelapse = np.uint8(timelapse / count)
#timelapse = np.uint8(timelapse)

print(timelapse)

cv2.imwrite(FINPUT + ".jpg", timelapse)  # save frame as JPEG file
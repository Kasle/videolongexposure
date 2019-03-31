import cv2
import numpy as np
import threading
import argparse
import sys
import time

class long_exposure_generator:

    nfact = 0.8

    def __init__(self, file_name, max_thread_count):

        self.video_capture = cv2.VideoCapture(file_name)
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.current_frame_count = 0

        self.read_lock = threading.Lock()
        self.max_check_lock = threading.Lock()

        rs, frame = self.video_capture.read()
        self.current_frame_count += 1
        self.long_exposure_output = np.array(frame, dtype=np.float64)
        self.max_frame = self.long_exposure_output

        self.threads = []
        self.finished_threads = 0

        for thread in range(max_thread_count):
            self.threads.append(threading.Thread(target=self.process_frame))
            self.threads[-1].daemon = True
            self.threads[-1].start()

        while self.finished_threads < max_thread_count:
            print("waiting:", self.finished_threads, max_thread_count)
            time.sleep(1)

        max_mult_factor = 0.45
        self.long_exposure_output = np.clip(self.long_exposure_output, 0, 255*self.frame_count) / self.frame_count
        final = np.clip(self.long_exposure_output + self.max_frame*max_mult_factor,0,255)
        final = np.uint8(final)
        print("writing")
        cv2.imwrite(file_name[:file_name.rfind(".")] + ".jpg", final)  # save frame as JPEG file
        print("done")
        exit()

    def process_frame(self):
        try:
            rs = True
            while rs:
                if self.current_frame_count > self.frame_count:
                    break
                self.read_lock.acquire()
                if self.current_frame_count > self.frame_count:
                    self.read_lock.release()
                    break
                #print(threading.get_ident(), "locking.")
                rs, frame = self.video_capture.read()
                self.current_frame_count += 1
                #print(threading.get_ident(), "releasing.")
                self.read_lock.release()
                if (rs):

                    print(threading.get_ident(), self.current_frame_count, self.frame_count)
                    # long_exposure_output += (255/(255**nfact))*np.power(np.array(frame, dtype=np.float64), nfact)
                    self.max_check_lock.acquire()
                    self.max_frame = np.maximum(self.max_frame, np.array(frame, dtype=np.uint64))
                    self.max_check_lock.release()
                    # long_exposure_output += np.array(frame, dtype=np.float64)
                    # long_exposure_output += np.power(np.array(frame, dtype=np.float64), 1.23)
                    # long_exposure_output += np.clip(np.power(np.array(frame, dtype=np.float64), 1.23), 0, 255)
                    # long_exposure_output += np.clip(255*np.power(np.array(frame, dtype=np.float64)/255, 1.2), 0, 255)
                    self.long_exposure_output += np.clip(np.power(np.array(frame, dtype=np.float64), 1.10), 0, 255)
        except:
            return
        self.finished_threads+=1


if __name__ == "__main__":
    long_exposure_generator(sys.argv[1], int(sys.argv[2]))

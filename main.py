import cv2
import numpy as np
import threading
import argparse
import sys
import time
from matplotlib import pyplot as plt
import os
import shutil
import pickle

class ti:
    def __init__(self):
        self.last_time_checked = time.time()

    def c(self, string_header="X"):
        print(string_header, time.time()-self.last_time_checked)
        self.last_time_checked = time.time()

    def r(self):
        self.last_time_checked = time.time()

class long_exposure_generator:

    def __init__(self, file_name):

        self.ti = ti()

        self.video_capture = cv2.VideoCapture(file_name)
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.frame_count = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

        self.current_frame_count = 0
        self.finished_frames = 0

        frame_process_count = 100


        self.exposure_lock = threading.Lock()
        #self.max_check_lock = threading.Lock()

        self.frame_accu_1 = []
        #self.frame_accu_2 = []
        #self.frame_accu_3 = []

        self.max_frame = []
        self.max_frame_buffer_1 = []
        self.max_frame_buffer_2 = []

        self.frame_buffer = []

        frames_available = True

        while (frames_available):

            self.frame_buffer = []
            self.max_frame_buffer_1 = []
            self.max_frame_buffer_2 = []

            for i in range(frame_process_count):

                frames_available, frame = self.video_capture.read()

                if not frames_available:
                    break

                self.frame_buffer.append(frame)
                self.max_frame_buffer_1.append(frame)

            max_thread = threading.Thread(target=self.process_max)
            exposure_thread = threading.Thread(target=self.process_exposure)

            max_thread.daemon = True
            exposure_thread.daemon = True

            max_thread.start()
            exposure_thread.start()

            max_thread.join()
            exposure_thread.join()



        # self.frame_buffer = []
        #
        # rs, frame = self.video_capture.read()
        # self.all_frames.append(frame)
        # self.current_frame_count += 1
        # self.long_exposure_output = np.array(frame, dtype=np.float64)
        # self.max_frame = self.long_exposure_output

        #cv2.imshow("image", np.array(self.max_frame, dtype=np.uint8))
        #cv2.waitKey(1)

        # self.finished_frames += 1
        #
        # self.threads = []
        # self.finished_threads = 0
        #
        # max_mult_factor = 0.5
        #
        # for thread in range(max_thread_count):
        #     self.threads.append(threading.Thread(target=self.process_frame))
        #     self.threads[-1].daemon = True
        #     self.threads[-1].start()
        #
        # ts = time.time()
        #
        # while self.finished_threads < max_thread_count:
        #
        #     #print("percent complete (%):", 100.0 * self.finished_frames / self.frame_count)
        #
        #     self.preview_image = np.clip(self.long_exposure_output, 0, 255*self.finished_frames) / self.finished_frames
        #     self.preview_image = np.clip(self.preview_image + self.max_frame*max_mult_factor,0,255)
        #
        #     cv2.imshow("image", np.uint8(self.preview_image))
        #     cv2.waitKey(1)
        #     #time.sleep(0.1)
        #
        #
        # self.long_exposure_output = np.clip(self.long_exposure_output, 0, 255*self.frame_count) / self.frame_count

        max_mult_factor = 0.5

        self.frame_accu_1 = np.clip(self.frame_accu_1, 0, 255*self.frame_count) / self.frame_count
        #self.frame_accu_1 = np.clip(self.frame_accu_1, 0, 255*frame_process_count) / frame_process_count

        final = np.clip(self.frame_accu_1 + self.max_frame*max_mult_factor,0,255)
        final = np.uint8(final)

        #cv2.imshow("image", final)
        #cv2.waitKey(0)

        print("writing")
        cv2.imwrite(file_name[:file_name.rfind(".")] + ".jpg", final)  # save frame as JPEG file

        self.ti.c("main")

        #print("done. took", time.time() - ts, "s using", max_thread_count, "threads")

        exit()

    def process_max(self):

        t = ti()

        while(1):

            #print("hello", len(self.max_frame_buffer_1))

            local_threads = []

            if len(self.max_frame_buffer_1) > 1:
                if not (len(self.max_frame_buffer_1) % 2): #even
                    for i in range(0, len(self.max_frame_buffer_1), 2):
                         local_threads.append(threading.Thread(target=self.compare_max, args=[i]))
                         local_threads[-1].daemon = True
                         local_threads[-1].start()
                    for thread in local_threads:
                        thread.join()
                    self.max_frame_buffer_1 = self.max_frame_buffer_2.copy()
                    self.max_frame_buffer_2 = []
                else: #odd
                    for i in range(0, len(self.max_frame_buffer_1)-1, 2):
                         local_threads.append(threading.Thread(target=self.compare_max, args=[i]))
                         local_threads[-1].daemon = True
                         local_threads[-1].start()
                    for thread in local_threads:
                        thread.join()
                    self.max_frame_buffer_2.append(self.max_frame_buffer_1[-1])
                    self.max_frame_buffer_1 = self.max_frame_buffer_2.copy()
                    self.max_frame_buffer_2 = []
            else:

                if len(self.max_frame):
                    self.max_frame = np.maximum(self.max_frame, self.max_frame_buffer_1[0])
                else:
                    self.max_frame = self.max_frame_buffer_1[0]
                break

        t.c("max")

    def compare_max(self, frame_index):
        self.max_frame_buffer_2.append(np.maximum(self.max_frame_buffer_1[frame_index], self.max_frame_buffer_1[frame_index+1]))

    def process_exposure(self):

        t = ti()

        local_threads = []

        for i in range(len(self.frame_buffer)):
             local_threads.append(threading.Thread(target=self.apply_exposure_to_frame, args=[i]))
             local_threads[-1].daemon = True
             local_threads[-1].start()
        for thread in local_threads:
            thread.join()

        t.c("exp")

        return

    def apply_exposure_to_frame(self, frame_index):

        temp_frame_accu = np.power(np.array(self.frame_buffer[frame_index], dtype=np.float32), 1.10)

        self.exposure_lock.acquire()

        if len(self.frame_accu_1):
            self.frame_accu_1 += temp_frame_accu
        else:
            self.frame_accu_1 = temp_frame_accu

        self.exposure_lock.release()


if __name__ == "__main__":
    long_exposure_generator(sys.argv[1])

# def process_frame(self):
#     try:
#         rs = True
#         tx1 = time.time()
#         while rs:
#             #print("----------------------------------")
#             if self.current_frame_count > self.frame_count:
#                 break
#             #print(0, (time.time()-tx1) * 1000)
#             tx1 = time.time()
#             self.read_lock.acquire()
#             if self.current_frame_count > self.frame_count:
#                 self.read_lock.release()
#                 break
#             #print(threading.get_ident(), "locking.")
#             rs, frame = self.video_capture.read()
#             self.current_frame_count += 1
#             #print(threading.get_ident(), "releasing.")
#             self.read_lock.release()
#             #print(1, (time.time()-tx1) * 1000)
#             tx1 = time.time()
#             if (rs):
#                 #print(threading.get_ident(), self.current_frame_count, self.frame_count)
#                 # long_exposure_output += (255/(255**n_fact))*np.power(np.array(frame, dtype=np.float64), n_fact)
#                 #print(2, (time.time()-tx1) * 1000)
#                 tx1 = time.time()
#                 self.max_check_lock.acquire()
#                 self.max_frame = np.maximum(self.max_frame, np.array(frame))
#                 self.max_check_lock.release()
#                 #print(3, (time.time()-tx1) * 1000)
#                 tx1 = time.time()
#                 # long_exposure_output += np.array(frame, dtype=np.float64)
#                 # long_exposure_output += np.power(np.array(frame, dtype=np.float64), 1.23)
#                 # long_exposure_output += np.clip(np.power(np.array(frame, dtype=np.float64), 1.23), 0, 255)
#                 # long_exposure_output += np.clip(255*np.power(np.array(frame, dtype=np.float64)/255, 1.2), 0, 255)
#                 #print(4, (time.time()-tx1) * 1000)
#                 tx1 = time.time()
#                 self.long_exposure_output += np.power(np.array(frame, dtype=np.float32), 1.10)
#                 #print(5, (time.time()-tx1) * 1000)
#                 tx1 = time.time()
#             self.finished_frames += 1
#     except:
#         return
#     self.finished_threads+=1




    # txa = time.time()
    # print("started import.")
    # while rs:
    #     rs, frame = self.video_capture.read()
    #     self.all_frames.append(frame)
    #
    # print("done import.", time.time() - txa)
    #
    # while 1:
    #     try:
    #         self.all_frames.pop()
    #     except:
    #         break
    #
    # print("done import.", time.time() - txa)

import pickle
import dlib
import imutils
from imutils import face_utils
from sklearn.svm import SVC
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
from imutils.face_utils import FaceAligner
from imutils.video import VideoStream
import time
import cv2

class verification_exam(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        frame = self.video.read()

        global person_name
        detector = dlib.get_frontal_face_detector()

        predictor = dlib.shape_predictor(
        'C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/shape_predictor_68_face_landmarks.dat')  # Add path to the shape predictor ######CHANGE TO RELATIVE PATH LATER
        svc_save_path = "C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/svc.sav"

        with open(svc_save_path, 'rb') as f:
            svc = pickle.load(f)
        fa = FaceAligner(predictor, desiredFaceWidth=96)
        encoder = LabelEncoder()
        encoder.classes_ = np.load('C:/Users/User/Documents/GitHub/EProctor/face_recognition_data/classes.npy')

        faces_encodings = np.zeros((1, 128))
        no_of_faces = len(svc.predict_proba(faces_encodings)[0])
        count = dict()
        present = dict()
        log_time = dict()
        start = dict()
        for i in range(no_of_faces):
            count[encoder.inverse_transform([i])[0]] = 0
            present[encoder.inverse_transform([i])[0]] = False

        #vs = VideoStream(src=0).start()

        sampleNum = 0

        while (True):
            #frame = vs.read()
            frame = imutils.resize(frame, width=800)

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray_frame, 0)

            for face in faces:
                print("INFO : inside for loop")
                (x, y, w, h) = face_utils.rect_to_bb(face)

                face_aligned = fa.align(frame, gray_frame, face)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

                (pred, prob) = predict(face_aligned, svc)

                if (pred != [-1]):

                    person_name = encoder.inverse_transform(np.ravel([pred]))[0]
                    pred = person_name
                    if count[pred] == 0:
                        start_time = time.time()
                        start[pred] = time.time()
                        count[pred] = count.get(pred, 0) + 1

                    if count[pred] == 4 and (time.time() - start[pred]) > 1.2:
                        count[pred] = 0
                    else:
                        # if count[pred] == 4 and (time.time()-start) <= 1.5:
                        present[pred] = True
                        # log_time[pred] = datetime.datetime.now()
                        count[pred] = count.get(pred, 0) + 1
                        print(pred, present[pred], count[pred])
                    cv2.putText(frame, str(person_name) + str(prob), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1)
                else:
                    person_name = "unknown"
                    cv2.putText(frame, str(person_name), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # if str(person_name) == request.user.username:
            #     messages.success(request, "Student identity verified successfully")
            #     break
            # else:
            #     messages.error(request, "Invalid student")
            #     break


        # cv2.putText()
        # Before continuing to the next loop, I want to give it a little pause
        # waitKey of 100 millisecond
        # cv2.waitKey(50)

        # Showing the image in another window
        # Creates a window with window name "Face" and with the image img
        #cv2.imshow("Identity Verification", frame)
        # Before closing it we need to give a wait command, otherwise the open cv wont work
        # @params with the millisecond of delay 1
        # cv2.waitKey(1)
        # To get out of the loop

        # if str(person_name) == request.user.username:
        #     messages.success(request, "Student identity verified successfully")
        #     break
        # else:
        #     messages.error(request, "Invalid student")
        #     break

    # Stoping the videostream
    #vs.stop()

    # destroying all the windows
    #cv2.destroyAllWindows()
    # update_attendance_in_db_in(present)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


def predict(face_aligned, svc, threshold=0.7):
    face_encodings = np.zeros((1, 128))
    try:
        x_face_locations = face_recognition.face_locations(face_aligned)
        faces_encodings = face_recognition.face_encodings(face_aligned, known_face_locations=x_face_locations)
        if (len(faces_encodings) == 0):
            return ([-1], [0])

    except:

        return ([-1], [0])

    prob = svc.predict_proba(faces_encodings)
    result = np.where(prob[0] == np.amax(prob[0]))
    if (prob[0][result[0]] <= threshold):
        return ([-1], prob[0][result[0]])


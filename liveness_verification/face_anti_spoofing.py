import random
import cv2
import imutils
from liveness_verification import f_liveness_detection
from liveness_verification import liveness_questions as questions

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


# instantiate camera
cv2.namedWindow('Liveness Detection')
cam = cv2.VideoCapture(0)

# parameters
COUNTER, TOTAL = 0, 0
counter_ok_questions = 0
counter_ok_consecutives = 0
limit_consecutives = 2
limit_questions = 6
counter_try = 0
limit_try = 50


def show_image(cam, text, color=(0, 0, 255)):
    ret, im = cam.read()
    im = imutils.resize(im, width=720)
    # im = cv2.flip(im, 1)
    cv2.putText(im, text, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    return im


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

    return (result[0], prob[0][result[0]])


for i_questions in range(0, limit_questions):
    # random questions generator
    index_question = random.randint(0, 2)
    question = questions.question_bank(index_question)

    #---------------------------------------------------------
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
    # ---------------------------------------------------------
    # im = show_image(cam, question)
    # cv2.imshow('Liveness detection', im)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

        # <----------------------- ingest data
    ret, im = cam.read()
    im = imutils.resize(im, width=720)
    im = cv2.flip(im, 1)
    gray_frame = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame, 0)
        # <----------------------- ingest data

    for i_try in range(limit_try):

        TOTAL_0 = TOTAL
        out_model = f_liveness_detection.detect_liveness(im, COUNTER, TOTAL_0)
        TOTAL = out_model['total_blinks']
        COUNTER = out_model['count_blinks_consecutive']
        dif_blink = TOTAL - TOTAL_0
        if dif_blink > 0:
            blinks_up = 1
        else:
            blinks_up = 0

        challenge_res = questions.challenge_result(question, out_model, blinks_up)

        im = show_image(cam, question)
        cv2.imshow('Liveness detection', im)

        for face in faces:
            (x, y, w, h) = face_utils.rect_to_bb(face)

            face_aligned = fa.align(im, gray_frame, face)
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 1)
            #cv2.imshow('Liveness detection', im)

            (pred, prob) = predict(face_aligned, svc)

            if (pred != [-1]):
                person_name = encoder.inverse_transform(np.ravel([pred]))[0]
                pred = person_name
                if count[pred] == 0:
                    # start_time = time.time()
                    # start[pred] = time.time()
                    count[pred] = count.get(pred, 0) + 1

                # if count[pred] == 4 and (time.time() - start[pred]) > 1.2:
                # count[pred] = 0
                else:
                    # if count[pred] == 4 and (time.time()-start) <= 1.5:
                    present[pred] = True
                    # log_time[pred] = datetime.datetime.now()
                    count[pred] = count.get(pred, 0) + 1
                    print(pred, present[pred], count[pred])

                #im = show_image(cam, str(person_name) + str(prob))
                #cv2.imshow('Liveness detection', im)
                cv2.putText(im, str(person_name) + str(prob), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0), 1)
                cv2.imshow('Liveness detection', im)
                user_name = str(person_name)
            else:
                person_name = "unknown"
                cv2.putText(im, str(person_name), (x + 6, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if challenge_res == "pass":

            im = show_image(cam, question + " : ok")
            cv2.imshow('Liveness detection', im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            counter_ok_consecutives += 1
            if counter_ok_consecutives == limit_consecutives:
                counter_ok_questions += 1
                counter_try = 0
                counter_ok_consecutives = 0
                break
            else:
                continue

        elif challenge_res == "fail":
            counter_try += 1
            show_image(cam, question + " : fail")
        elif i_try == limit_try - 1:
            break

    if counter_ok_questions == limit_questions:
        while True:
            im = show_image(cam, "LIVENESS SUCCESSFUL", color=(0, 255, 0))
            print("SUCCESSFUL STUDENT IDENTITY AND LIVENESS VERIFICATION")
            liveTest = True
            cv2.imshow('Liveness detection', im)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #cv2.waitKey(1)
            break
    elif i_try == limit_try - 1:
        while True:
            im = show_image(cam, "LIVENESS FAIL")
            print("UNSUCCESSFUL VERIFICATION")
            liveTest = False
            cv2.imshow('Liveness detection', im)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #cv2.waitKey(1)
            break
        break

    else:
        continue



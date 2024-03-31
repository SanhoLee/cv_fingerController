# ref : https://github.com/google/mediapipe/issues/4448

import cv2, math
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from cvzone.SerialModule import SerialObject

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

arduino = SerialObject()

class MediaPipe_BodyModule():
    def __init__(self):
        self.results = None
        self.fing_dist = 0


    def send_int_toArduino(self, dist):
        arduino.sendData([dist])        

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = np.copy(rgb_image)

        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx]

            # Draw the hand landmarks.
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
                ])
            
            # drawing each finger's landmark and connecting each of points
            solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - MARGIN

            # Draw handedness (left or right hand) on the image.
            cv2.putText(annotated_image, f"{handedness[0].category_name}",
                        (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                        FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)
            
            # for x,y in x_coordinates, y_coordinates:
            # for i in range(len(x_coordinates)):
            #     coordTemp = (int(x_coordinates[i] * width),int(y_coordinates[i] * height) - MARGIN)
            #     cv2.putText(annotated_image, f"#{i}",coordTemp, cv2.FONT_HERSHEY_DUPLEX,FONT_SIZE, (100,100,100), FONT_THICKNESS, cv2.LINE_AA)
                
            
            # idx of first finger : 4, second finger : 8
            s_pnt = (int(x_coordinates[4] * width),int(y_coordinates[4] * height) - MARGIN)
            d_pnt = (int(x_coordinates[8] * width),int(y_coordinates[8] * height) - MARGIN)
            l_color = (255,128,0)
            l_thk = 3

            # draw a line of idx 4 and 8 finger point.
            cv2.line(annotated_image, s_pnt, d_pnt,l_color,l_thk)

            # calculate minimum distance between idx 4 and 8.
            dist = int(math.sqrt(pow((s_pnt[0]-d_pnt[0]),2)+pow((s_pnt[1]-d_pnt[1]),2)))
            print(dist)
            cv2.putText(annotated_image, f"distance : {dist}",(10,30), cv2.FONT_HERSHEY_DUPLEX,FONT_SIZE, (255,0,0), FONT_THICKNESS, cv2.LINE_AA)


            # send dist data to arduino.
            self.fing_dist = dist
            self.send_int_toArduino(self.fing_dist)

        return annotated_image



    def print_result(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        # print('hand landmarker result: {}'.format(result))
        self.results = result




    def main(self):

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result
            )

        
        cap = cv2.VideoCapture(0)
        timestamp = 0
        with HandLandmarker.create_from_options(options) as landmarker:
            while cap.isOpened():
                ret, frame = cap.read()

                if not ret:
                    print("ignoring empty frame.")
                    break

                timestamp +=1
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                landmarker.detect_async(mp_image, timestamp)

                # if self.results is None:
                # if self.results:
                if not (self.results is None):
                    if len(self.results.handedness):
                        annotated_img = self.draw_landmarks_on_image(mp_image.numpy_view(), self.results)

                        cv2.imshow("annotated img", annotated_img)
                        # print("Hand detected....")
                    else:
                        cv2.imshow("annotated img", frame)
                        print("Hand Not detected....")
                        arduino.sendData([0])

                if(cv2.waitKey(1)) & 0xFF == ord('q'):
                    break
            
        cap.release()
        cv2.destroyAllWindows()
        arduino.sendData([0])


if __name__ == "__main__":
    body_module = MediaPipe_BodyModule()
    body_module.main()
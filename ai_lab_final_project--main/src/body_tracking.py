import cv2
import mediapipe as mp
import numpy as np

from src.frame import Frame
from src.exercise import Exercise

class BodyTracking:
    def __init__(self, source=0):
        """
        Constructor for the BodyTracking class.
        Args:
            source (int | string): The source of the video feed. If 0, the webcam is used. If a string, the video file is used.
        """        
        self.exercise = Exercise(save_model=True)
        self.source = cv2.VideoCapture(source)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.index = 0


    def track_frame(self, np_frame: np.ndarray) -> Frame:
        """
        Function that tracks the body landmarks of a person in a frame using the MediaPipe library.
        Args:
            frame (Frame): The frame object that contains the frame to be tracked.
        Returns:
            Frame: The frame object with the tracked body landmarks.
        """
        frame = Frame(np_frame)
        results = self.mp_pose.process(frame.frame)
        if results.pose_landmarks:
            frame.set_calculation_unit(results.pose_landmarks)
            self.exercise.update_prediction(frame.calculation_unit.angle_dicts)
        return frame
    
    def run(self):
        """
        Function that runs the body tracking process using the webcam or video file.
        """
        cap = self.source
        while cap.isOpened():
            self.index += 1
            ret, frame = cap.read()
            if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
            
            frame = self.track_frame(frame)
            frame.show(point_drawing_function=self.mp_drawing, exercise=self.exercise)

        
            key = cv2.waitKey(10)
            if key & 0xFF == ord('p'):
                while True:
                    key = cv2.waitKey(0)
                    if key & 0xFF == ord('p'):
                        break


        cap.release()
        cv2.destroyAllWindows()

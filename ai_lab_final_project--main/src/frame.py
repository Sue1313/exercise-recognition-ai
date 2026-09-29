"""
This module contains the Frame class, which is used to represent a frame of a video.
The Frame class contains the frame itself, the landmarks of the body pose detected in the frame,
"""

import cv2
import numpy as np
from mediapipe import solutions
from src.constants import IMPORTANT_ANGLES

class FrameCalculationUnit:
    """
    This class agreggates all functions used to calculate angles and predict exercises.
    """
    def __init__(self, mp_pose_points: any = None, frame: np.ndarray = None):
        self.guard = False
        if mp_pose_points is None or frame is None:
            self.guard = True
            return

        self.mp_pose_points = mp_pose_points
        self.frame = frame
        self.angle_dicts = {}

        self.numpy_landmarks = None
        self.calculate_pose_points_coordinate()
        self.calculate_angle_dicts()


    def calculate_pose_points_coordinate(self):
        """
        This function calculates the pose points in the coordinate system of the frame.
        """
        points = []

        for landmark in self.mp_pose_points.landmark:
            denormalized_x, denormalized_y = self.denormalize_point(landmark.x, landmark.y)
            points.append([denormalized_x, denormalized_y])

        self.numpy_landmarks = np.array(points)

    def denormalize_point(self, x, y):
        """
        This function denormalizes a point from the normalized coordinate system
        to the pixel coordinate system.
        """
        return int(x * self.frame.shape[1]), int(y * self.frame.shape[0])

    def calculate_angle_dicts(self):
        """
        This function calculates the angles between the points in the pose
        and a vertical axis.
        """

        for joint, indexes in IMPORTANT_ANGLES.items():
            points = self.numpy_landmarks[indexes]
            angle = FrameCalculationUnit.calculate_angle(points[0], points[1])
            self.angle_dicts[joint] = angle

    @staticmethod
    def calculate_angle(a, b):
        """
        This function calculates the angle between two points.
        """
        ref = np.array([b[0], b[1] - 50])
        p1_ref = a - b
        p2_ref = b - ref

        norm_cos = (1.0 * np.linalg.norm(p1_ref) * np.linalg.norm(p2_ref))
        cos_theta = (np.dot(p1_ref, p2_ref)) / norm_cos
        theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))

        degree = int(180 / np.pi) * theta

        return int(degree)

class Frame:
    """
    This class represents a frame of a video. It uses tools to process it and show it.
    """

    def __init__(self, frame, mp_pose_points=None):
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.calculation_unit = FrameCalculationUnit(mp_pose_points, frame)

    def set_calculation_unit(self, mp_pose_points):
        self.calculation_unit = FrameCalculationUnit(mp_pose_points, self.frame)

    def show(self, point_drawing_function=None, exercise=None):
        """
        This function shows the frame in a window.
        """
        try:
            self.show_pose_elements(point_drawing_function)
            self.show_exercise(exercise)
        except Exception as e:
            print("Error in Frame.show: ", e)

        cv2.imshow('MediaPipe Pose', cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))

    def show_pose_elements(self, point_drawing_function):
        if self.calculation_unit.guard or not point_drawing_function:
            return

        point_drawing_function.draw_landmarks(self.frame, self.calculation_unit.mp_pose_points,
            connections=solutions.pose.POSE_CONNECTIONS)
        self.plot_angles()

    def plot_angles(self):
        for angle_name, _index in self.calculation_unit.angle_dicts.items():
            self.plot_angle(angle_name)

    def show_exercise(self, exercise):
        if not exercise or self.calculation_unit.guard:
            return
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.rectangle(self.frame, (0, 0), (350, 60), (0, 0, 0), cv2.FILLED)
        cv2.putText(self.frame, exercise.current_exercise, (50, 50), font, 1, (255, 255, 255), 2)
        self.plot_wrong_lines(exercise)

    def plot_angle(self, angle_name, color = (51, 204, 255)):
        """
        This function plots the angle ABC between two points.
        """
        def get_angle_position():
            angle_index = IMPORTANT_ANGLES[angle_name]
            return self.calculation_unit.numpy_landmarks[angle_index]

        def draw_dashed_line(image, x1, y1, x2, y2, num_dots=7):
            """
            This function draws a dotted line between two points.
            """
            x_diff = x2 - x1
            y_diff = y2 - y1
            x_step = x_diff / num_dots
            y_step = y_diff / num_dots

            for i in range(num_dots):
                start = (int(x1 + i * x_step), int(y1 + i * y_step))
                end = (int(x1 + (i + 0.5) * x_step), int(y1 + (i + 0.5) * y_step))
                cv2.line(image, start, end, (255, 255, 255), 2)
        
        angles = get_angle_position()
        angle_value = self.calculation_unit.angle_dicts[angle_name]
        a = angles[0]
        b = angles[1]
        c = [b[0], b[1] - 50]
        cv2.circle(self.frame, (b[0] + 35, b[1] + 10), 20, (255,255,255, 0.5), cv2.FILLED)


        cv2.line(self.frame, a, b, color, 2)
        draw_dashed_line(self.frame, b[0], b[1], c[0], c[1])
        cv2.circle(self.frame, b, 3, color, cv2.FILLED)
        cv2.circle(self.frame, a, 3, color, cv2.FILLED)

        font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.rectangle(self.frame, (b[0] - 20, b[1] - 20), (b[0] + 20, b[1] + 20), (255, 255, 255), cv2.FILLED)    
        cv2.putText(self.frame, str(angle_value), (b[0] + 20, b[1] + 20), font, 0.8, color, 2)

    def plot_wrong_lines(self, exercise):
        for joint in exercise.incorrect_joints:
            points = self.calculation_unit.numpy_landmarks[IMPORTANT_ANGLES[joint]]
            cv2.line(self.frame, points[0], points[1], (255, 0, 0), 2)


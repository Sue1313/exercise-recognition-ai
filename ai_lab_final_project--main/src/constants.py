"""
Important angles show what are the observed points that form the lines of the angle.
The b mark should be the angle.
"""
IMPORTANT_ANGLES = {
    "right_knee": [24, 26],
    "left_knee": [23, 25],
    "right_hip": [12, 24],
    "left_hip": [11, 23],
    "right_shoulder": [14, 12],
    "left_shoulder": [13, 11],
    "right_elbow": [16, 14],
    "left_elbow": [15, 13],
}

ACTIONS = ['plank', 'romanian_deadlift', 'russian_twist', 'squat']

ANGLE_LIMITS = {
         'plank': {
            'right_hip': (75, 100),
            'left_hip': (75, 100),
            'right_knee': (80, 110),
            'left_knee': (80, 110),
            'right_shoulder': (0, 17),
            'left_shoulder': (0, 17),
            'right_elbow': (75, 100),
            'left_elbow': (75, 100),
        },
        'squat': {  
            'right_hip': (140, 170),
            'left_hip': (140, 170),
            'right_shoulder': (0, 15),
            'left_shoulder': (0, 15),
            'right_elbow': (140, 170),
            'left_elbow': (140, 170),
            'right_knee': (100, 140),
            'left_knee': (100, 140),
        },
        'romanian_deadlift': {  
            'right_hip': (130,150),
            'left_hip': (130,150),
            'right_shoulder': (0, 15),
            'left_shoulder': (0, 15),
            'right_elbow': (10, 30),
            'left_elbow': (10, 30),
            'right_knee': (110, 140),
            'left_knee': (110, 140),
        },
        'russian_twist': {
            'right_hip': (130, 150),
            'left_hip': (100, 130),
            'right_shoulder': (60, 80),
            'left_shoulder': (0, 30),
            'right_elbow': (75, 90),
            'left_elbow': (150, 175),
            'right_knee': (15, 40),
            'left_knee': (15, 40),

        }
}

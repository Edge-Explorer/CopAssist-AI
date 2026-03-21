try:
    import mediapipe.python.solutions.pose as mp_pose
    import mediapipe.python.solutions.drawing_utils as mp_draw
    print("Direct import SUCCESS! 🎉")
except Exception as e:
    print(f"Direct import FAIL: {e}")

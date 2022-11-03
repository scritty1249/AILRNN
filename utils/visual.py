from scenedetect import detect, ContentDetector
import io
import cv2

def get_scenes(filename: str, threshold = 12.0):
    scene_list = detect(filename, ContentDetector(threshold=threshold))
    return scene_list

def get_frames(filename: str, image_path: str, scenes: list):
    # Extract data from FrameTimeCode format
    frame_nums = [s[0].frame_num for s in scenes]
    
    frames = []
    cap = cv2.VideoCapture(filename)
    for frame in frame_nums:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        success, image = cap.read()
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        if success:
            img_name = "%s\\%s.jpg" % (image_path, timestamp)
            cv2.imwrite(img_name, image)
            frames.append([timestamp / 1000, img_name])
        else: break
    return frames
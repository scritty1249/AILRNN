from scenedetect import detect, ContentDetector, AdaptiveDetector, ThresholdDetector
import cv2

def get_scene_cuts(filename: str, threshold = 27.0, callback = False):
    """Function used for testing. Detects video scenes using the content detection algorithm.

    Args:
        filename (str): The path to the video file.
        threshold (float, optional): Threshold value for scene detection. Defaults to 27.0.
        callback (bool, optional): _description_. Defaults to False.

    Returns:
        frame_nums (list[int | None]): A list of frame numbers denoting the start of each scene. If the scene detection fails, this can be empty.
    """
    scene_list = detect(filename, ContentDetector(threshold=threshold), show_progress=callback)
    frame_nums = [s[0].frame_num for s in scene_list] # Extract data from FrameTimeCode format
    return frame_nums

def get_scene_rolling(filename: str, threshold = 3.0, callback = False):
    """Function used for testing. Detects video scenes using the adaptive detection algorithm.

    Args:
        filename (str): The path to the video file.
        threshold (float, optional): Threshold value for scene detection. Defaults to 3.0.
        callback (bool, optional): _description_. Defaults to False.

    Returns:
        frame_nums (list[int | None]): A list of frame numbers denoting the start of each scene. If the scene detection fails, this can be empty.
    """
    scene_list = detect(filename, AdaptiveDetector(adaptive_threshold=threshold), show_progress=callback)
    frame_nums = [s[0].frame_num for s in scene_list] # Extract data from FrameTimeCode format
    return frame_nums

def get_scene_thresh(filename: str, threshold = 12.0, callback = False):
    """Function used for testing. Detects video scenes using the threshold detection algorithm.

    Args:
        filename (str): The path to the video file.
        threshold (float, optional): Threshold value for scene detection. Defaults to 12.0.
        callback (bool, optional): _description_. Defaults to False.

    Returns:
        frame_nums (list[int | None]): A list of frame numbers denoting the start of each scene. If the scene detection fails, this can be empty.
    """
    scene_list = detect(filename, ThresholdDetector(adaptive_threshold=threshold), show_progress=callback)
    frame_nums = [s[0].frame_num for s in scene_list] # Extract data from FrameTimeCode format
    return frame_nums

def get_scenes(filename: str, content_threshold = 27.0, adaptive_threshold = 3.0, thresh_threshold = 12.0, interval = 10, callback = False):
    """Gets seperate scene frame numbers from a video file, using all three detection algorithms
       Each algorithm will be applied in order, if the previous algorithm fails. If all fail, frames
       at the specified interval will be returned.

    Args:
        filename (str): The path to the video file.
        content_threshold (float, optional): Threshold value for the content scene detection algorithm. Defaults to 27.0.
        adaptive_threshold (float, optional): Threshold value for the adaptive scene detection algorithm. Defaults to 3.0.
        thresh_threshold (float, optional): Threshold value for the threshold scene detection algorithm. Defaults to 12.0.
        interval (int, optional): Interval of frames to return by default if all algorithms fail, in seconds. Defaults to 10.
        callback (bool, optional): Enables the callback feature of each algorithm used. Defaults to False.

    Returns:
        frame_list (list[int]): A list of frames at the start of each significant scene.
    """
    detectors = [
        ContentDetector(threshold=content_threshold),
        AdaptiveDetector(adaptive_threshold=adaptive_threshold),
        ThresholdDetector(threshold=thresh_threshold)
        ]
    # Attempt to detect scenes, using each algorithm
    for detector in detectors:
        try:
            frame_list = detect(filename, detector, show_progress=callback)
        except:
            ...
        # Return scenes from the first successful algorithm
        if frame_list: 
            # Extracting the start frame of each scene from the FrameTimeCode format
            return [s[0].frame_num for s in frame_list]
    
    # If all detectors couldn't determine scenes
    if callback: print("Detectors failed, defaulting to %ss intervals" % interval)
    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count/fps # unnecessary value, but may be useful for later expansion
    frame_list = [frame for frame in range(int(fps * 3), int(frame_count), int(fps * interval))]
    
    return frame_list

def get_frames(filename: str, image_path: str, scenes: list):
    """Saves specified screenshots to image files.

    Args:
        filename (str): The path to the video file.
        image_path (str): The path to the image directory for storage.
        scenes (list[int]): The list of frames to store from the video.

    Returns:
        frames (list[float, str]): A list of timestamps in seconds, and their corrosponding image file paths.
    """
    frames = []
    cap = cv2.VideoCapture(filename)
    for frame in scenes:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        success, image = cap.read()
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
        if success:
            img_name = "%s/%s.jpg" % (image_path, timestamp)
            cv2.imwrite(img_name, image)
            frames.append([timestamp / 1000, img_name])
    return frames
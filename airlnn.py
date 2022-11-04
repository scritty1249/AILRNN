# This program is intended to take an mp4 format media file,
# transcribe the speech, and save it to a text formatted file.
#
# Addendum: Also saves text and periodic screenshots to a PDF file.
# screenshots are deterinmed by scene change detection algorithms, if
# any are found.
#
# Dev note: written for my SO, meant to transcribe her boring ass macroecon professor's lectures lmao
#
# Author: Kyle T. / Scritty

    # The GPU capable builds (Python, NodeJS, C++, etc) depend on CUDA 10.1 and CuDNN v7.6.
    # https://deepspeech.readthedocs.io/en/r0.9/USING.html#cuda-dependency-inference

# TODO:
#   - trim larger videos into smaller chunks to avoid memory leaks(?)
# ! - pickle Transcript object for faster testing
#   - add working progress bar
#   - add UI
#   - add confidence value(?)
#   - significant terms highlighting
#   - codec conversion / media file fixing (example: add moov atom if missing)

import os
from shutil import rmtree
from utils.sound import WAV, Transcript
from utils.visual import get_scenes, get_frames
from utils.pdf import Notes

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true' # Speeds up the DeepSpeech stt time by over 300% if 'true'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # 2: filters INFO and WARN messages, 3: Filter all messages
from deepspeech import Model

# Deepspeech lanugage model constants (specified in https://github.com/mozilla/DeepSpeech/releases)
lang_model = {"alpha": 0.931289039105002, "beta": 1.1834137581510284}

def init_DeepSpeech(model_path: str, lang_path: str):
    """Initalizes a preset DeepSpeech Model.

    Args:
        mdl_path (str): Path to the trained model. (.pbmmm)
        lang_path (str): Path to the language model. (.scorer file)

    Returns:
        deepspeech.Model: The initialized Model.
    """
    model = Model(model_path)
    model.enableExternalScorer(lang_path)
    return model

def test_callback(total_complete, total_length): # Broken, doesnt even work properly (total exceeds current value, buffer doesnt flush despite flush set to true)
    """Generic callback function to be used during testing.

    Args:
        total_complete (int): The current amount.
        total_length (int): The total amount at completion.
    """
    if total_complete == total_length:
        print("                 ")
    else:
        print("\r%s / %s" % (total_complete, total_length), end="", flush=True)
        
# Use ffmpeg-based module to trim larger videos into smaller chunks to avoid memory leaks(?)
# transcription chunking seems to break with any videos longer than 3 minutes...
mediaName = "CISC310_Trim" 
interval = 600 # supposed to be in milliseconds, 8000ms seems optimal


# Working file paths
path = os.path.dirname(os.path.abspath(__file__)) # current working directory
model_path = os.path.join(path, "deepspeech-0.9.3-models.pbmm") # path to model
lang_path = os.path.join(path, "deepspeech-0.9.3-models.scorer") # path to scorer / language model
media_path =  os.path.join(path, "media", mediaName + ".mp4") # path to testing media directory
text_path = os.path.join(path, "text", mediaName) # path to save transcript
pdf_path = os.path.join(path, "pdfs", mediaName) # path to save pdf

# Creating temporary directory for images
try:
    os.mkdir(".images")
except: pass
image_path = os.path.join(path, ".images")

# Initalizing the DeepSpeech model and processing speech
print("Loading Model")
model = init_DeepSpeech(model_path, lang_path)
print("Processing audio")
sample = WAV(media_path)
print("Processing speech")
text = Transcript(sample.file, model)
speech = text()

# Saving the transcript
print("Writing to text file")
text.write(text_path, test_callback)
print("Transcription written to %s" % text_path)


# Saving significant sections of the video
print("Getting scenes")
timestamps = get_scenes(media_path, interval=10)
print("Getting frames")
images = get_frames(media_path, image_path, timestamps)

# Saving the significant video frames with the transcript
print("Saving to pdf")
pdf = Notes(image_path)
pdf.write_scenes(images, speech)
pdf.save(pdf_path)
print("Saved to %s" % pdf_path)

# Cleaning up temporary image directory, with the images
rmtree(".images")
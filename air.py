# This program is intended to take an mp4 format media file,
# transcribe the speech, and save it to a text formatted file.
#
# Dev note: written for my SO, meant to transcribe her boring ass macroecon professor's lectures lmao
#
# Author: Kyle T. / Scritty

    # The GPU capable builds (Python, NodeJS, C++, etc) depend on CUDA 10.1 and CuDNN v7.6.
    # https://deepspeech.readthedocs.io/en/r0.9/USING.html#cuda-dependency-inference

import os
from shutil import rmtree
from utils.sound import WAV, Transcript
from utils.visual import get_scenes, get_frames
from utils.pdf import Notes

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # 2: filters INFO and WARN messages, 3: Filter all messages
from deepspeech import Model


# Deepspeech lanugage model constants (specified in https://github.com/mozilla/DeepSpeech/releases)
lang_model = {"alpha": 0.931289039105002, "beta": 1.1834137581510284}


path = os.path.dirname(os.path.abspath(__file__))

def init_DeepSpeech(mdl_path: str, lang_path: str):
    model = Model(mdl_path)
    model.enableExternalScorer(lang_path)
    return model

model_path = path + "\\deepspeech-0.9.3-models.pbmm"
lang_path = path + "\\deepspeech-0.9.3-models.scorer"
mediaName = "test"
interval = 8 * 1000 # supposed to be in milliseconds, 10000 seems optimal

# Creating temporary directories
try: os.mkdir("images")
except: pass

print("Getting scenes")
timestamps = get_scenes("media/%s.mp4" % mediaName)
print("Getting frames")
images = get_frames("media/%s.mp4" % mediaName, "images", timestamps)

print("Loading Model")
model = init_DeepSpeech(model_path, lang_path)
print("Processing audio")
sample = WAV("media/%s.mp4" % mediaName)
print("Processing speech")
text = Transcript(sample.file, model)
speech = text()
# print("Writing to text file")
# text.write("text/%s" % mediaName)
# print("Transcription written to file.")

print("Saving to file")
pdf = Notes("images")
pdf.write_scenes(images, speech)
pdf.save("notes")
print("Saved.")
rmtree("images")

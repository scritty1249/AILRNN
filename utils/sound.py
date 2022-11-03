import wave
import io
from pydub import AudioSegment as audio
import os
import numpy as np
from pydub.silence import split_on_silence, detect_nonsilent
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # 2: filters INFO and WARN messages, 3: Filter all messages
from deepspeech import Model

class WAV(object):
    def __init__(self, filename):
        filetype = filename.rsplit('.', 1)[1]
        self.file = audio.from_file(filename, filetype)
        
        with wave.open(self.file.export(io.BytesIO(), format='wav'), 'r') as w:
            self.rate = w.getframerate()
            self.frames = w.getnframes()
            self.buffer = w.readframes(self.frames)
            self.filename = filename.rsplit("/", 1)[1]
            self.location = filename
            

class Transcript(object):
    def __init__(self, audio: audio, model: Model):
        with wave.open(audio.export(io.BytesIO(), format='wav'), 'r') as w:
            frames = w.getnframes()
            self.buffer = w.readframes(frames)
        self.audio = audio
        self.model = model
        self.text = []
        self.stamps = []
        self._nonsilent = []
        
    def __call__(self, ms_interval = 5000):
        self._process(ms_interval)
        self._transcribe()
        return zip(self.text, self.stamps)
    
    def write(self, filename: str, callback = None):
        speech = self()
        with open(filename + '.txt', 'w') as f:
            for text, time in speech:
                f.write("%s[%s]\n" % (text, time[0]))
        
    def _transcribe(self, callback = None):
        total_len = sum([len(b) for b in self._nonsilent])
        processed = 0
        for speech in self._nonsilent:
            if not callback is None: callback(total_complete = processed, total_length = total_len)
            self.text.append(self._stt(speech))
            processed += len(speech)
        return self.text
        
    def _process(self, interval, min_silence_len = 100, silence_thresh = -45, keep_silence = 50):
        file = self.audio
        # resample to optimal deepspeech model parameters
        file = file.set_frame_rate(16000)
        file = file.set_channels(1)
        # split on silence
        audio_chunks = split_on_silence(file
                                ,min_silence_len = min_silence_len
                                ,silence_thresh = silence_thresh
                                ,keep_silence = keep_silence
                            )
        
        # pre-trained deepspeech model is used to segements of 4-5 seconds
        sanitized_audio = [audio_chunks[0]]
        for chunk in audio_chunks[1:]:
            if len(sanitized_audio[-1] + chunk) > interval:
                sanitized_audio.append(chunk)
            else:
                sanitized_audio[-1] += chunk

        # Convert to bytes
        sanitized_audio = [b.get_array_of_samples() for b in sanitized_audio]
        
        self._nonsilent = sanitized_audio
        
        # Get timestamps
        talking = detect_nonsilent(file, min_silence_len=min_silence_len, silence_thresh=silence_thresh, seek_step=1)
        for chunk in talking:
            self.stamps.append(
                [speech / 1000 for speech in chunk]
            )

    def _stt(self, data):
        data16 = np.frombuffer(data, dtype=np.int16)
        text = self.model.stt(data16)
        return text
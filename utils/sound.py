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
    """Container for extracting and holding waveform data from a video. Mainly for convenience.
    
    Attributes:
        filename (str): The base name of the file, with the file extension.
        location (str): The full path of the video file.
        
        rate (int): The framerate of the generated waveform.
        frames (int): The number of frames in the generated waveform.
        
        buffer (bytes): The buffer frame data in the generated waveform.
        
        file (pydub.AudioSegment): AudioSegment created of waveform from the video file.
    """
    def __init__(self, filename):
        self.filename = os.path.basename(filename)
        filetype = self.filename.rsplit('.', 1)[1]
        self.file = audio.from_file(filename, filetype)
        
        with wave.open(self.file.export(io.BytesIO(), format='wav'), 'r') as w:
            self.rate = w.getframerate()
            self.frames = w.getnframes()
            self.buffer = w.readframes(self.frames)
            self.location = filename
            

class Transcript(object):
    """Container for the audio and text of any speech.
    """
    def __init__(self, audio: audio, model: Model):
        with wave.open(audio.export(io.BytesIO(), format='wav'), 'r') as w:
            frames = w.getnframes()
            self.buffer = w.readframes(frames)
        self.audio = audio
        self.model = model
        self.text = []
        self.stamps = []
        self._nonsilent = []
        self._speech = None
        
    def __call__(self, ms_interval = 5000):
        """Generate text to speech data

        Args:
            ms_interval (int, optional): Chunk length to be fed into the DeepSpeech Model, in milliseconds. Defaults to 5000.

        Returns:
            speech (list): A list of transcribed text and the corrosponding timestamps.
        """
        self.text = []
        self.stamps = []
        self._process(ms_interval)
        self._transcribe()
        self._speech = list(zip(self.text, self.stamps))
        return self._speech
    
    def write(self, filename: str, callback = None):
        """Save transcribed audio data to a text file.

        Args:
            filename (str): File name (and optionally path) to save the text.
            callback (callable, optional): Callback function. Streams parameters total_complete and total_length.
        """
        if self._speech is None: self.__call__()
        total_len = len(list(self._speech))
        processed = 0
        with open(filename, 'w') as f:
            for text, time in self._speech:
                if not callback is None: callback(total_complete = processed, total_length = total_len)
                f.write("%s [%s - %s]\n" % (text, time[0], time[1]))
                processed += len(text)
        if not callback is None: callback(total_complete = total_len, total_length = total_len)
        
    def _transcribe(self, callback = None):
        """Internal function used to transcribe the speech data

        Args:
            callback (callable, optional): Callback function meant to be served from publically availble functions. Streams parameters total_complete and total_length.

        Returns:
            text (list[str]): A list of transcribed text, seperated into chunks defined by ms_interval as processing.
        """
        total_len = sum([len(b) for b in self._nonsilent])
        processed = 0
        for speech in self._nonsilent:
            if not callback is None: callback(total_complete = processed, total_length = total_len)
            self.text.append(self._stt(speech))
            processed += len(speech)
        return self.text
        
    def _process(self, interval, min_silence_len = 100, silence_thresh = -45):
        """Internal function used to split audio into chunks seperated by silence, and record timestamps for each chunk.

        Args:
            interval (int): Duration of audio chunks to be fed into the DeepSpeech model, in milliseconds.
            min_silence_len (int, optional): The minimum length of silence to split at. Defaults to 100.
            silence_thresh (int, optional): The base for what will be considered silence. Defaults to -45.
            
        Returns:
            None
        """
        file = self.audio
        # resample to optimal deepspeech model parameters
        file = file.set_frame_rate(16000)
        file = file.set_channels(1)
        # split on silence
        audio_chunks = split_on_silence(file
                                ,min_silence_len = min_silence_len
                                ,silence_thresh = silence_thresh
                                ,keep_silence = False
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
        """Interal convenience function to use the DeepSpeech Model speech-to-text function.

        Args:
            data (bytes): The raw buffer data from the audio to interpret.

        Returns:
            text (str): The interpreted transcription of the audio.
        """
        data16 = np.frombuffer(data, dtype=np.int16)
        text = self.model.stt(data16)
        return text
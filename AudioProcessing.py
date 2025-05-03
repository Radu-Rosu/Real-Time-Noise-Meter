import sounddevice as sd
import numpy as np

class AudioProcessor:
    def __init__(self, samplerate=44100, buffer_size=1024):
        self.samplerate = samplerate
        self.buffer_size = buffer_size
        self.current_db = 0
        self.data_history = []

    def capture_audio(self, callback):
        def process_audio(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            # Calculează RMS și convertește în decibeli
            volume_rms = np.sqrt(np.mean(indata**2))
            self.current_db = 20 * np.log10(volume_rms + 1e-6) + 100  # Evităm log(0)
            self.data_history.append(self.current_db)
            callback(self.current_db)  # Trimite valoarea curentă către interfață

        with sd.InputStream(callback=process_audio, blocksize=self.buffer_size, samplerate=self.samplerate, channels=1):
            try:
                while True:  # Captură continuă
                    sd.sleep(100)  # Pauză pentru procesare
            except KeyboardInterrupt:
                print("Audio capture stopped.")

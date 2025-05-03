from AudioProcessing import AudioProcessor
from Visualization import NoiseMeterApp

if __name__ == "__main__":
    print("Starting Real-Time Noise Meter...")
    processor = AudioProcessor()  # Creează procesorul audio
    app = NoiseMeterApp(processor)  # Creează interfața grafică cu procesorul
    app.run()

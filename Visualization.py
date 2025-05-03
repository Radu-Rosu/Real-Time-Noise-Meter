import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import threading

class NoiseMeterApp:
    def __init__(self, processor):
        self.processor = processor
        self.root = tk.Tk()
        self.root.title("Real-Time Noise Meter")
        self.root.geometry("800x600")

        # Indicator de nivel de zgomot
        self.noise_label = tk.Label(self.root, text="Noise Level: 0 dB", font=("Helvetica", 16))
        self.noise_label.pack(pady=10)

        # Bară de progres pentru zgomot
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate", maximum=120)
        self.progress.pack(pady=10)

        # Butoane Start/Stop
        self.start_button = tk.Button(self.root, text="Start", command=self.start_measurement, bg="green", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_measurement, bg="red", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=10)

        # Buton Export
        self.export_button = tk.Button(self.root, text="Export to CSV", command=self.export_to_csv, state=tk.DISABLED)
        self.export_button.pack(pady=10)

        # Praguri pentru zgomot
        self.threshold_frame = tk.Frame(self.root)
        self.threshold_frame.pack(pady=10)
        tk.Label(self.threshold_frame, text="Thresholds:").grid(row=0, column=0, padx=5)
        tk.Label(self.threshold_frame, text="Silence: <30 dB").grid(row=1, column=0, padx=5)
        tk.Label(self.threshold_frame, text="Normal: 30-60 dB").grid(row=2, column=0, padx=5)
        tk.Label(self.threshold_frame, text="Noisy: >60 dB").grid(row=3, column=0, padx=5)

        # Vizualizare grafică (graf)
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.ax.set_ylim(0, 120)  # Interval dB
        self.ax.set_title("Real-Time Noise Levels")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("dB")
        self.line, = self.ax.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        # Stiluri pentru bara de progres
        style = ttk.Style(self.root)
        style.configure("green.Horizontal.TProgressbar", foreground="green", background="green")
        style.configure("yellow.Horizontal.TProgressbar", foreground="yellow", background="yellow")
        style.configure("red.Horizontal.TProgressbar", foreground="red", background="red")

        self.running = False
        self.thread = None

    def start_measurement(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.DISABLED)
        self.thread = threading.Thread(target=self.processor.capture_audio, args=(self.update_visuals,))
        self.thread.start()

    def stop_measurement(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL)

    def update_visuals(self, db_level):
        if not self.running:
            return

        # Actualizare label și bară de progres
        self.noise_label.config(text=f"Noise Level: {db_level:.2f} dB")
        self.progress["value"] = min(max(db_level, 0), 120)

        # Schimbare culoare pe baza pragurilor
        if db_level < 30:
            self.progress.config(style="green.Horizontal.TProgressbar")
        elif 30 <= db_level <= 60:
            self.progress.config(style="yellow.Horizontal.TProgressbar")
        else:
            self.progress.config(style="red.Horizontal.TProgressbar")

        # Actualizare grafic
        self.line.set_ydata(self.processor.data_history)
        self.line.set_xdata(range(len(self.processor.data_history)))
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def export_to_csv(self):
        with open("noise_data.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Time (s)", "dB"])
            for i, db in enumerate(self.processor.data_history):
                writer.writerow([i / self.processor.samplerate, db])  # Normalizează timpul la secunde
        print("Data exported to noise_data.csv.")

    def run(self):
        self.root.mainloop()

import threading
import tkinter as tk
class ColorSquare:
    def __init__(self, color="red", size=50, corner="top_left"):
        self.root = tk.Tk()
        self.color = color
        self.size = size

        # Rimuove bordi e titolo della finestra
        self.root.overrideredirect(True)

        # Ottiene le dimensioni dello schermo
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Posiziona il quadrato nell'angolo specificato
        if corner == "top_left":
            self.x = 0
            self.y = 0
        elif corner == "top_right":
            self.x = self.screen_width - size
            self.y = 0
        elif corner == "bottom_left":
            self.x = 0
            self.y = self.screen_height - size
        elif corner == "bottom_right":
            self.x = self.screen_width - size
            self.y = self.screen_height - size

        # Imposta le dimensioni e la posizione della finestra
        self.root.geometry(f"{size}x{size}+{self.x}+{self.y}")

        # Crea un Canvas e disegna un rettangolo
        self.canvas = tk.Canvas(self.root, width=size, height=size, highlightthickness=0)
        self.square = self.canvas.create_rectangle(0, 0, size, size, fill=self.color, outline=self.color)
        self.canvas.pack()

        # Imposta la finestra in primo piano
        self.root.attributes('-topmost', True)

        # Avvia il thread per tkinter
        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def change_color(self, new_color):
        self.canvas.itemconfig(self.square, fill=new_color, outline=new_color)
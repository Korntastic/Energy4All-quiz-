import tkinter as tk
from tkinter import messagebox
import pandas as pd
import random
import pygame
from PIL import Image, ImageTk

# Initialize Pygame mixer for sound
pygame.mixer.init()

# Load quiz data
quiz_data = pd.read_csv("energy_quizzes.csv")
questions = quiz_data.to_dict(orient="records")
random.shuffle(questions)

# Sound files
BACKGROUND_MUSIC = "assets/sounds/background.mp3"
SUCCESS_SOUND = "assets/sounds/correct.mp3"
ERROR_SOUND = "assets/sounds/wrong.mp3"
TIP_SOUND = "assets/sounds/ding.mp3"

try:
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.play(-1)  # Loop forever
except Exception as e:
    print("Background music not found:", e)

# Color Palette
PRIMARY_BG = "#FFF1CA"   # Light Yellow
BUTTON_BG = "#FFB823"   # Bright Orange
TEXT_COLOR = "#2D4F2B"  # Dark Forest Green

# Avatar images
avatar_images = [
    "assets/images/avatar1.png",
    "assets/images/avatar2.png",
    "assets/images/avatar3.png"
]

class EnergyQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌱 Energy4All - Energy-Saving Quiz")
        self.root.geometry("900x650")
        self.root.configure(bg=PRIMARY_BG)

        self.score = 0
        self.current_index = 0
        self.avatar_index = 0

        # Frame for Avatar + Level + Progress
        self.top_frame = tk.Frame(root, bg=PRIMARY_BG)
        self.top_frame.pack(pady=20)

        # Avatar label
        self.avatar_label = tk.Label(self.top_frame, bg=PRIMARY_BG)
        self.avatar_label.pack(side=tk.LEFT, padx=20)

        # Level label
        self.level_label = tk.Label(self.top_frame, text="Level 0", font=("Arial", 16, "bold"), fg=TEXT_COLOR, bg=PRIMARY_BG)
        self.level_label.pack(side=tk.LEFT, padx=20)

        # Progress bar
        self.progress_bar = tk.Canvas(self.top_frame, width=400, height=20, bg="#c8e6c9", highlightthickness=0)
        self.progress_bar.pack(pady=10, side=tk.LEFT)

        # Question label
        self.question_label = tk.Label(
            root,
            text="🌿 Welcome to the Energy4All Quiz!\nClick below to start learning how to save energy.",
            font=("Helvetica", 18, "bold"),
            wraplength=700,
            justify="center",
            bg=PRIMARY_BG,
            fg=TEXT_COLOR
        )
        self.question_label.pack(pady=20)

        # Options frame
        self.options_frame = tk.Frame(root, bg=PRIMARY_BG)
        self.options_frame.pack()

        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.options_frame,
                text="",
                width=60,
                height=2,
                bg=BUTTON_BG,
                fg=TEXT_COLOR,
                font=("Arial", 12),
                relief="flat",
                bd=0,
                padx=10,
                pady=10,
                command=lambda idx=i: self.check_answer(idx)
            )
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#f0f0f0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BUTTON_BG))
            self.option_buttons.append(btn)

        # Tip label
        self.tip_label = tk.Label(
            root,
            text="",
            font=("Helvetica", 14),
            wraplength=700,
            bg="#CCF7BC",
            fg="green",
            padx=20,
            pady=10
        )

        # Next button (now placed directly below avatar section)
        self.next_button = tk.Button(
            root,
            text="Start Quiz ▶",
            command=self.start_quiz,
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            font=("Arial", 14),
            width=20,
            relief="flat",
            padx=10,
            pady=10
        )
        self.next_button.pack(pady=10)  # Moved closer

        # Start screen
        self.show_start_screen()

    def show_start_screen(self):
        self.question_label.config(text="🌿 Welcome to the Energy4All Quiz!\nClick below to start learning how to save energy.", font=("Helvetica", 18, "bold"))
        self.next_button.config(text="Start Quiz ▶", command=self.start_quiz)
        self.next_button.pack(pady=10)
        self.tip_label.pack_forget()
        for btn in self.option_buttons:
            btn.pack_forget()

    def start_quiz(self):
        self.question_label.config(font=("Helvetica", 16))
        self.current_index = 0
        self.score = 0
        self.wrong_questions = []
        self.load_question()

    def load_question(self):
        if self.current_index >= len(questions):
            self.show_final_score()
            return

        q = questions[self.current_index]
        self.question_label.config(text=q["question"])

        options = [q["option_a"], q["option_b"], q["option_c"], q["option_d"]]
        self.correct_answer = q["answer"].strip().lower()
        self.correct_index = ord(self.correct_answer) - ord("a")

        for i, btn in enumerate(self.option_buttons):
            btn.config(text=options[i], bg=BUTTON_BG, state=tk.NORMAL)
            btn.pack()
            btn.bind("<Button-1>", lambda e, idx=i: self.handle_click(idx))

        self.tip_label.config(text="")
        self.tip_label.pack_forget()
        self.next_button.pack_forget()

        self.update_progress()

    def handle_click(self, index):
        for btn in self.option_buttons:
            btn.unbind("<Button-1>")

        selected = chr(index + ord("a")).lower()

        if selected == self.correct_answer:
            self.score += 1
            self.option_buttons[index].config(bg="#b2fab4")  # Green
            play_sound(SUCCESS_SOUND)
        else:
            self.option_buttons[index].config(bg="#f8bfbf")  # Red
            self.option_buttons[self.correct_index].config(bg="#b2fab4")  # Highlight correct
            play_sound(ERROR_SOUND)

        self.avatar_index = min(self.score // 5, len(avatar_images) - 1)
        self.update_avatar_and_level()

        self.tip_label.config(text="💡 " + questions[self.current_index]["tip"])
        self.tip_label.pack(pady=10, fill=tk.X)
        play_sound(TIP_SOUND)

        self.next_button.config(text="Next Question ➡", command=self.next_question)
        self.next_button.pack(pady=10)

    def update_avatar_and_level(self):
        try:
            img = Image.open(avatar_images[self.avatar_index]).convert("RGBA").resize((100, 100), Image.LANCZOS)
            self.avatar_img = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.avatar_img)
        except Exception as e:
            print("Avatar image not found or failed to load:", e)
            self.avatar_label.config(text="🌳", font=("Arial", 40))

        # Update level text
        self.level_label.config(text=f"Level {self.avatar_index + 1}")

    def update_progress(self):
        percent = (self.current_index + 1) / len(questions) * 100
        self.progress_bar.delete("progress")
        self.progress_bar.create_rectangle(0, 0, percent * 4, 20, fill="#4caf50", tags="progress")
        self.progress_bar.create_text(200, 10, text=f"{int(percent)}%", fill="white", tags="progress")

    def next_question(self):
        self.current_index += 1
        self.tip_label.pack_forget()
        self.next_button.pack_forget()
        for btn in self.option_buttons:
            btn.config(bg=BUTTON_BG, state=tk.NORMAL)
        self.load_question()

    def show_final_score(self):
        self.question_label.config(
            text=f"🏆 Quiz Completed!\nYour final score is {self.score} out of {len(questions)}",
            font=("Helvetica", 20, "bold")
        )
        for btn in self.option_buttons:
            btn.pack_forget()
        self.tip_label.pack_forget()
        self.next_button.config(text="Try Again 🔁", command=self.restart_quiz)
        self.next_button.pack(pady=10)

    def restart_quiz(self):
        self.score = 0
        self.current_index = 0
        random.shuffle(questions)
        self.question_label.config(text="")
        for btn in self.option_buttons:
            btn.pack()
        self.next_button.pack_forget()
        self.show_start_screen()


def play_sound(file):
    try:
        pygame.mixer.Sound(file).play()
    except Exception:
        pass


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyQuizApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import os # Required for file existence check
import random
import re

# =================================================================
# === ACTIVITY 1: SCREEN PET (Encapsulated from screen pet.py) ===
# =================================================================

def run_screen_pet():
    # Helper to prevent Tcl error if called multiple times
    try:
        root_pet = tk.Toplevel() 
    except tk.TclError:
        root_pet = tk.Tk()
        
    root_pet.title("Screen Pet")

    body_color = 'SkyBlue' 
    idle_timer = None 
    cheeky_duration = 1000 
    poop_items = []

    # --- PET ACTION FUNCTIONS ---
    def toggle_eyes():
        current_color = c.itemcget(eye_left, 'fill')
        new_color = body_color if current_color == 'white' else 'white'
        
        current_state = c.itemcget(pupil_left, 'state')
        new_state = tk.NORMAL if current_state == tk.HIDDEN else tk.HIDDEN
        
        c.itemconfig(pupil_left, state=new_state)
        c.itemconfig(pupil_right, state=new_state)
        c.itemconfig(eye_left, fill=new_color)
        c.itemconfig(eye_right, fill=new_color)

    def blink():
        toggle_eyes()
        root_pet.after(250, toggle_eyes)
        root_pet.after(3000, blink)

    def toggle_pupils():
        if c.eyes_crossed:
            c.move(pupil_left, -10, 5)
            c.move(pupil_right, 10, 5)
            c.eyes_crossed = False
        elif not c.is_sad:
            c.move(pupil_left, 10, -5)
            c.move(pupil_right, -10, -5)
            c.eyes_crossed = True

    def cheeky(event):
        reset_idle_timer()

        # Hide ALL conflicting elements
        c.itemconfigure(mouth_normal, state=tk.HIDDEN)
        c.itemconfigure(mouth_happy, state=tk.HIDDEN)
        c.itemconfigure(mouth_sad, state=tk.HIDDEN)
        c.itemconfigure(cheek_left, state=tk.HIDDEN)
        c.itemconfigure(cheek_right, state=tk.HIDDEN)
        
        # Show the corrected cheeky mouth
        c.itemconfigure(mouth_cheeky, state=tk.NORMAL)
        
        # Ensure eyes are open and not crossed, matching the cheeky image
        if c.eyes_crossed:
            toggle_pupils()
        c.itemconfig(pupil_left, state=tk.NORMAL)
        c.itemconfig(pupil_right, state=tk.NORMAL)
        c.itemconfig(eye_left, fill='white')
        c.itemconfig(eye_right, fill='white')
        
        c.is_sad = False
        c.tongue_out = False
        
        # Schedule the return to normal state
        root_pet.after(cheeky_duration, lambda: hide_cheeky_and_restore_normal(event))

    def hide_cheeky_and_restore_normal(event):
        c.itemconfigure(mouth_cheeky, state=tk.HIDDEN)
        hide_happy(event)

    def show_happy(event):
        reset_idle_timer()
        if c.is_sad:
            # Restore color if it was changed (though `sad` is now modified not to change it)
            c.itemconfigure(body, fill=body_color) 
            c.itemconfigure(mouth_sad, state=tk.HIDDEN)
            c.itemconfigure(mouth_normal, state=tk.NORMAL)
            c.is_sad = False

        c.itemconfigure(mouth_cheeky, state=tk.HIDDEN)

        # Check if cursor is within the main body area (approx)
        if (20 <= event.x <= 350) and (20 <= event.y <= 350):
            c.itemconfigure(cheek_left, state=tk.NORMAL)
            c.itemconfigure(cheek_right, state=tk.NORMAL)
            c.itemconfigure(mouth_happy, state=tk.NORMAL)
            c.itemconfigure(mouth_normal, state=tk.HIDDEN)

    def hide_happy(event):
        reset_idle_timer()
        c.itemconfigure(cheek_left, state=tk.HIDDEN)
        c.itemconfigure(cheek_right, state=tk.HIDDEN)
        c.itemconfigure(mouth_happy, state=tk.HIDDEN)
        c.itemconfigure(mouth_sad, state=tk.HIDDEN)
        c.itemconfigure(mouth_cheeky, state=tk.HIDDEN)
        
        if not c.is_sad:
            c.itemconfigure(mouth_normal, state=tk.NORMAL)

    def sad():
        c.is_sad = True
        c.itemconfigure(mouth_happy, state=tk.HIDDEN)
        c.itemconfigure(mouth_normal, state=tk.HIDDEN)
        c.itemconfigure(mouth_sad, state=tk.NORMAL)
        c.itemconfigure(mouth_cheeky, state=tk.HIDDEN) 

        c.itemconfigure(cheek_left, state=tk.HIDDEN)
        c.itemconfigure(cheek_right, state=tk.HIDDEN)
        c.tongue_out = False 

        if c.eyes_crossed:
            toggle_pupils()
        c.itemconfig(pupil_left, state=tk.NORMAL)
        c.itemconfig(pupil_right, state=tk.NORMAL)
        c.itemconfig(eye_left, fill='white')
        c.itemconfig(eye_right, fill='white')

        # --- MODIFIED: Pet stays SkyBlue when sad ---
        c.itemconfig(body, fill=body_color) # Pet remains the original body_color ('SkyBlue')
        # --- END MODIFIED ---
        
        print("The pet is sad due to inactivity!")

    # --- IDLE TIMER MANAGEMENT ---
    def reset_idle_timer():
        nonlocal idle_timer
        if idle_timer is not None:
            root_pet.after_cancel(idle_timer)
        idle_timer = root_pet.after(5000, sad)

    # ===================================================================
    # === FEED AND CLEAN UP FUNCTIONS ===
    # ===================================================================

    def feed():
        reset_idle_timer()
        print("Pet has been fed! Scheduling a clean-up...")
        root_pet.after(5000, show_poo)

    def show_poo():
        for item in poop_items:
             c.itemconfigure(item, state=tk.NORMAL)
        print("Uh oh! The Screen Pet made a mess!")

    def clean_up():
        reset_idle_timer()
        for item in poop_items:
            c.itemconfigure(item, state=tk.HIDDEN)
        print("All clean! The pet is happy.")


    # =================================================================
    # === TKINTER SETUP and DRAWING ===
    # =================================================================

    main_frame = tk.Frame(root_pet)
    main_frame.pack()

    c = tk.Canvas(main_frame, width=400, height=400, highlightthickness=0)
    c.configure(bg='dark blue')

    # PET DRAWING OBJECTS
    body = c.create_oval(35, 20, 365, 350, outline=body_color, fill=body_color)
    ear_left = c.create_polygon(75, 80, 75, 10, 165, 70, outline=body_color, fill=body_color)
    ear_right = c.create_polygon(255, 45, 325, 10, 320, 70, outline=body_color, fill=body_color)
    foot_left = c.create_oval(65, 320, 145, 360, outline=body_color, fill=body_color)
    foot_right = c.create_oval(250, 320, 330, 360, outline=body_color, fill=body_color)

    eye_left = c.create_oval(130, 110, 160, 170, outline='black', fill='white')
    pupil_left = c.create_oval(140, 145, 150, 155, outline='black', fill='black')
    eye_right = c.create_oval(230, 110, 260, 170, outline='black', fill='white')
    pupil_right = c.create_oval(240, 145, 250, 155, outline='black', fill='black')

    # MOUTH AND TONGUE
    mouth_normal = c.create_line(170, 250, 200, 272, 230, 250, smooth=1, width=2, state=tk.NORMAL)
    mouth_happy = c.create_line(170, 250, 200, 282, 230, 250, smooth=1, width=2, state=tk.HIDDEN)
    mouth_sad = c.create_line(170, 250, 200, 232, 230, 250, smooth=1, width=2, state=tk.HIDDEN)

    # CORRECTED Cheeky Mouth Object
    mouth_cheeky = c.create_arc(160, 220, 240, 300, 
                                 start=0, extent=-180, 
                                 fill='red', outline='red', style='chord', state=tk.HIDDEN)

    # CHEEKS
    cheek_left = c.create_oval(70, 180, 120, 230, outline='pink', fill='pink', state=tk.HIDDEN)
    cheek_right = c.create_oval(280, 180, 330, 230, outline='pink', fill='pink', state=tk.HIDDEN)

    # POOP GRAPHIC CREATION
    poop_coords = [
        (180, 350, 200, 370), 
        (190, 340, 210, 360), 
        (200, 350, 220, 370),
        (210, 340, 230, 360) 
    ]
    for x1, y1, x2, y2 in poop_coords:
        poop_item = c.create_oval(x1, y1, x2, y2, fill='saddle brown', outline='saddle brown', state=tk.HIDDEN)
        poop_items.append(poop_item)

    c.pack() 

    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)

    feed_button = tk.Button(button_frame, text="Feed me!", command=feed)
    feed_button.pack(side=tk.LEFT, padx=10)

    clean_button = tk.Button(button_frame, text="Clean up!", command=clean_up)
    clean_button.pack(side=tk.LEFT, padx=10)

    # BINDINGS
    c.bind('<Motion>', show_happy) 
    c.bind('<Leave>', hide_happy) 
    c.bind('<Double-1>', cheeky) 

    root_pet.bind('<Button-1>', lambda event: reset_idle_timer())
    root_pet.bind('<Key>', lambda event: reset_idle_timer())

    # INITIAL STATE
    c.eyes_crossed = False
    c.tongue_out = False
    c.is_sad = False 

    root_pet.after(1000, blink)
    reset_idle_timer() 
    
# =================================================================
# === ACTIVITY 2: QUIZ (Modified from quizz.py to use Tkinter) ===
# =================================================================

# File for saving permanent questions in this self-contained Python app
# NOTE: In a true web application environment, this would use Firestore.
PERMANENT_QUESTIONS_FILE = 'quiz_questions.json'

class QuizApp:
    def __init__(self, master):
        self.master = master
        master.title("General Knowledge Quiz")
        master.geometry("500x400") # Increased height for new button
        master.config(bg='#f0f8ff') # AliceBlue background

        # Hardcoded questions
        self.default_questions = [
            ("what is 1 + 1?", '2'),
            ("which is da largest contry in da world?", 'Russia'),
            ("when did world war 2 start and end?(_____-_____) (e.g. 1900-1910)", '1939-1945')
        ]
        self.permanent_questions = self._load_permanent_questions()
        # Ensure 'self.questions' is always the combined list
        self.questions = self.default_questions + self.permanent_questions
        
        self.current_q = 0
        self.score = 0
        
        self.font_style = ("Inter", 12)
        self.header_font = ("Inter", 14, "bold")

        # UI Setup
        self.question_label = tk.Label(master, text="", font=self.header_font, bg='#f0f8ff')
        self.question_label.pack(pady=20)

        self.answer_entry = tk.Entry(master, font=self.font_style, width=30)
        self.answer_entry.pack(pady=10)
        
        self.submit_button = tk.Button(master, text="Submit Answer", command=self.check_answer, font=self.font_style, bg='#4CAF50', fg='white', relief=tk.RAISED)
        self.submit_button.pack(pady=10)
        
        self.status_label = tk.Label(master, text="", font=self.font_style, bg='#f0f8ff', fg='blue')
        self.status_label.pack(pady=10)

        # Permanent Question Management Buttons Frame
        self.management_frame = tk.Frame(master, bg='#f0f8ff')
        self.management_frame.pack(pady=5)
        
        # New button for adding questions
        self.add_q_button = tk.Button(self.management_frame, text="Add Permanent Question", command=self.open_add_question_window, font=("Inter", 10), bg='#FFA500', fg='white', relief=tk.RAISED)
        self.add_q_button.pack(side=tk.LEFT, padx=5)

        # New button for deleting the current permanent question (initially hidden)
        self.delete_q_button = tk.Button(
            self.management_frame, 
            text="Delete This Permanent Question", 
            command=self.delete_current_question, 
            font=("Inter", 10), 
            bg='#DC3545', # Red for danger/delete
            fg='white', 
            relief=tk.RAISED
        )
        self.delete_q_button.pack(side=tk.LEFT, padx=5)
        self.delete_q_button.pack_forget() # Hide it initially

        self.next_question()

    def _load_permanent_questions(self):
        """Loads questions from the local file."""
        if os.path.exists(PERMANENT_QUESTIONS_FILE):
            try:
                with open(PERMANENT_QUESTIONS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error reading permanent questions file. Starting fresh.")
                return []
        return []

    def _save_permanent_questions(self):
        """Saves current permanent questions list to the local file.""" 
        try:
            with open(PERMANENT_QUESTIONS_FILE, 'w') as f:
                json.dump(self.permanent_questions, f)
        except Exception as e:
            print(f"Error saving permanent questions: {e}")

    def is_permanent_question(self):
        """Checks if the current question is one of the user-added permanent questions.""" 
        # A question is permanent if its index is greater than or equal to 
        # the number of default questions.
        return self.current_q >= len(self.default_questions)

    def delete_current_question(self):
        """Deletes the current question if it is a permanent one.""" 
        if not self.is_permanent_question():
            # Should never happen if button is hidden correctly, but good for safety
            messagebox.showwarning("Error", "Only user-added permanent questions can be deleted.")
            return

        # Calculate the index of the question within the permanent_questions list
        permanent_index = self.current_q - len(self.default_questions)

        # Confirmation before deletion
        q_text, _ = self.questions[self.current_q]
        if not messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to permanently delete this question?\n\nQuestion: {q_text}"
        ):
            return

        # Delete the question from the permanent list
        del self.permanent_questions[permanent_index]
        self._save_permanent_questions()
        
        # Re-sync all questions
        self.questions = self.default_questions + self.permanent_questions

        messagebox.showinfo("Deleted", "Question successfully deleted! Moving to the next question.")

        # If the quiz is now finished after deletion
        if self.current_q >= len(self.questions):
             self.current_q = 0 # Reset to start if we deleted the last one and quiz is empty
             if not self.questions:
                 self.next_question()
                 return

        # Do not increment self.current_q as the remaining questions shifted back.
        # Just call next_question to display the question now at the same index.
        self.next_question()


    def open_add_question_window(self):
        """Opens a new window for adding a question/answer pair.""" 
        add_window = tk.Toplevel(self.master)
        add_window.title("Add New Quiz Question")
        add_window.geometry("400x200")
        add_window.config(bg='#e0ffff')

        tk.Label(add_window, text="New Question:", font=self.font_style, bg='#e0ffff').pack(pady=5)
        q_entry = tk.Entry(add_window, width=50, font=self.font_style)
        q_entry.pack(pady=5, padx=10)

        tk.Label(add_window, text="Correct Answer:", font=self.font_style, bg='#e0ffff').pack(pady=5)
        a_entry = tk.Entry(add_window, width=50, font=self.font_style)
        a_entry.pack(pady=5, padx=10)

        save_button = tk.Button(
            add_window, 
            text="Save Question Permanently", 
            command=lambda: self.add_permanent_question(add_window, q_entry.get(), a_entry.get()), 
            font=self.font_style, 
            bg='#1e90ff', 
            fg='white'
        )
        save_button.pack(pady=15)

    def add_permanent_question(self, window, question, answer):
        """Adds a new question to the permanent list and restarts the quiz.""" 
        question = question.strip()
        answer = answer.strip()

        if not question or not answer:
            messagebox.showwarning("Missing Input", "Please provide both a question and a correct answer.")
            return

        new_pair = (question, answer)
        self.permanent_questions.append(new_pair)
        self._save_permanent_questions()
        
        # Re-sync all questions
        self.questions = self.default_questions + self.permanent_questions

        messagebox.showinfo("Success", "Question saved! Restarting quiz with new content.")
        window.destroy()

        # Reset and restart the quiz flow
        self.current_q = 0
        self.score = 0
        self.next_question()

    def next_question(self):
        # Determine button visibility
        if self.is_permanent_question():
            self.delete_q_button.pack(side=tk.LEFT, padx=5)
        else:
            self.delete_q_button.pack_forget()

        if self.current_q < len(self.questions):
            q, _ = self.questions[self.current_q]
            self.question_label.config(text=f"Question {self.current_q + 1}/{len(self.questions)}: {q}")
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.config(state=tk.NORMAL)
            self.submit_button.config(state=tk.NORMAL)
            self.status_label.config(text="quizzz time!!! :)")
        else:
            self.question_label.config(text=f"Quiz Finished! Final Score: {self.score}/{len(self.questions)}")
            self.answer_entry.config(state=tk.DISABLED)
            self.submit_button.config(state=tk.DISABLED, text="Finished")
            self.delete_q_button.pack_forget() # Hide delete button when done
            self.status_label.config(text="Great job!")

    def check_answer(self):
        _, answer = self.questions[self.current_q]
        user_guess = self.answer_entry.get().strip()
        
        if user_guess.lower() == answer.lower():
            self.score += 1
            self.status_label.config(text="Correct Answer!", fg='green')
        else:
            self.status_label.config(text=f"Incorrect. The answer was: {answer}", fg='red')
            
        self.current_q += 1
        self.master.after(1500, self.next_question) # Wait a moment before moving on

def run_quiz():
    try:
        root_quiz = tk.Toplevel()
    except tk.TclError:
        root_quiz = tk.Tk()
    QuizApp(root_quiz)

# =================================================================
# === ACTIVITY 3: STORY MAKER (Upgraded with AI-ish generator) ===
# =================================================================

class StoryGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Interactive Story Creator")
        master.geometry("900x700")
        master.config(bg='#f4f7f6')

        # --- Styling ---
        self.font_style = ("Inter", 12)
        self.header_font = ("Inter", 18, "bold")

        # --- Main Title ---
        title_label = tk.Label(master, text="The Story Lab (AI-ish Generator)", font=self.header_font, bg='#f4f7f6', fg='#2c3e50')
        title_label.pack(pady=10)

        # --- 1. Tabbed Input Section (Notebook) ---
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=5, padx=20, fill="x")

        # Create Frames for each tab
        self.title_frame = ttk.Frame(self.notebook, padding="10")
        self.char_frame = ttk.Frame(self.notebook, padding="10")
        self.place_frame = ttk.Frame(self.notebook, padding="10")
        self.script_frame = ttk.Frame(self.notebook, padding="10")
        
        # Add the frames to the notebook (tabs)
        self.notebook.add(self.title_frame, text="Story Title")
        self.notebook.add(self.char_frame, text="Characters")
        self.notebook.add(self.place_frame, text="Places")
        self.notebook.add(self.script_frame, text="Story Script")

        # Title tab uses a simple Entry (user may provide a title)
        self._setup_title_tab(self.title_frame)

        # Other tabs use the reusable helper
        self._setup_input_tab(self.char_frame, "Character List (e.g., Hero, Villain, Sidekick):", "char_input")
        self._setup_input_tab(self.place_frame, "Key Locations (e.g., Magic Forest, Old Tower, Secret Base):", "place_input")
        self._setup_input_tab(self.script_frame, "Plot Summary / Prompt (Write a short prompt or scene you'd like to expand):", "script_input")
        
        # --- 2. Make Story Button ---
        make_story_button = tk.Button(
            master, 
            text="Generate Story Draft", 
            command=self.generate_story,
            font=("Inter", 14, "bold"),
            bg='#3498db', # Blue button
            fg='white', 
            activebackground='#2980b9',
            activeforeground='white',
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        make_story_button.pack(pady=10)
        
        # --- 3. Output Section ---
        output_label = tk.Label(master, text="Generated Story Output:", font=("Inter", 14, "bold"), bg='#f4f7f6', fg='#2c3e50')
        output_label.pack(pady=(10, 5), padx=20, anchor='w')
        
        self.story_output = scrolledtext.ScrolledText(
            master, 
            wrap=tk.WORD, 
            width=100, 
            height=22, 
            font=("Inter", 11),
            bg='white',
            fg='#333',
            bd=1,
            relief=tk.SUNKEN
        )
        self.story_output.pack(padx=20, pady=(0, 20), fill="both", expand=True)

    def _setup_title_tab(self, frame):
        """Title tab: a single-line input to optionally provide a title."""
        tk.Label(frame, text="Optional Story Title (leave blank to auto-generate):", font=self.font_style, bg='white', fg='#555').pack(pady=(0,5), anchor='w')
        self.title_entry = tk.Entry(frame, font=self.font_style, width=80)
        self.title_entry.pack(padx=5, pady=5, fill='x')

    def _setup_input_tab(self, frame, label_text, widget_name):
        """Helper function to set up the label and Text widget for each tab."""
        label = tk.Label(frame, text=label_text, font=self.font_style, bg='white', fg='#555')
        label.pack(pady=(0, 5), anchor='w')
        
        text_widget = scrolledtext.ScrolledText(
            frame, 
            wrap=tk.WORD, 
            width=80, 
            height=6, 
            font=self.font_style,
            bg='#ecf0f1', # Light gray background
            fg='#333',
            bd=1,
            relief=tk.FLAT
        )
        text_widget.pack(fill="both", expand=True)
        # Attach the text widget to the instance for later retrieval
        setattr(self, widget_name, text_widget)

    # -------------------------
    # Simple AI-ish helpers
    # -------------------------
    def _auto_title_from_prompt(self, prompt):
        """Create a short title from the prompt by picking salient words."""
        prompt = prompt.strip()
        if not prompt:
            return "Untitled Tale"
        # Remove punctuation, get words
        words = re.findall(r"\b\w+\b", prompt)
        # pick up to 5 unique words that are longer than 3 letters
        candidates = [w.capitalize() for w in words if len(w) > 3]
        if not candidates:
            # fallback to first words
            candidates = [w.capitalize() for w in words][:5]
        title_words = []
        seen = set()
        for w in candidates:
            if w.lower() not in seen:
                title_words.append(w)
                seen.add(w.lower())
            if len(title_words) >= 4:
                break
        title = " ".join(title_words)
        if len(title) < 3:
            title = "The " + (title_words[0] if title_words else "Journey")
        # add a short flair
        flair = random.choice(["Saga", "Tale", "Chronicle", "Legend", "Story"])
        return f"{title}: A {flair}"

    def _auto_characters_from_prompt(self, prompt, num=3):
        """Create a short list of characters from the prompt (or invent if none found)."""
        prompt = prompt.strip()
        # Look for capitalized words (proper nouns)
        caps = re.findall(r'\b[A-Z][a-z]{2,}\b', prompt)
        uniq = []
        for c in caps:
            if c not in uniq:
                uniq.append(c)
            if len(uniq) >= num:
                break
        if len(uniq) >= 1:
            # Map to roles
            roles = ["Protagonist", "Sidekick", "Antagonist"]
            characters = []
            for i in range(num):
                name = uniq[i] if i < len(uniq) else f"{roles[i]}{random.randint(1,99)}"
                characters.append(f"{roles[i]} - {name}")
            return characters

        # Otherwise pick salient words from prompt
        words = re.findall(r"\b\w+\b", prompt)
        freq = {}
        for w in words:
            lw = w.lower()
            if len(w) > 3:
                freq[lw] = freq.get(lw, 0) + 1
        # sort by frequency
        sorted_words = sorted(freq.keys(), key=lambda k: (-freq[k], k))
        characters = []
        roles = ["Protagonist", "Sidekick", "Antagonist"]
        for i in range(num):
            if i < len(sorted_words):
                candidate = sorted_words[i].capitalize()
            else:
                candidate = f"Character{i+1}"
            characters.append(f"{roles[i]} - {candidate}")
        return characters

    def _make_paragraphs_from_prompt(self, prompt, characters, places):
        """
        A simple template-based expansion to create multiple paragraphs from the prompt.
        This is intentionally simple so it works offline and consistently.
        """
        paras = []
        protagonist_name = characters[0].split(" - ")[1] if characters else "The Hero"
        sidekick_name = characters[1].split(" - ")[1] if len(characters) > 1 else "A Friend"
        antagonist_name = characters[2].split(" - ")[1] if len(characters) > 2 else "The Foe"

        place_list = [p.strip() for p in places.split(',')] if places else []
        first_place = place_list[0] if place_list and place_list[0] else "a distant place"

        # Opening
        paras.append(f"In the opening scene, {protagonist_name} finds themself at {first_place}. {prompt.strip()} This moment sets the tone for everything that follows.")

        # Inciting incident
        paras.append(f"An unexpected event forces {protagonist_name} to make a choice. With {sidekick_name} by their side, they must navigate the challenges the world throws at them.")

        # Rising action (introduce antagonist or obstacle)
        paras.append(f"Rumors grow of {antagonist_name}'s plan. Tension builds as the protagonists learn that the stakes are higher than they first believed. Allies are tested and secrets are revealed.")

        # Midpoint & twist
        paras.append(f"At the story's midpoint, {protagonist_name} confronts a painful truth. This confrontation changes the course of their journey, pushing them to grow and adapt.")

        # Climax
        paras.append(f"The final confrontation arrives. In a tense showdown at {first_place}, {protagonist_name}, aided by {sidekick_name}, faces {antagonist_name}. Choices are made, sacrifices given, and the outcome decides the future of their world.")

        # Resolution
        paras.append(f"After the dust settles, the characters reckon with what they've lost and what they've learned. {protagonist_name}'s journey concludes with new understanding, while the world bears the marks of their passage.")

        return "\n\n".join(paras)

    # -------------------------
    # UI: generate story
    # -------------------------
    def generate_story(self):
        """Retrieves inputs and generates a story structure (mock 'AI')."""
        title_text = self.title_entry.get().strip()
        characters_text = self.char_input.get("1.0", tk.END).strip()
        places_text = self.place_input.get("1.0", tk.END).strip()
        script = self.script_input.get("1.0", tk.END).strip()

        if not script:
            messagebox.showwarning("Missing Input", "Please provide a prompt in the 'Story Script' tab to generate a story.")
            return

        # Title: use provided or auto-generate
        if not title_text:
            title_text = self._auto_title_from_prompt(script)

        # Characters: prefer user-provided list, else auto-generate from prompt
        characters = []
        if characters_text:
            # split by commas or new lines
            lines = [line.strip() for line in re.split(r'[\n,]+', characters_text) if line.strip()]
            # Normalize into "Role - Name" if possible; if user gives names only, just use them
            for i, line in enumerate(lines):
                if '-' in line:
                    characters.append(line)
                else:
                    role = ["Protagonist", "Sidekick", "Antagonist"]
                    role_name = role[i] if i < len(role) else f"Character{i+1}"
                    characters.append(f"{role_name} - {line}")
        else:
            characters = self._auto_characters_from_prompt(script, num=3)

        # Create the story body
        story_body = self._make_paragraphs_from_prompt(script, characters, places_text)

        # Compose final output: characters first as requested
        header = f"*** Story Title: {title_text} ***\n\n--- Characters Introduced ---\n"
        header += "\n".join(f"- {c}" for c in characters)
        if places_text:
            header += f"\n\n--- Key Settings ---\n{places_text}\n"
        header += f"\n--- Prompt / Seed ---\n\"{script}\"\n\n--- Story ---\n"

        final_story = header + story_body + "\n\n--- The End ---"
        self.story_output.delete("1.0", tk.END)
        self.story_output.insert(tk.END, final_story)
        # Move focus to output for user to read
        self.story_output.see("1.0")

def run_story_generator():
    try:
        root_story = tk.Toplevel()
    except tk.TclError:
        root_story = tk.Tk()
    StoryGeneratorApp(root_story)


class SnakeGame:
    CELL_SIZE = 20
    COLUMNS = 30
    ROWS = 21

    def __init__(self, window):
        self.window = window
        self.window.title("Snake")
        self.window.geometry("660x530")
        self.window.resizable(False, False)
        self.window.configure(bg="#101820")
        self.after_id = None

        header = tk.Frame(window, bg="#101820", padx=20, pady=14)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Snake",
            font=("Segoe UI", 20, "bold"),
            fg="#F2F5F7",
            bg="#101820",
        ).pack(side="left")
        self.score_label = tk.Label(
            header,
            text="Score: 0",
            font=("Segoe UI", 12, "bold"),
            fg="#8EE3A1",
            bg="#101820",
        )
        self.score_label.pack(side="right")

        self.canvas = tk.Canvas(
            window,
            width=self.COLUMNS * self.CELL_SIZE,
            height=self.ROWS * self.CELL_SIZE,
            bg="#17232D",
            highlightthickness=1,
            highlightbackground="#334654",
            takefocus=True,
        )
        self.canvas.pack(padx=20)
        self.status = tk.Label(
            window,
            text="Arrow keys or WASD to move   |   Space to pause   |   R to restart",
            font=("Segoe UI", 10),
            fg="#B8C6CE",
            bg="#101820",
            pady=12,
        )
        self.status.pack()
        self.canvas.bind("<KeyPress>", self._on_key)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.restart()
        self.canvas.focus_set()

    def restart(self):
        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
            except tk.TclError:
                pass
        self.after_id = None
        self.snake = [(8, 10), (7, 10), (6, 10)]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.score = 0
        self.speed = 115
        self.paused = False
        self.game_over = False
        self.food = self._spawn_food()
        self.score_label.config(text="Score: 0")
        self._draw()
        self.status.config(
            text="Arrow keys or WASD to move   |   Space to pause   |   R to restart",
            fg="#B8C6CE",
        )
        self.after_id = self.window.after(self.speed, self._tick)
        self.canvas.focus_set()

    def _spawn_food(self):
        occupied = set(self.snake)
        available = [
            (column, row)
            for column in range(self.COLUMNS)
            for row in range(self.ROWS)
            if (column, row) not in occupied
        ]
        return random.choice(available) if available else None

    def _on_key(self, event):
        key = event.keysym.lower()
        directions = {
            "up": (0, -1), "w": (0, -1),
            "down": (0, 1), "s": (0, 1),
            "left": (-1, 0), "a": (-1, 0),
            "right": (1, 0), "d": (1, 0),
        }
        if key == "r":
            self.restart()
            return "break"
        if key == "space" and not self.game_over:
            self.paused = not self.paused
            if self.paused:
                if self.after_id:
                    self.window.after_cancel(self.after_id)
                    self.after_id = None
                self.status.config(text="Paused  |  Press Space to continue")
            elif not self.after_id:
                self.after_id = self.window.after(self.speed, self._tick)
            return "break"

        requested = directions.get(key)
        if requested and requested != (-self.direction[0], -self.direction[1]):
            self.next_direction = requested
        return "break"

    def _tick(self):
        self.after_id = None
        if self.paused or self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        next_head = (
            head_x + self.direction[0],
            head_y + self.direction[1],
        )
        eating = next_head == self.food
        collision_body = self.snake if eating else self.snake[:-1]
        if (
            next_head[0] < 0
            or next_head[0] >= self.COLUMNS
            or next_head[1] < 0
            or next_head[1] >= self.ROWS
            or next_head in collision_body
        ):
            self.game_over = True
            self.status.config(text="Game over  |  Press R to play again", fg="#FF8A80")
            self._draw()
            return

        self.snake.insert(0, next_head)
        if eating:
            self.score += 10
            self.score_label.config(text=f"Score: {self.score}")
            self.speed = max(55, self.speed - 2)
            self.food = self._spawn_food()
            if self.food is None:
                self.game_over = True
                self.status.config(text="You win!  |  Press R to play again", fg="#8EE3A1")
        else:
            self.snake.pop()

        self._draw()
        if not self.game_over:
            self.after_id = self.window.after(self.speed, self._tick)

    def _draw(self):
        self.canvas.delete("all")
        if self.food:
            x, y = self.food
            inset = 3
            self.canvas.create_oval(
                x * self.CELL_SIZE + inset,
                y * self.CELL_SIZE + inset,
                (x + 1) * self.CELL_SIZE - inset,
                (y + 1) * self.CELL_SIZE - inset,
                fill="#FF6B5F",
                outline="",
            )
        for index, (x, y) in enumerate(self.snake):
            inset = 2
            color = "#A4F0A5" if index == 0 else "#59C977"
            self.canvas.create_rectangle(
                x * self.CELL_SIZE + inset,
                y * self.CELL_SIZE + inset,
                (x + 1) * self.CELL_SIZE - inset,
                (y + 1) * self.CELL_SIZE - inset,
                fill=color,
                outline="",
            )

    def close(self):
        if self.after_id:
            try:
                self.window.after_cancel(self.after_id)
            except tk.TclError:
                pass
        self.window.destroy()


def run_snake_game():
    snake_window = tk.Toplevel()
    SnakeGame(snake_window)


# =================================================================
# === MAIN HUB APPLICATION ===
# =================================================================

class ActivityHubApp:
    def __init__(self, master):
        self.master = master
        master.title("play these!!")
        master.geometry("500x350")
        master.config(bg='#e6f2ff') # Light Blue background

        self.font_style = ("Inter", 12)
        self.header_font = ("Inter", 16, "bold")

        # Data for choices
        self.options = {
            'A': {"label": "Screen Pet", "action": run_screen_pet},
            'B': {"label": "Quiz", "action": run_quiz},
            'C': {"label": "Make Your Own Story", "action": run_story_generator},
            'D': {"label": "Snake", "action": run_snake_game},
        }
        
        self.selected_choice = tk.StringVar(master, 'A') # Default selection
        self.current_frame = None

        self.create_initial_menu()

    def destroy_current_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def create_initial_menu(self):
        """Creates the main menu with radio buttons and the dynamic button area."""
        self.destroy_current_frame()
        self.current_frame = tk.Frame(self.master, bg='#e6f2ff')
        self.current_frame.pack(fill='both', expand=True)

        # Question Label
        question_label = tk.Label(
            self.current_frame, 
            text="What do you want to do first?", 
            font=self.header_font, 
            bg='#e6f2ff', 
            fg="#1f4e79"
        )
        question_label.pack(pady=20)

        # Radio Button Frame
        radio_frame = tk.Frame(self.current_frame, bg='#e6f2ff')
        radio_frame.pack(pady=10)

        for key, data in self.options.items():
            radio_button = tk.Radiobutton(
                radio_frame, 
                text=f"{key}. {data['label']}", 
                variable=self.selected_choice, 
                value=key,
                font=self.font_style,
                bg='#e6f2ff',
                selectcolor="#cce6ff",
                command=self.update_action_buttons,
                anchor="w",
                padx=10,
                pady=5
            )
            radio_button.pack(fill="x")

        # Option E: Side-by-Side View
        radio_d = tk.Radiobutton(
            radio_frame,
            text="E. All activities side-by-side (Hub View)",
            variable=self.selected_choice,
            value='E',
            font=self.font_style,
            bg='#e6f2ff',
            selectcolor="#cce6ff",
            command=self.update_action_buttons,
            anchor="w",
            padx=10,
            pady=5
        )
        radio_d.pack(fill="x")


        # Dynamic Button Frame
        self.button_area = tk.Frame(self.current_frame, bg='#e6f2ff')
        self.button_area.pack(pady=20)
        
        # Initial call to set up buttons based on default 'A'
        self.update_action_buttons()


    def update_action_buttons(self):
        """Destroys existing buttons and creates new ones based on selection."""
        # Clear existing buttons
        for widget in self.button_area.winfo_children():
            widget.destroy()

        selection = self.selected_choice.get()
        data = self.options.get(selection)

        if selection in self.options:
            # Normal 'A', 'B', or 'C' selection: Show a single 'OK' button
            
            # The "Great choice" message appears immediately after selection
            message_label = tk.Label(
                self.button_area, 
                text=f"You chose {selection}. Press OK to confirm!", 
                font=("Inter", 12, "italic"), 
                bg='#e6f2ff', 
                fg="#1f4e79"
            )
            message_label.pack(pady=5)

            # The 'OK' button which transitions to the confirmation screen
            ok_button = tk.Button(
                self.button_area, 
                text="OK", 
                command=lambda: self.transition_to_confirmation(data['label'], data["action"]),
                font=("Inter", 14, "bold"),
                bg='#4CAF50', # Green button
                fg='white', 
                activebackground='#388e3c',
                relief=tk.RAISED,
                padx=15,
                pady=8
            )
            ok_button.pack(pady=10)


        elif selection == 'E':
            # Option 'E' selection: Show all activities side-by-side
            
            message_label = tk.Label(
                self.button_area, 
                text="Activity Hub View (Side-by-Side)", 
                font=("Inter", 12, "italic"), 
                bg='#e6f2ff', 
                fg="#1f4e79"
            )
            message_label.pack(pady=5)
            
            # Frame for side-by-side buttons
            side_by_side_frame = tk.Frame(self.button_area, bg='#e6f2ff')
            side_by_side_frame.pack()
            
            for key in self.options:
                data = self.options[key]
                button = tk.Button(
                    side_by_side_frame,
                    text=data["label"], # Use the full label for side-by-side
                    command=lambda action=data["action"]: self.execute_activity(action),
                    font=("Inter", 10, "bold"),
                    bg='#007bff', 
                    fg='white', 
                    activebackground='#0056b3',
                    relief=tk.RAISED,
                    padx=10,
                    pady=5
                )
                button.pack(side=tk.LEFT, padx=5)

    def transition_to_confirmation(self, chosen_activity_label, activity_action):
        """
        Handles the 'OK' button click, clears the menu, and displays the final message and buttons.
        """
        # Clear all menu widgets
        self.destroy_current_frame()

        self.current_frame = tk.Frame(self.master, bg='#e6f2ff')
        self.current_frame.pack(fill='both', expand=True)
        
        # 1. Display the confirmation message, including "That is the best choice you'll ever wish for!"
        confirmation_text = f"Great choice! You selected: {chosen_activity_label.upper()}\n\nThat is the best choice you'll ever wish for!"
        
        confirmation_label = tk.Label(
            self.current_frame, 
            text=confirmation_text, 
            font=("Inter", 16, "italic"), 
            bg="#e6f2ff", 
            fg="#28a745", # Green text for confirmation
            wraplength=450, 
            justify=tk.CENTER
        )
        confirmation_label.pack(expand=True, padx=20, pady=20)

        # Button to launch the activity from the confirmation screen
        launch_button = tk.Button(
            self.current_frame,
            text=f"Launch {chosen_activity_label}",
            command=lambda: self.execute_activity(activity_action),
            font=("Inter", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            relief=tk.RAISED,
            padx=15,
            pady=8
        )
        launch_button.pack(pady=10)

        # 2. Create Return button
        return_button = tk.Button(
            self.current_frame, 
            text="Return (Keep Selection)", 
            command=self.create_initial_menu, # Re-run the initial menu function
            font=self.font_style,
            bg="#ffc107", # Yellow background for return
            fg="#333",
            relief=tk.RAISED,
            padx=15,
            pady=8
        )
        return_button.pack(pady=5)
        
        # 3. Create Reset button
        reset_button = tk.Button(
            self.current_frame, 
            text="Reset (Start Over)", 
            command=self.reset_menu,
            font=self.font_style,
            bg="#dc3545", # Red background for reset
            fg="white",
            relief=tk.RAISED,
            padx=15,
            pady=8
        )
        reset_button.pack(pady=5)

    def reset_menu(self):
        """Resets selection to 'A' and returns to the initial menu."""
        self.selected_choice.set('A') 
        self.create_initial_menu()
        
    def execute_activity(self, action_func):
        """Launch the activity window on Tk's owning thread."""
        action_func()


def run_hub_app():
    root = tk.Tk()
    app = ActivityHubApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_hub_app()

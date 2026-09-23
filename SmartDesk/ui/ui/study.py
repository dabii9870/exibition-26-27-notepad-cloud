"""
SmartDesk Study Center and Quizzes.
"""

import tkinter as tk
from tkinter import messagebox

from database import increment_stat, log_activity


class StudyScreen(tk.Frame):
    """Study center with simple quiz support."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#0B1020", **kwargs)
        self._build()

    def _build(self):
        tk.Label(
            self, text="📚 Study Center",
            font=("Segoe UI", 28, "bold"),
            fg="white", bg="#0B1020"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        tk.Label(
            self,
            text="Review topics, practise questions, and track quiz results.",
            font=("Segoe UI", 11), fg="#94A3B8", bg="#0B1020"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        card = tk.Frame(self, bg="#111827", padx=25, pady=25)
        card.pack(fill="x", padx=30)

        tk.Label(
            card, text="Quick Quiz",
            font=("Segoe UI", 18, "bold"),
            fg="#38BDF8", bg="#111827"
        ).pack(anchor="w")

        tk.Label(
            card, text="What does CPU stand for?",
            font=("Segoe UI", 13),
            fg="white", bg="#111827"
        ).pack(anchor="w", pady=20)

        self.answer = tk.StringVar()

        for option in [
            "Central Processing Unit",
            "Computer Personal Utility",
            "Central Program User",
            "Control Processing Utility"
        ]:
            tk.Radiobutton(
                card, text=option, variable=self.answer, value=option,
                bg="#111827", fg="#CBD5E1",
                selectcolor="#1E293B",
                activebackground="#111827",
                activeforeground="white"
            ).pack(anchor="w", pady=3)

        tk.Button(
            card, text="Submit Answer", command=self.submit,
            bg="#2563EB", fg="white", relief="flat",
            cursor="hand2", padx=18, pady=9
        ).pack(anchor="w", pady=20)

    def submit(self):
        if not self.answer.get():
            messagebox.showwarning("Quiz", "Choose an answer.")
            return

        correct = self.answer.get() == "Central Processing Unit"
        increment_stat("quiz_attempts")

        if correct:
            increment_stat("quiz_correct")
            messagebox.showinfo("Quiz", "Correct! 🎉")
        else:
            messagebox.showinfo(
                "Quiz",
                "Not quite. The correct answer is Central Processing Unit."
            )

        log_activity("quiz", "Completed CPU quiz")

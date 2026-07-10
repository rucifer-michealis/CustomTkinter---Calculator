import customtkinter as ctk
import tkinter as tk
from tkextrafont import Font
from sympy import sympify, zoo
import sys
import os

theme = {
    "bg": "#56beba",
    "text_clr": "#399a99",
    "butn_clr": "#c0e4ea",
    "butn_clr_hover": "#56beba",
    "disp_clr": "#c0e4ea",
    "border_clr": "#399a99",
}


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class gui:
    def __init__(self):
        self.calc = calc(self)
        self.app = ctk.CTk()
        self.app.title("calculator")
        self.app.geometry("400x580")
        self.app.resizable(False, False)
        self.app.configure(fg_color=theme["bg"])

        custom_font = Font(file=resource_path("orbitron-medium.otf"), family="orbitron")
        self.button_size = 85
        self.buttons = [
            "7",
            "8",
            "9",
            "÷",
            "4",
            "5",
            "6",
            "×",
            "1",
            "2",
            "3",
            "-",
            "c",
            "0",
            "+",
            "=",
        ]
        self.op = ["+", "-", "×", "÷"]
        self.padding = 5
        self.after_id = None
        self.long_press = False

        self.text_top = tk.StringVar(value=self.calc.val)
        self.text_bottom = tk.StringVar(value=self.calc.answer)

        self.display_frame = ctk.CTkFrame(self.app)
        self.display_frame.pack(padx=10, pady=10)

        self.create_display()
        self.create_buttons()

    def create_display(self):
        display_data = [
            (self.text_top, 0, 10, theme["text_clr"]),
            (self.text_bottom, 1, 0, theme["text_clr"]),
        ]

        self.displays = []
        for textvar, row, pady, text_color in display_data:
            display = ctk.CTkLabel(
                self.display_frame,
                textvariable=textvar,
                width=380,
                height=70,
                fg_color=theme["disp_clr"],
                anchor="e",
                font=("orbitron", 40),
                border_width=2,
                border_color=theme["border_clr"],
                corner_radius=10,
                text_color=text_color,
            )
            display.grid(row=row, pady=pady)
            self.displays.append(display)

        self.display_bottom, self.display_micro = self.displays

        self.button_frame = ctk.CTkFrame(self.app)
        self.button_frame.pack(padx=10, pady=10, expand=False)

        self.display_frame.configure(fg_color=theme["bg"])
        self.button_frame.configure(fg_color=theme["bg"])

    def create_buttons(self):
        for i, text in enumerate(self.buttons):
            row = i // 4
            col = i % 4

            if text in self.op:
                command = lambda t=text: self.calc.operator(t)
                font = ("orbitron", 50)
            elif text == "c":
                command = None
                font = ("orbitron", 50)
            elif text == "=":
                command = self.calc.calculate
                font = ("orbitron", 50)
            else:
                command = lambda t=text: self.calc.number_entered(t)
                font = ("orbitron", 40)

            btn = ctk.CTkButton(
                self.button_frame,
                text=text,
                fg_color=theme["butn_clr"],
                width=self.button_size,
                height=self.button_size,
                corner_radius=10,
                hover_color=theme["butn_clr_hover"],
                command=command,
                font=font,
                text_color=theme["text_clr"],
                border_color=theme["border_clr"],
                border_width=1,
            )

            if text == "c":
                btn.bind("<ButtonPress-1>", self.on_press)
                btn.bind("<ButtonRelease-1>", self.on_release)

            btn.grid(row=row, column=col, padx=self.padding, pady=self.padding)

    def on_press(self, event):
        self.long_press = False
        self.after_id = self.app.after(500, self.long_press_action)

    def long_press_action(self):
        self.after_id = None
        self.long_press = True
        self.calc.all_clear()

    def on_release(self, event):
        if self.after_id:
            self.app.after_cancel(self.after_id)
            self.after_id = None

        if not self.long_press:
            self.calc.backspace()

    def update_display(self, expr):
        expr = expr.replace("*", "×").replace("/", "÷")
        self.text_top.set(expr)
        self.text_bottom.set(self.calc.answer)

    def run(self):
        self.app.mainloop()


class calc:
    def __init__(self, gui):
        self.gui = gui
        self.token = []
        self.val = ""
        self.answer = 0

    def filter(self):
        result = []
        number = ""
        operators = {"+", "-", "*", "/"}

        for ch in self.val:
            if ch.isdigit():
                number += ch
            else:
                if number:
                    result.append(str(int(number)))
                    number = ""

                if result and result[-1] in operators and ch in operators:
                    continue

                result.append(ch)

        if number:
            result.append(str(int(number)))

        self.val = "".join(result)

    def operator(self, op):
        self.op_map = {"×": "*", "÷": "/"}

        op = self.op_map.get(op, op)
        self.combine_token(op)
        self.gui.update_display(self.val)

    def backspace(self):
        if self.val == "Syntax Error" or self.val == "Math Error":
            self.all_clear()

        if self.token:
            self.token.pop(-1)
            self.val = "".join(self.token)
        else:
            self.all_clear()
        self.gui.update_display(self.val)

    def all_clear(self):
        self.val = ""
        self.token = []
        self.answer = 0
        self.gui.update_display(self.val)

    def calculate(self):
        try:
            self.filter()
            self.answer = round(float(sympify(self.val)), 8)
            if self.answer is zoo:
                raise ZeroDivisionError

            if self.answer.is_integer():
                self.answer = int(self.answer)
        except ZeroDivisionError:
            self.val = "Math Error"
            self.answer = 0
        finally:
            self.gui.update_display(self.val)
            print(self.answer)

    def number_entered(self, number):
        self.combine_token(number)
        self.gui.update_display(self.val)

    def combine_token(self, value):
        if len(self.val) >= 11:
            pass
        else:
            self.token.append(value)
        self.val = "".join(self.token)


if __name__ == "__main__":
    gui().run()

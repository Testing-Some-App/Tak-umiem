#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplikacja do rzucania dwiema 4-ściennymi kośćmi
Simple Polish tkinter application for rolling two 4-sided dice
"""

import tkinter as tk
from tkinter import ttk
import random


class DiceRollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rzut dwoma 4-ściennymi kośćmi")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Centrowanie okna na ekranie
        self.center_window()
        
        # Inicjalizacja zmiennych
        self.dice1_value = 0
        self.dice2_value = 0
        self.dice1_modifier = 0
        self.dice2_modifier = 0
        self.dice1_range_modifier = 0
        self.dice2_range_modifier = 0
        self.dice1_people_original = 0
        self.dice2_people_original = 0
        self.dice1_people_result = 0
        self.dice2_people_result = 0
        
        # Utworzenie interfejsu
        self.create_widgets()
    
    def center_window(self):
        """Centruje okno na ekranie"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Tworzy wszystkie elementy interfejsu"""
        # Główny frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Tytuł aplikacji
        title_label = ttk.Label(
            main_frame, 
            text="Rzut dwoma 4-ściennymi kośćmi", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame dla wyników kości (horizontal layout)
        dice_frame = ttk.LabelFrame(main_frame, text="Wyniki", padding="15")
        dice_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, 20))
        
        # Pierwsza strona - liczba ludzi i nazwa
        people1_frame = ttk.Frame(dice_frame)
        people1_frame.grid(row=0, column=0, padx=20)
        ttk.Label(people1_frame, text="Liczba ludzi:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        self.dice1_people_var = tk.StringVar(value="0")
        self.dice1_people_entry = ttk.Entry(people1_frame, textvariable=self.dice1_people_var, width=5, font=("Arial", 9))
        self.dice1_people_entry.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(dice_frame, text="Strona 1", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=20)
        self.dice1_label = ttk.Label(
            dice_frame, 
            text="--", 
            font=("Arial", 24, "bold"),
            foreground="gray"
        )
        self.dice1_label.grid(row=2, column=0, padx=20, pady=10)
        
        # Wynik liczby ludzi strona 1
        self.dice1_people_result_label = ttk.Label(
            dice_frame, 
            text="", 
            font=("Arial", 10),
            foreground="blue"
        )
        self.dice1_people_result_label.grid(row=3, column=0, padx=20)
        
        # Druga strona - liczba ludzi i nazwa
        people2_frame = ttk.Frame(dice_frame)
        people2_frame.grid(row=0, column=2, padx=20)
        ttk.Label(people2_frame, text="Liczba ludzi:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        self.dice2_people_var = tk.StringVar(value="0")
        self.dice2_people_entry = ttk.Entry(people2_frame, textvariable=self.dice2_people_var, width=5, font=("Arial", 9))
        self.dice2_people_entry.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(dice_frame, text="Strona 2", font=("Arial", 12, "bold")).grid(row=1, column=2, padx=20)
        self.dice2_label = ttk.Label(
            dice_frame, 
            text="--", 
            font=("Arial", 24, "bold"),
            foreground="gray"
        )
        self.dice2_label.grid(row=2, column=2, padx=20, pady=10)
        
        # Wynik liczby ludzi strona 2
        self.dice2_people_result_label = ttk.Label(
            dice_frame, 
            text="", 
            font=("Arial", 10),
            foreground="blue"
        )
        self.dice2_people_result_label.grid(row=3, column=2, padx=20)
        
        # Separator pionowy
        separator = ttk.Separator(dice_frame, orient='vertical')
        separator.grid(row=0, column=1, rowspan=4, sticky=tk.N+tk.S, padx=10)
        
        # Przycisk do generowania wyniku
        self.roll_button = ttk.Button(
            main_frame,
            text="Wynik",
            command=self.roll_dice,
            style="Roll.TButton"
        )
        self.roll_button.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Stylizacja przycisku
        style = ttk.Style()
        style.configure("Roll.TButton", font=("Arial", 12, "bold"))
        
        # Frame dla modyfikatorów
        modifiers_frame = ttk.LabelFrame(main_frame, text="Modyfikatory", padding="10")
        modifiers_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(10, 0))
        
        # Lewa kolumna - Strona 1
        left_frame = ttk.LabelFrame(modifiers_frame, text="Strona 1", padding="10")
        left_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=(0, 10))
        
        # Modyfikator do wyniku strony 1
        ttk.Label(left_frame, text="Modyfikator:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dice1_modifier_var = tk.StringVar(value="0")
        self.dice1_modifier_entry = ttk.Entry(left_frame, textvariable=self.dice1_modifier_var, width=5, font=("Arial", 10))
        self.dice1_modifier_entry.grid(row=0, column=1, padx=(0, 5))
        
        # Modyfikator zakresu strony 1
        ttk.Label(left_frame, text="Oczka +:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice1_range_var = tk.StringVar(value="0")
        self.dice1_range_entry = ttk.Entry(left_frame, textvariable=self.dice1_range_var, width=5, font=("Arial", 10))
        self.dice1_range_entry.grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        
        # Otoczony strona 1
        self.dice1_surrounded_var = tk.BooleanVar()
        self.dice1_surrounded_check = ttk.Checkbutton(left_frame, text="Otoczony (-1)", variable=self.dice1_surrounded_var, onvalue=True, offvalue=False)
        self.dice1_surrounded_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Doświadczenie strona 1
        ttk.Label(left_frame, text="Doświadczenie:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.dice1_exp_vars = {}
        exp_values = [-2, -1, 0, 1, 2, 3, 4, 5, 6]
        for i, exp_val in enumerate(exp_values):
            self.dice1_exp_vars[exp_val] = tk.BooleanVar()
            exp_check = ttk.Checkbutton(left_frame, text=f"Doświadczenie {exp_val:+d}", variable=self.dice1_exp_vars[exp_val])
            exp_check.grid(row=4 + i//3, column=i%3, sticky=tk.W, pady=(2, 0), padx=(0, 5))
        
        # Prawa kolumna - Strona 2
        right_frame = ttk.LabelFrame(modifiers_frame, text="Strona 2", padding="10")
        right_frame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=(10, 0))
        
        # Modyfikator do wyniku strony 2
        ttk.Label(right_frame, text="Modyfikator:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dice2_modifier_var = tk.StringVar(value="0")
        self.dice2_modifier_entry = ttk.Entry(right_frame, textvariable=self.dice2_modifier_var, width=5, font=("Arial", 10))
        self.dice2_modifier_entry.grid(row=0, column=1, padx=(0, 5))
        
        # Modyfikator zakresu strony 2
        ttk.Label(right_frame, text="Oczka +:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice2_range_var = tk.StringVar(value="0")
        self.dice2_range_entry = ttk.Entry(right_frame, textvariable=self.dice2_range_var, width=5, font=("Arial", 10))
        self.dice2_range_entry.grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        
        # Otoczony strona 2
        self.dice2_surrounded_var = tk.BooleanVar()
        self.dice2_surrounded_check = ttk.Checkbutton(right_frame, text="Otoczony (-1)", variable=self.dice2_surrounded_var, onvalue=True, offvalue=False)
        self.dice2_surrounded_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Doświadczenie strona 2
        ttk.Label(right_frame, text="Doświadczenie:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.dice2_exp_vars = {}
        for i, exp_val in enumerate(exp_values):
            self.dice2_exp_vars[exp_val] = tk.BooleanVar()
            exp_check = ttk.Checkbutton(right_frame, text=f"Doświadczenie {exp_val:+d}", variable=self.dice2_exp_vars[exp_val])
            exp_check.grid(row=4 + i//3, column=i%3, sticky=tk.W, pady=(2, 0), padx=(0, 5))
        
        # Informacja o zakresie wartości
        info_label = ttk.Label(
            main_frame,
            text="Każda strona: 1 do (4 + oczka) + modyfikatory",
            font=("Arial", 10),
            foreground="gray"
        )
        info_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Konfiguracja rozciągania kolumn
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        dice_frame.columnconfigure(0, weight=1)
        dice_frame.columnconfigure(2, weight=1)
        modifiers_frame.columnconfigure(0, weight=1)
        modifiers_frame.columnconfigure(1, weight=1)
        
        # Focus na przycisk
        self.roll_button.focus()
        
        # Bind Enter key to roll dice
        self.root.bind('<Return>', lambda event: self.roll_dice())
    
    def roll_dice(self):
        """Rzuca dwiema 4-ściennymi kośćmi i aktualizuje wyniki"""
        # Pobieranie podstawowych modyfikatorów
        try:
            self.dice1_modifier = int(self.dice1_modifier_var.get())
        except ValueError:
            self.dice1_modifier = 0
            self.dice1_modifier_var.set("0")
            
        try:
            self.dice2_modifier = int(self.dice2_modifier_var.get())
        except ValueError:
            self.dice2_modifier = 0
            self.dice2_modifier_var.set("0")
        
        # Pobieranie modyfikatorów zakresu
        try:
            self.dice1_range_modifier = int(self.dice1_range_var.get())
        except ValueError:
            self.dice1_range_modifier = 0
            self.dice1_range_var.set("0")
            
        try:
            self.dice2_range_modifier = int(self.dice2_range_var.get())
        except ValueError:
            self.dice2_range_modifier = 0
            self.dice2_range_var.set("0")
        
        # Pobieranie liczby ludzi
        try:
            self.dice1_people_original = int(self.dice1_people_var.get())
        except ValueError:
            self.dice1_people_original = 0
            self.dice1_people_var.set("0")
            
        try:
            self.dice2_people_original = int(self.dice2_people_var.get())
        except ValueError:
            self.dice2_people_original = 0
            self.dice2_people_var.set("0")
        
        # Losowanie wartości dla obu kości z uwzględnieniem modyfikatora zakresu
        dice1_max = 4 + self.dice1_range_modifier
        dice2_max = 4 + self.dice2_range_modifier
        
        self.dice1_value = random.randint(1, max(1, dice1_max))
        self.dice2_value = random.randint(1, max(1, dice2_max))
        
        # Obliczanie wszystkich modyfikatorów
        dice1_total_modifier = self.dice1_modifier
        dice2_total_modifier = self.dice2_modifier
        
        # Dodawanie modyfikatora "Otoczony"
        if self.dice1_surrounded_var.get():
            dice1_total_modifier -= 1
        if self.dice2_surrounded_var.get():
            dice2_total_modifier -= 1
        
        # Dodawanie modyfikatorów doświadczenia
        for exp_val, var in self.dice1_exp_vars.items():
            if var.get():
                dice1_total_modifier += exp_val
        
        for exp_val, var in self.dice2_exp_vars.items():
            if var.get():
                dice2_total_modifier += exp_val
        
        # Obliczanie wartości końcowych
        dice1_final = self.dice1_value + dice1_total_modifier
        dice2_final = self.dice2_value + dice2_total_modifier
        
        # Aktualizacja etykiet z wynikami i kolorami (kolor bazuje na wartości końcowej)
        self.dice1_label.config(text=str(dice1_final), foreground=self.get_color_for_value(dice1_final))
        self.dice2_label.config(text=str(dice2_final), foreground=self.get_color_for_value(dice2_final))
        
        # Aktualizacja wyników liczby ludzi (na razie ta sama co oryginalna)
        self.dice1_people_result = self.dice1_people_original
        self.dice2_people_result = self.dice2_people_original
        
        self.dice1_people_result_label.config(text=f"Wynik: {self.dice1_people_result} ludzi")
        self.dice2_people_result_label.config(text=f"Wynik: {self.dice2_people_result} ludzi")
        
        # Efekt wizualny - krótka animacja przycisku
        self.roll_button.config(state="disabled")
        self.root.after(200, lambda: self.roll_button.config(state="normal"))
        
        # Komunikat o wyniku w zależności od rzutu
        self.display_result_message()
    
    def get_color_for_value(self, value):
        """Zwraca kolor dla wartości kości (spektrum czerwony-zielony-niebieski)"""
        # Kolor bazuje na wartości końcowej, nie tylko na rzucie kości
        if value <= 1:
            return "#FF0000"  # Czerwony - najgorszy
        elif value == 2:
            return "#FF8000"  # Pomarańczowy
        elif value == 3:
            return "#FFFF00"  # Żółty
        elif value == 4:
            return "#80FF00"  # Zielono-żółty
        elif value == 5:
            return "#00FF00"  # Zielony - środek
        elif value == 6:
            return "#00FF80"  # Zielono-niebieski
        elif value == 7:
            return "#00FFFF"  # Cyan
        elif value == 8:
            return "#0080FF"  # Jasnoniebieski
        elif value >= 9:
            return "#0000FF"  # Niebieski - najlepszy
        else:
            return "black"
    
    def display_result_message(self):
        """Wyświetla komunikat w zależności od wyniku rzutu"""
        if self.dice1_value == self.dice2_value:
            message = f"Dublet! Obie strony pokazują {self.dice1_value}"
        elif self.dice1_value == 4 and self.dice2_value == 4:
            message = "Perfekcyjny rzut podstawowy! Obie strony 4!"
        elif self.dice1_value == 1 and self.dice2_value == 1:
            message = "Najgorszy rzut podstawowy! Obie strony 1!"
        else:
            message = f"Podstawowe strony: {self.dice1_value} i {self.dice2_value}"
        
        # Tymczasowe wyświetlenie wiadomości w title bar
        original_title = self.root.title()
        self.root.title(f"Rzut dwoma 4-ściennymi kośćmi - {message}")
        self.root.after(2000, lambda: self.root.title(original_title))


def main():
    """Główna funkcja aplikacji"""
    # Utworzenie głównego okna
    root = tk.Tk()
    
    # Utworzenie aplikacji
    app = DiceRollerApp(root)
    
    # Uruchomienie pętli głównej
    root.mainloop()


if __name__ == "__main__":
    main()

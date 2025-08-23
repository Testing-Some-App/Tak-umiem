#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplikacja do rzucania dwiema 4-ściennymi kośćmi
Simple Polish tkinter application for rolling two 4-sided dice
"""

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import random


class DiceRollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rzut dwoma 4-ściennymi kośćmi")
        self.root.geometry("1200x700")
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
        self.dice1_gets_exp = False
        self.dice2_gets_exp = False
        self.dice1_losses = 0
        self.dice2_losses = 0
        self.history = []  # Lista przechowująca historię rzutów
        
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
        # Tworzenie canvas i scrollbar dla przewijania
        canvas = tk.Canvas(self.root)
        scrollbar_v = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(self.root, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Grid layout dla canvas i scrollbars
        canvas.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        scrollbar_v.grid(row=0, column=1, sticky=tk.N+tk.S)
        scrollbar_h.grid(row=1, column=0, sticky=tk.W+tk.E)
        
        # Konfiguracja rozciągania root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Główny frame
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Frame po lewej stronie (główna gra)
        game_frame = ttk.Frame(main_frame)
        game_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=(0, 10))
        
        # Frame po prawej stronie (historia)
        history_frame = ttk.LabelFrame(main_frame, text="Historia ostatnich 12 rzutów", padding="10")
        history_frame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Scrollable text widget dla historii
        self.history_text = scrolledtext.ScrolledText(
            history_frame, 
            width=40, 
            height=35, 
            font=("Arial", 9),
            state=tk.DISABLED
        )
        self.history_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Bind scroll wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Tytuł aplikacji
        title_label = ttk.Label(
            game_frame, 
            text="Rzut dwoma 4-ściennymi kośćmi", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame dla wyników kości (horizontal layout)
        dice_frame = ttk.LabelFrame(game_frame, text="Wyniki", padding="15")
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
        
        # Wynik liczby ludzi i ikona doświadczenia strona 1
        result1_frame = ttk.Frame(dice_frame)
        result1_frame.grid(row=3, column=0, padx=20)
        self.dice1_people_result_label = ttk.Label(
            result1_frame, 
            text="", 
            font=("Arial", 10),
            foreground="blue"
        )
        self.dice1_people_result_label.grid(row=0, column=0)
        self.dice1_exp_icon = ttk.Label(
            result1_frame, 
            text="", 
            font=("Arial", 12, "bold"),
            foreground="gold"
        )
        self.dice1_exp_icon.grid(row=0, column=1, padx=(5, 0))
        
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
        
        # Wynik liczby ludzi i ikona doświadczenia strona 2
        result2_frame = ttk.Frame(dice_frame)
        result2_frame.grid(row=3, column=2, padx=20)
        self.dice2_people_result_label = ttk.Label(
            result2_frame, 
            text="", 
            font=("Arial", 10),
            foreground="blue"
        )
        self.dice2_people_result_label.grid(row=0, column=0)
        self.dice2_exp_icon = ttk.Label(
            result2_frame, 
            text="", 
            font=("Arial", 12, "bold"),
            foreground="gold"
        )
        self.dice2_exp_icon.grid(row=0, column=1, padx=(5, 0))
        
        # Separator pionowy
        separator = ttk.Separator(dice_frame, orient='vertical')
        separator.grid(row=0, column=1, rowspan=4, sticky=tk.N+tk.S, padx=10)
        
        # Przycisk do generowania wyniku
        self.roll_button = ttk.Button(
            game_frame,
            text="Wynik",
            command=self.roll_dice,
            style="Roll.TButton"
        )
        self.roll_button.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Stylizacja przycisku
        style = ttk.Style()
        style.configure("Roll.TButton", font=("Arial", 12, "bold"))
        
        # Frame dla modyfikatorów
        modifiers_frame = ttk.LabelFrame(game_frame, text="Modyfikatory", padding="10")
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
        
        # Doświadczenie strona 1 (tylko jeden może być wybrany)
        ttk.Label(left_frame, text="Doświadczenie:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.dice1_exp_var = tk.IntVar(value=0)
        exp_values = [-2, -1, 0, 1, 2, 3, 4, 5, 6]
        for i, exp_val in enumerate(exp_values):
            exp_radio = ttk.Radiobutton(left_frame, text=f"Doświadczenie {exp_val:+d}", variable=self.dice1_exp_var, value=exp_val)
            exp_radio.grid(row=4 + i//3, column=i%3, sticky=tk.W, pady=(2, 0), padx=(0, 5))
        
        # Dodatkowe modyfikatory strona 1
        ttk.Label(left_frame, text="Dodatkowe:", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.dice1_defense_var = tk.BooleanVar()
        self.dice1_defense_check = ttk.Checkbutton(left_frame, text="Obrona w zabudowaniach (+1)", variable=self.dice1_defense_var)
        self.dice1_defense_check.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        self.dice1_supply_var = tk.BooleanVar()
        self.dice1_supply_check = ttk.Checkbutton(left_frame, text="Brak zaopatrzenia (-1)", variable=self.dice1_supply_var)
        self.dice1_supply_check.grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        ttk.Label(left_frame, text="Fortyfikacje:", font=("Arial", 10)).grid(row=10, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice1_fort_var = tk.IntVar(value=0)
        fort_combo1 = ttk.Combobox(left_frame, textvariable=self.dice1_fort_var, values=["0", "1", "2", "3"], width=3, state="readonly")
        fort_combo1.grid(row=10, column=1, padx=(0, 5), pady=(5, 0))
        
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
        
        # Doświadczenie strona 2 (tylko jeden może być wybrany)
        ttk.Label(right_frame, text="Doświadczenie:", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.dice2_exp_var = tk.IntVar(value=0)
        for i, exp_val in enumerate(exp_values):
            exp_radio = ttk.Radiobutton(right_frame, text=f"Doświadczenie {exp_val:+d}", variable=self.dice2_exp_var, value=exp_val)
            exp_radio.grid(row=4 + i//3, column=i%3, sticky=tk.W, pady=(2, 0), padx=(0, 5))
        
        # Dodatkowe modyfikatory strona 2
        ttk.Label(right_frame, text="Dodatkowe:", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.dice2_defense_var = tk.BooleanVar()
        self.dice2_defense_check = ttk.Checkbutton(right_frame, text="Obrona w zabudowaniach (+1)", variable=self.dice2_defense_var)
        self.dice2_defense_check.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        self.dice2_supply_var = tk.BooleanVar()
        self.dice2_supply_check = ttk.Checkbutton(right_frame, text="Brak zaopatrzenia (-1)", variable=self.dice2_supply_var)
        self.dice2_supply_check.grid(row=9, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        ttk.Label(right_frame, text="Fortyfikacje:", font=("Arial", 10)).grid(row=10, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice2_fort_var = tk.IntVar(value=0)
        fort_combo2 = ttk.Combobox(right_frame, textvariable=self.dice2_fort_var, values=["0", "1", "2", "3"], width=3, state="readonly")
        fort_combo2.grid(row=10, column=1, padx=(0, 5), pady=(5, 0))
        
        # Informacja o zakresie wartości
        info_label = ttk.Label(
            game_frame,
            text="Każda strona: 1 do (4 + oczka) + modyfikatory",
            font=("Arial", 10),
            foreground="gray"
        )
        info_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Konfiguracja rozciągania kolumn
        main_frame.columnconfigure(0, weight=2)  # Gra
        main_frame.columnconfigure(1, weight=1)  # Historia
        game_frame.columnconfigure(0, weight=1)
        game_frame.columnconfigure(1, weight=1)
        game_frame.columnconfigure(2, weight=1)
        dice_frame.columnconfigure(0, weight=1)
        dice_frame.columnconfigure(2, weight=1)
        modifiers_frame.columnconfigure(0, weight=1)
        modifiers_frame.columnconfigure(1, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
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
        
        # Dodawanie modyfikatorów doświadczenia (tylko jeden może być wybrany)
        dice1_total_modifier += self.dice1_exp_var.get()
        dice2_total_modifier += self.dice2_exp_var.get()
        
        # Dodawanie innych modyfikatorów
        if self.dice1_defense_var.get():
            dice1_total_modifier += 1
        if self.dice2_defense_var.get():
            dice2_total_modifier += 1
            
        if self.dice1_supply_var.get():
            dice1_total_modifier -= 1
        if self.dice2_supply_var.get():
            dice2_total_modifier -= 1
            
        # Fortyfikacje
        try:
            dice1_total_modifier += int(self.dice1_fort_var.get())
        except ValueError:
            pass
        try:
            dice2_total_modifier += int(self.dice2_fort_var.get())
        except ValueError:
            pass
        
        # Obliczanie wartości końcowych
        dice1_final = self.dice1_value + dice1_total_modifier
        dice2_final = self.dice2_value + dice2_total_modifier
        
        # Aktualizacja etykiet z wynikami i kolorami (kolor bazuje na wartości końcowej)
        self.dice1_label.config(text=str(dice1_final), foreground=self.get_color_for_value(dice1_final))
        self.dice2_label.config(text=str(dice2_final), foreground=self.get_color_for_value(dice2_final))
        
        # Obliczanie wyników bitwy
        self.calculate_battle_results(dice1_final, dice2_final)
        
        # Aktualizacja wyników liczby ludzi ze stratami
        dice1_text = f"Wynik: {self.dice1_people_result} ludzi\nStraty: {getattr(self, 'dice1_losses', 0)}"
        dice2_text = f"Wynik: {self.dice2_people_result} ludzi\nStraty: {getattr(self, 'dice2_losses', 0)}"
        
        self.dice1_people_result_label.config(text=dice1_text)
        self.dice2_people_result_label.config(text=dice2_text)
        
        # Aktualizacja ikon doświadczenia
        self.dice1_exp_icon.config(text="⭐ Doświadczenie +" if self.dice1_gets_exp else "")
        self.dice2_exp_icon.config(text="⭐ Doświadczenie +" if self.dice2_gets_exp else "")
        
        # Dodanie do historii
        self.add_to_history(dice1_final, dice2_final)
        
        # Efekt wizualny - krótka animacja przycisku
        self.roll_button.config(state="disabled")
        self.root.after(200, lambda: self.roll_button.config(state="normal"))
        
        # Komunikat o wyniku w zależności od rzutu
        self.display_result_message()
    
    def calculate_battle_results(self, dice1_final, dice2_final):
        """Oblicza wyniki bitwy na podstawie rzutów kośćmi"""
        # Resetowanie flag doświadczenia
        self.dice1_gets_exp = False
        self.dice2_gets_exp = False
        
        # Obliczanie różnicy
        difference = abs(dice1_final - dice2_final)
        
        # Inicjalne wartości - brak strat
        self.dice1_people_result = self.dice1_people_original
        self.dice2_people_result = self.dice2_people_original
        
        # Jeśli brak ludzi, nie ma co obliczać
        if self.dice1_people_original == 0 and self.dice2_people_original == 0:
            return
        
        # Przy różnicy +2, wyższa strona dostaje ikonkę "Doświadczenie +"
        if difference >= 2:
            if dice1_final > dice2_final:
                self.dice1_gets_exp = True
            elif dice2_final > dice1_final:
                self.dice2_gets_exp = True
        
        # Nowa logika strat - bazuje na wyniku kostki z bazą 150 ludzi
        def get_base_loss_percentage_for_result(result):
            """Zwraca procent strat dla danego wyniku kostki (od 1 do 12+)"""
            if result == 1:
                return random.uniform(0.0, 0.02)  # 0-2%
            elif result == 2:
                return random.uniform(0.03, 0.06)  # 3-6%
            elif result == 3:
                return random.uniform(0.07, 0.10)  # 7-10%
            elif result == 4:
                return random.uniform(0.11, 0.14)  # 11-14%
            elif result == 5:
                return random.uniform(0.15, 0.18)  # 15-18%
            elif result == 6:
                return random.uniform(0.19, 0.22)  # 19-22%
            elif result == 7:
                return random.uniform(0.23, 0.28)  # 23-28%
            elif result == 8:
                return random.uniform(0.29, 0.35)  # 29-35%
            elif result == 9:
                return random.uniform(0.36, 0.45)  # 36-45%
            elif result == 10:
                return random.uniform(0.46, 0.55)  # 46-55%
            elif result == 11:
                return random.uniform(0.56, 0.70)  # 56-70%
            elif result >= 12:
                return random.uniform(0.75, 0.85)  # 75-85%
            else:
                return 0.05
        
        def calculate_losses_for_side(enemy_result, own_people, own_fortifications, own_no_supply, own_defense_buildings, enemy_fortifications):
            """Oblicza straty dla jednej strony"""
            # Bazowy procent strat na podstawie wyniku przeciwnika
            base_loss_percentage = get_base_loss_percentage_for_result(enemy_result)
            
            # Modyfikatory własne (obrona)
            defense_modifier = 1.0  # Bazowy mnożnik
            
            # Fortyfikacje własne zmniejszają straty własne
            if own_fortifications == 1:
                defense_modifier -= 0.05  # -5%
            elif own_fortifications == 2:
                defense_modifier -= 0.10  # -10%
            elif own_fortifications == 3:
                defense_modifier -= 0.15  # -15%
            
            # Brak zaopatrzenia zwiększa straty własne
            if own_no_supply:
                defense_modifier += 0.05  # +5%
            
            # Obrona w zabudowaniach zmniejsza straty własne
            if own_defense_buildings:
                defense_modifier -= 0.05  # -5%
            
            # Modyfikatory ataku przeciwnika (fortyfikacje przeciwnika zwiększają nasze straty)
            attack_modifier = 1.0  # Bazowy mnożnik
            
            # Fortyfikacje przeciwnika zwiększają nasze straty
            if enemy_fortifications == 1:
                attack_modifier += random.uniform(0.10, 0.15)  # +10-15%
            elif enemy_fortifications == 2:
                attack_modifier += random.uniform(0.16, 0.25)  # +16-25%
            elif enemy_fortifications == 3:
                attack_modifier += random.uniform(0.30, 0.40)  # +30-40%
            
            # Końcowy procent strat (nie może być ujemny)
            final_loss_percentage = max(0.0, base_loss_percentage * defense_modifier * attack_modifier)
            
            # WAŻNE: Obliczenia na bazie 150 ludzi, nie rzeczywistej liczby
            absolute_losses = int(150 * final_loss_percentage)
            
            # Aplikowanie strat - nie może być mniej niż 0
            if own_people > 0:
                actual_losses = min(absolute_losses, own_people)  # Nie więcej niż mamy
                remaining_people = max(0, own_people - actual_losses)
                return remaining_people, actual_losses
            else:
                return 0, 0
        
        # Pobieranie wartości modyfikatorów dla obu stron
        dice1_fort = int(self.dice1_fort_var.get()) if self.dice1_fort_var.get() else 0
        dice2_fort = int(self.dice2_fort_var.get()) if self.dice2_fort_var.get() else 0
        
        dice1_no_supply = self.dice1_supply_var.get()
        dice2_no_supply = self.dice2_supply_var.get()
        
        dice1_defense = self.dice1_defense_var.get()
        dice2_defense = self.dice2_defense_var.get()
        
        # Obliczanie strat dla obu stron
        self.dice1_people_result, self.dice1_losses = calculate_losses_for_side(
            dice2_final, self.dice1_people_original, dice1_fort, dice1_no_supply, dice1_defense, dice2_fort
        )
        
        self.dice2_people_result, self.dice2_losses = calculate_losses_for_side(
            dice1_final, self.dice2_people_original, dice2_fort, dice2_no_supply, dice2_defense, dice1_fort
        )
    
    def add_to_history(self, dice1_final, dice2_final):
        """Dodaje wynik do historii"""
        # Format: "Strona 1: X | Strona 2: Y | Ludzie: A->B | C->D"
        history_entry = {
            'dice1': dice1_final,
            'dice2': dice2_final,
            'people1_before': self.dice1_people_original,
            'people1_after': self.dice1_people_result,
            'people2_before': self.dice2_people_original,
            'people2_after': self.dice2_people_result,
            'exp1': self.dice1_gets_exp,
            'exp2': self.dice2_gets_exp
        }
        
        # Dodanie do listy historii
        self.history.append(history_entry)
        
        # Zachowanie tylko ostatnich 12 wyników
        if len(self.history) > 12:
            self.history.pop(0)
        
        # Aktualizacja wyświetlania historii
        self.update_history_display()
    
    def update_history_display(self):
        """Aktualizuje wyświetlanie historii"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        for i, entry in enumerate(reversed(self.history), 1):
            exp1_icon = " ⭐" if entry['exp1'] else ""
            exp2_icon = " ⭐" if entry['exp2'] else ""
            
            history_line = f"#{i}: Strona 1: {entry['dice1']}{exp1_icon} | Strona 2: {entry['dice2']}{exp2_icon}\n"
            history_line += f"    Ludzie: {entry['people1_before']}→{entry['people1_after']} | {entry['people2_before']}→{entry['people2_after']}\n\n"
            
            self.history_text.insert(tk.END, history_line)
        
        self.history_text.config(state=tk.DISABLED)
        self.history_text.see(tk.END)  # Przewiń na dół
    
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

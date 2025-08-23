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
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Centrowanie okna na ekranie
        self.center_window()
        
        # Inicjalizacja zmiennych
        self.dice1_value = 0
        self.dice2_value = 0
        self.dice1_modifier = 0
        self.dice2_modifier = 0
        
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
        
        # Pierwsza strona
        ttk.Label(dice_frame, text="Strona 1", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20)
        self.dice1_label = ttk.Label(
            dice_frame, 
            text="--", 
            font=("Arial", 24, "bold"),
            foreground="gray"
        )
        self.dice1_label.grid(row=1, column=0, padx=20, pady=10)
        
        # Druga strona
        ttk.Label(dice_frame, text="Strona 2", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=20)
        self.dice2_label = ttk.Label(
            dice_frame, 
            text="--", 
            font=("Arial", 24, "bold"),
            foreground="gray"
        )
        self.dice2_label.grid(row=1, column=2, padx=20, pady=10)
        
        # Separator pionowy
        separator = ttk.Separator(dice_frame, orient='vertical')
        separator.grid(row=0, column=1, rowspan=2, sticky=tk.N+tk.S, padx=10)
        
        # Przycisk do rzucania kośćmi
        self.roll_button = ttk.Button(
            main_frame,
            text="Rzuć kośćmi!",
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
        
        # Modyfikator strony 1
        ttk.Label(modifiers_frame, text="Modyfikator strony 1:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.dice1_modifier_var = tk.StringVar(value="0")
        self.dice1_modifier_entry = ttk.Entry(
            modifiers_frame, 
            textvariable=self.dice1_modifier_var,
            width=5,
            font=("Arial", 10)
        )
        self.dice1_modifier_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Modyfikator strony 2
        ttk.Label(modifiers_frame, text="Modyfikator strony 2:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.dice2_modifier_var = tk.StringVar(value="0")
        self.dice2_modifier_entry = ttk.Entry(
            modifiers_frame, 
            textvariable=self.dice2_modifier_var,
            width=5,
            font=("Arial", 10)
        )
        self.dice2_modifier_entry.grid(row=0, column=3)
        
        # Informacja o zakresie wartości
        info_label = ttk.Label(
            main_frame,
            text="Każda strona ma wartości od 1 do 4 + modyfikator",
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
        modifiers_frame.columnconfigure(1, weight=1)
        modifiers_frame.columnconfigure(3, weight=1)
        
        # Focus na przycisk
        self.roll_button.focus()
        
        # Bind Enter key to roll dice
        self.root.bind('<Return>', lambda event: self.roll_dice())
    
    def roll_dice(self):
        """Rzuca dwiema 4-ściennymi kośćmi i aktualizuje wyniki"""
        # Pobieranie modyfikatorów
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
        
        # Losowanie wartości dla obu kości (1-4)
        self.dice1_value = random.randint(1, 4)
        self.dice2_value = random.randint(1, 4)
        
        # Obliczanie wartości końcowych z modyfikatorami
        dice1_final = self.dice1_value + self.dice1_modifier
        dice2_final = self.dice2_value + self.dice2_modifier
        
        # Aktualizacja etykiet z wynikami i kolorami
        self.dice1_label.config(text=str(dice1_final), foreground=self.get_color_for_value(self.dice1_value))
        self.dice2_label.config(text=str(dice2_final), foreground=self.get_color_for_value(self.dice2_value))
        
        # Efekt wizualny - krótka animacja przycisku
        self.roll_button.config(state="disabled")
        self.root.after(200, lambda: self.roll_button.config(state="normal"))
        
        # Komunikat o wyniku w zależności od rzutu
        self.display_result_message()
    
    def get_color_for_value(self, value):
        """Zwraca kolor dla wartości kości (spektrum czerwony-zielony-niebieski)"""
        if value == 1:
            return "red"
        elif value == 2:
            return "orange"
        elif value == 3:
            return "green"
        elif value == 4:
            return "blue"
        else:
            return "black"
    
    def display_result_message(self):
        """Wyświetla komunikat w zależności od wyniku rzutu"""
        if self.dice1_value == self.dice2_value:
            message = f"Dublet! Obie strony pokazują {self.dice1_value}"
        elif self.dice1_value == 4 and self.dice2_value == 4:
            message = "Perfekcyjny rzut! Obie strony 4!"
        elif self.dice1_value == 1 and self.dice2_value == 1:
            message = "Najgorszy rzut! Obie strony 1!"
        else:
            message = f"Strony: {self.dice1_value} i {self.dice2_value}"
        
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

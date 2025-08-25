#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplikacja do rzucania dwiema 4-ściennymi kośćmi
Simple Polish tkinter application for rolling two 4-sided dice
"""

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog, messagebox
import random
import json
import string
from datetime import datetime


class DiceRollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rzut dwoma 4-ściennymi kośćmi")
        self.root.geometry("2000x700")
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
        
        # System bitew
        self.battles = {}  # Słownik bitew: {nazwa: {"history": [], "created": datetime}}
        self.current_battle = "Niezapisana"  # Obecnie wybrana bitwa
        self.battle_names = ["Niezapisana"]  # Lista nazw bitew dla combobox
        
        # System jednostek
        self.units = {"własne": {}, "wroga": {}}  # Słownik jednostek: {"własne": {id: dane}, "wroga": {id: dane}}
        self.current_unit = None  # Obecnie wybrana jednostka (ID)
        self.current_unit_side = "własne"  # Strona obecnie wybranej jednostki
        
        # Mapy ID->display name dla comboboxów bitwy
        self.unit_side1_id_to_display = {}
        self.unit_side2_id_to_display = {}
        
        # System batalionów
        self.battalions = {}  # Słownik batalionów: {id: {"nazwa": string, "id": string}}
        self.current_battalion = None  # Obecnie wybrany batalion (ID)
        
        
        # Jednostki biorące udział w bitwie
        self.participating_units = {"strona1": [], "strona2": []}  # Lista jednostek na każdej stronie
        self.side1_locked = False  # Czy strona 1 ma zablokowane automatyczne uzupełnianie
        self.side2_locked = False  # Czy strona 2 ma zablokowane automatyczne uzupełnianie
        
        # Jednostki wybrane do bitwy
        self.selected_unit_side1 = None  # ID wybranej jednostki dla strony 1
        self.selected_unit_side2 = None  # ID wybranej jednostki dla strony 2
        self.unit_side1_type = "brak"  # "własne", "wroga", "brak"
        self.unit_side2_type = "brak"  # "własne", "wroga", "brak"
        
        # Zmienne dla systemu atak/obrona
        self.side1_attack = True  # Strona 1 domyślnie atak
        self.side2_defense = True  # Strona 2 domyślnie obrona
        self.side1_in_motion = False
        self.side2_in_motion = False
        
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
    
    def generate_random_id(self):
        """Generuje losowy 5-znakowy identyfikator"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    
    def get_unit_display_name(self, unit_id, side):
        """Zwraca sformatowaną nazwę jednostki do wyświetlania"""
        if unit_id not in self.units[side]:
            return "Nieznana jednostka"
        
        unit_data = self.units[side][unit_id]
        number = unit_data.get('numer', 1)
        unit_type = unit_data.get('typ', 'kompania')
        battalion_id = unit_data.get('batalion', None)
        
        # Formatowanie typu jednostki
        type_suffix = "Komp." if unit_type == "kompania" else "Grupa"
        
        # Formatowanie batalionu
        battalion_part = ""
        if battalion_id and battalion_id in self.battalions:
            battalion_name = self.battalions[battalion_id]['nazwa']
            battalion_part = f" Bat. {battalion_name}"
        
        return f"{number} {type_suffix}{battalion_part}"
    
    def get_battalion_display_name(self, battalion_id):
        """Zwraca nazwę batalionu do wyświetlania"""
        if battalion_id not in self.battalions:
            return "Nieznany batalion"
        return self.battalions[battalion_id]['nazwa']
    
    def create_new_battalion(self):
        """Tworzy nowy batalion"""
        battalion_name = self.new_battalion_var.get().strip()
        if not battalion_name:
            messagebox.showwarning("Błąd", "Wprowadź nazwę batalionu!")
            return
        
        # Sprawdź czy batalion o tej nazwie już istnieje
        for battalion_id, data in self.battalions.items():
            if data['nazwa'] == battalion_name:
                messagebox.showwarning("Błąd", "Batalion o tej nazwie już istnieje!")
                return
        
        # Stwórz nowy batalion
        battalion_id = self.generate_random_id()
        self.battalions[battalion_id] = {
            'nazwa': battalion_name,
            'id': battalion_id
        }
        
        # Aktualizacja interfejsu
        self.update_battalion_combos()
        self.new_battalion_var.set("")
        
        messagebox.showinfo("Sukces", f"Batalion '{battalion_name}' został utworzony!")
    
    def on_battalion_selected(self, event=None):
        """Obsługuje wybór batalionu"""
        battalion_name = self.battalion_var.get()
        if not battalion_name:
            self.battalion_info_label.config(text="")
            return
        
        # Znajdź batalion po nazwie
        battalion_id = None
        for bid, data in self.battalions.items():
            if data['nazwa'] == battalion_name:
                battalion_id = bid
                break
        
        if not battalion_id:
            self.battalion_info_label.config(text="")
            return
        
        # Policz jednostki i ludzi w batalionie
        unit_count = 0
        total_people = 0
        
        for side in ['własne', 'wroga']:
            for unit_id, unit_data in self.units[side].items():
                if unit_data.get('batalion') == battalion_id:
                    unit_count += 1
                    total_people += unit_data.get('liczba_ludzi', 0)
        
        self.battalion_info_label.config(text=f"Jednostek: {unit_count}, Ludzi: {total_people}")
    
    def update_battalion_combos(self):
        """Aktualizuje comboboxi batalionów"""
        battalion_names = [data['nazwa'] for data in self.battalions.values()]
        self.battalion_combo.config(values=battalion_names)
        self.new_unit_battalion_combo.config(values=[''] + battalion_names)
    
    def update_next_unit_number(self):
        """Aktualizuje następny numer jednostki dla wybranego batalionu"""
        side = self.new_unit_side_var.get()
        battalion_name = self.new_unit_battalion_var.get()
        
        if not battalion_name:
            # Bez batalionu - znajdź najwyższy numer na stronie
            max_number = 0
            for unit_data in self.units[side].values():
                if unit_data.get('batalion') is None:
                    unit_number = unit_data.get('numer', 0)
                    if unit_number > max_number:
                        max_number = unit_number
        else:
            # Z batalionem - znajdź najwyższy numer w batalionie
            battalion_id = None
            for bid, bdata in self.battalions.items():
                if bdata['nazwa'] == battalion_name:
                    battalion_id = bid
                    break
            
            max_number = 0
            if battalion_id:
                for unit_data in self.units[side].values():
                    if unit_data.get('batalion') == battalion_id:
                        unit_number = unit_data.get('numer', 0)
                        if unit_number > max_number:
                            max_number = unit_number
        
        next_number = max_number + 1
        self.new_unit_number_var.set(str(next_number))
    
    def migrate_old_units(self):
        """Migruje stare jednostki (z nazwami jako klucze) do nowego formatu z ID"""
        units_to_migrate = {}
        
        for side in ['własne', 'wroga']:
            units_to_migrate[side] = []
            
            for unit_key, unit_data in list(self.units[side].items()):
                # Sprawdź czy to stara jednostka (bez pola 'id')
                if 'id' not in unit_data:
                    # To stara jednostka - przygotuj do migracji
                    new_unit_id = self.generate_random_id()
                    
                    # Utwórz nowe dane jednostki
                    # Znajdź najwyższy numer na tej stronie dla migracji
                    max_number = 0
                    for existing_data in self.units[side].values():
                        if 'numer' in existing_data:
                            if existing_data['numer'] > max_number:
                                max_number = existing_data['numer']
                    
                    new_unit_data = {
                        "id": new_unit_id,
                        "numer": max_number + 1,
                        "typ": "kompania",  # domyślnie kompania
                        "batalion": None,   # brak batalionu
                        "liczba_ludzi": unit_data.get("liczba_ludzi", 150),
                        "doświadczenie": unit_data.get("doświadczenie", 0),
                        "zapasy": unit_data.get("zapasy", 3),
                        "liczba_zwycięstw": unit_data.get("liczba_zwycięstw", 0),
                        "liczba_uzupełnień": unit_data.get("liczba_uzupełnień", 0),
                        "strona": side,
                        "historia_bitew": unit_data.get("historia_bitew", [])
                    }
                    
                    units_to_migrate[side].append((unit_key, new_unit_id, new_unit_data))
        
        # Wykonaj migrację
        for side in ['własne', 'wroga']:
            for old_key, new_id, new_data in units_to_migrate[side]:
                # Usuń starą jednostkę
                del self.units[side][old_key]
                # Dodaj nową jednostkę z ID
                self.units[side][new_id] = new_data
        
        # Aktualizuj interfejs jeśli były migracje
        total_migrated = sum(len(units_to_migrate[side]) for side in ['własne', 'wroga'])
        if total_migrated > 0:
            print(f"Zmigrowano {total_migrated} jednostek do nowego formatu")
    
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
        self.game_frame = ttk.Frame(main_frame)
        self.game_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=(0, 10))
        
        # Frame środkowy (historia ostatnich rzutów)
        history_frame = ttk.LabelFrame(main_frame, text="Historia ostatnich 12 rzutów", padding="10")
        history_frame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=(5, 5))
        
        # Scrollable text widget dla historii
        self.history_text = scrolledtext.ScrolledText(
            history_frame, 
            width=35, 
            height=35, 
            font=("Arial", 9),
            state=tk.DISABLED
        )
        self.history_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Frame po prawej stronie (historia bitew)
        battles_frame = ttk.LabelFrame(main_frame, text="Historia bitew", padding="10")
        battles_frame.grid(row=0, column=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=(5, 5))
        
        # Frame najdalej po prawej (wykaz jednostek)
        units_frame = ttk.LabelFrame(main_frame, text="Wykaz Jednostek", padding="10")
        units_frame.grid(row=0, column=3, sticky=tk.W+tk.E+tk.N+tk.S, padx=(5, 0))
        
        # Wybor bitwy
        battle_selection_frame = ttk.Frame(battles_frame)
        battle_selection_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Label(battle_selection_frame, text="Wybierz bitwę:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        self.battle_var = tk.StringVar(value="Niezapisana")
        self.battle_combo = ttk.Combobox(battle_selection_frame, textvariable=self.battle_var, 
                                        values=self.battle_names, state="readonly", width=20)
        self.battle_combo.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(5, 0))
        self.battle_combo.bind("<<ComboboxSelected>>", self.on_battle_selected)
        
        # Tworzenie nowej bitwy
        new_battle_frame = ttk.Frame(battles_frame)
        new_battle_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(10, 10))
        
        ttk.Label(new_battle_frame, text="Nowa bitwa:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        self.new_battle_var = tk.StringVar()
        self.new_battle_entry = ttk.Entry(new_battle_frame, textvariable=self.new_battle_var, width=15)
        self.new_battle_entry.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(5, 5))
        
        ttk.Button(new_battle_frame, text="Stwórz", command=self.create_new_battle).grid(row=1, column=1, padx=(5, 0), pady=(5, 5))
        
        # Informacje o stratach dla wybranej bitwy
        self.battle_stats_label = ttk.Label(battles_frame, text="", font=("Arial", 9), 
                                           foreground="blue", justify=tk.LEFT)
        self.battle_stats_label.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(10, 10))
        
        # Historia wybranej bitwy
        self.battle_history_text = scrolledtext.ScrolledText(
            battles_frame, 
            width=35, 
            height=25, 
            font=("Arial", 9),
            state=tk.DISABLED
        )
        self.battle_history_text.grid(row=3, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Przyciski zapisz/wczytaj
        save_load_frame = ttk.Frame(battles_frame)
        save_load_frame.grid(row=4, column=0, sticky=tk.W+tk.E, pady=(10, 0))
        
        ttk.Button(save_load_frame, text="Zapisz rejestr", command=self.save_battles).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(save_load_frame, text="Wczytaj rejestr", command=self.load_battles).grid(row=0, column=1, padx=(5, 0))
        
        # === WYKAZ JEDNOSTEK ===
        
        # Przyciski zapisz/wczytaj jednostek
        units_save_load_frame = ttk.Frame(units_frame)
        units_save_load_frame.grid(row=0, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Button(units_save_load_frame, text="Zapisz", command=self.save_units).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(units_save_load_frame, text="Wczytaj", command=self.load_units).grid(row=0, column=1, padx=(5, 0))
        
        # Wybierz jednostkę
        unit_selection_frame = ttk.Frame(units_frame)
        unit_selection_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        
        ttk.Label(unit_selection_frame, text="Wybierz jednostkę:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, columnspan=2)
        
        # Jednostki własne
        ttk.Label(unit_selection_frame, text="Własne:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.own_units_var = tk.StringVar()
        self.own_units_combo = ttk.Combobox(unit_selection_frame, textvariable=self.own_units_var, 
                                           values=[], state="readonly", width=18)
        self.own_units_combo.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(2, 5))
        self.own_units_combo.bind("<<ComboboxSelected>>", lambda e: self.on_unit_selected("własne"))
        
        # Jednostki wroga
        ttk.Label(unit_selection_frame, text="Wroga:", font=("Arial", 9)).grid(row=3, column=0, sticky=tk.W)
        self.enemy_units_var = tk.StringVar()
        self.enemy_units_combo = ttk.Combobox(unit_selection_frame, textvariable=self.enemy_units_var, 
                                             values=[], state="readonly", width=18)
        self.enemy_units_combo.grid(row=4, column=0, sticky=tk.W+tk.E, pady=(2, 5))
        self.enemy_units_combo.bind("<<ComboboxSelected>>", lambda e: self.on_unit_selected("wroga"))
        
        # === BATALIONY ===
        battalions_frame = ttk.LabelFrame(units_frame, text="Bataliony", padding="5")
        battalions_frame.grid(row=2, column=0, sticky=tk.W+tk.E, pady=(10, 10))
        
        # Wybór batalionu
        ttk.Label(battalions_frame, text="Batalion:", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        self.battalion_var = tk.StringVar()
        self.battalion_combo = ttk.Combobox(battalions_frame, textvariable=self.battalion_var, 
                                           values=[], state="readonly", width=15)
        self.battalion_combo.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(2, 5))
        self.battalion_combo.bind("<<ComboboxSelected>>", self.on_battalion_selected)
        
        # Informacje o batalionie
        self.battalion_info_label = ttk.Label(battalions_frame, text="", font=("Arial", 8), 
                                             foreground="blue")
        self.battalion_info_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        # Tworzenie nowego batalionu
        new_battalion_frame = ttk.Frame(battalions_frame)
        new_battalion_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(5, 0))
        
        self.new_battalion_var = tk.StringVar()
        self.new_battalion_entry = ttk.Entry(new_battalion_frame, textvariable=self.new_battalion_var, width=10)
        self.new_battalion_entry.grid(row=0, column=0, sticky=tk.W+tk.E)
        
        ttk.Button(new_battalion_frame, text="+", command=self.create_new_battalion, width=3).grid(row=0, column=1, padx=(5, 0))
        
        # Stwórz jednostkę
        create_unit_frame = ttk.Frame(units_frame)
        create_unit_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(10, 10))
        
        ttk.Label(create_unit_frame, text="Stwórz jednostkę:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, columnspan=2)
        
        # Numer jednostki
        ttk.Label(create_unit_frame, text="Numer:", font=("Arial", 9)).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.new_unit_number_var = tk.StringVar()
        self.new_unit_number_entry = ttk.Entry(create_unit_frame, textvariable=self.new_unit_number_var, width=8)
        self.new_unit_number_entry.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Typ jednostki
        ttk.Label(create_unit_frame, text="Typ:", font=("Arial", 9)).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.new_unit_type_var = tk.StringVar(value="kompania")
        unit_type_frame = ttk.Frame(create_unit_frame)
        unit_type_frame.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        ttk.Radiobutton(unit_type_frame, text="Kompania", variable=self.new_unit_type_var, value="kompania").grid(row=0, column=0)
        ttk.Radiobutton(unit_type_frame, text="Grupa", variable=self.new_unit_type_var, value="grupa").grid(row=0, column=1, padx=(10, 0))
        
        # Batalion
        ttk.Label(create_unit_frame, text="Batalion:", font=("Arial", 9)).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.new_unit_battalion_var = tk.StringVar()
        self.new_unit_battalion_combo = ttk.Combobox(create_unit_frame, textvariable=self.new_unit_battalion_var, 
                                                    values=[], state="readonly", width=12)
        self.new_unit_battalion_combo.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        self.new_unit_battalion_combo.bind("<<ComboboxSelected>>", lambda e: self.update_next_unit_number())
        
        # Przyciski wyboru strony dla nowej jednostki
        create_buttons_frame = ttk.Frame(create_unit_frame)
        create_buttons_frame.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        
        self.new_unit_side_var = tk.StringVar(value="własne")
        ttk.Radiobutton(create_buttons_frame, text="Swoje", variable=self.new_unit_side_var, value="własne").grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(create_buttons_frame, text="Wróg", variable=self.new_unit_side_var, value="wroga").grid(row=0, column=1, padx=(10, 0))
        
        ttk.Button(create_unit_frame, text="Stwórz", command=self.create_new_unit).grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        # Frame dla szczegółów jednostki (początkowo ukryty)
        self.unit_details_frame = ttk.LabelFrame(units_frame, text="Szczegóły jednostki", padding="10")
        # Nie gridujemy go na początku - pojawi się po wybraniu jednostki
        
        # Migracja starych jednostek do nowego formatu
        self.migrate_old_units()
        
        # Inicjalizacja comboboxów dla batalionów i automat. numer
        self.update_battalion_combos()
        self.new_unit_side_var.trace('w', lambda *args: self.update_next_unit_number())
        self.update_next_unit_number()
        
        # Bind scroll wheel to canvas for both vertical and horizontal scrolling
        def _on_mousewheel(event):
            # Sprawdzenie czy wciśnięty jest Shift
            if event.state & 0x1:  # Shift is pressed
                # Horizontal scrolling
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                # Vertical scrolling (default)
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bindowanie do całego okna aplikacji, żeby działało wszędzie
        self.root.bind("<MouseWheel>", _on_mousewheel)
        
        # Dodatkowe bindowanie dla systemów Linux/Unix (Button-4 i Button-5)
        def _on_mousewheel_linux_up(event):
            if event.state & 0x1:  # Shift is pressed
                canvas.xview_scroll(-1, "units")
            else:
                canvas.yview_scroll(-1, "units")
        
        def _on_mousewheel_linux_down(event):
            if event.state & 0x1:  # Shift is pressed
                canvas.xview_scroll(1, "units")
            else:
                canvas.yview_scroll(1, "units")
        
        self.root.bind("<Button-4>", _on_mousewheel_linux_up)
        self.root.bind("<Button-5>", _on_mousewheel_linux_down)
        
        # Tytuł aplikacji
        title_label = ttk.Label(
            self.game_frame, 
            text="Rzut dwoma 4-ściennymi kośćmi", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame dla ustawień atak/obrona/w ruchu
        combat_mode_frame = ttk.LabelFrame(self.game_frame, text="Rodzaj działania", padding="10")
        combat_mode_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Strona 1 - opcje
        side1_frame = ttk.Frame(combat_mode_frame)
        side1_frame.grid(row=0, column=0, sticky=tk.E, padx=(0, 20))
        ttk.Label(side1_frame, text="Strona 1:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        self.side1_attack_var = tk.BooleanVar(value=True)
        self.side1_attack_check = ttk.Checkbutton(side1_frame, text="Atak", variable=self.side1_attack_var, command=self.on_side1_attack_change)
        self.side1_attack_check.grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        self.side1_defense_var = tk.BooleanVar(value=False)
        self.side1_defense_check = ttk.Checkbutton(side1_frame, text="Obrona", variable=self.side1_defense_var, command=self.on_side1_defense_change)
        self.side1_defense_check.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        
        self.side1_motion_var = tk.BooleanVar(value=False)
        self.side1_motion_check = ttk.Checkbutton(side1_frame, text="W ruchu", variable=self.side1_motion_var, command=self.on_side1_motion_change)
        self.side1_motion_check.grid(row=1, column=2, sticky=tk.W)
        
        # Strona 2 - opcje
        side2_frame = ttk.Frame(combat_mode_frame)
        side2_frame.grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Label(side2_frame, text="Strona 2:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        self.side2_attack_var = tk.BooleanVar(value=False)
        self.side2_attack_check = ttk.Checkbutton(side2_frame, text="Atak", variable=self.side2_attack_var, command=self.on_side2_attack_change)
        self.side2_attack_check.grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        self.side2_defense_var = tk.BooleanVar(value=True)
        self.side2_defense_check = ttk.Checkbutton(side2_frame, text="Obrona", variable=self.side2_defense_var, command=self.on_side2_defense_change)
        self.side2_defense_check.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        
        self.side2_motion_var = tk.BooleanVar(value=False)
        self.side2_motion_check = ttk.Checkbutton(side2_frame, text="W ruchu", variable=self.side2_motion_var, command=self.on_side2_motion_change)
        self.side2_motion_check.grid(row=1, column=2, sticky=tk.W)
        
        # Separator pionowy
        separator_combat = ttk.Separator(combat_mode_frame, orient='vertical')
        separator_combat.grid(row=0, column=1, sticky=tk.N+tk.S, padx=20)
        
        # Frame dla wyboru jednostek
        units_selection_frame = ttk.LabelFrame(self.game_frame, text="Wybór jednostek do bitwy", padding="10")
        units_selection_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(10, 10))
        
        # Strona 1 - wybór jednostki
        side1_unit_frame = ttk.Frame(units_selection_frame)
        side1_unit_frame.grid(row=0, column=0, sticky=tk.E, padx=(0, 20))
        ttk.Label(side1_unit_frame, text="Strona 1:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        self.unit_side1_type_var = tk.StringVar(value="brak")
        ttk.Radiobutton(side1_unit_frame, text="Własne", variable=self.unit_side1_type_var, value="własne", command=self.on_unit_type_change).grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(side1_unit_frame, text="Wroga", variable=self.unit_side1_type_var, value="wroga", command=self.on_unit_type_change).grid(row=1, column=1, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(side1_unit_frame, text="Brak", variable=self.unit_side1_type_var, value="brak", command=self.on_unit_type_change).grid(row=1, column=2, sticky=tk.W)
        
        self.unit_side1_var = tk.StringVar()
        self.unit_side1_combo = ttk.Combobox(side1_unit_frame, textvariable=self.unit_side1_var, values=[], state="readonly", width=15)
        self.unit_side1_combo.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(5, 0))
        self.unit_side1_combo.bind("<<ComboboxSelected>>", self.on_battle_unit_selected)
        
        # Przycisk "Dodaj więcej" dla strony 1
        ttk.Button(side1_unit_frame, text="Dodaj więcej", command=lambda: self.add_more_units_side(1)).grid(row=3, column=0, columnspan=3, pady=(5, 0))
        
        # Strona 2 - wybór jednostki
        side2_unit_frame = ttk.Frame(units_selection_frame)
        side2_unit_frame.grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Label(side2_unit_frame, text="Strona 2:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        self.unit_side2_type_var = tk.StringVar(value="brak")
        ttk.Radiobutton(side2_unit_frame, text="Własne", variable=self.unit_side2_type_var, value="własne", command=self.on_unit_type_change).grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(side2_unit_frame, text="Wroga", variable=self.unit_side2_type_var, value="wroga", command=self.on_unit_type_change).grid(row=1, column=1, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(side2_unit_frame, text="Brak", variable=self.unit_side2_type_var, value="brak", command=self.on_unit_type_change).grid(row=1, column=2, sticky=tk.W)
        
        self.unit_side2_var = tk.StringVar()
        self.unit_side2_combo = ttk.Combobox(side2_unit_frame, textvariable=self.unit_side2_var, values=[], state="readonly", width=15)
        self.unit_side2_combo.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(5, 0))
        self.unit_side2_combo.bind("<<ComboboxSelected>>", self.on_battle_unit_selected)
        
        # Przycisk "Dodaj więcej" dla strony 2
        ttk.Button(side2_unit_frame, text="Dodaj więcej", command=lambda: self.add_more_units_side(2)).grid(row=3, column=0, columnspan=3, pady=(5, 0))
        
        # Separator pionowy
        separator_units = ttk.Separator(units_selection_frame, orient='vertical')
        separator_units.grid(row=0, column=1, sticky=tk.N+tk.S, padx=20)
        
        # Frame kontener dla wyników z przyciskiem reset
        results_container = ttk.Frame(self.game_frame)
        results_container.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, 20))
        
        # Frame dla wyników kości (horizontal layout) - wycentrowany
        dice_frame = ttk.LabelFrame(results_container, text="Wyniki", padding="15")
        dice_frame.grid(row=0, column=0, sticky=tk.W+tk.E, padx=(50, 50))
        
        # Mały przycisk reset obok tabeli wyników
        reset_button = ttk.Button(results_container, text="R", command=self.reset_participating_units, width=2)
        reset_button.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Konfiguracja kolumn
        results_container.columnconfigure(0, weight=1)
        results_container.columnconfigure(1, weight=0)
        
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
        
        # Ikon dla jednostek strony 1
        self.side1_units_label = ttk.Label(dice_frame, text="", font=("Arial", 10))
        self.side1_units_label.grid(row=3, column=0, padx=20)
        
        # Wynik liczby ludzi i ikona doświadczenia strona 1
        result1_frame = ttk.Frame(dice_frame)
        result1_frame.grid(row=4, column=0, padx=20)
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
            foreground="#B8860B"
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
        
        # Ikon dla jednostek strony 2
        self.side2_units_label = ttk.Label(dice_frame, text="", font=("Arial", 10))
        self.side2_units_label.grid(row=3, column=2, padx=20)
        
        # Wynik liczby ludzi i ikona doświadczenia strona 2
        result2_frame = ttk.Frame(dice_frame)
        result2_frame.grid(row=4, column=2, padx=20)
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
            foreground="#B8860B"
        )
        self.dice2_exp_icon.grid(row=0, column=1, padx=(5, 0))
        
        
        # Separator pionowy
        separator = ttk.Separator(dice_frame, orient='vertical')
        separator.grid(row=0, column=1, rowspan=4, sticky=tk.N+tk.S, padx=10)
        
        # Wynik taktyczny (nad przyciskiem)
        self.tactical_result_label = ttk.Label(
            self.game_frame,
            text="",
            font=("Arial", 12, "bold"),
            foreground="darkgreen"
        )
        self.tactical_result_label.grid(row=4, column=0, columnspan=3, pady=(10, 5))
        
        
        # Przycisk do generowania wyniku
        self.roll_button = ttk.Button(
            self.game_frame,
            text="Wynik",
            command=self.roll_dice,
            style="Roll.TButton"
        )
        self.roll_button.grid(row=5, column=0, columnspan=3, pady=(5, 20))
        
        # Stylizacja przycisków
        style = ttk.Style()
        style.configure("Roll.TButton", font=("Arial", 12, "bold"))
        style.configure("Reset.TButton", font=("Arial", 10))
        
        # Frame dla modyfikatorów
        modifiers_frame = ttk.LabelFrame(self.game_frame, text="Modyfikatory", padding="10")
        modifiers_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(10, 0))
        
        # Przycisk Reset na górze modyfikatorów
        reset_button = ttk.Button(
            modifiers_frame,
            text="Reset",
            command=self.reset_modifiers,
            style="Reset.TButton"
        )
        reset_button.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Lewa kolumna - Strona 1
        left_frame = ttk.LabelFrame(modifiers_frame, text="Strona 1", padding="10")
        left_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, padx=(0, 10))
        
        # Modyfikator do wyniku strony 1
        ttk.Label(left_frame, text="Dodatek:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dice1_modifier_var = tk.StringVar(value="0")
        self.dice1_modifier_entry = ttk.Entry(left_frame, textvariable=self.dice1_modifier_var, width=5, font=("Arial", 10))
        self.dice1_modifier_entry.grid(row=0, column=1, padx=(0, 5))
        # Label dla bonusu doświadczenia do dodatku
        self.dice1_modifier_bonus_label = ttk.Label(left_frame, text="", font=("Arial", 9), foreground="green")
        self.dice1_modifier_bonus_label.grid(row=0, column=2, padx=(5, 0))
        
        # Modyfikator zakresu strony 1
        ttk.Label(left_frame, text="Oczka +:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice1_range_var = tk.StringVar(value="0")
        self.dice1_range_entry = ttk.Entry(left_frame, textvariable=self.dice1_range_var, width=5, font=("Arial", 10))
        self.dice1_range_entry.grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        # Label dla bonusu doświadczenia do oczek
        self.dice1_range_bonus_label = ttk.Label(left_frame, text="", font=("Arial", 9), foreground="green")
        self.dice1_range_bonus_label.grid(row=1, column=2, padx=(5, 0))
        
        # Otoczony strona 1
        self.dice1_surrounded_var = tk.BooleanVar()
        self.dice1_surrounded_check = ttk.Checkbutton(left_frame, text="Otoczony (-1)", variable=self.dice1_surrounded_var, onvalue=True, offvalue=False)
        self.dice1_surrounded_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Doświadczenie strona 1 (dropdown jak fortyfikacje)
        ttk.Label(left_frame, text="Doświadczenie:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice1_exp_var = tk.IntVar(value=0)
        exp_combo1 = ttk.Combobox(left_frame, textvariable=self.dice1_exp_var, values=["-2", "-1", "0", "1", "2", "3", "4", "5", "6"], width=3, state="readonly")
        exp_combo1.grid(row=3, column=1, padx=(0, 5), pady=(5, 0))
        exp_combo1.bind("<<ComboboxSelected>>", self.update_exp_bonuses_display)
        
        # Dodatkowe modyfikatory strona 1
        ttk.Label(left_frame, text="Dodatkowe:", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.dice1_defense_var = tk.BooleanVar()
        self.dice1_defense_check = ttk.Checkbutton(left_frame, text="Obrona w zabudowaniach (+1)", variable=self.dice1_defense_var)
        self.dice1_defense_check.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        self.dice1_supply_var = tk.BooleanVar()
        self.dice1_supply_check = ttk.Checkbutton(left_frame, text="Brak zaopatrzenia (-1)", variable=self.dice1_supply_var)
        self.dice1_supply_check.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        ttk.Label(left_frame, text="Fortyfikacje:", font=("Arial", 10)).grid(row=7, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice1_fort_var = tk.IntVar(value=0)
        fort_combo1 = ttk.Combobox(left_frame, textvariable=self.dice1_fort_var, values=["0", "1", "2", "3"], width=3, state="readonly")
        fort_combo1.grid(row=7, column=1, padx=(0, 5), pady=(5, 0))
        
        # Prawa kolumna - Strona 2
        right_frame = ttk.LabelFrame(modifiers_frame, text="Strona 2", padding="10")
        right_frame.grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S, padx=(10, 0))
        
        # Modyfikator do wyniku strony 2
        ttk.Label(right_frame, text="Dodatek:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dice2_modifier_var = tk.StringVar(value="0")
        self.dice2_modifier_entry = ttk.Entry(right_frame, textvariable=self.dice2_modifier_var, width=5, font=("Arial", 10))
        self.dice2_modifier_entry.grid(row=0, column=1, padx=(0, 5))
        # Label dla bonusu doświadczenia do dodatku
        self.dice2_modifier_bonus_label = ttk.Label(right_frame, text="", font=("Arial", 9), foreground="green")
        self.dice2_modifier_bonus_label.grid(row=0, column=2, padx=(5, 0))
        
        # Modyfikator zakresu strony 2
        ttk.Label(right_frame, text="Oczka +:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice2_range_var = tk.StringVar(value="0")
        self.dice2_range_entry = ttk.Entry(right_frame, textvariable=self.dice2_range_var, width=5, font=("Arial", 10))
        self.dice2_range_entry.grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        # Label dla bonusu doświadczenia do oczek
        self.dice2_range_bonus_label = ttk.Label(right_frame, text="", font=("Arial", 9), foreground="green")
        self.dice2_range_bonus_label.grid(row=1, column=2, padx=(5, 0))
        
        # Otoczony strona 2
        self.dice2_surrounded_var = tk.BooleanVar()
        self.dice2_surrounded_check = ttk.Checkbutton(right_frame, text="Otoczony (-1)", variable=self.dice2_surrounded_var, onvalue=True, offvalue=False)
        self.dice2_surrounded_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Doświadczenie strona 2 (dropdown jak fortyfikacje)
        ttk.Label(right_frame, text="Doświadczenie:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice2_exp_var = tk.IntVar(value=0)
        exp_combo2 = ttk.Combobox(right_frame, textvariable=self.dice2_exp_var, values=["-2", "-1", "0", "1", "2", "3", "4", "5", "6"], width=3, state="readonly")
        exp_combo2.grid(row=3, column=1, padx=(0, 5), pady=(5, 0))
        exp_combo2.bind("<<ComboboxSelected>>", self.update_exp_bonuses_display)
        
        # Dodatkowe modyfikatory strona 2
        ttk.Label(right_frame, text="Dodatkowe:", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.dice2_defense_var = tk.BooleanVar()
        self.dice2_defense_check = ttk.Checkbutton(right_frame, text="Obrona w zabudowaniach (+1)", variable=self.dice2_defense_var)
        self.dice2_defense_check.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        self.dice2_supply_var = tk.BooleanVar()
        self.dice2_supply_check = ttk.Checkbutton(right_frame, text="Brak zaopatrzenia (-1)", variable=self.dice2_supply_var)
        self.dice2_supply_check.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        ttk.Label(right_frame, text="Fortyfikacje:", font=("Arial", 10)).grid(row=7, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.dice2_fort_var = tk.IntVar(value=0)
        fort_combo2 = ttk.Combobox(right_frame, textvariable=self.dice2_fort_var, values=["0", "1", "2", "3"], width=3, state="readonly")
        fort_combo2.grid(row=7, column=1, padx=(0, 5), pady=(5, 0))
        
        # Informacja o zakresie wartości
        info_label = ttk.Label(
            self.game_frame,
            text="Każda strona: 1 do (4 + oczka) + modyfikatory",
            font=("Arial", 10),
            foreground="gray"
        )
        info_label.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        # Konfiguracja rozciągania kolumn
        main_frame.columnconfigure(0, weight=2)  # Gra
        main_frame.columnconfigure(1, weight=1)  # Historia
        main_frame.columnconfigure(2, weight=1)  # Bitwy
        main_frame.columnconfigure(3, weight=1)  # Jednostki
        self.game_frame.columnconfigure(0, weight=1)
        self.game_frame.columnconfigure(1, weight=1)
        self.game_frame.columnconfigure(2, weight=1)
        dice_frame.columnconfigure(0, weight=1)
        dice_frame.columnconfigure(2, weight=1)
        combat_mode_frame.columnconfigure(0, weight=1)
        combat_mode_frame.columnconfigure(1, weight=0)
        combat_mode_frame.columnconfigure(2, weight=1)
        modifiers_frame.columnconfigure(0, weight=1)
        modifiers_frame.columnconfigure(1, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        battles_frame.columnconfigure(0, weight=1)
        battles_frame.rowconfigure(3, weight=1)
        battle_selection_frame.columnconfigure(0, weight=1)
        new_battle_frame.columnconfigure(0, weight=1)
        save_load_frame.columnconfigure(0, weight=1)
        save_load_frame.columnconfigure(1, weight=1)
        
        # Focus na przycisk
        self.roll_button.focus()
        
        # Bind Enter key to roll dice
        self.root.bind('<Return>', lambda event: self.roll_dice())
    
    def reset_modifiers(self):
        """Resetuje wszystkie modyfikatory do wartości domyślnych"""
        # Reset modyfikatorów strony 1
        self.dice1_modifier_var.set("0")
        self.dice1_range_var.set("0")
        self.dice1_surrounded_var.set(False)
        self.dice1_exp_var.set(0)
        self.dice1_defense_var.set(False)
        self.dice1_supply_var.set(False)
        self.dice1_fort_var.set(0)
        
        # Reset modyfikatorów strony 2
        self.dice2_modifier_var.set("0")
        self.dice2_range_var.set("0")
        self.dice2_surrounded_var.set(False)
        self.dice2_exp_var.set(0)
        self.dice2_defense_var.set(False)
        self.dice2_supply_var.set(False)
        self.dice2_fort_var.set(0)
        
        # Aktualizacja wyświetlania bonusów doświadczenia
        self.update_exp_bonuses_display()
    
    def on_side1_attack_change(self):
        """Obsługuje zmianę ataku strony 1"""
        if self.side1_attack_var.get():
            self.side1_defense_var.set(False)
            self.side1_motion_var.set(False)
            self.side2_attack_var.set(False)
            self.side2_defense_var.set(True)
            self.side2_motion_var.set(False)
    
    def on_side1_defense_change(self):
        """Obsługuje zmianę obrony strony 1"""
        if self.side1_defense_var.get():
            self.side1_attack_var.set(False)
            self.side1_motion_var.set(False)
            self.side2_attack_var.set(True)
            self.side2_defense_var.set(False)
            self.side2_motion_var.set(False)
    
    def on_side1_motion_change(self):
        """Obsługuje zmianę ruchu strony 1"""
        if self.side1_motion_var.get():
            self.side1_attack_var.set(False)
            self.side1_defense_var.set(False)
            # Nie wyłączamy W ruchu dla strony 2 - może być niezależnie
    
    def on_side2_attack_change(self):
        """Obsługuje zmianę ataku strony 2"""
        if self.side2_attack_var.get():
            self.side2_defense_var.set(False)
            self.side2_motion_var.set(False)
            self.side1_attack_var.set(False)
            self.side1_defense_var.set(True)
            self.side1_motion_var.set(False)
    
    def on_side2_defense_change(self):
        """Obsługuje zmianę obrony strony 2"""
        if self.side2_defense_var.get():
            self.side2_attack_var.set(False)
            self.side2_motion_var.set(False)
            self.side1_attack_var.set(True)
            self.side1_defense_var.set(False)
            self.side1_motion_var.set(False)
    
    def on_side2_motion_change(self):
        """Obsługuje zmianę ruchu strony 2"""
        if self.side2_motion_var.get():
            self.side2_attack_var.set(False)
            self.side2_defense_var.set(False)
            # Nie wyłączamy W ruchu dla strony 1 - może być niezależnie
    
    def update_exp_bonuses_display(self, event=None):
        """Aktualizuje wyświetlanie bonusów doświadczenia obok pól wejściowych"""
        # Strona 1
        exp1 = self.dice1_exp_var.get() if self.dice1_exp_var.get() > 0 else 0
        if exp1 > 0:
            self.dice1_modifier_bonus_label.config(text=f"(+{exp1})")
            self.dice1_range_bonus_label.config(text=f"(+{exp1 * 2})")
        else:
            self.dice1_modifier_bonus_label.config(text="")
            self.dice1_range_bonus_label.config(text="")
        
        # Strona 2
        exp2 = self.dice2_exp_var.get() if self.dice2_exp_var.get() > 0 else 0
        if exp2 > 0:
            self.dice2_modifier_bonus_label.config(text=f"(+{exp2})")
            self.dice2_range_bonus_label.config(text=f"(+{exp2 * 2})")
        else:
            self.dice2_modifier_bonus_label.config(text="")
            self.dice2_range_bonus_label.config(text="")
    
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
        
        # Obliczanie przewagi liczebnej (2.1x = +1, 4.2x = +2, itd.)
        numerical_advantage_1 = 0
        numerical_advantage_2 = 0
        
        if self.dice1_people_original > 0 and self.dice2_people_original > 0:
            ratio_1_vs_2 = self.dice1_people_original / self.dice2_people_original
            ratio_2_vs_1 = self.dice2_people_original / self.dice1_people_original
            
            if ratio_1_vs_2 >= 2.1:
                numerical_advantage_1 = int(ratio_1_vs_2 / 2.1)
            elif ratio_2_vs_1 >= 2.1:
                numerical_advantage_2 = int(ratio_2_vs_1 / 2.1)
        
        # Dodanie bonusów doświadczenia do zakresu i modyfikatora
        dice1_exp = self.dice1_exp_var.get() if self.dice1_exp_var.get() > 0 else 0
        dice2_exp = self.dice2_exp_var.get() if self.dice2_exp_var.get() > 0 else 0
        
        dice1_exp_range_bonus = dice1_exp * 2  # +2 do oczek za każdy poziom
        dice2_exp_range_bonus = dice2_exp * 2
        
        # Losowanie wartości dla obu kości z uwzględnieniem modyfikatora zakresu i bonusów doświadczenia
        dice1_max = 4 + self.dice1_range_modifier + dice1_exp_range_bonus
        dice2_max = 4 + self.dice2_range_modifier + dice2_exp_range_bonus
        
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
        
        # Dodawanie modyfikatorów doświadczenia i przewagi liczebnej
        dice1_total_modifier += self.dice1_exp_var.get() + numerical_advantage_1
        dice2_total_modifier += self.dice2_exp_var.get() + numerical_advantage_2
        
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
        
        # Aktualizacja wyników liczby ludzi ze stratami i przewagą liczebną
        dice1_text = f"Wynik: {self.dice1_people_result} ludzi\nStraty: {getattr(self, 'dice1_losses', 0)}"
        dice2_text = f"Wynik: {self.dice2_people_result} ludzi\nStraty: {getattr(self, 'dice2_losses', 0)}"
        
        # Dodanie informacji o przewadze liczebnej pod stratami
        if numerical_advantage_1 > 0:
            dice1_text += f"\nPrzewaga: +{numerical_advantage_1}"
        if numerical_advantage_2 > 0:
            dice2_text += f"\nPrzewaga: +{numerical_advantage_2}"
        
        self.dice1_people_result_label.config(text=dice1_text)
        self.dice2_people_result_label.config(text=dice2_text)
        
        # Informacja o przewadze liczebnej wyświetlana w tabeli wyników
        
        # Aktualizacja ikon doświadczenia
        self.dice1_exp_icon.config(text="⭐ Zwycięstwo" if self.dice1_gets_exp else "")
        self.dice2_exp_icon.config(text="⭐ Zwycięstwo" if self.dice2_gets_exp else "")
        
        # Rozdzielenie strat między jednostkami uczestniczącymi
        self.distribute_losses_among_units()
        
        # Aktualizacja statystyk jednostek po rzucie
        self.update_unit_stats_after_battle(dice1_final, dice2_final)
        
        # Obliczanie i wyświetlanie wyników taktycznych
        self.calculate_and_display_tactical_results(dice1_final, dice2_final)
        
        # Dodanie do historii (bez informacji o jednostkach)
        self.add_to_history(dice1_final, dice2_final)
        
        # Dodanie do historii jednostek
        self.add_to_unit_battle_history(dice1_final, dice2_final)
        
        # Efekt wizualny - krótka animacja przycisku
        self.roll_button.config(state="disabled")
        self.root.after(200, lambda: self.roll_button.config(state="normal"))
        
        # Komunikat o wyniku w zależności od rzutu
        self.display_result_message()
    
    def calculate_and_display_tactical_results(self, dice1_final, dice2_final):
        """Oblicza i wyświetla wyniki taktyczne na podstawie systemu atak/obrona"""
        # Sprawdzanie czy mamy klasyczną sytuację atak vs obrona
        attack_result = 0
        defense_result = 0
        
        if self.side1_attack_var.get() and self.side2_defense_var.get():
            attack_result = dice1_final
            defense_result = dice2_final
        elif self.side2_attack_var.get() and self.side1_defense_var.get():
            attack_result = dice2_final
            defense_result = dice1_final
        else:
            # Brak jasnego ataku vs obrony - wyczyść wynik
            self.tactical_result_label.config(text="")
            return
        
        # Obliczanie wyniku taktycznego
        tactical_outcome = self.get_tactical_outcome(attack_result, defense_result)
        outcome_description = self.get_tactical_description(tactical_outcome)
        
        # Wyświetlanie jednego wyniku nad przyciskiem
        self.tactical_result_label.config(text=f"Wynik ataku: {outcome_description}")
    
    def get_tactical_outcome(self, attack_result, defense_result):
        """Określa wynik taktyczny na skali 1-6"""
        difference = attack_result - defense_result
        
        if difference <= 0:
            # Obrona wygrywa lub remis - dodajemy element losowości dla różnicy -1
            if difference == -1 and random.random() < 0.3:
                return 1  # Pozycja nienaruszona (30% szansy przy -1)
            else:
                return 1  # Pozycja nienaruszona
        elif difference == 1:
            return 2  # Lokalne wejście
        elif difference == 2:
            return 3  # Częściowe wysunięcie
        elif difference == 3:
            return 4  # Wyłom taktyczny
        elif difference == 4:
            return 5  # Załamanie obrony
        else:  # difference >= 5
            return 6  # Przełamanie strategiczne
    
    def get_tactical_description(self, outcome):
        """Zwraca opis wyniku taktycznego"""
        descriptions = {
            1: "Pozycja nienaruszona",
            2: "Lokalne wejście", 
            3: "Częściowe wysunięcie",
            4: "Wyłom taktyczny",
            5: "Załamanie obrony",
            6: "Przełamanie strategiczne"
        }
        return descriptions.get(outcome, "Nieznany wynik")
    
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
        
        # Przy różnicy +1, wyższa strona dostaje ikonkę "Zwycięstwo"
        if difference >= 1:
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
        
        def calculate_losses_for_side(enemy_result, own_people, own_fortifications, own_no_supply, own_defense_buildings, enemy_fortifications, enemy_defense_buildings, own_experience, own_attacking, enemy_defending, enemy_in_motion):
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
            
            # Negatywne doświadczenie zwiększa straty własne
            if own_experience == -1:
                defense_modifier += 0.10  # +10%
            elif own_experience == -2:
                defense_modifier += 0.25  # +25%
            
            # Modyfikatory ataku przeciwnika (fortyfikacje przeciwnika zwiększają nasze straty)
            attack_modifier = 1.0  # Bazowy mnożnik
            
            # Fortyfikacje przeciwnika zwiększają nasze straty
            if enemy_fortifications == 1:
                attack_modifier += random.uniform(0.10, 0.15)  # +10-15%
            elif enemy_fortifications == 2:
                attack_modifier += random.uniform(0.16, 0.25)  # +16-25%
            elif enemy_fortifications == 3:
                attack_modifier += random.uniform(0.30, 0.40)  # +30-40%
            
            # Obrona w zabudowaniach przeciwnika zwiększa nasze straty
            if enemy_defense_buildings:
                attack_modifier += random.uniform(0.05, 0.15)  # +5-15%
            
            # Nowe mechaniki atak/obrona/w ruchu
            
            # Straty atakujących są 5% większe, gdy druga strona ma zaznaczoną obronę
            if own_attacking and enemy_defending:
                attack_modifier += 0.05  # +5% strat dla atakujących vs obrona
            
            # W przypadku zaznaczenia "W Ruchu", strona przeciwna ma straty 10% mniejsze
            if enemy_in_motion:
                defense_modifier -= 0.10  # -10% strat gdy przeciwnik jest w ruchu
            
            # Końcowy procent strat (nie może być ujemny)
            final_loss_percentage = max(0.0, base_loss_percentage * defense_modifier * attack_modifier)
            
            # Obliczenia strat: dla ≤150 ludzi - baza 150, dla >150 ludzi - baza rzeczywista
            loss_base = 150 if own_people <= 150 else own_people
            absolute_losses = int(loss_base * final_loss_percentage)
            
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
        
        # Pobieranie informacji o stanie atak/obrona/w ruchu
        side1_attacking = self.side1_attack_var.get()
        side1_defending = self.side1_defense_var.get()
        side1_in_motion = self.side1_motion_var.get()
        
        side2_attacking = self.side2_attack_var.get()
        side2_defending = self.side2_defense_var.get()
        side2_in_motion = self.side2_motion_var.get()
        
        # Obliczanie strat dla obu stron
        dice1_experience = self.dice1_exp_var.get()
        dice2_experience = self.dice2_exp_var.get()
        
        self.dice1_people_result, self.dice1_losses = calculate_losses_for_side(
            dice2_final, self.dice1_people_original, dice1_fort, dice1_no_supply, dice1_defense, dice2_fort, dice2_defense, dice1_experience,
            side1_attacking, side2_defending, side2_in_motion
        )
        
        self.dice2_people_result, self.dice2_losses = calculate_losses_for_side(
            dice1_final, self.dice2_people_original, dice2_fort, dice2_no_supply, dice2_defense, dice1_fort, dice1_defense, dice2_experience,
            side2_attacking, side1_defending, side1_in_motion
        )
    
    def add_to_history(self, dice1_final, dice2_final):
        """Dodaje wynik do historii"""
        # Zbierz informacje o jednostkach uczestniczących z sformatowanymi nazwami
        side1_units = []
        for u in self.participating_units["strona1"]:
            unit_id = u.get('id', u.get('name', ''))
            side_name = u.get('side', '')
            display_name = self.get_unit_display_name(unit_id, side_name) if unit_id and side_name else u.get('name', unit_id)
            side1_units.append(display_name)
            
        side2_units = []
        for u in self.participating_units["strona2"]:
            unit_id = u.get('id', u.get('name', ''))
            side_name = u.get('side', '')
            display_name = self.get_unit_display_name(unit_id, side_name) if unit_id and side_name else u.get('name', unit_id)
            side2_units.append(display_name)
        
        # Dodaj jednostki wybrane normalnie (nie przez "Dodaj więcej")
        if self.selected_unit_side1 and self.unit_side1_type != "brak":
            display_name = self.get_unit_display_name(self.selected_unit_side1, self.unit_side1_type)
            if display_name not in side1_units:
                side1_units.append(display_name)
        
        if self.selected_unit_side2 and self.unit_side2_type != "brak":
            display_name = self.get_unit_display_name(self.selected_unit_side2, self.unit_side2_type)
            if display_name not in side2_units:
                side2_units.append(display_name)
        
        # Określ tryb walki - użyj poprawnych nazw zmiennych
        side1_attacking = self.side1_attack_var.get()
        side2_attacking = self.side2_attack_var.get() 
        side1_in_motion = self.side1_motion_var.get()
        side2_in_motion = self.side2_motion_var.get()
        
        history_entry = {
            'dice1': dice1_final,
            'dice2': dice2_final,
            'people1_before': self.dice1_people_original,
            'people1_after': self.dice1_people_result,
            'people2_before': self.dice2_people_original,
            'people2_after': self.dice2_people_result,
            'exp1': self.dice1_gets_exp,
            'exp2': self.dice2_gets_exp,
            'side1_units': side1_units,
            'side2_units': side2_units,
            'side1_attacking': side1_attacking,
            'side2_attacking': side2_attacking,
            'side1_in_motion': side1_in_motion,
            'side2_in_motion': side2_in_motion
        }
        
        # Dodanie do listy historii
        self.history.append(history_entry)
        
        # Zachowanie tylko ostatnich 12 wyników
        if len(self.history) > 12:
            self.history.pop(0)
        
        # Dodanie do historii wybranej bitwy (jeśli nie "Niezapisana")
        if self.current_battle != "Niezapisana":
            if self.current_battle not in self.battles:
                self.battles[self.current_battle] = {"history": [], "created": datetime.now().isoformat()}
            self.battles[self.current_battle]["history"].append(history_entry)
        
        # Aktualizacja wyświetlania historii
        self.update_history_display()
        self.update_battle_stats()
        self.update_battle_history_display()
    
    def update_history_display(self):
        """Aktualizuje wyświetlanie historii"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        for i, entry in enumerate(reversed(self.history), 1):
            exp1_icon = " ⭐" if entry['exp1'] else ""
            exp2_icon = " ⭐" if entry['exp2'] else ""
            
            # Nowy format nazw w zależności od trybu i jednostek
            side1_units = entry.get('side1_units', [])
            side2_units = entry.get('side2_units', [])
            
            # Określ format na podstawie jednostek i trybu
            if side1_units and side2_units:
                # Mamy jednostki po obu stronach
                side1_in_motion = entry.get('side1_in_motion', False)
                side2_in_motion = entry.get('side2_in_motion', False)
                side1_attacking = entry.get('side1_attacking', False)
                side2_attacking = entry.get('side2_attacking', False)
                
                # Formatuj nazwę jednostek (główna + dodatkowe po przecinku)
                side1_name = side1_units[0]
                if len(side1_units) > 1:
                    side1_name += ", " + ", ".join(side1_units[1:])
                    
                side2_name = side2_units[0]
                if len(side2_units) > 1:
                    side2_name += ", " + ", ".join(side2_units[1:])
                
                if side1_in_motion or side2_in_motion:
                    # W ruchu
                    battle_desc = f"Bitwa \"{side1_name}\" z \"{side2_name}\""
                elif side1_attacking:
                    # Strona 1 atakuje
                    battle_desc = f"Ofensywa \"{side1_name}\" na \"{side2_name}\""
                elif side2_attacking:
                    # Strona 2 atakuje
                    battle_desc = f"Ofensywa \"{side2_name}\" na \"{side1_name}\""
                else:
                    # Domyślnie atak vs obrona
                    battle_desc = f"Ofensywa \"{side1_name}\" na \"{side2_name}\""
            else:
                # Brak jednostek - format oryginalny
                battle_desc = f"Strona 1: {entry['dice1']}{exp1_icon} | Strona 2: {entry['dice2']}{exp2_icon}"
            
            if side1_units and side2_units:
                history_line = f"#{i}: {battle_desc}\n"
                history_line += f"    Kostki: {entry['dice1']}{exp1_icon} vs {entry['dice2']}{exp2_icon}\n"
            else:
                history_line = f"#{i}: {battle_desc}\n"
                
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
    
    def on_battle_selected(self, event=None):
        """Obsługuje wybór bitwy z combobox"""
        self.current_battle = self.battle_var.get()
        self.update_battle_stats()
        self.update_battle_history_display()
    
    def create_new_battle(self):
        """Tworzy nową bitwę"""
        battle_name = self.new_battle_var.get().strip()
        if not battle_name:
            messagebox.showwarning("Błąd", "Wprowadź nazwę bitwy!")
            return
        
        if battle_name in self.battle_names:
            messagebox.showwarning("Błąd", "Bitwa o tej nazwie już istnieje!")
            return
        
        if battle_name == "Niezapisana":
            messagebox.showwarning("Błąd", "Nazwa 'Niezapisana' jest zarezerwowana!")
            return
        
        # Dodanie nowej bitwy
        self.battle_names.append(battle_name)
        self.battles[battle_name] = {"history": [], "created": datetime.now().isoformat()}
        
        # Aktualizacja combobox
        self.battle_combo.config(values=self.battle_names)
        self.battle_var.set(battle_name)
        self.current_battle = battle_name
        
        # Wyczyszczenie pola nazwy
        self.new_battle_var.set("")
        
        # Aktualizacja wyświetlania
        self.update_battle_stats()
        self.update_battle_history_display()
        
        messagebox.showinfo("Sukces", f"Utworzono bitwę: {battle_name}")
    
    def update_battle_stats(self):
        """Aktualizuje wyświetlanie statystyk wybranej bitwy"""
        if self.current_battle == "Niezapisana" or self.current_battle not in self.battles:
            self.battle_stats_label.config(text="")
            return
        
        battle_history = self.battles[self.current_battle]["history"]
        if not battle_history:
            self.battle_stats_label.config(text="Brak rzutów w tej bitwie.")
            return
        
        # Obliczanie sumarycznych strat
        total_losses_1 = 0
        total_losses_2 = 0
        
        for entry in battle_history:
            losses_1 = entry['people1_before'] - entry['people1_after']
            losses_2 = entry['people2_before'] - entry['people2_after']
            total_losses_1 += losses_1
            total_losses_2 += losses_2
        
        stats_text = f"Sumaryczne straty:\nStrona 1: {total_losses_1} ludzi\nStrona 2: {total_losses_2} ludzi\n\nLiczba rzutów: {len(battle_history)}"
        self.battle_stats_label.config(text=stats_text)
    
    def update_battle_history_display(self):
        """Aktualizuje wyświetlanie historii wybranej bitwy"""
        self.battle_history_text.config(state=tk.NORMAL)
        self.battle_history_text.delete(1.0, tk.END)
        
        if self.current_battle == "Niezapisana" or self.current_battle not in self.battles:
            self.battle_history_text.config(state=tk.DISABLED)
            return
        
        battle_history = self.battles[self.current_battle]["history"]
        
        for i, entry in enumerate(battle_history, 1):
            exp1_icon = " ⭐" if entry['exp1'] else ""
            exp2_icon = " ⭐" if entry['exp2'] else ""
            
            # Nowy format nazw w zależności od trybu i jednostek
            side1_units = entry.get('side1_units', [])
            side2_units = entry.get('side2_units', [])
            
            # Określ format na podstawie jednostek i trybu
            if side1_units and side2_units:
                # Mamy jednostki po obu stronach
                side1_in_motion = entry.get('side1_in_motion', False)
                side2_in_motion = entry.get('side2_in_motion', False)
                side1_attacking = entry.get('side1_attacking', False)
                side2_attacking = entry.get('side2_attacking', False)
                
                # Formatuj nazwę jednostek (główna + dodatkowe po przecinku)
                side1_name = side1_units[0]
                if len(side1_units) > 1:
                    side1_name += ", " + ", ".join(side1_units[1:])
                    
                side2_name = side2_units[0]
                if len(side2_units) > 1:
                    side2_name += ", " + ", ".join(side2_units[1:])
                
                if side1_in_motion or side2_in_motion:
                    # W ruchu
                    battle_desc = f"Bitwa \"{side1_name}\" z \"{side2_name}\""
                elif side1_attacking:
                    # Strona 1 atakuje
                    battle_desc = f"Ofensywa \"{side1_name}\" na \"{side2_name}\""
                elif side2_attacking:
                    # Strona 2 atakuje
                    battle_desc = f"Ofensywa \"{side2_name}\" na \"{side1_name}\""
                else:
                    # Domyślnie atak vs obrona
                    battle_desc = f"Ofensywa \"{side1_name}\" na \"{side2_name}\""
                
                history_line = f"#{i}: {battle_desc}\n"
                history_line += f"    Kostki: {entry['dice1']}{exp1_icon} vs {entry['dice2']}{exp2_icon}\n"
            else:
                # Stary format dla starych zapisów lub brak jednostek
                unit1_info = f" ({entry.get('unit1_name', '')})" if entry.get('unit1_name') else ""
                unit2_info = f" ({entry.get('unit2_name', '')})" if entry.get('unit2_name') else ""
                
                history_line = f"#{i}: Strona 1: {entry['dice1']}{exp1_icon}{unit1_info} | Strona 2: {entry['dice2']}{exp2_icon}{unit2_info}\n"
                
            history_line += f"    Ludzie: {entry['people1_before']}→{entry['people1_after']} | {entry['people2_before']}→{entry['people2_after']}\n\n"
            
            self.battle_history_text.insert(tk.END, history_line)
        
        self.battle_history_text.config(state=tk.DISABLED)
        self.battle_history_text.see(tk.END)
    
    def save_battles(self):
        """Zapisuje rejestr bitew do pliku JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Zapisz rejestr bitew",
                defaultextension=".json",
                filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")]
            )
            
            if filename:
                data = {
                    "battles": self.battles,
                    "battle_names": self.battle_names,
                    "saved_at": datetime.now().isoformat()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Sukces", f"Rejestr bitew zapisany do: {filename}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać rejestru: {str(e)}")
    
    def load_battles(self):
        """Wczytuje rejestr bitew z pliku JSON"""
        try:
            filename = filedialog.askopenfilename(
                title="Wczytaj rejestr bitew",
                filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Sprawdzenie struktury danych
                if "battles" not in data or "battle_names" not in data:
                    messagebox.showerror("Błąd", "Nieprawidłowy format pliku!")
                    return
                
                # Wczytanie danych
                self.battles = data["battles"]
                self.battle_names = data["battle_names"]
                
                # Upewnienie się, że "Niezapisana" jest na początku
                if "Niezapisana" not in self.battle_names:
                    self.battle_names.insert(0, "Niezapisana")
                
                # Aktualizacja interfejsu
                self.battle_combo.config(values=self.battle_names)
                self.battle_var.set("Niezapisana")
                self.current_battle = "Niezapisana"
                
                self.update_battle_stats()
                self.update_battle_history_display()
                
                messagebox.showinfo("Sukces", f"Rejestr bitew wczytany z: {filename}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać rejestru: {str(e)}")
    
    # === FUNKCJE DLA ZARZĄDZANIA JEDNOSTKAMI ===
    
    def save_units(self):
        """Zapisuje wykaz jednostek do pliku JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Zapisz wykaz jednostek",
                defaultextension=".json",
                filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")]
            )
            
            if filename:
                data = {
                    "units": self.units,
                    "saved_at": datetime.now().isoformat()
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Sukces", f"Wykaz jednostek zapisany do: {filename}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać wykazu: {str(e)}")
    
    def load_units(self):
        """Wczytuje wykaz jednostek z pliku JSON"""
        try:
            filename = filedialog.askopenfilename(
                title="Wczytaj wykaz jednostek",
                filetypes=[("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Sprawdzenie struktury danych
                if "units" not in data:
                    messagebox.showerror("Błąd", "Nieprawidłowy format pliku!")
                    return
                
                # Wczytanie danych
                self.units = data["units"]
                
                # Upewnienie się o prawidłowej strukturze
                if "własne" not in self.units:
                    self.units["własne"] = {}
                if "wroga" not in self.units:
                    self.units["wroga"] = {}
                
                # Dodanie pola historia_bitew do istniejących jednostek
                for side in ["własne", "wroga"]:
                    for unit_name, unit_data in self.units[side].items():
                        if "historia_bitew" not in unit_data:
                            unit_data["historia_bitew"] = []
                
                # Aktualizacja interfejsu
                self.update_units_combos()
                self.update_battle_units_combos()
                self.hide_unit_details()
                
                messagebox.showinfo("Sukces", f"Wykaz jednostek wczytany z: {filename}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać wykazu: {str(e)}")
    
    def create_new_unit(self):
        """Tworzy nową jednostkę"""
        # Pobranie wybranej strony z przycisków radio
        side = self.new_unit_side_var.get()
        
        # Pobranie batalionu (potrzebne do sprawdzania duplikatów)
        battalion_name = self.new_unit_battalion_var.get()
        battalion_id = None
        if battalion_name:
            for bid, data in self.battalions.items():
                if data['nazwa'] == battalion_name:
                    battalion_id = bid
                    break
        
        # Pobranie numeru jednostki
        try:
            unit_number = int(self.new_unit_number_var.get() or "1")
        except ValueError:
            messagebox.showwarning("Błąd", "Numer jednostki musi być liczbą!")
            return
        
        # Sprawdzenie czy jednostka o tym numerze już istnieje w tym batalionie
        for unit_id, unit_data in self.units[side].items():
            if (unit_data.get('numer', 1) == unit_number and 
                unit_data.get('batalion') == battalion_id):
                battalion_display = self.get_battalion_display_name(battalion_id) if battalion_id else "(bez batalionu)"
                messagebox.showwarning("Błąd", f"Jednostka o numerze {unit_number} już istnieje w batalionie {battalion_display}!")
                return
        
        # Pobranie typu jednostki
        unit_type = self.new_unit_type_var.get()
        
        
        # Generowanie ID jednostki
        unit_id = self.generate_random_id()
        
        # Tworzenie nowej jednostki z nowymi polami
        unit_data = {
            "id": unit_id,
            "numer": unit_number,
            "typ": unit_type,
            "batalion": battalion_id,
            "liczba_ludzi": 150,
            "doświadczenie": 0,
            "zapasy": 3,
            "liczba_zwycięstw": 0,
            "liczba_uzupełnień": 0,
            "strona": side,
            "historia_bitew": []
        }
        
        # Dodanie jednostki
        self.units[side][unit_id] = unit_data
        
        
        # Aktualizacja interfejsu
        self.update_units_combos()
        
        # Automatyczne wybranie utworzonej jednostki
        self.current_unit = unit_id
        self.current_unit_side = side
        display_name = self.get_unit_display_name(unit_id, side)
        if side == "własne":
            self.own_units_var.set(display_name)
            self.enemy_units_var.set("")
        else:
            self.enemy_units_var.set(display_name)
            self.own_units_var.set("")
        
        self.show_unit_details()
        
        # Automatyczne zwiększenie numeru dla następnej jednostki (zachowaj batalion)
        self.new_unit_number_var.set(str(unit_number + 1))
        
        messagebox.showinfo("Sukces", f"Utworzono jednostkę: {display_name}")
    
    def on_unit_selected(self, side):
        """Obsługuje wybór jednostki"""
        if side == "własne":
            display_name = self.own_units_var.get()
            self.enemy_units_var.set("")  # Wyczyść drugą stronę
        else:
            display_name = self.enemy_units_var.get()
            self.own_units_var.set("")  # Wyczyść drugą stronę
        
        if display_name:
            # Znajdź unit_id na podstawie nazwy wyświetlanej
            unit_id = None
            for uid, unit_data in self.units[side].items():
                if self.get_unit_display_name(uid, side) == display_name:
                    unit_id = uid
                    break
            
            if unit_id:
                self.current_unit = unit_id
                self.current_unit_side = side
                self.show_unit_details()
            else:
                self.hide_unit_details()
        else:
            self.hide_unit_details()
    
    def update_units_combos(self):
        """Aktualizuje zawartość comboboxów jednostek"""
        # Twórz listy nazw do wyświetlania
        own_units_display = [self.get_unit_display_name(unit_id, "własne") for unit_id in self.units["własne"].keys()]
        enemy_units_display = [self.get_unit_display_name(unit_id, "wroga") for unit_id in self.units["wroga"].keys()]
        
        self.own_units_combo.config(values=own_units_display)
        self.enemy_units_combo.config(values=enemy_units_display)
    
    def show_unit_details(self):
        """Pokazuje szczegóły wybranej jednostki"""
        if not self.current_unit or self.current_unit_side not in self.units:
            return
        
        if self.current_unit not in self.units[self.current_unit_side]:
            return
        
        # Pokaż frame szczegółów
        self.unit_details_frame.grid(row=4, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(10, 0))
        
        # Uaktualnij tytuł
        display_name = self.get_unit_display_name(self.current_unit, self.current_unit_side)
        self.unit_details_frame.config(text=f"Szczegóły: {display_name} ({self.current_unit_side})")
        
        # Usuń poprzednie contentery jeśli istnieją
        for widget in self.unit_details_frame.winfo_children():
            widget.destroy()
        
        unit_data = self.units[self.current_unit_side][self.current_unit]
        
        # Numer jednostki
        row = 0
        ttk.Label(self.unit_details_frame, text="Numer:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5))
        self.unit_number_var = tk.StringVar(value=str(unit_data.get("numer", 1)))
        self.unit_number_entry = ttk.Entry(self.unit_details_frame, textvariable=self.unit_number_var, width=8)
        self.unit_number_entry.grid(row=row, column=1, sticky=tk.W, padx=(0, 5))
        self.unit_number_entry.bind('<KeyRelease>', self.on_unit_data_change)
        
        # Typ jednostki
        row += 1
        ttk.Label(self.unit_details_frame, text="Typ:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_type_var = tk.StringVar(value=unit_data.get("typ", "kompania"))
        unit_type_detail_frame = ttk.Frame(self.unit_details_frame)
        unit_type_detail_frame.grid(row=row, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Radiobutton(unit_type_detail_frame, text="Komp.", variable=self.unit_type_var, value="kompania", command=self.on_unit_data_change).grid(row=0, column=0)
        ttk.Radiobutton(unit_type_detail_frame, text="Grupa", variable=self.unit_type_var, value="grupa", command=self.on_unit_data_change).grid(row=0, column=1, padx=(10, 0))
        
        # Batalion
        row += 1
        ttk.Label(self.unit_details_frame, text="Batalion:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        battalion_id = unit_data.get("batalion", None)
        battalion_name = ""
        if battalion_id and battalion_id in self.battalions:
            battalion_name = self.battalions[battalion_id]['nazwa']
        self.unit_battalion_var = tk.StringVar(value=battalion_name)
        self.unit_battalion_combo = ttk.Combobox(self.unit_details_frame, textvariable=self.unit_battalion_var, 
                                                values=[''] + [data['nazwa'] for data in self.battalions.values()], 
                                                state="readonly", width=12)
        self.unit_battalion_combo.grid(row=row, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_battalion_combo.bind('<<ComboboxSelected>>', self.on_unit_data_change)
        
        
        # Liczba ludzi (format X/150)
        row += 1
        ttk.Label(self.unit_details_frame, text="Ludzie:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        people_frame = ttk.Frame(self.unit_details_frame)
        people_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=(0, 5), pady=(5, 0))
        
        self.unit_people_var = tk.StringVar(value=str(unit_data["liczba_ludzi"]))
        self.unit_people_entry = ttk.Entry(people_frame, textvariable=self.unit_people_var, width=5)
        self.unit_people_entry.grid(row=0, column=0)
        self.unit_people_entry.bind('<KeyRelease>', self.on_unit_data_change)
        ttk.Label(people_frame, text="/150", font=("Arial", 9)).grid(row=0, column=1, padx=(2, 0))
        
        # Doświadczenie
        row += 1
        ttk.Label(self.unit_details_frame, text="Doświadczenie:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_exp_var = tk.StringVar(value=str(unit_data["doświadczenie"]))
        self.unit_exp_entry = ttk.Entry(self.unit_details_frame, textvariable=self.unit_exp_var, width=5)
        self.unit_exp_entry.grid(row=row, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_exp_entry.bind('<KeyRelease>', self.on_unit_data_change)
        
        # Zapasy (format X/3)
        row += 1
        ttk.Label(self.unit_details_frame, text="Zapasy:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        supplies_frame = ttk.Frame(self.unit_details_frame)
        supplies_frame.grid(row=row, column=1, sticky=tk.W+tk.E, padx=(0, 5), pady=(5, 0))
        
        self.unit_supplies_var = tk.StringVar(value=str(unit_data["zapasy"]))
        self.unit_supplies_entry = ttk.Entry(supplies_frame, textvariable=self.unit_supplies_var, width=5)
        self.unit_supplies_entry.grid(row=0, column=0)
        self.unit_supplies_entry.bind('<KeyRelease>', self.on_unit_data_change)
        ttk.Label(supplies_frame, text="/3", font=("Arial", 9)).grid(row=0, column=1, padx=(2, 0))
        
        # Liczba zwycięstw
        row += 1
        ttk.Label(self.unit_details_frame, text="Zwycięstwa:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_victories_var = tk.StringVar(value=str(unit_data["liczba_zwycięstw"]))
        self.unit_victories_entry = ttk.Entry(self.unit_details_frame, textvariable=self.unit_victories_var, width=5)
        self.unit_victories_entry.grid(row=row, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_victories_entry.bind('<KeyRelease>', self.on_unit_data_change)
        
        # Liczba uzupełnień
        row += 1
        ttk.Label(self.unit_details_frame, text="Uzupełnienia:", font=("Arial", 9)).grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_reinforcements_var = tk.StringVar(value=str(unit_data["liczba_uzupełnień"]))
        self.unit_reinforcements_entry = ttk.Entry(self.unit_details_frame, textvariable=self.unit_reinforcements_var, width=5)
        self.unit_reinforcements_entry.grid(row=row, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.unit_reinforcements_entry.bind('<KeyRelease>', self.on_unit_data_change)
        
        # Przyciski wyboru strony na dole
        row += 1
        side_buttons_frame = ttk.Frame(self.unit_details_frame)
        side_buttons_frame.grid(row=row, column=0, columnspan=2, pady=(10, 5))
        
        self.unit_side_var = tk.StringVar(value=unit_data.get("strona", self.current_unit_side))
        ttk.Radiobutton(side_buttons_frame, text="Swoje", variable=self.unit_side_var, value="własne", command=self.on_unit_side_change).grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(side_buttons_frame, text="Wróg", variable=self.unit_side_var, value="wroga", command=self.on_unit_side_change).grid(row=0, column=1, padx=(10, 0))
        
        # Przyciski na dole
        row += 1
        buttons_bottom_frame = ttk.Frame(self.unit_details_frame)
        buttons_bottom_frame.grid(row=row, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(buttons_bottom_frame, text="Eksportuj dane", command=self.export_unit_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_bottom_frame, text="📋", command=lambda unit_data=unit_data: self.show_unit_battle_history(unit_data), width=3).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(buttons_bottom_frame, text="🗑️", command=lambda unit_data=unit_data: self.delete_unit(unit_data), width=3).pack(side=tk.LEFT, padx=(5, 0))
    
    def delete_unit(self, unit_data):
        """Usuwa jednostkę"""
        unit_id = unit_data['id']
        unit_side = unit_data['strona']
        display_name = self.get_unit_display_name(unit_id, unit_side)
        
        # Potwierdzenie usunięcia
        if not messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć jednostkę '{display_name}'?\n\nTa operacja jest nieodwracalna!"):
            return
        
        # Sprawdź czy jednostka nie uczestniczy w bitwie
        participating_in_side1 = any(u['name'] == unit_id for u in self.participating_units["strona1"])
        participating_in_side2 = any(u['name'] == unit_id for u in self.participating_units["strona2"])
        
        if participating_in_side1 or participating_in_side2:
            messagebox.showwarning("Błąd", "Nie można usunąć jednostki która uczestniczy w bitwie!\nPierw zresetuj jednostki biorące udział w bitwie.")
            return
        
        # Historia jednostki zostanie usunięta wraz z jednostką
        
        # Usuń jednostkę
        del self.units[unit_side][unit_id]
        
        # Ukryj szczegóły
        self.hide_unit_details()
        
        # Zapisz zmiany
        self.save_units()
        
        # Aktualizuj wyświetlanie
        self.update_units_combos()
        self.update_battle_units_combos()
        
        messagebox.showinfo("Sukces", f"Jednostka '{display_name}' została usunięta.")
    
    def hide_unit_details(self):
        """Ukrywa szczegóły jednostki"""
        self.unit_details_frame.grid_remove()
        self.current_unit = None
        self.current_unit_side = "własne"
    
    def on_unit_data_change(self, event=None):
        """Obsługuje zmiany danych jednostki"""
        if not self.current_unit or self.current_unit_side not in self.units:
            return
        
        if self.current_unit not in self.units[self.current_unit_side]:
            return
        
        try:
            # Aktualizacja danych jednostki
            unit_data = self.units[self.current_unit_side][self.current_unit]
            
            # Aktualizacja numeru
            if hasattr(self, 'unit_number_var'):
                numer = int(self.unit_number_var.get() or 1)
                unit_data["numer"] = numer
            
            # Aktualizacja typu
            if hasattr(self, 'unit_type_var'):
                unit_data["typ"] = self.unit_type_var.get()
            
            # Aktualizacja batalionu
            if hasattr(self, 'unit_battalion_var'):
                battalion_name = self.unit_battalion_var.get()
                battalion_id = None
                if battalion_name:
                    for bid, data in self.battalions.items():
                        if data['nazwa'] == battalion_name:
                            battalion_id = bid
                            break
                unit_data["batalion"] = battalion_id
            
            # Aktualizuj wyświetlaną nazwę w interfejsie
            new_display_name = self.get_unit_display_name(self.current_unit, self.current_unit_side)
            if self.current_unit_side == "własne":
                self.own_units_var.set(new_display_name)
            else:
                self.enemy_units_var.set(new_display_name)
            
            # Aktualizuj tytuł szczegółów
            self.unit_details_frame.config(text=f"Szczegóły: {new_display_name} ({self.current_unit_side})")
            
            # Aktualizuj comboboxy
            self.update_units_combos()
            
            # Liczba ludzi (max 150)
            if hasattr(self, 'unit_people_var'):
                people = int(self.unit_people_var.get() or 0)
                people = max(0, min(150, people))
                unit_data["liczba_ludzi"] = people
                self.unit_people_var.set(str(people))
            
            # Doświadczenie
            if hasattr(self, 'unit_exp_var'):
                exp = int(self.unit_exp_var.get() or 0)
                unit_data["doświadczenie"] = exp
            
            # Zapasy (max 3)
            if hasattr(self, 'unit_supplies_var'):
                supplies = int(self.unit_supplies_var.get() or 0)
                supplies = max(0, min(3, supplies))
                unit_data["zapasy"] = supplies
                self.unit_supplies_var.set(str(supplies))
            
            # Zwycięstwa
            if hasattr(self, 'unit_victories_var'):
                victories = int(self.unit_victories_var.get() or 0)
                victories = max(0, victories)
                unit_data["liczba_zwycięstw"] = victories
            
            # Uzupełnienia
            if hasattr(self, 'unit_reinforcements_var'):
                reinforcements = int(self.unit_reinforcements_var.get() or 0)
                reinforcements = max(0, reinforcements)
                unit_data["liczba_uzupełnień"] = reinforcements
            
        except ValueError:
            # Ignoruj błędy konwersji podczas wpisywania
            pass
        except KeyError:
            # Ignoruj błędy gdy jednostka nie istnieje (może być w trakcie przenoszenia)
            pass
    
    def export_unit_data(self):
        """Eksportuje dane jednostki w określonym formacie"""
        if not self.current_unit or self.current_unit_side not in self.units:
            return
        
        if self.current_unit not in self.units[self.current_unit_side]:
            return
        
        unit_data = self.units[self.current_unit_side][self.current_unit]
        
        # Format doświadczenia
        exp = unit_data["doświadczenie"]
        exp_text = ""
        if exp > 0:
            exp_text = "+" * exp
        elif exp == -1:
            exp_text = "-"
        elif exp == -2:
            exp_text = "--"
        elif exp < -2:
            exp_text = "-" * abs(exp)
        # Dla exp == 0 nie dodawać nic
        
        # Formatting zgodnie z wymaganiami
        export_text = f"Doświadczenie = {exp_text} Wx{unit_data['liczba_zwycięstw']} Ux{unit_data['liczba_uzupełnień']}\n"
        export_text += f"Ludzie = {unit_data['liczba_ludzi']}/150\n"
        export_text += f"Zapasy = {unit_data['zapasy']}/3"
        
        # Skopiuj do schowka (prostym sposobem - pokaż w oknie do kopiowania)
        export_window = tk.Toplevel(self.root)
        export_window.title(f"Eksport: {self.current_unit}")
        export_window.geometry("400x200")
        export_window.resizable(False, False)
        
        ttk.Label(export_window, text="Skopiuj poniższe dane:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        text_widget = tk.Text(export_window, height=6, width=40, font=("Arial", 10))
        text_widget.pack(pady=(5, 10), padx=10, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, export_text)
        text_widget.config(state=tk.DISABLED)
        
        # Przycisk zamknij
        ttk.Button(export_window, text="Zamknij", command=export_window.destroy).pack(pady=(0, 10))
        
        # Zaznacz wszystko w text widget
        text_widget.config(state=tk.NORMAL)
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.focus()
    
    # === FUNKCJE DLA WYBORU JEDNOSTEK DO BITWY ===
    
    def on_unit_type_change(self):
        """Obsługuje zmianę typu jednostki (własne/wroga/brak)"""
        # Aktualizacja comboboxów dla strony 1
        unit_type1 = self.unit_side1_type_var.get()
        if unit_type1 == "brak":
            self.unit_side1_combo.config(values=[], state="disabled")
            self.unit_side1_var.set("")
            self.selected_unit_side1 = None
        else:
            # Stwórz mapę ID -> sformatowana nazwa i lista sformatowanych nazw
            units_display_names = []
            self.unit_side1_id_to_display = {}
            for unit_id in self.units[unit_type1].keys():
                display_name = self.get_unit_display_name(unit_id, unit_type1)
                units_display_names.append(display_name)
                self.unit_side1_id_to_display[display_name] = unit_id
            
            self.unit_side1_combo.config(values=units_display_names, state="readonly")
            self.unit_side1_var.set("")
            self.selected_unit_side1 = None
        
        # Aktualizacja comboboxów dla strony 2
        unit_type2 = self.unit_side2_type_var.get()
        if unit_type2 == "brak":
            self.unit_side2_combo.config(values=[], state="disabled")
            self.unit_side2_var.set("")
            self.selected_unit_side2 = None
        else:
            # Stwórz mapę ID -> sformatowana nazwa i lista sformatowanych nazw
            units_display_names = []
            self.unit_side2_id_to_display = {}
            for unit_id in self.units[unit_type2].keys():
                display_name = self.get_unit_display_name(unit_id, unit_type2)
                units_display_names.append(display_name)
                self.unit_side2_id_to_display[display_name] = unit_id
            
            self.unit_side2_combo.config(values=units_display_names, state="readonly")
            self.unit_side2_var.set("")
            self.selected_unit_side2 = None
        
        # Zapisz typy jednostek
        self.unit_side1_type = unit_type1
        self.unit_side2_type = unit_type2
        
        # NIE resetuj pól doświadczenia i liczby ludzi - tylko gdy wybierze się konkretną jednostkę
    
    def on_battle_unit_selected(self, event=None):
        """Obsługuje wybór konkretnej jednostki do bitwy"""
        if not event:
            return
            
        # Strona 1
        if hasattr(event, 'widget') and event.widget == self.unit_side1_combo:
            display_name = self.unit_side1_var.get()
            if display_name and self.unit_side1_type != "brak":
                # Konwertuj display name na ID jednostki
                if hasattr(self, 'unit_side1_id_to_display') and display_name in self.unit_side1_id_to_display:
                    unit_id = self.unit_side1_id_to_display[display_name]
                    self.selected_unit_side1 = unit_id
                    # Automatyczne wypełnienie danych z jednostki
                    unit_data = self.units[self.unit_side1_type][unit_id]
                    self.dice1_exp_var.set(unit_data["doświadczenie"])
                    
                    # Ustaw liczbę ludzi tylko jeśli strona nie jest zablokowana
                    if not self.side1_locked:
                        self.dice1_people_var.set(str(unit_data["liczba_ludzi"]))
                    
                    self.update_exp_bonuses_display()
        
        # Strona 2
        if hasattr(event, 'widget') and event.widget == self.unit_side2_combo:
            display_name = self.unit_side2_var.get()
            if display_name and self.unit_side2_type != "brak":
                # Konwertuj display name na ID jednostki
                if hasattr(self, 'unit_side2_id_to_display') and display_name in self.unit_side2_id_to_display:
                    unit_id = self.unit_side2_id_to_display[display_name]
                    self.selected_unit_side2 = unit_id
                    # Automatyczne wypełnienie danych z jednostki
                    unit_data = self.units[self.unit_side2_type][unit_id]
                    self.dice2_exp_var.set(unit_data["doświadczenie"])
                    
                    # Ustaw liczbę ludzi tylko jeśli strona nie jest zablokowana
                    if not self.side2_locked:
                        self.dice2_people_var.set(str(unit_data["liczba_ludzi"]))
                    
                    self.update_exp_bonuses_display()
    
    def update_battle_units_combos(self):
        """Aktualizuje comboboxi wyboru jednostek do bitwy po załadowaniu danych"""
        # Combobox dla strony 1
        if hasattr(self, 'unit_side1_combo'):
            if self.unit_side1_type == "brak":
                self.unit_side1_combo.config(values=[], state="disabled")
            else:
                # Pobierz wszystkie jednostki z sformatowanymi nazwami i ukryj te, które już uczestniczą
                all_unit_ids = list(self.units[self.unit_side1_type].keys())
                participating_ids = [self.get_unit_id(u) for u in self.participating_units["strona1"]]
                available_unit_ids = [unit_id for unit_id in all_unit_ids if unit_id not in participating_ids]
                
                # Stwórz listę sformatowanych nazw i mapę
                units_display_names = []
                self.unit_side1_id_to_display = {}
                for unit_id in available_unit_ids:
                    display_name = self.get_unit_display_name(unit_id, self.unit_side1_type)
                    units_display_names.append(display_name)
                    self.unit_side1_id_to_display[display_name] = unit_id
                
                self.unit_side1_combo.config(values=units_display_names, state="readonly")
        
        # Combobox dla strony 2
        if hasattr(self, 'unit_side2_combo'):
            if self.unit_side2_type == "brak":
                self.unit_side2_combo.config(values=[], state="disabled")
            else:
                # Pobierz wszystkie jednostki z sformatowanymi nazwami i ukryj te, które już uczestniczą
                all_unit_ids = list(self.units[self.unit_side2_type].keys())
                participating_ids = [self.get_unit_id(u) for u in self.participating_units["strona2"]]
                available_unit_ids = [unit_id for unit_id in all_unit_ids if unit_id not in participating_ids]
                
                # Stwórz listę sformatowanych nazw i mapę
                units_display_names = []
                self.unit_side2_id_to_display = {}
                for unit_id in available_unit_ids:
                    display_name = self.get_unit_display_name(unit_id, self.unit_side2_type)
                    units_display_names.append(display_name)
                    self.unit_side2_id_to_display[display_name] = unit_id
                
                self.unit_side2_combo.config(values=units_display_names, state="readonly")
    
    def on_unit_side_change(self, event=None):
        """Obsługuje zmianę strony jednostki w szczegółach"""
        if not self.current_unit or self.current_unit_side not in self.units:
            return
        
        if self.current_unit not in self.units[self.current_unit_side]:
            return
        
        new_side = self.unit_side_var.get()
        old_side = self.current_unit_side
        
        if new_side != old_side:
            # Sprawdź czy nazwa już istnieje po drugiej stronie
            if self.current_unit in self.units[new_side]:
                messagebox.showwarning("Błąd", f"Jednostka o nazwie '{self.current_unit}' już istnieje po stronie '{new_side}'!")
                self.unit_side_var.set(old_side)  # Przywróć poprzednią wartość
                return
            
            # Przenieś jednostkę
            unit_data = self.units[old_side][self.current_unit]
            unit_data["strona"] = new_side
            
            del self.units[old_side][self.current_unit]
            self.units[new_side][self.current_unit] = unit_data
            
            # Aktualizuj stan
            self.current_unit_side = new_side
            
            # Aktualizuj interfejs
            self.update_units_combos()
            self.update_battle_units_combos()
            
            # Zaktualizuj wybór w głównych comboboxach
            if new_side == "własne":
                self.own_units_var.set(self.current_unit)
                self.enemy_units_var.set("")
            else:
                self.enemy_units_var.set(self.current_unit)
                self.own_units_var.set("")
            
            # Zaktualizuj tytuł szczegółów
            self.unit_details_frame.config(text=f"Szczegóły: {self.current_unit} ({new_side})")
            
            messagebox.showinfo("Sukces", f"Jednostka '{self.current_unit}' przeniesiona na stronę '{new_side}'")
    
    def get_all_participating_units(self, side_number):
        """Pomocnicza funkcja do zbierania wszystkich jednostek uczestniczących po stronie"""
        if side_number == 1:
            all_units = list(self.participating_units["strona1"])
            if self.selected_unit_side1 and self.unit_side1_type != "brak":
                if not any(self.get_unit_id(u) == self.selected_unit_side1 for u in all_units):
                    unit_data = self.units[self.unit_side1_type][self.selected_unit_side1]
                    all_units.append({
                        'id': self.selected_unit_side1,
                        'name': self.selected_unit_side1,
                        'people': unit_data["liczba_ludzi"],
                        'side': self.unit_side1_type
                    })
        else:
            all_units = list(self.participating_units["strona2"])
            if self.selected_unit_side2 and self.unit_side2_type != "brak":
                if not any(self.get_unit_id(u) == self.selected_unit_side2 for u in all_units):
                    unit_data = self.units[self.unit_side2_type][self.selected_unit_side2]
                    all_units.append({
                        'id': self.selected_unit_side2,
                        'name': self.selected_unit_side2,
                        'people': unit_data["liczba_ludzi"],
                        'side': self.unit_side2_type
                    })
        return all_units
    
    def get_unit_id(self, unit):
        """Pomocnicza funkcja do pobierania ID jednostki z obiektu"""
        return unit.get('id', unit.get('name', ''))
    
    def update_unit_stats_after_battle(self, dice1_final, dice2_final):
        """Aktualizuje statystyki jednostek po bitwie (tylko zwycięstwa, straty obsługuje distribute_losses_among_units)"""
        side1_won = dice1_final > 1 and dice1_final > dice2_final
        side2_won = dice2_final > 1 and dice2_final > dice1_final
        
        # Debug info z sformatowanymi nazwami
        all_side1_units = self.get_all_participating_units(1)
        all_side2_units = self.get_all_participating_units(2)
        
        side1_names = [self.get_unit_display_name(self.get_unit_id(u), u.get('side', '')) for u in all_side1_units]
        side2_names = [self.get_unit_display_name(self.get_unit_id(u), u.get('side', '')) for u in all_side2_units]
        
        
        # Aktualizuj zwycięstwa dla strony 1
        for unit in all_side1_units:
            if side1_won:
                self.update_unit_victories(self.get_unit_id(unit))
        
        # Aktualizuj zwycięstwa dla strony 2
        for unit in all_side2_units:
            if side2_won:
                self.update_unit_victories(self.get_unit_id(unit))
        
        # Aktualizacja interfejsu
        if self.current_unit:
            self.show_unit_details()
        self.update_battle_units_combos()
    
    def update_unit_victories(self, unit_id):
        """Aktualizuje liczbę zwycięstw jednostki"""
        for side_name in ['własne', 'wroga']:
            if unit_id in self.units[side_name]:
                self.units[side_name][unit_id]["liczba_zwycięstw"] += 1
                break
    
    def distribute_losses_among_units(self):
        """Rozdziela straty między jednostkami uczestniczącymi w bitwie"""
        self.distribute_losses_for_side(1)
        self.distribute_losses_for_side(2)
    
    def distribute_losses_for_side(self, side_number):
        """Rozdziela straty dla określonej strony"""
        all_units = self.get_all_participating_units(side_number)
        
        if not all_units:
            return
            
        if side_number == 1:
            total_losses = self.dice1_people_original - self.dice1_people_result
            participating_key = "strona1"
        else:
            total_losses = self.dice2_people_original - self.dice2_people_result
            participating_key = "strona2"
            
        if total_losses <= 0:
            return
            
        losses_per_unit = total_losses // len(all_units)
        remainder = total_losses % len(all_units)
        
        for i, unit in enumerate(all_units):
            losses = losses_per_unit
            if i < remainder:
                losses += 1
            
            unit_id = self.get_unit_id(unit)
            
            # Aktualizuj w głównym słowniku jednostek
            for side_name in ['własne', 'wroga']:
                if unit_id in self.units[side_name]:
                    new_people = max(0, self.units[side_name][unit_id]['liczba_ludzi'] - losses)
                    self.units[side_name][unit_id]['liczba_ludzi'] = new_people
                    
                    # Aktualizuj także w participating_units jeśli tam jest
                    for pu in self.participating_units[participating_key]:
                        if self.get_unit_id(pu) == unit_id:
                            pu['people'] = new_people
                            break
                    break
    
    def add_more_units_side(self, side_number):
        """Dodaje jednostkę do udziału w bitwie dla określonej strony"""
        if side_number == 1:
            # Strona 1
            if self.unit_side1_type == "brak" or not hasattr(self, 'selected_unit_side1') or not self.selected_unit_side1:
                messagebox.showwarning("Błąd", "Wybierz jednostkę dla strony 1!")
                return
            
            # Pobierz rzeczywistą liczbę ludzi z jednostki
            unit_data = self.units[self.unit_side1_type][self.selected_unit_side1]
            unit_people = unit_data["liczba_ludzi"]
            
            unit_info = {
                'id': self.selected_unit_side1,
                'name': self.selected_unit_side1,
                'people': unit_people,
                'side': self.unit_side1_type
            }
            
            # Sprawdź czy jednostka już nie uczestniczy
            existing = [u for u in self.participating_units["strona1"] if self.get_unit_id(u) == unit_info['id']]
            if existing:
                messagebox.showwarning("Błąd", "Ta jednostka już uczestniczy w bitwie!")
                return
            
            # Dodaj jednostkę
            self.participating_units["strona1"].append(unit_info)
            
            # Zwiększ liczbę ludzi tylko jeśli to nie pierwsza jednostka
            # (pierwsza jednostka już ma swoją liczbę ludzi w polu)
            if len(self.participating_units["strona1"]) > 1:
                current_people = int(self.dice1_people_var.get() or "0")
                new_total = current_people + unit_people
                self.dice1_people_var.set(str(new_total))
            else:
                # Dla pierwszej jednostki zostaw obecną wartość
                new_total = int(self.dice1_people_var.get() or "0")
            
            # Zablokuj automatyczne uzupełnianie dla strony 1
            self.side1_locked = True
            
            # Reset modyfikatorów dla strony 1
            self.dice1_exp_var.set(0)
            
            # Wyczyść wybór jednostki dla strony 1
            self.unit_side1_var.set("")
            self.selected_unit_side1 = None
            
            # Aktualizuj combobox - ukryj dodane jednostki
            self.update_battle_units_combos()
            
            messagebox.showinfo("Sukces", f"Jednostka dodana do strony 1! (Dodano: {unit_people}, Łącznie: {new_total})")
            
        elif side_number == 2:
            # Strona 2
            if self.unit_side2_type == "brak" or not hasattr(self, 'selected_unit_side2') or not self.selected_unit_side2:
                messagebox.showwarning("Błąd", "Wybierz jednostkę dla strony 2!")
                return
            
            # Pobierz rzeczywistą liczbę ludzi z jednostki
            unit_data = self.units[self.unit_side2_type][self.selected_unit_side2]
            unit_people = unit_data["liczba_ludzi"]
            
            unit_info = {
                'id': self.selected_unit_side2,
                'name': self.selected_unit_side2,
                'people': unit_people,
                'side': self.unit_side2_type
            }
            
            # Sprawdź czy jednostka już nie uczestniczy
            existing = [u for u in self.participating_units["strona2"] if self.get_unit_id(u) == unit_info['id']]
            if existing:
                messagebox.showwarning("Błąd", "Ta jednostka już uczestniczy w bitwie!")
                return
            
            # Dodaj jednostkę
            self.participating_units["strona2"].append(unit_info)
            
            # Zwiększ liczbę ludzi tylko jeśli to nie pierwsza jednostka
            # (pierwsza jednostka już ma swoją liczbę ludzi w polu)
            if len(self.participating_units["strona2"]) > 1:
                current_people = int(self.dice2_people_var.get() or "0")
                new_total = current_people + unit_people
                self.dice2_people_var.set(str(new_total))
            else:
                # Dla pierwszej jednostki zostaw obecną wartość
                new_total = int(self.dice2_people_var.get() or "0")
            
            # Zablokuj automatyczne uzupełnianie dla strony 2
            self.side2_locked = True
            
            # Reset modyfikatorów dla strony 2
            self.dice2_exp_var.set(0)
            
            # Wyczyść wybór jednostki dla strony 2
            self.unit_side2_var.set("")
            self.selected_unit_side2 = None
            
            # Aktualizuj combobox - ukryj dodane jednostki
            self.update_battle_units_combos()
            
            messagebox.showinfo("Sukces", f"Jednostka dodana do strony 2! (Dodano: {unit_people}, Łącznie: {new_total})")
        
        # Aktualizuj wyświetlanie
        self.update_units_display()
        self.update_exp_bonuses_display()
        self.update_battle_units_combos()
    
    def reset_participating_units(self):
        """Resetuje jednostki biorące udział w bitwie"""
        self.participating_units = {"strona1": [], "strona2": []}
        
        # Odblokuj automatyczne uzupełnianie
        self.side1_locked = False
        self.side2_locked = False
        
        # Reset wszystkich pól
        self.dice1_exp_var.set(0)
        self.dice2_exp_var.set(0)
        self.dice1_people_var.set("0")
        self.dice2_people_var.set("0")
        
        # Wyczyść wybory jednostek
        self.unit_side1_var.set("")
        self.unit_side2_var.set("")
        self.selected_unit_side1 = None
        self.selected_unit_side2 = None
        
        # Aktualizuj wyświetlanie
        self.update_units_display()
        self.update_exp_bonuses_display()
        self.update_battle_units_combos()
    
    def update_units_display(self):
        """Aktualizuje wyświetlanie ikon jednostek"""
        # Ikon dla strony 1
        if hasattr(self, 'side1_units_label'):
            if self.participating_units["strona1"]:
                icons = "🪖" * len(self.participating_units["strona1"])
                total_people = sum(u['people'] for u in self.participating_units["strona1"])
                self.side1_units_label.config(text=f"{icons} ({total_people} ludzi)")
            else:
                self.side1_units_label.config(text="")
        
        # Ikon dla strony 2
        if hasattr(self, 'side2_units_label'):
            if self.participating_units["strona2"]:
                icons = "🪖" * len(self.participating_units["strona2"])
                total_people = sum(u['people'] for u in self.participating_units["strona2"])
                self.side2_units_label.config(text=f"{icons} ({total_people} ludzi)")
            else:
                self.side2_units_label.config(text="")
    
    def add_to_unit_battle_history(self, dice1_final, dice2_final):
        """Dodaje informacje o bitwie do historii jednostek"""
        import datetime
        
        # Zbierz ID jednostek (do operacji na danych) i nazwy (do wyświetlania)
        side1_unit_ids = [u.get('id', u.get('name', '')) for u in self.participating_units["strona1"]]
        side2_unit_ids = [u.get('id', u.get('name', '')) for u in self.participating_units["strona2"]]
        
        # Nazwy do wyświetlania w historii
        side1_display_names = []
        for u in self.participating_units["strona1"]:
            unit_id = u.get('id', u.get('name', ''))
            side_name = u.get('side', '')
            display_name = self.get_unit_display_name(unit_id, side_name) if unit_id and side_name else u.get('name', unit_id)
            side1_display_names.append(display_name)
            
        side2_display_names = []
        for u in self.participating_units["strona2"]:
            unit_id = u.get('id', u.get('name', ''))
            side_name = u.get('side', '')
            display_name = self.get_unit_display_name(unit_id, side_name) if unit_id and side_name else u.get('name', unit_id)
            side2_display_names.append(display_name)
        
        # Dodaj jednostki wybrane normalnie
        if self.selected_unit_side1 and self.unit_side1_type != "brak":
            if self.selected_unit_side1 not in side1_unit_ids:
                side1_unit_ids.append(self.selected_unit_side1)
                side1_display_names.append(self.get_unit_display_name(self.selected_unit_side1, self.unit_side1_type))
        
        if self.selected_unit_side2 and self.unit_side2_type != "brak":
            if self.selected_unit_side2 not in side2_unit_ids:
                side2_unit_ids.append(self.selected_unit_side2)
                side2_display_names.append(self.get_unit_display_name(self.selected_unit_side2, self.unit_side2_type))
        
        # Określ tryb walki - użyj poprawnych nazw zmiennych  
        side1_attacking = self.side1_attack_var.get()
        side2_attacking = self.side2_attack_var.get() 
        side1_in_motion = self.side1_motion_var.get()
        side2_in_motion = self.side2_motion_var.get()
        
        battle_info = {
            'data': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
            'wynik_kostki': None,
            'przeciwnik_kostka': None,
            'straty': 0,
            'zwyciestwo': False,
            'side1_units': side1_display_names,
            'side2_units': side2_display_names,
            'side1_attacking': side1_attacking,
            'side2_attacking': side2_attacking,
            'side1_in_motion': side1_in_motion,
            'side2_in_motion': side2_in_motion
        }
        
        # Pobierz wszystkie jednostki strony 1
        all_side1_units = self.get_all_participating_units(1)
        
        # Historia dla jednostek strony 1
        if all_side1_units:
            battle_info_side1 = battle_info.copy()
            battle_info_side1['wynik_kostki'] = dice1_final
            battle_info_side1['przeciwnik_kostka'] = dice2_final
            battle_info_side1['straty'] = max(0, self.dice1_people_original - self.dice1_people_result)
            battle_info_side1['zwyciestwo'] = dice1_final > dice2_final and dice1_final > 1
            
            # Rozdziel straty między jednostkami
            total_losses = battle_info_side1['straty']
            if len(all_side1_units) > 0:
                losses_per_unit = total_losses // len(all_side1_units) if total_losses > 0 else 0
                remainder = total_losses % len(all_side1_units) if total_losses > 0 else 0
                
                for i, unit in enumerate(all_side1_units):
                    unit_losses = losses_per_unit
                    if i < remainder:
                        unit_losses += 1
                    
                    unit_battle_info = battle_info_side1.copy()
                    unit_battle_info['straty'] = unit_losses
                    # Dodaj informacje specyficzne dla strony 1
                    unit_battle_info['friendly_units'] = side1_display_names
                    unit_battle_info['enemy_units'] = side2_display_names
                    
                    # Dodaj do historii jednostki
                    unit_id = self.get_unit_id(unit)
                    for side_name in ['własne', 'wroga']:
                        if unit_id in self.units[side_name]:
                            if 'historia_bitew' not in self.units[side_name][unit_id]:
                                self.units[side_name][unit_id]['historia_bitew'] = []
                            self.units[side_name][unit_id]['historia_bitew'].append(unit_battle_info)
                            break
        
        # Pobierz wszystkie jednostki strony 2
        all_side2_units = self.get_all_participating_units(2)
        
        # Historia dla jednostek strony 2
        if all_side2_units:
            battle_info_side2 = battle_info.copy()
            battle_info_side2['wynik_kostki'] = dice2_final
            battle_info_side2['przeciwnik_kostka'] = dice1_final
            battle_info_side2['straty'] = max(0, self.dice2_people_original - self.dice2_people_result)
            battle_info_side2['zwyciestwo'] = dice2_final > dice1_final and dice2_final > 1
            
            # Rozdziel straty między jednostkami
            total_losses = battle_info_side2['straty']
            if len(all_side2_units) > 0:
                losses_per_unit = total_losses // len(all_side2_units) if total_losses > 0 else 0
                remainder = total_losses % len(all_side2_units) if total_losses > 0 else 0
                
                for i, unit in enumerate(all_side2_units):
                    unit_losses = losses_per_unit
                    if i < remainder:
                        unit_losses += 1
                    
                    unit_battle_info = battle_info_side2.copy()
                    unit_battle_info['straty'] = unit_losses
                    # Dodaj informacje specyficzne dla strony 2
                    unit_battle_info['friendly_units'] = side2_display_names
                    unit_battle_info['enemy_units'] = side1_display_names
                    
                    # Dodaj do historii jednostki
                    unit_id = self.get_unit_id(unit)
                    for side_name in ['własne', 'wroga']:
                        if unit_id in self.units[side_name]:
                            if 'historia_bitew' not in self.units[side_name][unit_id]:
                                self.units[side_name][unit_id]['historia_bitew'] = []
                            self.units[side_name][unit_id]['historia_bitew'].append(unit_battle_info)
                            break
    
    def show_unit_battle_history(self, unit_data):
        """Pokazuje okienko z historią bitew jednostki"""
        # Upewnij się, że jednostka ma historię bitew
        if 'historia_bitew' not in unit_data:
            unit_data['historia_bitew'] = []
        
        # Utworzenie okna historii
        history_window = tk.Toplevel(self.root)
        display_name = self.get_unit_display_name(unit_data['id'], unit_data['strona'])
        history_window.title(f"Historia bitew: {display_name}")
        history_window.geometry("500x400")
        history_window.resizable(True, True)
        
        # Ramka główna
        main_frame = ttk.Frame(history_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        history_window.columnconfigure(0, weight=1)
        history_window.rowconfigure(0, weight=1)
        
        # Nagłówek
        display_name = self.get_unit_display_name(unit_data['id'], unit_data['strona'])
        header_label = ttk.Label(main_frame, text=f"Historia bitew: {display_name}", font=("Arial", 12, "bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Statystyki ogólne
        total_battles = len(unit_data['historia_bitew'])
        total_losses = sum(battle['straty'] for battle in unit_data['historia_bitew'])
        victories = sum(1 for battle in unit_data['historia_bitew'] if battle['zwyciestwo'])
        
        stats_text = f"Liczba bitew: {total_battles} | Zwycięstwa: {victories} | Łączne straty: {total_losses}"
        stats_label = ttk.Label(main_frame, text=stats_text, font=("Arial", 10))
        stats_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Przycisk do pokazania szczegółów
        ttk.Button(main_frame, text="Pokaż szczegóły bitew", 
                  command=lambda: self.show_detailed_battle_history(unit_data)).grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Przycisk zamknij
        ttk.Button(main_frame, text="Zamknij", command=history_window.destroy).grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def show_detailed_battle_history(self, unit_data):
        """Pokazuje szczegółową historię bitew w osobnym oknie"""
        details_window = tk.Toplevel(self.root)
        display_name = self.get_unit_display_name(unit_data['id'], unit_data['strona'])
        details_window.title(f"Szczegóły bitew: {display_name}")
        details_window.geometry("600x500")
        details_window.resizable(True, True)
        
        # Ramka główna
        main_frame = ttk.Frame(details_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        details_window.columnconfigure(0, weight=1)
        details_window.rowconfigure(0, weight=1)
        
        # Nagłówek  
        display_name = self.get_unit_display_name(unit_data['id'], unit_data['strona'])
        header_label = ttk.Label(main_frame, text=f"Szczegółowa historia: {display_name}", font=("Arial", 12, "bold"))
        header_label.grid(row=0, column=0, pady=(0, 10))
        
        # Tekst z historią
        history_frame = ttk.Frame(main_frame)
        history_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Scrollowany tekst
        history_text = tk.Text(history_frame, wrap=tk.WORD, height=20, width=70)
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=history_text.yview)
        history_text.configure(yscrollcommand=scrollbar.set)
        
        history_text.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        
        # Wypełnienie historii
        if not unit_data['historia_bitew']:
            history_text.insert(tk.END, "Brak historii bitew dla tej jednostki.\n")
        else:
            for i, battle in enumerate(reversed(unit_data['historia_bitew']), 1):
                victory_icon = " ⭐" if battle['zwyciestwo'] else ""
                
                # Nowy format z ofensywami jeśli są dostępne dane
                friendly_units = battle.get('friendly_units', [])
                enemy_units = battle.get('enemy_units', [])
                
                if friendly_units and enemy_units:
                    # Nowy format z nazwami jednostek i trybem bitwy
                    side_in_motion = battle.get('side1_in_motion', False) or battle.get('side2_in_motion', False)
                    side_attacking = battle.get('side1_attacking', False) or battle.get('side2_attacking', False)
                    
                    # Formatuj nazwy jednostek
                    friendly_name = friendly_units[0]
                    if len(friendly_units) > 1:
                        friendly_name += ", " + ", ".join(friendly_units[1:])
                        
                    enemy_name = enemy_units[0]
                    if len(enemy_units) > 1:
                        enemy_name += ", " + ", ".join(enemy_units[1:])
                    
                    # Określ typ bitwy
                    if side_in_motion:
                        battle_desc = f"Bitwa \"{friendly_name}\" z \"{enemy_name}\""
                    elif side_attacking:
                        # Sprawdź kto atakuje na podstawie wyników
                        if battle['wynik_kostki'] >= battle['przeciwnik_kostka']:
                            battle_desc = f"Ofensywa \"{friendly_name}\" na \"{enemy_name}\""
                        else:
                            battle_desc = f"Obrona \"{friendly_name}\" przed \"{enemy_name}\""
                    else:
                        battle_desc = f"Ofensywa \"{friendly_name}\" na \"{enemy_name}\""
                    
                    history_line = f"#{i}: {battle['data']}\n"
                    history_line += f"   {battle_desc}\n"
                    history_line += f"   Kostka: {battle['wynik_kostki']}{victory_icon} vs Przeciwnik: {battle['przeciwnik_kostka']}\n"
                    history_line += f"   Straty: {battle['straty']} ludzi\n\n"
                else:
                    # Stary format dla starych zapisów
                    history_line = f"#{i}: {battle['data']}\n"
                    history_line += f"   Kostka: {battle['wynik_kostki']}{victory_icon} vs Przeciwnik: {battle['przeciwnik_kostka']}\n"
                    history_line += f"   Straty: {battle['straty']} ludzi\n\n"
                
                history_text.insert(tk.END, history_line)
        
        history_text.config(state=tk.DISABLED)
        
        # Przycisk zamknij
        ttk.Button(main_frame, text="Zamknij", command=details_window.destroy).grid(row=2, column=0, pady=(10, 0))
        
        # Konfiguracja kolumn i wierszy
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)


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

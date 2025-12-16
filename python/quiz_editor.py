import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import shutil
from pathlib import Path
import sys

class QuizEditor:
    def __init__(self, root, mode="sentence"):
        self.root = root
        self.mode = mode  # "sentence" or "guess"
        self.root.title(f"📚 Quiz Editor - {'Sentence Quiz' if mode == 'sentence' else 'Guess Game'}")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        
        # Data
        self.data = {}
        self.current_category = None
        self.current_difficulty = None
        self.current_index = -1
        
        # Image preview
        self.blurred_preview = None
        self.original_preview = None
        
        # Paths
        self.base_path = Path(__file__).parent
        self.json_path = self.base_path / ("quiz_data.json" if mode == "sentence" else "guess_data.json")
        self.assets_path = self.base_path / "assets" / "guess_game"
        
        # Create assets folders if not exist
        if mode == "guess":
            (self.assets_path / "blurred").mkdir(parents=True, exist_ok=True)
            (self.assets_path / "original").mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.load_data()
        
        # Build UI
        self.build_ui()
        
        # Apply modern theme
        self.apply_theme()
        
    def apply_theme(self):
        """Apply modern theme colors"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TCombobox', fieldbackground='white', background='#3498DB')
        style.configure('TButton', background='#3498DB', foreground='white', padding=6)
        style.map('TButton', background=[('active', '#2980B9')])
        
    def load_data(self):
        """Load quiz data"""
        try:
            if self.json_path.exists():
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"[OK] Loaded data from {self.json_path}")
            else:
                if self.mode == "sentence":
                    self.data = {
                        "Present": {"easy": [], "medium": [], "hard": []},
                        "Past": {"easy": [], "medium": [], "hard": []},
                        "Future": {"easy": [], "medium": [], "hard": []},
                        "Past Future": {"easy": [], "medium": [], "hard": []}
                    }
                else:  # guess
                    self.data = []
                self.save_data()
                print(f"[OK] Created new data file: {self.json_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.data = {} if self.mode == "sentence" else []
    
    def save_data(self):
        """Save quiz data"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", "✅ Data saved successfully!")
            print(f"[OK] Data saved to {self.json_path}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
            return False
    
    def build_ui(self):
        """Build user interface"""
        if self.mode == "sentence":
            self.build_sentence_ui()
        else:
            self.build_guess_ui()
    
    def build_sentence_ui(self):
        """Build UI for sentence quiz editor"""
        # Top frame - Category & Difficulty selection
        top_frame = tk.Frame(self.root, bg="#2C3E50", pady=15)
        top_frame.pack(fill=tk.X)
        
        # Title
        title_label = tk.Label(top_frame, text="📝 SENTENCE QUIZ EDITOR", 
                              bg="#2C3E50", fg="white", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Selection frame
        select_frame = tk.Frame(top_frame, bg="#2C3E50")
        select_frame.pack()
        
        tk.Label(select_frame, text="Category:", bg="#2C3E50", fg="white", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        
        self.category_var = tk.StringVar(value="Present")
        category_menu = ttk.Combobox(select_frame, textvariable=self.category_var, 
                                     values=["Present", "Past", "Future", "Past Future"],
                                     state="readonly", width=15, font=("Arial", 10))
        category_menu.pack(side=tk.LEFT, padx=5)
        category_menu.bind("<<ComboboxSelected>>", lambda e: self.load_questions_list())
        
        tk.Label(select_frame, text="Difficulty:", bg="#2C3E50", fg="white", 
                font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(20, 5))
        
        self.difficulty_var = tk.StringVar(value="easy")
        difficulty_menu = ttk.Combobox(select_frame, textvariable=self.difficulty_var,
                                       values=["easy", "medium", "hard"],
                                       state="readonly", width=10, font=("Arial", 10))
        difficulty_menu.pack(side=tk.LEFT, padx=5)
        difficulty_menu.bind("<<ComboboxSelected>>", lambda e: self.load_questions_list())
        
        # Main container
        main_container = tk.Frame(self.root, bg="#ECF0F1")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Questions list
        left_panel = tk.Frame(main_container, width=280, bg="#ECF0F1")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # List header
        list_header = tk.Frame(left_panel, bg="#3498DB", height=40)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text="📋 Questions List", bg="#3498DB", fg="white", 
                font=("Arial", 12, "bold")).pack(expand=True)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(left_panel, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.questions_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                            font=("Arial", 9), bg="white", 
                                            selectbackground="#3498DB", selectforeground="white")
        self.questions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.questions_listbox.yview)
        
        self.questions_listbox.bind("<<ListboxSelect>>", self.on_question_select)
        
        # Count label
        self.count_label = tk.Label(left_panel, text="Total: 0 questions", 
                                    bg="#ECF0F1", fg="#2C3E50", font=("Arial", 9, "italic"))
        self.count_label.pack(pady=5)
        
        # Buttons below list
        btn_frame = tk.Frame(left_panel, bg="#ECF0F1")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="➕ New Question", command=self.new_question, 
                 bg="#27AE60", fg="white", font=("Arial", 10, "bold"), 
                 relief=tk.FLAT, cursor="hand2").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="🗑️ Delete", command=self.delete_question,
                 bg="#E74C3C", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="🔄 Refresh List", command=self.load_questions_list,
                 bg="#95A5A6", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2").pack(fill=tk.X, pady=2)
        
        # Right panel - Question editor
        right_panel = tk.Frame(main_container, bg="white")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header
        editor_header = tk.Frame(right_panel, bg="#34495E", height=40)
        editor_header.pack(fill=tk.X)
        editor_header.pack_propagate(False)
        
        tk.Label(editor_header, text="✏️ Question Editor", bg="#34495E", fg="white",
                font=("Arial", 12, "bold")).pack(expand=True)
        
        # Scrollable frame for form
        canvas = tk.Canvas(right_panel, bg="white")
        scrollbar_right = tk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_right.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Form fields
        form_frame = tk.Frame(scrollable_frame, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Question
        tk.Label(form_frame, text="❓ Question (Indonesian):", bg="white", 
                font=("Arial", 11, "bold"), fg="#2C3E50").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.question_entry = tk.Entry(form_frame, font=("Arial", 11), width=60,
                                      relief=tk.SOLID, bd=1)
        self.question_entry.grid(row=1, column=0, pady=(0, 15), sticky="ew", ipady=5)
        
        # Words (comma-separated)
        tk.Label(form_frame, text="📝 Words (comma-separated):", bg="white",
                font=("Arial", 11, "bold"), fg="#2C3E50").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.words_entry = tk.Entry(form_frame, font=("Arial", 11), width=60,
                                    relief=tk.SOLID, bd=1)
        self.words_entry.grid(row=3, column=0, pady=(0, 5), sticky="ew", ipady=5)
        tk.Label(form_frame, text="💡 Example: She, eats, rice, every, day", 
                bg="white", fg="gray", font=("Arial", 9, "italic")).grid(row=4, column=0, sticky="w", pady=(0, 15))
        
        # Correct Answer (comma-separated)
        tk.Label(form_frame, text="✅ Correct Answer (comma-separated):", bg="white",
                font=("Arial", 11, "bold"), fg="#2C3E50").grid(row=5, column=0, sticky="w", pady=(0, 5))
        self.answer_entry = tk.Entry(form_frame, font=("Arial", 11), width=60,
                                     relief=tk.SOLID, bd=1)
        self.answer_entry.grid(row=6, column=0, pady=(0, 5), sticky="ew", ipady=5)
        tk.Label(form_frame, text="💡 Example: She, eats, rice, every, day", 
                bg="white", fg="gray", font=("Arial", 9, "italic")).grid(row=7, column=0, sticky="w", pady=(0, 15))
        
        # Timer
        tk.Label(form_frame, text="⏱️ Timer (seconds):", bg="white",
                font=("Arial", 11, "bold"), fg="#2C3E50").grid(row=8, column=0, sticky="w", pady=(0, 5))
        timer_frame = tk.Frame(form_frame, bg="white")
        timer_frame.grid(row=9, column=0, sticky="w", pady=(0, 20))
        
        self.timer_entry = tk.Entry(timer_frame, font=("Arial", 11), width=10,
                                    relief=tk.SOLID, bd=1)
        self.timer_entry.pack(side=tk.LEFT, ipady=5)
        self.timer_entry.insert(0, "30")
        
        tk.Label(timer_frame, text="  (Recommended: Easy=25-30, Medium=35-40, Hard=45-50)", 
                bg="white", fg="gray", font=("Arial", 9, "italic")).pack(side=tk.LEFT, padx=5)
        
        # Save button
        save_btn = tk.Button(form_frame, text="💾 SAVE QUESTION", command=self.save_question,
                 bg="#3498DB", fg="white", font=("Arial", 13, "bold"), 
                 pady=12, relief=tk.FLAT, cursor="hand2")
        save_btn.grid(row=10, column=0, sticky="ew", pady=(20, 0))
        
        # Hover effect for save button
        def on_enter(e):
            save_btn['bg'] = '#2980B9'
        def on_leave(e):
            save_btn['bg'] = '#3498DB'
        
        save_btn.bind("<Enter>", on_enter)
        save_btn.bind("<Leave>", on_leave)
        
        form_frame.columnconfigure(0, weight=1)
        
        # Load initial list
        self.load_questions_list()
    
    def build_guess_ui(self):
        """Build UI for guess game editor"""
        # Top frame - Title
        top_frame = tk.Frame(self.root, bg="#8E44AD", pady=20)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="🎨 GUESS GAME EDITOR", bg="#8E44AD", fg="white", 
                font=("Arial", 18, "bold")).pack()
        
        tk.Label(top_frame, text="Create questions with blurred images", 
                bg="#8E44AD", fg="white", font=("Arial", 10, "italic")).pack(pady=(5, 0))
        
        # Main container
        main_container = tk.Frame(self.root, bg="#ECF0F1")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Questions list
        left_panel = tk.Frame(main_container, width=280, bg="#ECF0F1")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # List header
        list_header = tk.Frame(left_panel, bg="#9B59B6", height=40)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text="📋 Questions List", bg="#9B59B6", fg="white",
                font=("Arial", 12, "bold")).pack(expand=True)
        
        # Listbox
        list_frame = tk.Frame(left_panel, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.questions_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                            font=("Arial", 9), bg="white",
                                            selectbackground="#9B59B6", selectforeground="white")
        self.questions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.questions_listbox.yview)
        
        self.questions_listbox.bind("<<ListboxSelect>>", self.on_guess_select)
        
        # Count label
        self.count_label = tk.Label(left_panel, text="Total: 0 questions", 
                                    bg="#ECF0F1", fg="#2C3E50", font=("Arial", 9, "italic"))
        self.count_label.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(left_panel, bg="#ECF0F1")
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="➕ New Question", command=self.new_guess_question,
                 bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="🗑️ Delete", command=self.delete_guess_question,
                 bg="#E74C3C", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2").pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="🔄 Refresh List", command=self.load_guess_list,
                 bg="#95A5A6", fg="white", font=("Arial", 10, "bold"),
                 relief=tk.FLAT, cursor="hand2").pack(fill=tk.X, pady=2)
        
        # Right panel - Editor
        right_panel = tk.Frame(main_container, bg="white")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header
        editor_header = tk.Frame(right_panel, bg="#7D3C98", height=40)
        editor_header.pack(fill=tk.X)
        editor_header.pack_propagate(False)
        
        tk.Label(editor_header, text="✏️ Question Editor", bg="#7D3C98", fg="white",
                font=("Arial", 12, "bold")).pack(expand=True)
        
        # Scrollable content
        canvas = tk.Canvas(right_panel, bg="white")
        scrollbar_right = tk.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_right.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        form_frame = tk.Frame(scrollable_frame, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Images section
        images_frame = tk.Frame(form_frame, bg="#F8F9F9", relief=tk.SOLID, bd=1)
        images_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20), padx=5)
        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)
        
        # Blurred Image column
        blurred_col = tk.Frame(images_frame, bg="#F8F9F9")
        blurred_col.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tk.Label(blurred_col, text="🔒 Blurred Image (Question)", bg="#F8F9F9",
                font=("Arial", 11, "bold"), fg="#E74C3C").pack(pady=(0, 5))
        
        self.blurred_preview_label = tk.Label(blurred_col, text="No image selected", 
                                              bg="white", width=25, height=10,
                                              relief=tk.SOLID, bd=1)
        self.blurred_preview_label.pack(pady=5)
        
        self.blurred_entry = tk.Entry(blurred_col, font=("Arial", 9), width=30,
                                      relief=tk.SOLID, bd=1, state="readonly")
        self.blurred_entry.pack(pady=5, ipady=3)
        
        tk.Button(blurred_col, text="📁 Browse Blurred Image", 
                 command=self.browse_blurred, bg="#E67E22", fg="white",
                 font=("Arial", 9, "bold"), relief=tk.FLAT, cursor="hand2").pack(pady=5)
        
        # Original Image column
        original_col = tk.Frame(images_frame, bg="#F8F9F9")
        original_col.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(original_col, text="🔓 Original Image (Answer)", bg="#F8F9F9",
                font=("Arial", 11, "bold"), fg="#27AE60").pack(pady=(0, 5))
        
        self.original_preview_label = tk.Label(original_col, text="No image selected",
                                               bg="white", width=25, height=10,
                                               relief=tk.SOLID, bd=1)
        self.original_preview_label.pack(pady=5)
        
        self.original_entry = tk.Entry(original_col, font=("Arial", 9), width=30,
                                       relief=tk.SOLID, bd=1, state="readonly")
        self.original_entry.pack(pady=5, ipady=3)
        
        tk.Button(original_col, text="📁 Browse Original Image",
                 command=self.browse_original, bg="#27AE60", fg="white",
                 font=("Arial", 9, "bold"), relief=tk.FLAT, cursor="hand2").pack(pady=5)
        
        # Options section
        tk.Label(form_frame, text="📝 Answer Options (4 required):", bg="white",
                font=("Arial", 12, "bold"), fg="#2C3E50").grid(row=1, column=0, sticky="w", pady=(10, 10))
        
        options_frame = tk.Frame(form_frame, bg="white")
        options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        self.option_entries = []
        for i in range(4):
            opt_frame = tk.Frame(options_frame, bg="white")
            opt_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(opt_frame, text=f"Option {i+1}:", bg="white",
                    font=("Arial", 10, "bold"), width=10, anchor="w").pack(side=tk.LEFT, padx=(0, 10))
            entry = tk.Entry(opt_frame, font=("Arial", 11), relief=tk.SOLID, bd=1)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
            self.option_entries.append(entry)
        
        # Correct Answer
        tk.Label(form_frame, text="✅ Correct Answer:", bg="white",
                font=("Arial", 12, "bold"), fg="#27AE60").grid(row=3, column=0, sticky="w", pady=(15, 5))
        
        correct_frame = tk.Frame(form_frame, bg="white")
        correct_frame.grid(row=4, column=0, sticky="ew", pady=(0, 5))
        
        self.correct_guess_entry = tk.Entry(correct_frame, font=("Arial", 11), 
                                            relief=tk.SOLID, bd=1)
        self.correct_guess_entry.pack(fill=tk.X, ipady=5)
        
        tk.Label(form_frame, text="💡 Must exactly match one of the options above", 
                bg="white", fg="gray", font=("Arial", 9, "italic")).grid(row=5, column=0, sticky="w", pady=(0, 20))
        
        # Save button
        save_btn = tk.Button(form_frame, text="💾 SAVE QUESTION", command=self.save_guess_question,
                 bg="#9B59B6", fg="white", font=("Arial", 13, "bold"),
                 pady=12, relief=tk.FLAT, cursor="hand2")
        save_btn.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        
        # Hover effect
        def on_enter(e):
            save_btn['bg'] = '#8E44AD'
        def on_leave(e):
            save_btn['bg'] = '#9B59B6'
        
        save_btn.bind("<Enter>", on_enter)
        save_btn.bind("<Leave>", on_leave)
        
        form_frame.columnconfigure(0, weight=1)
        
        # Load list
        self.load_guess_list()
    
    def load_questions_list(self):
        """Load questions list for sentence quiz"""
        self.questions_listbox.delete(0, tk.END)
        
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        
        questions = self.data.get(category, {}).get(difficulty, [])
        
        for i, q in enumerate(questions):
            question_text = q.get("question", "No question")
            display_text = f"{i+1}. {question_text[:45]}..."
            self.questions_listbox.insert(tk.END, display_text)
        
        # Update count
        self.count_label.config(text=f"Total: {len(questions)} questions")
    
    def load_guess_list(self):
        """Load questions list for guess game"""
        self.questions_listbox.delete(0, tk.END)
        
        for i, q in enumerate(self.data):
            correct = q.get("correct_answer", "Unknown")
            self.questions_listbox.insert(tk.END, f"{i+1}. {correct}")
        
        # Update count
        self.count_label.config(text=f"Total: {len(self.data)} questions")
    
    def on_question_select(self, event):
        """Handle question selection in sentence quiz"""
        selection = self.questions_listbox.curselection()
        if not selection:
            return
        
        self.current_index = selection[0]
        
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        question = self.data[category][difficulty][self.current_index]
        
        # Fill form
        self.question_entry.delete(0, tk.END)
        self.question_entry.insert(0, question.get("question", ""))
        
        self.words_entry.delete(0, tk.END)
        self.words_entry.insert(0, ", ".join(question.get("words", [])))
        
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.insert(0, ", ".join(question.get("correct_answer", [])))
        
        self.timer_entry.delete(0, tk.END)
        self.timer_entry.insert(0, str(question.get("timer", 30)))
    
    def on_guess_select(self, event):
        """Handle question selection in guess game"""
        selection = self.questions_listbox.curselection()
        if not selection:
            return
        
        self.current_index = selection[0]
        question = self.data[self.current_index]
        
        # Fill form
        self.blurred_entry.config(state="normal")
        self.blurred_entry.delete(0, tk.END)
        self.blurred_entry.insert(0, question.get("blurred_image", ""))
        self.blurred_entry.config(state="readonly")
        
        self.original_entry.config(state="normal")
        self.original_entry.delete(0, tk.END)
        self.original_entry.insert(0, question.get("original_image", ""))
        self.original_entry.config(state="readonly")
        
        # Load preview images
        self.load_image_preview(question.get("blurred_image", ""), "blurred")
        self.load_image_preview(question.get("original_image", ""), "original")
        
        options = question.get("options", ["", "", "", ""])
        for i, entry in enumerate(self.option_entries):
            entry.delete(0, tk.END)
            if i < len(options):
                entry.insert(0, options[i])
        
        self.correct_guess_entry.delete(0, tk.END)
        self.correct_guess_entry.insert(0, question.get("correct_answer", ""))
    
    def load_image_preview(self, filename, img_type):
        """Load image preview"""
        if not filename:
            return
        
        try:
            img_path = self.assets_path / img_type / filename
            if img_path.exists():
                img = Image.open(img_path)
                img.thumbnail((200, 150))
                photo = ImageTk.PhotoImage(img)
                
                if img_type == "blurred":
                    self.blurred_preview = photo
                    self.blurred_preview_label.config(image=photo, text="")
                else:
                    self.original_preview = photo
                    self.original_preview_label.config(image=photo, text="")
        except Exception as e:
            print(f"[X] Error loading preview: {e}")
    
    def new_question(self):
        """Create new question for sentence quiz"""
        self.current_index = -1
        self.question_entry.delete(0, tk.END)
        self.words_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)
        self.timer_entry.delete(0, tk.END)
        self.timer_entry.insert(0, "30")
        self.questions_listbox.selection_clear(0, tk.END)
    
    def new_guess_question(self):
        """Create new question for guess game"""
        self.current_index = -1
        
        self.blurred_entry.config(state="normal")
        self.blurred_entry.delete(0, tk.END)
        self.blurred_entry.config(state="readonly")
        
        self.original_entry.config(state="normal")
        self.original_entry.delete(0, tk.END)
        self.original_entry.config(state="readonly")
        
        self.blurred_preview_label.config(image='', text="No image selected")
        self.original_preview_label.config(image='', text="No image selected")
        
        for entry in self.option_entries:
            entry.delete(0, tk.END)
        self.correct_guess_entry.delete(0, tk.END)
        self.questions_listbox.selection_clear(0, tk.END)
    
    def save_question(self):
        """Save question for sentence quiz"""
        question_text = self.question_entry.get().strip()
        words_text = self.words_entry.get().strip()
        answer_text = self.answer_entry.get().strip()
        timer_text = self.timer_entry.get().strip()
        
        if not question_text or not words_text or not answer_text:
            messagebox.showwarning("Warning", "⚠️ Please fill all required fields!")
            return
        
        try:
            timer = int(timer_text)
            if timer <= 0:
                raise ValueError()
        except:
            messagebox.showerror("Error", "❌ Timer must be a positive number!")
            return
        
        # Parse words and answer
        words = [w.strip() for w in words_text.split(",") if w.strip()]
        answer = [a.strip() for a in answer_text.split(",") if a.strip()]
        
        if not words or not answer:
            messagebox.showwarning("Warning", "⚠️ Words and answer cannot be empty!")
            return
        
        # Validate that all answer words are in words list
        for ans_word in answer:
            if ans_word not in words:
                messagebox.showwarning("Warning", 
                    f"⚠️ Answer word '{ans_word}' is not in the words list!\nPlease make sure all answer words are available in the words list.")
                return
        
        question_data = {
            "question": question_text,
            "words": words,
            "correct_answer": answer,
            "timer": timer
        }
        
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        
        if self.current_index >= 0:
            # Update existing
            self.data[category][difficulty][self.current_index] = question_data
            action = "updated"
        else:
            # Add new
            self.data[category][difficulty].append(question_data)
            action = "added"
        
        if self.save_data():
            self.load_questions_list()
            self.new_question()
            print(f"[OK] Question {action} successfully")
    
    def save_guess_question(self):
        """Save question for guess game"""
        blurred = self.blurred_entry.get().strip()
        original = self.original_entry.get().strip()
        
        options = [e.get().strip() for e in self.option_entries]
        correct = self.correct_guess_entry.get().strip()
        
        if not blurred or not original or not all(options) or not correct:
            messagebox.showwarning("Warning", "⚠️ Please fill all fields and upload both images!")
            return
        
        if correct not in options:
            messagebox.showerror("Error", "❌ Correct answer must be one of the options!")
            return
        
        question_data = {
            "blurred_image": blurred,
            "original_image": original,
            "options": options,
            "correct_answer": correct
        }
        
        if self.current_index >= 0:
            # Update
            self.data[self.current_index] = question_data
            action = "updated"
        else:
            # Add new
            self.data.append(question_data)
            action = "added"
        
        if self.save_data():
            self.load_guess_list()
            self.new_guess_question()
            print(f"[OK] Question {action} successfully")
    
    def delete_question(self):
        """Delete question from sentence quiz"""
        if self.current_index < 0:
            messagebox.showwarning("Warning", "⚠️ Please select a question to delete!")
            return
        
        if messagebox.askyesno("Confirm", "🗑️ Are you sure you want to delete this question?"):
            category = self.category_var.get()
            difficulty = self.difficulty_var.get()
            del self.data[category][difficulty][self.current_index]
            
            if self.save_data():
                self.load_questions_list()
                self.new_question()
                print("[OK] Question deleted")
    
    def delete_guess_question(self):
        """Delete question from guess game"""
        if self.current_index < 0:
            messagebox.showwarning("Warning", "⚠️ Please select a question to delete!")
            return
        
        if messagebox.askyesno("Confirm", "🗑️ Are you sure you want to delete this question?"):
            del self.data[self.current_index]
            
            if self.save_data():
                self.load_guess_list()
                self.new_guess_question()
                print("[OK] Question deleted")
    
    def browse_blurred(self):
        """Browse and copy blurred image"""
        filename = filedialog.askopenfilename(
            title="Select Blurred Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        
        if filename:
            src = Path(filename)
            # Create unique filename
            import time
            timestamp = int(time.time())
            dst_name = f"blurred_{timestamp}_{src.name}"
            dst = self.assets_path / "blurred" / dst_name
            
            try:
                shutil.copy(src, dst)
                self.blurred_entry.config(state="normal")
                self.blurred_entry.delete(0, tk.END)
                self.blurred_entry.insert(0, dst_name)
                self.blurred_entry.config(state="readonly")
                
                # Load preview
                self.load_image_preview(dst_name, "blurred")
                
                messagebox.showinfo("Success", f"✅ Image copied to:\n{dst}")
                print(f"[OK] Blurred image copied: {dst_name}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to copy image: {e}")
    
    def browse_original(self):
        """Browse and copy original image"""
        filename = filedialog.askopenfilename(
            title="Select Original Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        
        if filename:
            src = Path(filename)
            # Create unique filename
            import time
            timestamp = int(time.time())
            dst_name = f"original_{timestamp}_{src.name}"
            dst = self.assets_path / "original" / dst_name
            
            try:
                shutil.copy(src, dst)
                self.original_entry.config(state="normal")
                self.original_entry.delete(0, tk.END)
                self.original_entry.insert(0, dst_name)
                self.original_entry.config(state="readonly")
                
                # Load preview
                self.load_image_preview(dst_name, "original")
                
                messagebox.showinfo("Success", f"✅ Image copied to:\n{dst}")
                print(f"[OK] Original image copied: {dst_name}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to copy image: {e}")

def main():
    # Check command line argument for mode
    mode = "sentence"
    if len(sys.argv) > 1:
        if sys.argv[1] == "guess":
            mode = "guess"
    
    print(f"\n{'='*60}")
    print(f"[*] Starting Quiz Editor - Mode: {mode.upper()}")
    print(f"{'='*60}\n")
    
    root = tk.Tk()
    app = QuizEditor(root, mode=mode)
    
    print("[OK] Editor window opened")
    print("[*] Edit your questions and click Save")
    print("[*] Remember to reload the game after editing (press 'r')")
    print(f"{'='*60}\n")
    
    root.mainloop()
    
    print("\n[*] Editor closed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[X] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
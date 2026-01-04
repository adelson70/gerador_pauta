import tkinter as tk
from tkinter import ttk, filedialog
import fitz
from PIL import Image, ImageTk
import tempfile
import os
import io

from src.config import settings


class NoteCheckboxPanel(tk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.checkboxes = {}
        self.on_change_callback = None
        self._create_widgets()
    
    def _create_widgets(self):
        title_label = tk.Label(self, text="Selecionar Notas:", font=("Helvetica", 10, "bold"))
        title_label.pack(anchor="w", pady=(0, 5))
        
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", pady=(0, 10))
        
        select_all_btn = tk.Button(button_frame, text="Selecionar Todas", 
                                   command=self.select_all, width=15)
        select_all_btn.pack(side="left", padx=(0, 5))
        
        clear_all_btn = tk.Button(button_frame, text="Limpar Seleção", 
                                  command=self.clear_all, width=15)
        clear_all_btn.pack(side="left")
        
        strings_frame = tk.Frame(self)
        strings_frame.pack(fill="both", expand=True)
        
        for string_name, notes in settings.NOTES_BY_STRING.items():
            self._create_string_section(strings_frame, string_name, notes)
    
    def _create_string_section(self, parent, string_name, notes):
        string_label = tk.Label(parent, text=f"Corda {string_name}:", 
                               font=("Helvetica", 9, "bold"))
        string_label.pack(anchor="w", pady=(5, 2))
        
        notes_frame = tk.Frame(parent)
        notes_frame.pack(anchor="w", padx=(10, 0))
        
        for i, note in enumerate(notes):
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(notes_frame, text=note, variable=var, 
                               font=("Helvetica", 9),
                               command=self._on_checkbox_change)
            cb.pack(side="left", padx=(0, 10))
            self.checkboxes[note] = var
    
    def _on_checkbox_change(self):
        if self.on_change_callback:
            self.on_change_callback()
    
    def set_on_change_callback(self, callback):
        self.on_change_callback = callback
    
    def get_selected_notes(self):
        selected = []
        for note, var in self.checkboxes.items():
            if var.get():
                selected.append(note)
        return selected
    
    def select_all(self):
        for var in self.checkboxes.values():
            var.set(True)
        self._on_checkbox_change()
    
    def clear_all(self):
        for var in self.checkboxes.values():
            var.set(False)
        self._on_checkbox_change()


class PDFPreviewCanvas(tk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pdf_path = None
        self.images = []
        self.current_page = 0
        self.image_preview = None
        self.photo = None
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        self.btn_prev = tk.Button(main_frame, text="◀", font=("Helvetica", 16),
                                  command=self._prev_page, width=3, state="disabled")
        self.btn_prev.pack(side="left", fill="y", padx=(5, 5))
        
        self.canvas = tk.Canvas(main_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.btn_next = tk.Button(main_frame, text="▶", font=("Helvetica", 16),
                                  command=self._next_page, width=3, state="disabled")
        self.btn_next.pack(side="left", fill="y", padx=(5, 5))
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def load_pdf(self, pdf_path):
        if not os.path.exists(pdf_path):
            self.clear()
            return
        
        try:
            doc = fitz.open(pdf_path)
            
            self.images = []
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                self.images.append(img)
            
            doc.close()
            self.pdf_path = pdf_path
            self.current_page = 0
            
            self._update_navigation_buttons()
            
            self._redraw_image()
            
        except Exception as e:
            print(f"Erro ao carregar PDF: {e}")
            self.clear()
    
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_navigation_buttons()
            self._redraw_image()
    
    def _next_page(self):
        if self.current_page < len(self.images) - 1:
            self.current_page += 1
            self._update_navigation_buttons()
            self._redraw_image()
    
    def _update_navigation_buttons(self):
        if len(self.images) <= 1:
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
        else:
            self.btn_prev.config(state="normal" if self.current_page > 0 else "disabled")
            self.btn_next.config(state="normal" if self.current_page < len(self.images) - 1 else "disabled")
    
    def _on_canvas_configure(self, event=None):
        if self.images:
            self._redraw_image()
    
    def _redraw_image(self):
        if not self.images or self.current_page >= len(self.images):
            return
        
        try:
            image = self.images[self.current_page]
            
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 500
                canvas_height = 700
            
            a4_ratio = 297.0 / 210.0
            
            max_width_by_canvas = canvas_width
            max_height_by_width = max_width_by_canvas * a4_ratio
            
            max_height_by_canvas = canvas_height
            max_width_by_height = max_height_by_canvas / a4_ratio
            
            if max_height_by_width <= canvas_height:
                display_width = max_width_by_canvas
                display_height = max_height_by_width
            else:
                display_width = max_width_by_height
                display_height = max_height_by_canvas
            
            final_width = int(display_width)
            final_height = int(display_height)
            
            self.image_preview = image.resize((final_width, final_height), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(self.image_preview)
            
            self.canvas.delete("all")
            x = (canvas_width - final_width) // 2
            y = (canvas_height - final_height) // 2
            self.canvas.create_image(x, y, anchor="nw", image=self.photo)
            
            if len(self.images) > 1:
                page_text = f"Página {self.current_page + 1} de {len(self.images)}"
                self.canvas.create_text(canvas_width - 10, 10, anchor="ne", 
                                       text=page_text, font=("Helvetica", 10), fill="gray")
            
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
            
        except Exception as e:
            print(f"Erro ao redesenhar imagem: {e}")
    
    def clear(self):
        self.canvas.delete("all")
        self.pdf_path = None
        self.images = []
        self.current_page = 0
        self.image_preview = None
        self.photo = None
        self._update_navigation_buttons()


class ConfigurationPanel(tk.Frame):
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.output_path = tk.StringVar(value="")
        self.on_change_callback = None
        self._create_widgets()
    
    def _create_widgets(self):
        quantity_frame = tk.Frame(self)
        quantity_frame.pack(fill="x", pady=(0, 15))
        
        quantity_label = tk.Label(quantity_frame, text="Quantidade de pautas:", 
                                  font=("Helvetica", 10))
        quantity_label.pack(side="left", padx=(0, 5))
        
        self.quantity_var = tk.IntVar(value=6)
        quantity_spinbox = tk.Spinbox(quantity_frame, from_=1, to=6, 
                                      textvariable=self.quantity_var, width=10,
                                      command=self._on_quantity_change)
        quantity_spinbox.pack(side="left")
        try:
            self.quantity_var.trace_add("write", lambda *args: self._on_quantity_change())
        except AttributeError:
            self.quantity_var.trace("w", lambda *args: self._on_quantity_change())
        
        gap_frame = tk.Frame(self)
        gap_frame.pack(fill="x", pady=(0, 15))
        
        gap_label = tk.Label(gap_frame, text="Espaçamento entre pautas (cm):", 
                            font=("Helvetica", 10))
        gap_label.pack(side="left", padx=(0, 5))
        
        self.gap_var = tk.DoubleVar(value=5.0)
        gap_spinbox = tk.Spinbox(gap_frame, from_=3.0, to=20.0, 
                                 increment=0.1, textvariable=self.gap_var, 
                                 width=10, command=self._on_gap_change)
        gap_spinbox.pack(side="left")
        try:
            self.gap_var.trace_add("write", lambda *args: self._on_gap_change())
        except AttributeError:
            self.gap_var.trace("w", lambda *args: self._on_gap_change())
        
        notes_per_staff_frame = tk.Frame(self)
        notes_per_staff_frame.pack(fill="x", pady=(0, 15))
        
        notes_per_staff_label = tk.Label(notes_per_staff_frame, text="Notas por pauta:", 
                                         font=("Helvetica", 10))
        notes_per_staff_label.pack(side="left", padx=(0, 5))
        
        self.notes_per_staff_var = tk.IntVar(value=17)
        notes_per_staff_spinbox = tk.Spinbox(notes_per_staff_frame, from_=1, to=17, 
                                             textvariable=self.notes_per_staff_var, width=10,
                                             command=self._on_notes_per_staff_change)
        notes_per_staff_spinbox.pack(side="left")
        try:
            self.notes_per_staff_var.trace_add("write", lambda *args: self._on_notes_per_staff_change())
        except AttributeError:
            self.notes_per_staff_var.trace("w", lambda *args: self._on_notes_per_staff_change())
        
        pages_frame = tk.Frame(self)
        pages_frame.pack(fill="x", pady=(0, 15))
        
        pages_label = tk.Label(pages_frame, text="Número de páginas:", 
                              font=("Helvetica", 10))
        pages_label.pack(side="left", padx=(0, 5))
        
        self.pages_var = tk.IntVar(value=1)
        pages_spinbox = tk.Spinbox(pages_frame, from_=1, to=100, 
                                   textvariable=self.pages_var, width=10,
                                   command=self._on_pages_change)
        pages_spinbox.pack(side="left")
        try:
            self.pages_var.trace_add("write", lambda *args: self._on_pages_change())
        except AttributeError:
            self.pages_var.trace("w", lambda *args: self._on_pages_change())
        
        mode_frame = tk.Frame(self)
        mode_frame.pack(fill="x", pady=(0, 15))
        
        mode_label = tk.Label(mode_frame, text="Modo:", font=("Helvetica", 10))
        mode_label.pack(side="left", padx=(0, 10))
        
        self.mode_var = tk.StringVar(value="sequencial")
        
        sequential_radio = tk.Radiobutton(mode_frame, text="Sequencial", 
                                         variable=self.mode_var, value="sequencial",
                                         font=("Helvetica", 9),
                                         command=self._on_mode_change)
        sequential_radio.pack(side="left", padx=(0, 10))
        
        random_radio = tk.Radiobutton(mode_frame, text="Aleatório", 
                                     variable=self.mode_var, value="aleatorio",
                                     font=("Helvetica", 9),
                                     command=self._on_mode_change)
        random_radio.pack(side="left")
        
        output_frame = tk.Frame(self)
        output_frame.pack(fill="x", pady=(0, 10))
        
        output_label = tk.Label(output_frame, text="Salvar em:", 
                               font=("Helvetica", 10))
        output_label.pack(anchor="w", pady=(0, 5))
        
        path_frame = tk.Frame(output_frame)
        path_frame.pack(fill="x")
        
        self.path_entry = tk.Entry(path_frame, textvariable=self.output_path, 
                                   font=("Helvetica", 9))
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = tk.Button(path_frame, text="Buscar", 
                              command=self._browse_output_path, width=10)
        browse_btn.pack(side="left")
    
    def _browse_output_path(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Escolher local para salvar PDF"
        )
        if filename:
            self.output_path.set(filename)
    
    def _on_quantity_change(self, *args):
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_gap_change(self, *args):
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_notes_per_staff_change(self, *args):
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_pages_change(self, *args):
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_mode_change(self):
        if self.on_change_callback:
            self.on_change_callback()
    
    def set_on_change_callback(self, callback):
        self.on_change_callback = callback
    
    def get_quantity(self):
        return self.quantity_var.get()
    
    def get_staff_gap(self):
        return self.gap_var.get()
    
    def get_notes_per_staff(self):
        return self.notes_per_staff_var.get()
    
    def get_pages(self):
        return self.pages_var.get()
    
    def get_mode(self):
        return self.mode_var.get()
    
    def get_output_path(self):
        return self.output_path.get()


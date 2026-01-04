import tkinter as tk
from tkinter import messagebox
import tempfile
import os

from src.gui.widgets import NoteCheckboxPanel, PDFPreviewCanvas, ConfigurationPanel
from src.core.pdf_generator import PautaPDFGenerator


class PautaGeneratorGUI(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.title("Gerador de Pautas - Violino")
        self.geometry("1200x800")
        
        self.pdf_generator = PautaPDFGenerator()
        
        self.temp_pdf_path = None
        
        self.preview_update_id = None
        
        self._create_widgets()
        
        self._setup_auto_preview()
        
        self.after(100, self._update_preview)
    
    def _create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_frame, relief="sunken", borderwidth=2)
        left_panel.pack(side="left", fill="both", padx=(0, 5))
        left_panel.config(width=400)
        left_panel.pack_propagate(False)
        
        self._create_left_panel(left_panel)
        
        right_panel = tk.Frame(main_frame, relief="sunken", borderwidth=2)
        right_panel.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        self._create_right_panel(right_panel)
    
    def _create_left_panel(self, parent):
        title_label = tk.Label(parent, text="CONFIGURAÇÕES", 
                              font=("Helvetica", 12, "bold"))
        title_label.pack(pady=(10, 15))
        
        self.config_panel = ConfigurationPanel(parent)
        self.config_panel.pack(fill="x", padx=10, pady=(0, 15))
        
        self.note_panel = NoteCheckboxPanel(parent)
        self.note_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def _setup_auto_preview(self):
        self.config_panel.set_on_change_callback(self._schedule_preview_update)
        
        self.note_panel.set_on_change_callback(self._schedule_preview_update)
    
    def _schedule_preview_update(self):
        if self.preview_update_id:
            self.after_cancel(self.preview_update_id)
        
        self.preview_update_id = self.after(500, self._update_preview)
    
    def _update_preview(self):
        selected_notes = self.note_panel.get_selected_notes()
        if not selected_notes:
            self.preview_canvas.clear()
            return
        
        quantity = self.config_panel.get_quantity()
        if quantity < 1:
            return
        
        try:
            staff_gap_cm = self.config_panel.get_staff_gap()
            num_pages = self.config_panel.get_pages()
            notes_per_staff = self.config_panel.get_notes_per_staff()
            mode = self.config_panel.get_mode()
            random_mode = (mode == "aleatorio")
            
            if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
                try:
                    os.remove(self.temp_pdf_path)
                except:
                    pass
            
            temp_fd, self.temp_pdf_path = tempfile.mkstemp(suffix=".pdf", 
                                                          prefix="pauta_preview_")
            os.close(temp_fd)
            
            self.pdf_generator.generate(
                notes_sequence=selected_notes,
                quantity=quantity,
                output_path=self.temp_pdf_path,
                num_pages=num_pages,
                staff_gap_cm=staff_gap_cm,
                random_mode=random_mode,
                notes_per_staff=notes_per_staff
            )
            
            self.preview_canvas.load_pdf(self.temp_pdf_path)
            
        except Exception as e:
            self.preview_canvas.clear()
    
    def _create_right_panel(self, parent):
        title_label = tk.Label(parent, text="PREVIEW", 
                              font=("Helvetica", 12, "bold"))
        title_label.pack(pady=(10, 5))
        
        self.preview_canvas = PDFPreviewCanvas(parent)
        self.preview_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        button_frame = tk.Frame(parent)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        generate_pdf_btn = tk.Button(button_frame, text="Gerar PDF Final", 
                                     command=self._on_generate_pdf,
                                     font=("Helvetica", 10, "bold"),
                                     bg="#2196F3", fg="white",
                                     width=25, height=2)
        generate_pdf_btn.pack()
    
    def _validate_inputs(self):
        selected_notes = self.note_panel.get_selected_notes()
        if not selected_notes:
            return False, "Selecione pelo menos uma nota."
        
        quantity = self.config_panel.get_quantity()
        if quantity < 1:
            return False, "A quantidade de pautas deve ser pelo menos 1."
        
        return True, None
    
    def _on_generate_pdf(self):
        is_valid, error_msg = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("Erro de Validação", error_msg)
            return
        
        output_path = self.config_panel.get_output_path()
        if not output_path:
            messagebox.showerror("Erro", "Escolha um local para salvar o PDF.")
            return
        
        try:
            selected_notes = self.note_panel.get_selected_notes()
            quantity = self.config_panel.get_quantity()
            staff_gap_cm = self.config_panel.get_staff_gap()
            num_pages = self.config_panel.get_pages()
            notes_per_staff = self.config_panel.get_notes_per_staff()
            mode = self.config_panel.get_mode()
            random_mode = (mode == "aleatorio")
            
            self.pdf_generator.generate(
                notes_sequence=selected_notes,
                quantity=quantity,
                output_path=output_path,
                num_pages=num_pages,
                staff_gap_cm=staff_gap_cm,
                random_mode=random_mode,
                notes_per_staff=notes_per_staff
            )
            
            messagebox.showinfo("Sucesso", 
                              f"PDF gerado com sucesso!\n\nLocal: {output_path}")
            
            self.preview_canvas.load_pdf(output_path)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF:\n{str(e)}")
    
    def __del__(self):
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try:
                os.remove(self.temp_pdf_path)
            except:
                pass


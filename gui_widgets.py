"""
Módulo com widgets personalizados para a interface gráfica.
Componentes reutilizáveis para a GUI do gerador de pautas.
"""
import tkinter as tk
from tkinter import ttk, filedialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tempfile
import os
import io

import config


class NoteCheckboxPanel(tk.Frame):
    """Painel com checkboxes para seleção de notas organizadas por corda."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.checkboxes = {}
        self.on_change_callback = None  # Callback para mudanças
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do painel de notas."""
        # Título
        title_label = tk.Label(self, text="Selecionar Notas:", font=("Helvetica", 10, "bold"))
        title_label.pack(anchor="w", pady=(0, 5))
        
        # Botões de ação rápida
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", pady=(0, 10))
        
        select_all_btn = tk.Button(button_frame, text="Selecionar Todas", 
                                   command=self.select_all, width=15)
        select_all_btn.pack(side="left", padx=(0, 5))
        
        clear_all_btn = tk.Button(button_frame, text="Limpar Seleção", 
                                  command=self.clear_all, width=15)
        clear_all_btn.pack(side="left")
        
        # Container para os checkboxes organizados por corda
        strings_frame = tk.Frame(self)
        strings_frame.pack(fill="both", expand=True)
        
        # Criar checkboxes para cada corda
        for string_name, notes in config.NOTES_BY_STRING.items():
            self._create_string_section(strings_frame, string_name, notes)
    
    def _create_string_section(self, parent, string_name, notes):
        """Cria uma seção de checkboxes para uma corda."""
        # Label da corda
        string_label = tk.Label(parent, text=f"Corda {string_name}:", 
                               font=("Helvetica", 9, "bold"))
        string_label.pack(anchor="w", pady=(5, 2))
        
        # Frame para os checkboxes da corda
        notes_frame = tk.Frame(parent)
        notes_frame.pack(anchor="w", padx=(10, 0))
        
        # Criar checkbox para cada nota
        for i, note in enumerate(notes):
            var = tk.BooleanVar(value=True)  # Por padrão, todas selecionadas
            cb = tk.Checkbutton(notes_frame, text=note, variable=var, 
                               font=("Helvetica", 9),
                               command=self._on_checkbox_change)
            cb.pack(side="left", padx=(0, 10))
            self.checkboxes[note] = var
    
    def _on_checkbox_change(self):
        """Callback quando um checkbox muda."""
        if self.on_change_callback:
            self.on_change_callback()
    
    def set_on_change_callback(self, callback):
        """Define callback para ser chamado quando há mudanças."""
        self.on_change_callback = callback
    
    def get_selected_notes(self):
        """Retorna lista de notas selecionadas."""
        selected = []
        for note, var in self.checkboxes.items():
            if var.get():
                selected.append(note)
        return selected
    
    def select_all(self):
        """Marca todos os checkboxes."""
        for var in self.checkboxes.values():
            var.set(True)
        self._on_checkbox_change()
    
    def clear_all(self):
        """Desmarca todos os checkboxes."""
        for var in self.checkboxes.values():
            var.set(False)
        self._on_checkbox_change()


class PDFPreviewCanvas(tk.Frame):
    """Canvas para preview de PDF com navegação entre páginas."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pdf_path = None
        self.images = []  # Lista de imagens de todas as páginas
        self.current_page = 0
        self.image_preview = None  # Imagem redimensionada da página atual
        self.photo = None
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do canvas de preview."""
        # Frame principal para canvas e setas
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)
        
        # Botão seta esquerda
        self.btn_prev = tk.Button(main_frame, text="◀", font=("Helvetica", 16),
                                  command=self._prev_page, width=3, state="disabled")
        self.btn_prev.pack(side="left", fill="y", padx=(5, 5))
        
        # Canvas no centro
        self.canvas = tk.Canvas(main_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Botão seta direita
        self.btn_next = tk.Button(main_frame, text="▶", font=("Helvetica", 16),
                                  command=self._next_page, width=3, state="disabled")
        self.btn_next.pack(side="left", fill="y", padx=(5, 5))
        
        # Bind para redimensionar preview quando o canvas mudar de tamanho
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def load_pdf(self, pdf_path):
        """
        Carrega um PDF e armazena todas as páginas em alta resolução.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
        """
        if not os.path.exists(pdf_path):
            self.clear()
            return
        
        try:
            # Abrir PDF com PyMuPDF
            doc = fitz.open(pdf_path)
            
            # Converter todas as páginas para imagens
            self.images = []
            zoom = 2.0  # Alta resolução para manter qualidade
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
            
            # Atualizar botões de navegação
            self._update_navigation_buttons()
            
            # Redesenhar a imagem no canvas
            self._redraw_image()
            
        except Exception as e:
            print(f"Erro ao carregar PDF: {e}")
            self.clear()
    
    def _prev_page(self):
        """Vai para a página anterior."""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_navigation_buttons()
            self._redraw_image()
    
    def _next_page(self):
        """Vai para a próxima página."""
        if self.current_page < len(self.images) - 1:
            self.current_page += 1
            self._update_navigation_buttons()
            self._redraw_image()
    
    def _update_navigation_buttons(self):
        """Atualiza o estado dos botões de navegação."""
        if len(self.images) <= 1:
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
        else:
            self.btn_prev.config(state="normal" if self.current_page > 0 else "disabled")
            self.btn_next.config(state="normal" if self.current_page < len(self.images) - 1 else "disabled")
    
    def _on_canvas_configure(self, event=None):
        """Callback quando o canvas é redimensionado."""
        if self.images:
            self._redraw_image()
    
    def _redraw_image(self):
        """Redesenha a imagem da página atual no canvas mantendo proporção A4 exata."""
        if not self.images or self.current_page >= len(self.images):
            return
        
        try:
            image = self.images[self.current_page]
            
            # Obter dimensões do canvas
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Se o canvas ainda não tem tamanho definido, usar valores padrão
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 500
                canvas_height = 700
            
            # Proporção A4 exata: altura/largura = 297/210 = 1.4142857...
            a4_ratio = 297.0 / 210.0  # altura/largura
            
            # Calcular tamanho máximo mantendo proporção A4 exata
            # Tentar ajustar pela largura do canvas
            max_width_by_canvas = canvas_width
            max_height_by_width = max_width_by_canvas * a4_ratio
            
            # Tentar ajustar pela altura do canvas
            max_height_by_canvas = canvas_height
            max_width_by_height = max_height_by_canvas / a4_ratio
            
            # Escolher a combinação que cabe completamente no canvas
            if max_height_by_width <= canvas_height:
                # Cabe ajustando pela largura
                display_width = max_width_by_canvas
                display_height = max_height_by_width
            else:
                # Cabe ajustando pela altura
                display_width = max_width_by_height
                display_height = max_height_by_canvas
            
            # Calcular dimensões finais mantendo proporção A4
            final_width = int(display_width)
            final_height = int(display_height)
            
            # Redimensionar imagem
            self.image_preview = image.resize((final_width, final_height), Image.Resampling.LANCZOS)
            
            # Converter para PhotoImage do tkinter
            self.photo = ImageTk.PhotoImage(self.image_preview)
            
            # Limpar canvas e adicionar imagem centralizada
            self.canvas.delete("all")
            # Centralizar a imagem no canvas
            x = (canvas_width - final_width) // 2
            y = (canvas_height - final_height) // 2
            self.canvas.create_image(x, y, anchor="nw", image=self.photo)
            
            # Adicionar informação da página
            if len(self.images) > 1:
                page_text = f"Página {self.current_page + 1} de {len(self.images)}"
                self.canvas.create_text(canvas_width - 10, 10, anchor="ne", 
                                       text=page_text, font=("Helvetica", 10), fill="gray")
            
            # Configurar scrollregion para o tamanho do canvas
            self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
            
        except Exception as e:
            print(f"Erro ao redesenhar imagem: {e}")
    
    def clear(self):
        """Limpa o canvas."""
        self.canvas.delete("all")
        self.pdf_path = None
        self.images = []
        self.current_page = 0
        self.image_preview = None
        self.photo = None
        self._update_navigation_buttons()


class ConfigurationPanel(tk.Frame):
    """Painel com configurações de quantidade, modo e caminho de saída."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.output_path = tk.StringVar(value="")
        self.on_change_callback = None  # Callback para mudanças
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do painel de configurações."""
        # Quantidade de pautas
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
        # Também adicionar trace para capturar mudanças diretas na variável
        try:
            # Python 3.7+
            self.quantity_var.trace_add("write", lambda *args: self._on_quantity_change())
        except AttributeError:
            # Python 3.6 ou anterior
            self.quantity_var.trace("w", lambda *args: self._on_quantity_change())
        
        # Espaçamento entre pautas
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
        # Adicionar trace para capturar mudanças
        try:
            self.gap_var.trace_add("write", lambda *args: self._on_gap_change())
        except AttributeError:
            self.gap_var.trace("w", lambda *args: self._on_gap_change())
        
        # Quantidade de notas por pauta
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
        # Adicionar trace para capturar mudanças
        try:
            self.notes_per_staff_var.trace_add("write", lambda *args: self._on_notes_per_staff_change())
        except AttributeError:
            self.notes_per_staff_var.trace("w", lambda *args: self._on_notes_per_staff_change())
        
        # Número de páginas
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
        # Adicionar trace para capturar mudanças
        try:
            self.pages_var.trace_add("write", lambda *args: self._on_pages_change())
        except AttributeError:
            self.pages_var.trace("w", lambda *args: self._on_pages_change())
        
        # Modo de geração
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
        
        # Caminho de saída
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
        """Abre diálogo para escolher local de salvamento."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Escolher local para salvar PDF"
        )
        if filename:
            self.output_path.set(filename)
    
    def _on_quantity_change(self, *args):
        """Callback quando a quantidade muda."""
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_gap_change(self, *args):
        """Callback quando o espaçamento muda."""
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_notes_per_staff_change(self, *args):
        """Callback quando a quantidade de notas por pauta muda."""
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_pages_change(self, *args):
        """Callback quando o número de páginas muda."""
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_mode_change(self):
        """Callback quando o modo muda."""
        if self.on_change_callback:
            self.on_change_callback()
    
    def set_on_change_callback(self, callback):
        """Define callback para ser chamado quando há mudanças."""
        self.on_change_callback = callback
    
    def get_quantity(self):
        """Retorna a quantidade de pautas."""
        return self.quantity_var.get()
    
    def get_staff_gap(self):
        """Retorna o espaçamento entre pautas em cm."""
        return self.gap_var.get()
    
    def get_notes_per_staff(self):
        """Retorna a quantidade de notas por pauta."""
        return self.notes_per_staff_var.get()
    
    def get_pages(self):
              """Retorna o número de páginas."""
              return self.pages_var.get()
    
    def get_mode(self):
        """Retorna o modo selecionado ('sequencial' ou 'aleatorio')."""
        return self.mode_var.get()
    
    def get_output_path(self):
        """Retorna o caminho de saída."""
        return self.output_path.get()


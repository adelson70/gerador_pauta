"""
Módulo responsável pela geração do PDF com as pautas de violino.
Encapsula toda a lógica de desenho das pautas e notas.
"""
import random
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

import config
import note_helpers


class PautaPDFGenerator:
    """Classe responsável por gerar PDFs com pautas de violino."""
    
    def __init__(self):
        """Inicializa o gerador de PDF."""
        # Caminho para a imagem da clave de sol
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.clef_image_path = os.path.join(script_dir, "clave_de_sol.png")
    
    def generate(self, notes_sequence, quantity, output_path, num_pages, staff_gap_cm=None, random_mode=True, notes_per_staff=15):
        """
        Gera o PDF com as pautas e notas.
        
        Args:
            notes_sequence: Lista de notas selecionadas pelo usuário
            quantity: Quantidade de pautas por página
            output_path: Caminho onde o PDF será salvo
            num_pages: Número de páginas a gerar
            staff_gap_cm: Espaçamento entre pautas em cm (se None, usa 4cm)
            random_mode: Se True, sorteia notas aleatoriamente
            notes_per_staff: Quantidade de notas por pauta (1 a 17)
        """
        if not notes_sequence:
            raise ValueError("Nenhuma nota selecionada para gerar o PDF")
        
        # Criar PDF
        c = canvas.Canvas(output_path, pagesize=config.PAGE_SIZE)
        
        # Usar espaçamento fornecido pelo usuário
        if staff_gap_cm is not None:
            staff_gap = staff_gap_cm * cm
        else:
            # Valor padrão se não fornecido
            staff_gap = 4 * cm
        
        # Gerar cada página
        for page in range(num_pages):
            if page > 0:
                # Nova página
                c.showPage()
            
            # Desenhar todas as pautas da página
            for staff_index in range(quantity):
                y_staff = config.Y_START - staff_index * staff_gap
                
                # Para cada pauta, criar sequência com a quantidade especificada de notas
                target_notes_count = notes_per_staff
                if random_mode:
                    if len(notes_sequence) >= target_notes_count:
                        # Se tem 15 ou mais, usar sample de 15 (sem repetição)
                        current_staff_notes = random.sample(notes_sequence, target_notes_count)
                    else:
                        # Se tem menos, repetir aleatoriamente até ter exatamente 15
                        current_staff_notes = []
                        while len(current_staff_notes) < target_notes_count:
                            remaining = target_notes_count - len(current_staff_notes)
                            current_staff_notes.extend(random.sample(notes_sequence, min(remaining, len(notes_sequence))))
                else: # Modo sequencial
                    current_staff_notes = notes_sequence * (target_notes_count // len(notes_sequence))
                    current_staff_notes.extend(notes_sequence[:target_notes_count % len(notes_sequence)])
                
                self._draw_staff(c, y_staff)
                self._draw_notes(c, current_staff_notes, y_staff, notes_per_staff)
        
        # Salvar PDF
        c.save()
    
    def _draw_staff(self, canvas_obj, y_staff):
        """Desenha as 5 linhas da pauta com clave de sol e barra final."""
        # Desenhar linhas da pauta completas
        for line in range(5):
            line_y = y_staff + line * 10
            canvas_obj.line(config.X_START, line_y, config.X_START + config.STAFF_WIDTH, line_y)
        
        # Desenhar barra vertical final (|)
        staff_top = y_staff
        staff_bottom = y_staff + 40
        canvas_obj.line(config.BARLINE_X, staff_top, config.BARLINE_X, staff_bottom)
        
        # Desenhar clave de sol no início
        self._draw_clef(canvas_obj, y_staff)
    
    def _draw_clef(self, canvas_obj, y_staff):
        """
        Desenha a clave de sol no início da pauta usando imagem PNG.
        
        Args:
            canvas_obj: Canvas do reportlab
            y_staff: Posição Y da linha inferior da pauta
        """
        # Verificar se a imagem existe
        if not os.path.exists(self.clef_image_path):
            # Fallback: desenhar uma linha simples se a imagem não existir
            canvas_obj.line(config.X_START, y_staff, config.X_START, y_staff + 40)
            return
        
        # Linhas da pauta (de baixo para cima)
        line1_y = y_staff  # Mi4
        line2_y = y_staff + 10  # Sol4 (linha central da clave)
        line5_y = y_staff + 40  # Fa5
        
        # A clave de sol envolve a linha 2 (Sol4)
        # A imagem é 500x500 pixels (quadrada), precisa escalar para caber na pauta
        # Altura da pauta: 40 pontos (5 linhas com espaçamento de 10)
        # A clave tradicionalmente se estende significativamente acima e abaixo da pauta
        # Baseado na referência, a clave deve ser maior que a pauta
        
        clef_height = 70  # Altura em pontos (significativamente maior que a pauta de 40 pontos)
        clef_width = 70  # Largura proporcional (imagem é quadrada, manter proporção 1:1)
        
        # Posição X da clave de sol (início da pauta)
        clef_x = config.X_START - 0.5 * cm
        
        # Posição Y: centralizar a linha 2 da pauta (Sol4) com o centro vertical da imagem
        # A linha 2 está em line2_y = y_staff + 10
        # A clave deve estar um pouco mais alta (subir um pouco)
        # drawImage usa coordenada do canto inferior esquerdo
        # Ajustar para mover a clave para cima: adicionar offset positivo
        clef_y = line2_y - (clef_height / 2) + 7  # +7 pontos move a clave para cima
        
        # Desenhar a imagem da clave de sol
        # Usar preserveAspectRatio=True para manter proporção da imagem
        try:
            canvas_obj.drawImage(
                self.clef_image_path,
                clef_x,  # Posição X
                clef_y,  # Posição Y (canto inferior esquerdo)
                width=clef_width,
                height=clef_height,
                mask='auto',  # Usar transparência automaticamente (RGBA)
                preserveAspectRatio=True
            )
        except Exception as e:
            # Fallback: desenhar uma linha simples se houver erro
            print(f"Erro ao desenhar clave de sol: {e}")
            canvas_obj.line(config.X_START, y_staff, config.X_START, y_staff + 40)
    
    def _draw_notes(self, canvas_obj, notes, y_staff, notes_per_staff):
        """
        Desenha todas as notas e suas linhas suplementares em uma pauta.
        
        Args:
            canvas_obj: Canvas do reportlab
            notes: Lista de nomes de notas (ex: ["Sol3", "La3", ...])
            y_staff: Posição Y da linha inferior da pauta
            notes_per_staff: Quantidade de notas por pauta (para calcular espaçamento)
        """
        # Calcular espaçamento dinamicamente baseado na quantidade de notas
        from reportlab.lib.units import cm
        clef_width_pt = 70  # Largura da clave de sol em pontos
        clef_x_offset = -0.5 * cm  # Offset da clave (já aplicado no _draw_clef)
        clef_start = config.X_START + clef_x_offset
        clef_end = clef_start + clef_width_pt
        
        # Primeira nota começa logo após a clave (espaçamento mínimo)
        note_start = clef_end + 0.05 * cm
        
        # Largura disponível: da primeira nota até a barra final (com margem mínima antes da barra)
        margin_before_bar = 0.3 * cm  # Margem mínima antes da barra para não colar a última nota
        
        # Para N notas, há N-1 espaços entre elas
        # Calcular para que a última nota fique com um espaçamento adequado da barra (considerando o raio da nota)
        last_note_center_x = config.BARLINE_X - margin_before_bar - config.NOTE_RADIUS
        note_spacing = (last_note_center_x - note_start) / (notes_per_staff - 1) if notes_per_staff > 1 else 0
        
        # Calcular posições X e Y de todas as notas primeiro
        note_positions = []
        x = note_start
        
        # Limite máximo: barra final menos margem
        max_x = config.BARLINE_X - margin_before_bar
        
        for note in notes:
            if note not in config.NOTE_POSITIONS:
                continue  # Pular notas inválidas
            
            # Verificar se a nota cabe antes da barra final
            if x + config.NOTE_RADIUS > max_x:
                break  # Parar se não houver mais espaço
            
            y = y_staff + config.NOTE_POSITIONS[note]
            note_positions.append((x, y, note))
            x += note_spacing
        
        # Desenhar notas e linhas suplementares
        for x_note, y_note, note_name in note_positions:
            self._draw_note(canvas_obj, x_note, y_note, y_staff)
    
    def _draw_note(self, canvas_obj, x_note, y_note, y_staff):
        """
        Desenha uma nota individual com suas linhas suplementares (se necessário).
        
        Args:
            canvas_obj: Canvas do reportlab
            x_note: Posição X da nota
            y_note: Posição Y da nota
            y_staff: Posição Y da linha inferior da pauta
        """
        # Calcular offset da nota relativo à pauta
        offset = y_note - y_staff
        
        # Verificar se está fora da pauta
        is_outside = (offset < 0) or (offset > 40)
        
        # Verificar se está em uma linha (múltiplo de 10, com tolerância)
        remainder = abs(offset % 10)
        is_on_line = (remainder < 2) or (remainder > 8)
        
        # Desenhar linhas suplementares PRIMEIRO (antes do círculo branco)
        if is_outside:
            supp_lines = note_helpers.get_supplementary_lines(y_note, y_staff)
            half_line_length = config.SUPPLEMENTARY_LINE_LENGTH // 2
            for supp_line_y in supp_lines:
                # Desenhar linha suplementar (pequena linha horizontal)
                canvas_obj.line(x_note - half_line_length, supp_line_y, 
                                x_note + half_line_length, supp_line_y)
        
        # Desenhar círculo branco APENAS se a nota está em um ESPAÇO (não em linha)
        # Isso se aplica tanto para notas dentro quanto fora da pauta
        if not is_on_line:
            canvas_obj.setFillColorRGB(1, 1, 1)  # Branco
            canvas_obj.circle(x_note, y_note, config.NOTE_RADIUS, stroke=0, fill=1)
            canvas_obj.setFillColorRGB(0, 0, 0)  # Voltar para preto
        
        # Cabeça da nota (apenas contorno, não preenchida)
        canvas_obj.circle(x_note, y_note, config.NOTE_RADIUS, stroke=1, fill=0)

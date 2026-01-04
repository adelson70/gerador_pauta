import random
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from src.config import settings
from src.core import note_helpers


class PautaPDFGenerator:
    
    def __init__(self):
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.clef_image_path = os.path.join(script_dir, "assets", "clave_de_sol.png")
    
    def generate(self, notes_sequence, quantity, output_path, num_pages, staff_gap_cm=None, random_mode=True, notes_per_staff=15):
        if not notes_sequence:
            raise ValueError("Nenhuma nota selecionada para gerar o PDF")
        
        c = canvas.Canvas(output_path, pagesize=settings.PAGE_SIZE)
        
        if staff_gap_cm is not None:
            staff_gap = staff_gap_cm * cm
        else:
            staff_gap = 4 * cm
        
        for page in range(num_pages):
            if page > 0:
                c.showPage()
            
            for staff_index in range(quantity):
                y_staff = settings.Y_START - staff_index * staff_gap
                
                target_notes_count = notes_per_staff
                if random_mode:
                    if len(notes_sequence) >= target_notes_count:
                        current_staff_notes = random.sample(notes_sequence, target_notes_count)
                    else:
                        current_staff_notes = []
                        while len(current_staff_notes) < target_notes_count:
                            remaining = target_notes_count - len(current_staff_notes)
                            current_staff_notes.extend(random.sample(notes_sequence, min(remaining, len(notes_sequence))))
                else:
                    current_staff_notes = notes_sequence * (target_notes_count // len(notes_sequence))
                    current_staff_notes.extend(notes_sequence[:target_notes_count % len(notes_sequence)])
                
                self._draw_staff(c, y_staff)
                self._draw_notes(c, current_staff_notes, y_staff, notes_per_staff)
        
        c.save()
    
    def _draw_staff(self, canvas_obj, y_staff):
        for line in range(5):
            line_y = y_staff + line * 10
            canvas_obj.line(settings.X_START, line_y, settings.X_START + settings.STAFF_WIDTH, line_y)
        
        staff_top = y_staff
        staff_bottom = y_staff + 40
        canvas_obj.line(settings.BARLINE_X, staff_top, settings.BARLINE_X, staff_bottom)
        
        self._draw_clef(canvas_obj, y_staff)
    
    def _draw_clef(self, canvas_obj, y_staff):
        if not os.path.exists(self.clef_image_path):
            canvas_obj.line(settings.X_START, y_staff, settings.X_START, y_staff + 40)
            return
        
        line1_y = y_staff
        line2_y = y_staff + 10
        line5_y = y_staff + 40
        
        clef_height = 70
        clef_width = 70
        
        clef_x = settings.X_START - 0.5 * cm
        
        clef_y = line2_y - (clef_height / 2) + 7
        
        try:
            canvas_obj.drawImage(
                self.clef_image_path,
                clef_x,
                clef_y,
                width=clef_width,
                height=clef_height,
                mask='auto',
                preserveAspectRatio=True
            )
        except Exception as e:
            print(f"Erro ao desenhar clave de sol: {e}")
            canvas_obj.line(settings.X_START, y_staff, settings.X_START, y_staff + 40)
    
    def _draw_notes(self, canvas_obj, notes, y_staff, notes_per_staff):
        from reportlab.lib.units import cm
        clef_width_pt = 70
        clef_x_offset = -0.5 * cm
        clef_start = settings.X_START + clef_x_offset
        clef_end = clef_start + clef_width_pt
        
        note_start = clef_end + 0.05 * cm
        
        margin_before_bar = 0.3 * cm
        
        last_note_center_x = settings.BARLINE_X - margin_before_bar - settings.NOTE_RADIUS
        note_spacing = (last_note_center_x - note_start) / (notes_per_staff - 1) if notes_per_staff > 1 else 0
        
        note_positions = []
        x = note_start
        
        max_x = settings.BARLINE_X - margin_before_bar
        
        for note in notes:
            if note not in settings.NOTE_POSITIONS:
                continue
            
            if x + settings.NOTE_RADIUS > max_x:
                break
            
            y = y_staff + settings.NOTE_POSITIONS[note]
            note_positions.append((x, y, note))
            x += note_spacing
        
        for x_note, y_note, note_name in note_positions:
            self._draw_note(canvas_obj, x_note, y_note, y_staff)
    
    def _draw_note(self, canvas_obj, x_note, y_note, y_staff):
        offset = y_note - y_staff
        
        is_outside = (offset < 0) or (offset > 40)
        
        remainder = abs(offset % 10)
        is_on_line = (remainder < 2) or (remainder > 8)
        
        if is_outside:
            supp_lines = note_helpers.get_supplementary_lines(y_note, y_staff)
            half_line_length = settings.SUPPLEMENTARY_LINE_LENGTH // 2
            for supp_line_y in supp_lines:
                canvas_obj.line(x_note - half_line_length, supp_line_y, 
                                x_note + half_line_length, supp_line_y)
        
        if not is_on_line:
            canvas_obj.setFillColorRGB(1, 1, 1)
            canvas_obj.circle(x_note, y_note, settings.NOTE_RADIUS, stroke=0, fill=1)
            canvas_obj.setFillColorRGB(0, 0, 0)
        
        canvas_obj.circle(x_note, y_note, settings.NOTE_RADIUS, stroke=1, fill=0)


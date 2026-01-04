import math


def is_note_on_line(y, y_staff, tolerance=2):
    offset = y - y_staff
    if 0 <= offset <= 40:
        remainder = abs(offset % 10)
        if remainder < tolerance or remainder > (10 - tolerance):
            line_y = y_staff + round(offset / 10) * 10
            return True, line_y
    return False, None


def is_note_in_space(y, y_staff, tolerance=2):
    if y < y_staff or y > y_staff + 40:
        return False, None
    
    is_on_line, _ = is_note_on_line(y, y_staff, tolerance=tolerance)
    if not is_on_line:
        offset = y - y_staff
        space_y = y_staff + (round(offset / 10) * 10) + 5
        return True, space_y
    
    return False, None


def is_note_outside_staff(y, y_staff):
    return y < y_staff or y > y_staff + 40


def is_note_on_supplementary_line(y, y_staff, tolerance=0.5):
    if not is_note_outside_staff(y, y_staff):
        return False, None
    
    offset = y - y_staff
    remainder = abs(offset % 10)
    
    if remainder < tolerance or remainder > (10 - tolerance):
        line_y = y_staff + round(offset / 10) * 10
        return True, line_y
    
    return False, None


def get_supplementary_lines(y, y_staff, tolerance=0.5):
    if not is_note_outside_staff(y, y_staff):
        return []
    
    lines = []
    offset = y - y_staff
    
    remainder = abs(offset % 10)
    is_on_line = (remainder < tolerance) or (remainder > (10 - tolerance))
    
    if y < y_staff:
        if is_on_line:
            start_offset = round(offset / 10) * 10
        else:
            start_offset = math.floor(offset / 10) * 10
        
        current_offset = start_offset
        while current_offset < 0:
            lines.append(y_staff + current_offset)
            current_offset += 10
            
    else:
        if is_on_line:
            end_offset = round(offset / 10) * 10
        else:
            end_offset = math.ceil(offset / 10) * 10
        
        current_offset = 50
        while current_offset <= end_offset:
            lines.append(y_staff + current_offset)
            current_offset += 10
    
    return lines


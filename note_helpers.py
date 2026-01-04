"""
Módulo com funções auxiliares para cálculos de posição de notas.
Funções puras para verificação de posicionamento de notas nas pautas.
"""
import math


def is_note_on_line(y, y_staff, tolerance=2):
    """Verifica se a nota está exatamente em uma linha da pauta"""
    # Verificar se está próximo de um múltiplo de 10 (linhas estão em 0, 10, 20, 30, 40)
    offset = y - y_staff
    if 0 <= offset <= 40:
        remainder = abs(offset % 10)
        if remainder < tolerance or remainder > (10 - tolerance):
            # Está próximo de uma linha
            line_y = y_staff + round(offset / 10) * 10
            return True, line_y
    return False, None


def is_note_in_space(y, y_staff, tolerance=2):
    """Verifica se a nota está em um espaço entre linhas (dentro da pauta)"""
    if y < y_staff or y > y_staff + 40:
        return False, None
    
    # Se não está em uma linha, está em um espaço
    is_on_line, _ = is_note_on_line(y, y_staff, tolerance=tolerance)
    if not is_on_line:
        # Calcular qual espaço
        offset = y - y_staff
        space_y = y_staff + (round(offset / 10) * 10) + 5
        return True, space_y
    
    return False, None


def is_note_outside_staff(y, y_staff):
    """Verifica se a nota está fora da pauta (requer linha suplementar)"""
    return y < y_staff or y > y_staff + 40


def is_note_on_supplementary_line(y, y_staff, tolerance=0.5):
    """Verifica se a nota está em uma linha suplementar (fora da pauta, mas em múltiplo de 10)"""
    if not is_note_outside_staff(y, y_staff):
        return False, None
    
    # Verificar se está em múltiplo de 10 relativo a y_staff
    offset = y - y_staff
    remainder = abs(offset % 10)
    
    # Se o resto está próximo de 0 ou 10, está em uma linha
    if remainder < tolerance or remainder > (10 - tolerance):
        # Está em uma linha suplementar
        line_y = y_staff + round(offset / 10) * 10
        return True, line_y
    
    return False, None


def get_supplementary_lines(y, y_staff, tolerance=0.5):
    """Retorna TODAS as linhas suplementares entre a nota e a pauta"""
    if not is_note_outside_staff(y, y_staff):
        return []
    
    lines = []
    offset = y - y_staff
    
    # Calcular se a nota está em linha ou espaço
    remainder = abs(offset % 10)
    is_on_line = (remainder < tolerance) or (remainder > (10 - tolerance))
    
    if y < y_staff:
        # Nota abaixo da pauta - desenhar TODAS as linhas entre a nota e a pauta
        # offset é negativo (ex: -20 para Sol3, -15 para La3, -10 para Si3, -5 para Do4)
        
        # Determinar a linha mais baixa (onde começa)
        if is_on_line:
            # Nota está em linha suplementar
            start_offset = round(offset / 10) * 10
        else:
            # Nota está em espaço suplementar - começar da linha abaixo do espaço
            start_offset = math.floor(offset / 10) * 10
        
        # Desenhar todas as linhas desde a nota até logo abaixo da pauta
        current_offset = start_offset
        while current_offset < 0:  # Enquanto está abaixo da pauta (offset < 0)
            lines.append(y_staff + current_offset)
            current_offset += 10
            
    else:
        # Nota acima da pauta - desenhar TODAS as linhas entre a pauta e a nota
        # offset é positivo (ex: 45 para Fa5, 50 para Sol5, 55 para La5, 60 para Si5)
        
        # Determinar a linha mais alta (onde termina)
        if is_on_line:
            # Nota está em linha suplementar
            end_offset = round(offset / 10) * 10
        else:
            # Nota está em espaço suplementar - terminar na linha acima do espaço
            end_offset = math.ceil(offset / 10) * 10
        
        # Desenhar todas as linhas desde acima da pauta até a nota
        current_offset = 50  # Primeira linha acima da pauta
        while current_offset <= end_offset:
            lines.append(y_staff + current_offset)
            current_offset += 10
    
    return lines


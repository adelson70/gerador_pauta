"""
Módulo de configurações e constantes do gerador de pautas de violino.
Centraliza todas as constantes utilizadas na geração do PDF.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# ===== CONFIGURAÇÕES DE PDF =====
PAGE_SIZE = A4
PAGE_WIDTH, PAGE_HEIGHT = A4

# ===== POSIÇÃO DAS NOTAS =====
# Referência: linha inferior da pauta (linha 1) = Mi4
# Linhas da pauta (0, 10, 20, 30, 40): Mi4, Sol4, Si4, Re5, Fa5
# Espaços da pauta (5, 15, 25, 35): Fa4, La4, Do5, Mi5
NOTE_POSITIONS = {
    "Sol3": -25, "La3": -20, "Si3": -15, "Do4": -10, "Re4": -5,
    "Mi4": 0,   "Fa4": 5,   "Sol4": 10, "La4": 15, "Si4": 20,
    "Do5": 25,  "Re5": 30,  "Mi5": 35, "Fa5": 40,
    "Sol5": 45, "La5": 50,  "Si5": 55
}

# ===== SEQUÊNCIA PADRÃO DE NOTAS =====
# Treino percorrendo as 4 cordas do violino:
# Corda SOL: Sol3, La3, Si3, Do4, Re4
# Corda RÉ:  Re4, Mi4, Fa4, Sol4, La4
# Corda LÁ:  La4, Si4, Do5, Re5, Mi5
# Corda MI:  Mi5, Fa5, Sol5, La5, Si5
DEFAULT_SEQUENCE = [
    "Sol3", "La3", "Si3", "Do4", "Re4",  # Corda SOL
    "Mi4", "Fa4", "Sol4", "La4",          # Corda RÉ (continua de Re4)
    "Si4", "Do5", "Re5", "Mi5",           # Corda LÁ (continua de La4)
    "Fa5", "Sol5", "La5", "Si5"           # Corda MI (continua de Mi5)
]

# ===== NOTAS ORGANIZADAS POR CORDA =====
NOTES_BY_STRING = {
    "SOL": ["Sol3", "La3", "Si3", "Do4", "Re4"],
    "RÉ": ["Mi4", "Fa4", "Sol4", "La4"],
    "LÁ": ["Si4", "Do5", "Re5", "Mi5"],
    "MI": ["Fa5", "Sol5", "La5", "Si5"]
}

# ===== CONFIGURAÇÃO DE LAYOUT =====
X_START = 2 * cm
STAFF_WIDTH = PAGE_WIDTH - 4 * cm
Y_START = PAGE_HEIGHT - 3 * cm  # Começar do topo com margem pequena
CLEF_WIDTH = 1.2 * cm  # Largura aproximada da clave de sol
BARLINE_X = X_START + STAFF_WIDTH  # Posição X da barra final

# Limites
MAX_STAFFS_PER_PAGE = 6  # Máximo de pautas por folha

# Espaçamento entre notas
# Calcular para caber exatamente 17 notas por pauta (sequência completa)
# Largura da clave: 70 pontos (definido no pdf_generator.py)
# Largura disponível = STAFF_WIDTH - largura_clave - margem da barra
# Espaçamento = largura_disponível / 17
CLEF_WIDTH_PT = 70  # Largura da clave de sol em pontos (para cálculo de espaçamento)
available_width_for_notes = STAFF_WIDTH - CLEF_WIDTH_PT - 0.3 * cm
NOTE_X_SPACING = available_width_for_notes / 17
NOTE_X_OFFSET = CLEF_WIDTH_PT + 0.2 * cm  # Offset inicial da primeira nota (depois da clave)

# Tamanho das notas
NOTE_RADIUS = 4
SUPPLEMENTARY_LINE_LENGTH = 16  # Comprimento das linhas suplementares (±8 de cada lado)


# Gerador de Pautas - Violino

Aplicação gráfica para gerar pautas de violino em PDF com interface intuitiva.

## Requisitos do Sistema

### Fedora Linux

Instale o tkinter (necessário para a interface gráfica):

```bash
sudo dnf install python3-tkinter
```

### Ubuntu/Debian

```bash
sudo apt-get install python3-tk
```

### Outras distribuições

Consulte a documentação da sua distribuição para instalar o pacote Python tkinter correspondente.

## Instalação

1. **Instale o tkinter no sistema** (necessário antes de instalar as dependências Python):

   Fedora:
   ```bash
   sudo dnf install python3-tkinter
   ```

   Ubuntu/Debian:
   ```bash
   sudo apt-get install python3-tk
   ```

2. **Instale as dependências Python**:

```bash
pip install -r requirements.txt
```

   **Nota importante**: Se você instalou o tkinter após já ter o Pillow instalado, pode ser necessário reinstalá-lo:
   ```bash
   pip install --upgrade --force-reinstall Pillow
   ```

3. Execute a aplicação:

```bash
python3 main.py
```

## Funcionalidades

- Seleção de notas por corda (SOL, RÉ, LÁ, MI)
- Modo sequencial ou aleatório
- Preview do PDF antes de gerar
- Escolha do local de salvamento
- Interface gráfica intuitiva com tkinter

## Estrutura do Projeto

- `main.py` - Ponto de entrada da aplicação
- `config.py` - Constantes e configurações
- `note_helpers.py` - Funções auxiliares de notas
- `pdf_generator.py` - Lógica de geração de PDF
- `gui_widgets.py` - Widgets personalizados da GUI
- `gui_main.py` - Interface gráfica principal


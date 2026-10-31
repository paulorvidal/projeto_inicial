# Projeto Inicial — MASPY

Simulação de agentes Walker competindo por dois targets com valores diferentes.

## Pré-requisitos

- Windows com PowerShell.
- Python instalado e disponível no terminal. Versão utilizada: **3.14.4**.
- Git instalado para clonar o repositório.

## Como executar

### 1. Clonar o repositório

```powershell
git clone https://github.com/paulorvidal/projeto_inicial.git
cd projeto_inicial
```

### 2. Criar o ambiente virtual

```powershell
python -m venv venv
```

### 3. Instalar as dependências

```powershell
.\venv\Scripts\python.exe -m pip install maspy-ml==2026.5.13 maspy-gui==2026.5.13.post3 pygame-ce==2.5.8
```

- **maspy-ml:** framework dos agentes.
- **maspy-gui:** dependência importada pelo código atual.
- **pygame-ce:** visualização gráfica da simulação.

As demais dependências são instaladas automaticamente pelo pip.

### 4. Iniciar a aplicação

Na raiz do projeto, execute:

```powershell
.\venv\Scripts\python.exe .\trabalho\Walker_Main.py
```

Ou abra `trabalho/Walker_Main.py` no VS Code e clique no botão **▶ Run Python File**, com o interpretador do `venv` selecionado.

Clique em **Start Simulation** e aguarde o treinamento inicial dos agentes.


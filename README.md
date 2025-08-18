# Projeto de Simulação e Análise de Portfólio de Crédito

## 📊 Visão Geral do Projeto

Este projeto simula um portfólio de contratos de crédito, calcula métricas financeiras e de risco, aplica uma alocação de fluxo de caixa em um modelo de *waterfall* (tranches Sênior e Subordinada) e gera relatórios automáticos em Excel e PDF. O objetivo é fornecer uma ferramenta completa para análise de performance e risco de um portfólio de crédito.

## ✨ Funcionalidades Principais

- **Simulação de Contratos**: Geração de um portfólio diversificado de contratos de crédito (financiamento, consignado, cartão) com atributos realistas (principal, taxa de juros, prazo, probabilidade de default e taxa de recuperação).
- **Geração de Fluxo de Caixa**: Simulação detalhada do fluxo de caixa mensal para cada contrato, aplicando a Tabela Price e incorporando eventos de default e recuperação.
- **Cálculo de Métricas Chave**: Determinação de indicadores financeiros e de risco, como saldo total do portfólio, taxa de inadimplência e Retorno Interno de Retorno (IRR) esperado.
- **Alocação Waterfall**: Distribuição do fluxo de caixa real entre diferentes tranches (Sênior e Subordinada) com base em percentuais predefinidos, simulando a estrutura de capital de uma securitização ou fundo.
- **Geração de Relatórios Automáticos**: Criação de relatórios completos em:
    - **Excel (.xlsx)**: Contendo um resumo de KPIs, o fluxo de caixa mensal detalhado e a alocação do waterfall, além de gráficos visuais.
    - **PDF (.pdf)**: Um resumo executivo de uma página com os principais KPIs e gráficos ilustrativos.
- **Pipeline Dinâmico**: Um script principal (`main.ipynb` ou `main.py`) que orquestra todas as etapas do pipeline de forma sequencial e dinâmica, com logging detalhado e organização dos artefatos gerados por timestamp.

## 📂 Estrutura do Projeto

.
├── data/                   # Armazena os CSVs gerados pela simulação (portifolio.csv, cashflows.csv)
├── reports/                # Contém os relatórios gerados (Excel, PDF, gráficos) organizados por timestamp
│   └── run_YYYYMMDD_HHMMSS/
│       ├── report.xlsx
│       ├── report.pdf
│       ├── fluxo_chart.png
│       └── waterfall_chart.png
├── src/
│   ├── Simulate_Portifolio.py  # Módulo para simulação de contratos e fluxos de caixa
│   ├── calculete_metrics.py    # Módulo para cálculo de métricas do portfólio
│   ├── allocate_waterfall.py   # Módulo para alocação de fluxo no modelo waterfall
│   ├── generate_reports.py     # Módulo para geração de relatórios em Excel e PDF
│   └── main.ipynb              # Notebook principal que orquestra todo o pipeline
└── README.md               # Este arquivo

**Nota**: Os arquivos `.ipynb` mencionados na estrutura podem ser convertidos para `.py` para uso em scripts Python tradicionais, mantendo a modularidade.

## 🚀 Como Rodar o Projeto

Para executar o pipeline completo e gerar os relatórios, siga os passos abaixo:

### Pré-requisitos

Certifique-se de ter as seguintes bibliotecas Python instaladas:

```bash
pip install pandas numpy matplotlib openpyxl reportlab
```

### Execução via Jupyter Notebook

1. Navegue até o diretório `src/`.
2. Abra o `main.ipynb` em um ambiente Jupyter (Jupyter Notebook ou JupyterLab).
3. Execute todas as células do notebook.

```bash
# Exemplo de como iniciar o Jupyter (se não estiver rodando)
jupyter notebook
```

Ao final da execução, os arquivos `portifolio.csv` e `cashflows.csv` serão salvos na pasta `data/`, e os relatórios (`.xlsx` e `.pdf`) junto com os gráficos serão gerados em um novo subdiretório dentro de `reports/` (ex: `reports/run_20250818_103045/`).

## ⚙️ Parâmetros Configuráveis

No `main.ipynb`, você pode ajustar os seguintes parâmetros no início do script:

```python
N_CONTRACTS = 10_000    # Número de contratos a serem simulados
SEED = 42               # Semente para reprodutibilidade da simulação
SENIOR_PERC = 0.8       # Percentual do fluxo de caixa destinado à Tranche Sênior no waterfall
```

## 🤝 Contribuição

Sinta-se à vontade para explorar, modificar e aprimorar este projeto. Sugestões e melhorias são bem-vindas!

---
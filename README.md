🌾 Agri-Trend Sentinel: AI-Driven Commodity Forecasting
Status do Projeto: 🏗️ Em Planejamento / Desenvolvimento Inicial

1. Visão Geral
O Agri-Trend Sentinel é uma solução de inteligência de mercado focada no agronegócio. O objetivo é democratizar o acesso à análise técnica de commodities, oferecendo previsões de tendência (Curto, Médio e Longo Prazo) e monitoramento automatizado via Agentes de IA.

Diferente de dashboards passivos, este projeto atua ativamente: um Agente Autônomo monitora os mercados e envia alertas por e-mail quando identifica configurações gráficas favoráveis, justificando a oportunidade com dados e linguagem natural.

2. O Problema
Produtores rurais e analistas de logística enfrentam dois problemas principais:

Excesso de Ruído: Acompanhar cotações diárias de Soja, Milho e Café gera ansiedade e decisões precipitadas.

Falta de Tempo: Monitorar múltiplos gráficos para identificar reversões de tendência exige dedicação integral.

Solução: Um sistema que filtra o ruído, foca na tendência (macro) e notifica apenas quando relevante.

3. Arquitetura da Solução
O projeto será desenvolvido em Python, utilizando Jupyter Notebooks para prototipagem e validação, e Streamlit para a interface final.

🛠️ Tech Stack
Linguagem: Python 3.10+

Coleta de Dados: yfinance (Yahoo Finance API)

Processamento & ETL: Pandas, NumPy

Visualização: Plotly (Gráficos Interativos) e Matplotlib (Geração de imagens estáticas para e-mail)

Modelagem de Tendência: Médias Móveis Exponenciais (EMA), RSI, MACD e Regressão Linear (Scikit-Learn).

Inteligência Artificial (O Agente): Google Gemini API (Geração de Análise de Mercado em Texto).

Interface: Streamlit.

Automação: smtplib (Envio de E-mails) e GitHub Actions (Agendamento).

4. Roteiro de Desenvolvimento (Roadmap)
O projeto será executado em 5 fases distintas:

🔹 Fase 1: Engenharia de Dados (ETL)
Objetivo: Criar um pipeline robusto que baixa dados brutos, trata feriados/nulos e padroniza o formato.

Entrega: Script etl_commodities.py e dataset limpo (commodities_tratado.csv).

Ambiente: Jupyter Notebook.

🔹 Fase 2: Motor de Análise Técnica
Objetivo: Implementar a lógica matemática que define "Tendência".

Funcionalidade:

Cálculo de Janelas Temporais: Mensal (Curto), Trimestral (Médio), Semestral (Longo).

Indicadores: Cruzamento de Médias e Força Relativa (RSI).

Entrega: Notebook de validação com gráficos plotados.

🔹 Fase 3: O Agente de IA (Cérebro)
Objetivo: Integrar a API do Gemini para "ler" os números da Fase 2 e gerar um texto analítico.

Prompt Engineering: Criar o comando certo para que a IA atue como um "Analista Sênior de Commodities".

Entrega: Função que recebe um DataFrame e retorna um texto: "A Soja rompeu a resistência de $12.50, indicando alta para o próximo trimestre..."

🔹 Fase 4: Interface do Usuário (Dashboard)
Objetivo: Permitir que o usuário explore os dados interativamente.

Funcionalidade: Seletor de Commodities e visualização das previsões.

Entrega: Aplicação app.py rodando no Streamlit.

🔹 Fase 5: Automação e Notificação (O Robô)
Objetivo: O sistema roda sozinho, identifica o "Destaque da Semana" e envia um e-mail.

Entrega: Script daily_job.py e configuração de disparo de e-mail com anexo.

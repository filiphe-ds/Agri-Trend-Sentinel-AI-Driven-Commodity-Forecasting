import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from google import genai
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agri-Trend Sentinel", layout="wide", page_icon="🌾")

# --- CSS CUSTOMIZADO (Para ficar bonitão) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA IA (Pegando do secrets.toml) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("⚠️ Chave de API não encontrada! Crie o arquivo .streamlit/secrets.toml")
    st.stop()

# --- FUNÇÕES DE CARREGAMENTO (ETL) ---
@st.cache_data(ttl=3600) # Cache de 1 hora para não ficar baixando toda hora
def carregar_dados(ticker):
    df = yf.download(ticker, period="2y", progress=False)
    
    # Tratamento de MultiIndex do Yahoo
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs(ticker, level=1, axis=1)
        except:
            pass
            
    df.reset_index(inplace=True)
    
    # Cálculos Técnicos
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # RSI Manual
    delta = df['Close'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganho / perda
    df['RSI'] = 100 - (100 / (1 + rs))
    
    return df

# --- INTERFACE LATERAL ---
st.sidebar.title("🌾 Agri-Sentinel")
commodities = {
    "Soja (Soybean)": "ZS=F",
    "Milho (Corn)": "ZC=F",
    "Café Arábica": "KC=F",
    "Boi Gordo": "LE=F",
    "Ouro": "GC=F"
}
escolha = st.sidebar.selectbox("Selecione o Ativo:", list(commodities.keys()))
ticker_escolhido = commodities[escolha]

# --- MAIN APP ---
st.title(f"Análise de Mercado: {escolha}")

with st.spinner("Baixando dados do mercado..."):
    df = carregar_dados(ticker_escolhido)

if df.empty:
    st.error("Erro ao carregar dados. Tente novamente mais tarde.")
    st.stop()

# Pegar última linha
ultimo = df.iloc[-1]
penultimo = df.iloc[-2]
variacao = ((ultimo['Close'] - penultimo['Close']) / penultimo['Close']) * 100

# --- KPI CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Preço Atual", f"${ultimo['Close']:.2f}", f"{variacao:.2f}%")
col2.metric("RSI (14 dias)", f"{ultimo['RSI']:.1f}", "Sobrecompra > 70" if ultimo['RSI'] > 70 else "Normal")
col3.metric("Média 200 (Tendência)", f"${ultimo['SMA_200']:.2f}")

# Lógica simples para cor do texto
tendencia = "ALTA 🐂" if ultimo['Close'] > ultimo['SMA_200'] else "BAIXA 🐻"
col4.metric("Tendência Primária", tendencia)

# --- GRÁFICO ---
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Preço"))
fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_200'], line=dict(color='orange', width=2), name="Média 200"))
fig.update_layout(height=500, title="Gráfico Técnico Diário", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# --- O AGENTE DE IA ---
st.subheader("🤖 Agente de Inteligência Artificial")
st.info("O Agente analisa os indicadores técnicos e gera um resumo executivo.")

if st.button("Gerar Análise do Agente"):
    with st.spinner("O Agente está lendo o gráfico..."):
        # Preparar o Prompt
        dados_texto = f"""
        Ativo: {escolha}
        Preço: {ultimo['Close']:.2f}
        Média 200: {ultimo['SMA_200']:.2f}
        RSI: {ultimo['RSI']:.2f}
        Tendência Técnica: {tendencia}
        """
        
        prompt = """
        Você é um Trader Institucional Sênior. Analise os dados abaixo e forneça:
        1. Contexto da Tendência (O preço está esticado? Está revertendo?)
        2. Análise do RSI (Há espaço para subir ou risco de queda?)
        3. Veredito Final (Compra, Venda ou Aguardar).
        Seja direto e use linguagem profissional de mercado financeiro.
        """
        
        try:
            # Usando o modelo que funcionou para você!
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt + "\n\nDados:\n" + dados_texto
            )
            
            st.success("Análise Gerada!")
            st.markdown(f"### 📝 Relatório do Agente\n{response.text}")
            
        except Exception as e:
            st.error(f"Erro ao conectar com o Agente: {e}")
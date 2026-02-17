import yfinance as yf
import pandas as pd
import os
from google import genai
from datetime import datetime

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
def pegar_chave_api():
    """Lê a chave do arquivo secrets.toml sem precisar de biblioteca extra"""
    try:
        with open(".streamlit/secrets.toml", "r") as f:
            for linha in f:
                if "GEMINI_API_KEY" in linha:
                    # Limpa a string para pegar só o código
                    return linha.split('=')[1].strip().replace('"', '').replace("'", "")
    except Exception as e:
        print(f"❌ Erro ao ler segredos: {e}")
        return None

API_KEY = pegar_chave_api()
client = genai.Client(api_key=API_KEY)

# --- 2. LISTA DE VIGILÂNCIA ---
COMMODITIES = {
    "Soja (Soybean)": "ZS=F",
    "Milho (Corn)": "ZC=F",
    "Café Arábica": "KC=F",
    "Boi Gordo": "LE=F",
    "Ouro": "GC=F"
}

# --- 3. MOTOR TÉCNICO (O CÁLCULO) ---
def analisar_tecnica(ticker):
    # Baixa dados (período curto para ser rápido)
    df = yf.download(ticker, period="1y", progress=False)
    
    # Tratamento básico (igual ao do App)
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs(ticker, level=1, axis=1)
        except:
            pass
    df.reset_index(inplace=True)

    # Indicadores
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # RSI (Cálculo Otimizado)
    delta = df['Close'].diff()
    ganho = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perda = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganho / perda
    df['RSI'] = 100 - (100 / (1 + rs))

    return df.iloc[-1] # Retorna só o dado de hoje

# --- 4. O FILTRO INTELIGENTE (SCREENER) ---
def verificar_gatilho(dados):
    """
    Retorna True se houver uma oportunidade técnica clara.
    Isso economiza dinheiro (tokens da IA) e tempo.
    """
    preco = dados['Close']
    sma200 = dados['SMA_200']
    rsi = dados['RSI']
    
    motivo = []
    
    # Regra 1: RSI Extremo (Reversão à média)
    if rsi < 30:
        motivo.append("RSI SOBREVENDIDO (Oportunidade de Compra)")
    elif rsi > 70:
        motivo.append("RSI SOBRECOMPRADO (Risco de Queda)")
        
    # Regra 2: Distância da Média (Tendência)
    distancia_media = ((preco - sma200) / sma200) * 100
    if abs(distancia_media) < 2: # Se estiver a 2% da média (Cruzamento)
        motivo.append("TESTE DE SUPORTE/RESISTÊNCIA NA MÉDIA DE 200")

    return motivo # Se lista vazia, retorna False (Python considera lista vazia como False)

# --- 5. O ESCRITOR (IA + ARQUIVO) ---
def gerar_alerta(nome, dados, motivos):
    print(f"🚨 OPORTUNIDADE ENCONTRADA EM: {nome}")
    
    # Prompt focado em Email Executivo
    prompt = f"""
    Você é um Consultor de Agronegócio. Escreva um E-MAIL CURTO para um produtor rural.
    
    Assunto: Alerta de Oportunidade - {nome}
    Dados Técnicos:
    - Preço: ${dados['Close']:.2f}
    - RSI: {dados['RSI']:.2f}
    - Gatilho Técnico: {', '.join(motivos)}
    
    Instrução: Explique por que esse gatilho técnico é importante e sugira uma ação (Hedge, Venda ou Compra).
    Seja profissional e direto.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Ou 'gemini-flash-latest'
            contents=prompt
        )
        
        # Salva no arquivo de simulação
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("CAIXA_DE_SAIDA_SIMULADA.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{'='*40}\n")
            f.write(f"DATA DO ENVIO: {timestamp}\n")
            f.write(f"PARA: usuario@agri-sentinel.com\n")
            f.write(f"CONTEÚDO GERADO PELA IA:\n")
            f.write(f"{response.text}\n")
            f.write(f"{'='*40}\n")
            
        print("✅ Email simulado salvo em 'CAIXA_DE_SAIDA_SIMULADA.txt'")
        
    except Exception as e:
        print(f"❌ Erro na IA: {e}")

# --- 6. EXECUÇÃO PRINCIPAL ---
print("🤖 Iniciando Ronda de Vigilância do Mercado...")

# Limpa o arquivo de email anterior
with open("CAIXA_DE_SAIDA_SIMULADA.txt", "w", encoding="utf-8") as f:
    f.write("--- INÍCIO DA SIMULAÇÃO DE ENVIOS ---\n")

for nome, ticker in COMMODITIES.items():
    print(f"🔎 Analisando {nome}...")
    try:
        dados_hoje = analisar_tecnica(ticker)
        motivos = verificar_gatilho(dados_hoje)
        
        if motivos:
            # Se achou motivo técnico, chama a IA
            gerar_alerta(nome, dados_hoje, motivos)
        else:
            print(f"   💤 Nada relevante em {nome} hoje. (RSI={dados_hoje['RSI']:.1f})")
            
    except Exception as e:
        print(f"   ⚠️ Erro ao processar {nome}: {e}")

print("\n🏁 Ronda Finalizada. Verifique o arquivo 'CAIXA_DE_SAIDA_SIMULADA.txt'.")
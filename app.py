import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime
import random
import time
import json

# --- SIMULAÇÃO DE CLIENTE AWS IOT ---
class AWSIoTMock:
    def publish(self, topic, payload):
        st.success(f"✅ Dados enviados para AWS IoT Core - Tópico: `{topic}`")
        with st.expander("📦 Payload enviado"):
            st.json(payload)

# --- CLASSE DO SISTEMA DE ENERGIA ---
class SmartEnergySystem:
    def __init__(self):
        self.aws_client = AWSIoTMock()
        self.historico_solar = []
        self.historico_bateria_ev = []
        self.historico_inversor = []
        self.timestamps = []
        self.bateria_ev_percent = 50
        self.producao_solar_kwh = 0
        self.status_inversor = "REDE"

    def gerar_dados_simulados(self):
        """Simula a leitura de sensores físicos"""
        agora = datetime.now().strftime("%H:%M:%S")
        self.timestamps.append(agora)

        variacao = random.randint(-2, 5)
        self.bateria_ev_percent += variacao
        self.bateria_ev_percent = max(0, min(100, self.bateria_ev_percent))
        self.historico_bateria_ev.append(self.bateria_ev_percent)

        eficiencia = random.randint(20, 100)
        self.producao_solar_kwh = eficiencia
        self.historico_solar.append(self.producao_solar_kwh)

        if self.producao_solar_kwh > 80:
            self.status_inversor = "SOLAR (Exportando)"
            carga = 1
        elif self.producao_solar_kwh > 40:
            self.status_inversor = "BATERIA (Armazenando)"
            carga = 0.5
        else:
            self.status_inversor = "REDE (Consumindo)"
            carga = -1

        self.historico_inversor.append(carga)
        return agora

    def enviar_para_nuvem(self):
        """Monta o pacote JSON e envia para AWS"""
        payload = {
            "device_id": "ESP32_OFFICE_01",
            "timestamp": datetime.now().isoformat(),
            "sensores": {
                "ev_battery": self.bateria_ev_percent,
                "solar_production": self.producao_solar_kwh,
                "inverter_status": self.status_inversor
            },
            "alerta": "Bateria Baixa" if self.bateria_ev_percent < 20 else "Normal"
        }
        self.aws_client.publish("energia/monitoramento/escritorio", payload)

# --- CONFIGURAÇÃO STREAMLIT ---
st.set_page_config(
    page_title="Smart Energy System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR SESSÃO ---
if 'sistema' not in st.session_state:
    st.session_state.sistema = SmartEnergySystem()

sistema = st.session_state.sistema

# --- HEADER ---
st.title("⚡ Global Solution - Smart Energy System")
st.markdown("*Monitoramento de Energia Solar, Carro Elétrico e Inversor Híbrido*")
st.divider()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎮 Controle do Sistema")
    
    opcao = st.radio(
        "Selecione uma ação:",
        options=["📊 Dashboard", "🔧 Controles", "📈 Relatório", "☁️ AWS IoT"]
    )

# --- PAGE 1: DASHBOARD ---
if opcao == "📊 Dashboard":
    st.header("Dashboard em Tempo Real")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🔋 Bateria EV",
            value=f"{sistema.bateria_ev_percent}%",
            delta=f"{sistema.historico_bateria_ev[-1] - sistema.historico_bateria_ev[-2] if len(sistema.historico_bateria_ev) > 1 else 0}%"
        )
        if sistema.bateria_ev_percent < 20:
            st.warning("⚠️ Bateria baixa! Carregamento urgente necessário.")
    
    with col2:
        st.metric(
            label="☀️ Painel Solar",
            value=f"{sistema.producao_solar_kwh}%",
            delta="Eficiência"
        )
    
    with col3:
        status_emoji = "🟢" if "SOLAR" in sistema.status_inversor else "🟡" if "BATERIA" in sistema.status_inversor else "🔴"
        st.metric(
            label="🔌 Inversor",
            value=status_emoji,
            delta=sistema.status_inversor
        )
    
    st.divider()
    
    # Botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Atualizar Sensores", key="update", use_container_width=True):
            tempo = sistema.gerar_dados_simulados()
            st.success(f"✅ Leitura realizada às {tempo}")
            st.rerun()
    
    with col2:
        if st.button("⚡ Simular N Leituras", key="multi", use_container_width=True):
            n = st.number_input("Quantas leituras?", min_value=1, max_value=20, value=5)
            progress_bar = st.progress(0)
            for i in range(n):
                sistema.gerar_dados_simulados()
                progress_bar.progress((i+1)/n)
            st.success(f"✅ {n} leituras realizadas!")
            st.rerun()
    
    st.divider()
    
    # Gráficos interativos com Plotly
    st.subheader("📈 Análise de Dados")
    
    if len(sistema.timestamps) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=sistema.timestamps,
                y=sistema.historico_solar,
                mode='lines+markers',
                name='Produção Solar',
                line=dict(color='orange', width=2),
                marker=dict(size=8)
            ))
            fig1.update_layout(
                title="☀️ Eficiência do Painel Solar",
                xaxis_title="Tempo",
                yaxis_title="Produção (%)",
                hovermode='x unified'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=sistema.timestamps,
                y=sistema.historico_bateria_ev,
                mode='lines+markers',
                name='Carga EV',
                line=dict(color='green', width=2),
                marker=dict(size=8),
                fill='tozeroy'
            ))
            fig2.update_layout(
                title="🔋 Nível da Bateria do Carro Elétrico",
                xaxis_title="Tempo",
                yaxis_title="Carga (%)",
                yaxis=dict(range=[0, 100]),
                hovermode='x unified'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Status do Inversor
        fig3 = go.Figure()
        cores = ['red' if x < 0 else 'yellow' for x in sistema.historico_inversor]
        fig3.add_trace(go.Bar(
            x=sistema.timestamps,
            y=sistema.historico_inversor,
            marker_color=cores,
            name='Status'
        ))
        fig3.update_layout(
            title="🔌 Status do Inversor Híbrido",
            xaxis_title="Tempo",
            yaxis_title="Modo",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("👆 Clique em 'Atualizar Sensores' para começar a coletar dados.")

# --- PAGE 2: CONTROLES ---
elif opcao == "🔧 Controles":
    st.header("Painel de Controle")
    
    st.subheader("🎚️ Simuladores Manuais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bateria_manual = st.slider("🔋 Ajustar Bateria EV (%)", 0, 100, sistema.bateria_ev_percent)
        sistema.bateria_ev_percent = bateria_manual
    
    with col2:
        solar_manual = st.slider("☀️ Ajustar Produção Solar (%)", 0, 100, sistema.producao_solar_kwh)
        sistema.producao_solar_kwh = solar_manual
    
    with col3:
        if sistema.producao_solar_kwh > 80:
            sistema.status_inversor = "SOLAR (Exportando)"
        elif sistema.producao_solar_kwh > 40:
            sistema.status_inversor = "BATERIA (Armazenando)"
        else:
            sistema.status_inversor = "REDE (Consumindo)"
        
        st.selectbox("🔌 Status Inversor", 
                    options=["REDE (Consumindo)", "BATERIA (Armazenando)", "SOLAR (Exportando)"],
                    index=0)
    
    st.divider()
    st.subheader("⚙️ Configurações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        modo_automatico = st.toggle("🤖 Modo Automático", value=False)
        if modo_automatico:
            intervalo = st.slider("Intervalo de atualização (seg)", 1, 10, 3)
            st.info(f"Sistema atualizará a cada {intervalo} segundos")
    
    with col2:
        limiar_alerta = st.slider("⚠️ Limiar de Alerta Bateria (%)", 0, 50, 20)

# --- PAGE 3: RELATÓRIO ---
elif opcao == "📈 Relatório":
    st.header("Relatório de Energia")
    
    if len(sistema.timestamps) > 1:
        # Criar DataFrame
        df = pd.DataFrame({
            'Tempo': sistema.timestamps,
            'Bateria EV (%)': sistema.historico_bateria_ev,
            'Solar (%)': sistema.historico_solar,
            'Inversor': ['REDE' if x < 0 else 'BATERIA' if x == 0.5 else 'SOLAR' for x in sistema.historico_inversor]
        })
        
        st.subheader("📊 Estatísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Média Bateria", f"{df['Bateria EV (%)'].mean():.1f}%")
        
        with col2:
            st.metric("Média Solar", f"{df['Solar (%)'].mean():.1f}%")
        
        with col3:
            st.metric("Máx Bateria", f"{df['Bateria EV (%)'].max()}%")
        
        with col4:
            st.metric("Mín Bateria", f"{df['Bateria EV (%)'].min()}%")
        
        st.divider()
        
        st.subheader("📋 Tabela de Dados")
        st.dataframe(df, use_container_width=True)
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"energia_relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Não há dados suficientes para gerar relatório.")

# --- PAGE 4: AWS IOT ---
elif opcao == "☁️ AWS IoT":
    st.header("Integração AWS IoT Core")
    
    st.info("📡 Envie dados em tempo real para a nuvem AWS")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configurações de Conexão")
        
        device_id = st.text_input("Device ID", value="ESP32_OFFICE_01")
        topic = st.text_input("Tópico MQTT", value="energia/monitoramento/escritorio")
        
        st.text_area(
            "Endpoint AWS",
            value="xxxxxxxx-ats.iot.us-east-1.amazonaws.com",
            disabled=True
        )
    
    with col2:
        st.subheader("Status")
        if st.button("🔌 Conectar AWS", use_container_width=True):
            with st.spinner("Conectando..."):
                time.sleep(1)
                st.success("✅ Conectado com sucesso!")
    
    st.divider()
    
    if st.button("📤 Enviar Dados para AWS", use_container_width=True, type="primary"):
        sistema.enviar_para_nuvem()
        
# --- FOOTER ---
st.divider()
st.markdown("""
    <center>
    <small>Global Solution - Soluções em Energias Renováveis e Sustentáveis</small><br>
    <small>Ciências da Computação 2º Semestre 2025</small>
    </center>
""", unsafe_allow_html=True)
# Global Solution — Smart Energy System (Interface Streamlit)

 **Resumo**
- Projeto de simulação e visualização de um sistema doméstico com painéis solares, carro elétrico e inversor híbrido.
- Interface construída com Streamlit para monitoramento em tempo real de dados simulados, controle manual, relatório e envio (simulado) para Alexa IoT.


**Descrição da Solução**

Desenvolvimento de um sistema backend IoT em Python que simula o gerenciamento inteligente de energia em um escritório corporativo. O sistema integra a geração de energia solar com o carregamento de veículos elétricos, otimizando o consumo para reduzir custos e pegada de carbono.


Funcionalidades principais
- Dashboard em tempo real: métricas de bateria EV, produção solar e status do inversor.
- Simulação: geração de leituras de sensores artificiais com histórico e gráficos interativos (Plotly).
- Controles manuais: sliders para ajustar bateria e produção solar; modo automático.
- Relatórios: estatísticas e exportação de CSV.
- Integração com a Alexa IoT

Estrutura do repositório
- app.py — aplicação Streamlit (interface principal).
- README.md — este arquivo.

Pré-requisitos
- Windows, Python 3.9+ (recomendado).
- Recomendado usar virtual environment.

Exemplo mínimo requirements.txt

    streamlit
    pandas
    plotly
    matplotlib
    numpy
    pytest

Para executar, vc vai abrir o terminal e colcar isso daqui:

    python -m streamlit run app.py




"""
Agente de IA para verificação de extintores em modelos IFC
==========================================================
Exemplo educativo: skill + tool com Agno + Claude

Este script demonstra o uso conjunto de:
1. uma skill com referência normativa
2. uma tool Python que lê um arquivo IFC

Dependências:
    pip install agno ifcopenshell groq fastapi uvicorn python-dotenv

Uso:
    python agente_extintores.py
"""



from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.skills import Skills, LocalSkills
from agno.tools import tool
from agno.os import AgentOS


# carrega GROQ_API_KEY de um arquivo .env (se existir)
load_dotenv()


# =============================================================================
# AGENTE — configuração e instruções de domínio
# =============================================================================
model = Groq(id="openai/gpt-oss-120b")

agente = Agent(
    id="AgenteExtintoresIFC",
    model=model,
    skills=Skills(loaders=[LocalSkills("./skills")]),    
    instructions=[
        "Quando o usuário pedir para verificar os extintores de um arquivo .ifc",
        "use a skill nbr15808 como referência técnica e use a tool ler_extintores_ifc para ler o arquivo IFC",
        "responda de forma curta e didática, adequada para demonstração em aula",
    ],
    markdown=True,
    debug_mode=True,
)

# usando o Agent OS (opcional, para servir o agente via API)
agent_os = AgentOS(
    id="AgenteExtintoresIFC",
    description="Agente para verificar extintores em arquivos IFC usando a NBR 15808 como referência",
    agents=[agente],
)

app=agent_os.get_app()



# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":

    arquivo_ifc = Path("extintores.ifc")

    
    # agente.print_response(
    #     f"Analise o arquivo '{arquivo_ifc}' usando a tool disponível e verifique, de forma simples, "
    #     f"se os extintores parecem compatíveis com a NBR 15808.",
    #     stream=True,
    # )   
    
   
    agent_os.serve(app="Aula_04_2_Agentes:app", reload=True)


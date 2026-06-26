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
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.skills import Skills, LocalSkills
from agno.tools import tool
from agno.os import AgentOS
import ifcopenshell
import ifcopenshell.util.element
import json
#from skills.nbr15808.scripts.ler_extintores_ifc import ler_extintores_ifc

def ler_extintores_ifc(caminho_ifc: str) -> str:
    """Lê um IFC e retorna um JSON simples com os extintores encontrados."""
    caminho = Path(caminho_ifc)
    if not caminho.is_absolute() and not caminho.exists():
        raiz_projeto = Path(__file__).resolve().parents[3]
        caminho_na_raiz = raiz_projeto / caminho
        if caminho_na_raiz.exists():
            caminho = caminho_na_raiz

    model = ifcopenshell.open(str(caminho))

    extintores = list(model.by_type("IfcFireSuppressionTerminal"))
    if not extintores:
        extintores = [
            elemento
            for elemento in model.by_type("IfcBuildingElementProxy")
            if elemento.Name and "extintor" in elemento.Name.lower()
        ]

    dados = []
    for extintor in extintores:
        psets = ifcopenshell.util.element.get_psets(extintor)
        pset_nbr = psets.get("FireExtinguisher_NBR15808", {})
        dados.append(
            {
                "id": extintor.GlobalId,
                "nome": extintor.Name or "Sem nome",
                "tipo_agente": pset_nbr.get("ExtinguisherType", "Não informado"),
                "capacidade_extintora": pset_nbr.get(
                    "ExtinguishingCapacity", "Não informada"
                ),
                "certificado_inmetro": pset_nbr.get(
                    "INMETRO_Certified", "Não informado"
                ),
            }
        )

    return json.dumps(
        {"arquivo": str(caminho), "total_extintores": len(dados), "extintores": dados},
        ensure_ascii=False,
        indent=2,
    )

# carrega GROQ_API_KEY e ANTHROPI_API_KEY de um arquivo .env (se existir)
load_dotenv()


# =============================================================================
# AGENTE — configuração e instruções de domínio
# =============================================================================
model = Claude(id="claude-sonnet-4-6")

agente = Agent(
    id="AgenteExtintoresIFC",
    model=model,
    skills=Skills(loaders=[LocalSkills("./skills")]),    
    tools=[ler_extintores_ifc],
    instructions=[
        "Quando o usuário pedir para verificar os extintores de um arquivo .ifc",
        "use a skill nbr15808 como referência técnica e use a tool ler_extintores_ifc para ler o arquivo IFC",
    ],
    markdown=True,
    debug_mode=False,
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


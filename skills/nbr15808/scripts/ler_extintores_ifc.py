import ifcopenshell
import json

def ler_extintores_ifc(caminho_ifc: str) -> str:
    """Lê um IFC e retorna um JSON simples com os extintores encontrados."""
    model = ifcopenshell.open(caminho_ifc)

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
        {"arquivo": caminho_ifc, "total_extintores": len(dados), "extintores": dados},
        ensure_ascii=False,
        indent=2,
    )


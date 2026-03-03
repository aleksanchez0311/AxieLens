from search_marketplace import fetch_marketplace
from itertools import combinations


def get_market_comparison(base_axie):
    """
    Lógica de búsqueda iterativa:
    1. Forma + 6 Evo + Clase + 6 Base (exacta).
    2. Sin forma + 6 Evo + Clase + 6 Base.
    3a. Sin ojos Evo + resto evo + Clase + 6 Base.
    3b. Sin orejas Evo + resto evo + Clase + 6 Base.
    4. Sin ojos Evo + Sin orejas Evo + probar combinaciones resto evo + Clase + 6 Base.
    5. Sin evo + clase + 6 partes base.
    6. Sin evo + sin clase + 6 partes base.
    7a. Sin evo + sin clase + sin ojos base + resto partes base.
    7b. Sin evo + sin clase + sin orejas base + resto partes base.
    8. Sin evo + sin clase + sin ojos base + sin orejas base + resto partes base.
    9. Sin evo + sin clase + sin ojos base + sin orejas base + probar 4 partes Base.
    """
    if not base_axie:
        return None, "Error de datos"

    base_class = base_axie.get("class")
    body_shape = base_axie.get("bodyShape")
    parts = base_axie.get("parts", [])

    base_parts = []
    evolved_parts = []
    priority_order = ["Eyes", "Ears", "Mouth", "Horn", "Back", "Tail"]

    for part in parts:
        part_id = part.get("id")
        part_type = part.get("type")
        stage = part.get("stage", 1)
        if stage == 2 or "_2" in str(part_id):
            evolved_parts.append({"id": part_id, "type": part_type})
        else:
            base_parts.append({"id": part_id, "type": part_type})

    # Ordenar por prioridad
    evolved_ordered = []
    for ptype in priority_order:
        for evo in evolved_parts:
            if evo["type"] == ptype:
                evolved_ordered.append(evo)
                break

    base_ordered = []
    for ptype in priority_order:
        for bp in base_parts:
            if bp["type"] == ptype:
                base_ordered.append(bp)
                break

    all_evolved_ids = [p["id"] for p in evolved_parts]
    all_base_ids = [p["id"] for p in base_parts]
    all_parts_ids = all_base_ids + all_evolved_ids

    steps = []

    # 1. Forma + 6 Evo + Clase + 6 Base (exacta)
    steps.append(
        {
            "desc": "1. Forma + 6 Evo + Clase + 6 Base (exacta)",
            "bodyShapes": [body_shape],
            "classes": [base_class],
            "parts": all_parts_ids,
            "remaining": all_parts_ids.copy(),
        }
    )

    # 2. Sin forma + 6 Evo + Clase + 6 Base
    steps.append(
        {
            "desc": "2. Sin forma + 6 Evo + Clase + 6 Base",
            "bodyShapes": None,
            "classes": [base_class],
            "parts": all_parts_ids,
            "remaining": all_parts_ids.copy(),
        }
    )

    # 3a. Sin ojos Evo + resto evo + Clase + 6 Base
    remaining_evo_after_eyes = [e for e in evolved_ordered if e["type"] != "Eyes"]
    if remaining_evo_after_eyes:
        remaining_evo_ids = [e["id"] for e in remaining_evo_after_eyes]
        remaining_parts = remaining_evo_ids + all_base_ids
        steps.append(
            {
                "desc": f"3a. Sin ojos Evo + {len(remaining_evo_ids)} evo + Clase + 6 Base",
                "bodyShapes": None,
                "classes": [base_class],
                "parts": remaining_parts,
                "remaining": remaining_parts.copy(),
            }
        )

    # 3b. Sin orejas Evo + resto evo + Clase + 6 Base
    remaining_evo_after_ears = [e for e in evolved_ordered if e["type"] != "Ears"]
    if remaining_evo_after_ears:
        remaining_evo_ids = [e["id"] for e in remaining_evo_after_ears]
        remaining_parts = remaining_evo_ids + all_base_ids
        steps.append(
            {
                "desc": f"3b. Sin orejas Evo + {len(remaining_evo_ids)} evo + Clase + 6 Base",
                "bodyShapes": None,
                "classes": [base_class],
                "parts": remaining_parts,
                "remaining": remaining_parts.copy(),
            }
        )

    # 4. Sin ojos Evo + Sin orejas Evo + probar combinaciones resto evo + Clase + 6 Base
    remaining_evo_after_eyes_ears = [
        e for e in evolved_ordered if e["type"] not in ["Eyes", "Ears"]
    ]
    if remaining_evo_after_eyes_ears:
        remaining_evo_ids = [e["id"] for e in remaining_evo_after_eyes_ears]
        remaining_parts = remaining_evo_ids + all_base_ids
        steps.append(
            {
                "desc": f"4. Sin ojos+orejas Evo + {len(remaining_evo_ids)} evo + Clase + 6 Base",
                "bodyShapes": None,
                "classes": [base_class],
                "parts": remaining_parts,
                "remaining": remaining_parts.copy(),
            }
        )

    # 5. Sin evo + clase + 6 partes base
    steps.append(
        {
            "desc": "5. Sin evo + clase + 6 partes base",
            "bodyShapes": None,
            "classes": [base_class],
            "parts": all_base_ids,
            "remaining": all_base_ids.copy(),
        }
    )

    # 6. Sin evo + sin clase + 6 partes base
    steps.append(
        {
            "desc": "6. Sin evo + sin clase + 6 partes base",
            "bodyShapes": None,
            "classes": None,
            "parts": all_base_ids,
            "remaining": all_base_ids.copy(),
        }
    )

    # 7a. Sin evo + sin clase + sin ojos base + resto partes base
    remaining_base_after_eyes = [b for b in base_ordered if b["type"] != "Eyes"]
    if remaining_base_after_eyes:
        remaining_base_ids = [b["id"] for b in remaining_base_after_eyes]
        steps.append(
            {
                "desc": f"7a. Sin evo + sin clase + sin ojos base + {len(remaining_base_ids)} partes base",
                "bodyShapes": None,
                "classes": None,
                "parts": remaining_base_ids,
                "remaining": remaining_base_ids.copy(),
            }
        )

    # 7b. Sin evo + sin clase + sin orejas base + resto partes base
    remaining_base_after_ears = [b for b in base_ordered if b["type"] != "Ears"]
    if remaining_base_after_ears:
        remaining_base_ids = [b["id"] for b in remaining_base_after_ears]
        steps.append(
            {
                "desc": f"7b. Sin evo + sin clase + sin orejas base + {len(remaining_base_ids)} partes base",
                "bodyShapes": None,
                "classes": None,
                "parts": remaining_base_ids,
                "remaining": remaining_base_ids.copy(),
            }
        )

    # 8. Sin evo + sin clase + sin ojos base + sin orejas base + resto partes base
    remaining_base_after_eyes_ears = [
        b for b in base_ordered if b["type"] not in ["Eyes", "Ears"]
    ]
    if remaining_base_after_eyes_ears:
        remaining_base_ids = [b["id"] for b in remaining_base_after_eyes_ears]
        steps.append(
            {
                "desc": f"8. Sin evo + sin clase + sin ojos+orejas base + {len(remaining_base_ids)} partes base",
                "bodyShapes": None,
                "classes": None,
                "parts": remaining_base_ids,
                "remaining": remaining_base_ids.copy(),
            }
        )

    # 9. Sin evo + sin clase + sin ojos base + sin orejas base + probar 4 partes Base
    if len(remaining_base_after_eyes_ears) >= 4:
        for combo in combinations(remaining_base_after_eyes_ears, 4):
            combo_ids = [b["id"] for b in combo]
            steps.append(
                {
                    "desc": f"9. Sin evo + sin clase + sin ojos+orejas + 4 partes: {combo_ids}",
                    "bodyShapes": None,
                    "classes": None,
                    "parts": combo_ids,
                    "remaining": combo_ids.copy(),
                }
            )

    print("\n")
    print("=" * 60)
    print(f"[DEBUG] Total steps: {len(steps)}")

    for idx, step in enumerate(steps):
        print(f"[*] {idx + 1}/{len(steps)}: {step['desc']}...")
        criteria = {}
        if step.get("bodyShapes"):
            criteria["bodyShapes"] = step["bodyShapes"]
        if step.get("classes"):
            criteria["classes"] = step["classes"]
        if step.get("parts"):
            criteria["parts"] = step["parts"]

        data = fetch_marketplace(criteria)
        if data and data.get("total", 0) > 0:
            result = data["results"][0]
            result["remaining_parts"] = step.get("remaining", [])
            return result, step["desc"]

    return None, "No se hallaron coincidencias suficientes."

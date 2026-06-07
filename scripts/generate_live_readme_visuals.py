import json
from pathlib import Path

OUT = Path("docs/diagrams")
OUT.mkdir(parents=True, exist_ok=True)


def svg_text(x, y, text, size=16, weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" font-family="Arial">{text}</text>'


def box(x, y, w, h, label, status):
    colors = {
        "PASS": "#d1fae5",
        "BLOCK": "#fee2e2",
        "PENDING": "#fef3c7",
    }
    stroke = {
        "PASS": "#059669",
        "BLOCK": "#dc2626",
        "PENDING": "#d97706",
    }
    fill = colors.get(status, "#e5e7eb")
    border = stroke.get(status, "#6b7280")
    return f'''
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{border}" stroke-width="3"/>
{text_center(x+w/2, y+35, label, 17, "700")}
{text_center(x+w/2, y+66, status, 22, "700")}
'''


def text_center(x, y, text, size=16, weight="400"):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" font-weight="{weight}" font-family="Arial">{text}</text>'


def generate_rollout_control_tower():
    data = json.loads(Path("docs/live/global_rollout_state.json").read_text())

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="950" height="310" viewBox="0 0 950 310">',
        '<rect width="950" height="310" rx="22" fill="#f8fafc"/>',
        svg_text(36, 45, "Global Rollout Control Tower", 24, "700"),
        svg_text(36, 74, f"Deployment: {data['deployment_id']} · Reason: {data['reason']}", 14),
    ]

    x = 55
    for wave in data["waves"]:
        parts.append(box(x, 115, 220, 100, f"{wave['wave']} · {wave['region']}", wave["status"]))
        x += 285

    rollback = "TRUE" if data["rollback"] else "FALSE"
    freeze = "TRUE" if data["freeze_next_wave"] else "FALSE"

    parts += [
        '<rect x="205" y="245" width="250" height="42" rx="12" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>',
        text_center(330, 273, f"Rollback: {rollback}", 18, "700"),
        '<rect x="500" y="245" width="250" height="42" rx="12" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>',
        text_center(625, 273, f"Freeze next wave: {freeze}", 18, "700"),
        "</svg>",
    ]

    Path("docs/diagrams/global_rollout_control_tower.svg").write_text("\n".join(parts))


def generate_dependency_risk_svg():
    data = json.loads(Path("docs/live/dependency_risk.json").read_text())
    services = data["services"]

    max_risk = 100
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="370" viewBox="0 0 900 370">',
        '<rect width="900" height="370" rx="22" fill="#f8fafc"/>',
        svg_text(36, 45, "Dependency Risk Graph", 24, "700"),
        svg_text(36, 74, f"Highest risk: {data['highest_risk_node']} · release_decision={data['release_decision']}", 14),
    ]

    y = 120
    for item in services:
        risk = item["risk"]
        width = int((risk / max_risk) * 620)
        label = item["service"]
        fill = "#fee2e2" if risk >= 80 else "#fef3c7" if risk >= 60 else "#d1fae5"
        stroke = "#dc2626" if risk >= 80 else "#d97706" if risk >= 60 else "#059669"

        parts += [
            svg_text(50, y + 23, label, 15, "700"),
            f'<rect x="190" y="{y}" width="620" height="30" rx="8" fill="#e5e7eb"/>',
            f'<rect x="190" y="{y}" width="{width}" height="30" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1"/>',
            svg_text(825, y + 22, str(risk), 15, "700"),
        ]
        y += 45

    parts.append("</svg>")
    Path("docs/diagrams/dependency_risk_graph.svg").write_text("\n".join(parts))


def generate_capacity_cost_svg():
    data = json.loads(Path("docs/live/capacity_cost_forecast.json").read_text())["forecast"]
    max_cost = max(x["estimated_cost_usd"] for x in data)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="330" viewBox="0 0 900 330">',
        '<rect width="900" height="330" rx="22" fill="#f8fafc"/>',
        svg_text(36, 45, "Capacity & Cost Forecast", 24, "700"),
        svg_text(36, 74, "Projected replicas and estimated infrastructure cost by planning window.", 14),
    ]

    x = 95
    for item in data:
        h = int((item["estimated_cost_usd"] / max_cost) * 150)
        y = 245 - h
        parts += [
            f'<rect x="{x}" y="{y}" width="145" height="{h}" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>',
            text_center(x + 72, 270, item["window"], 15, "700"),
            text_center(x + 72, y - 10, f"${item['estimated_cost_usd']:,}", 15, "700"),
            text_center(x + 72, y + 28, f"{item['required_replicas']} replicas", 14, "700"),
        ]
        x += 260

    parts.append("</svg>")
    Path("docs/diagrams/capacity_cost_forecast.svg").write_text("\n".join(parts))


def generate_mermaid():
    mermaid = """```mermaid
graph TD
    EdgeGateway[edge-gateway<br/>risk 25] --> API[api<br/>risk 45]
    API --> Auth[auth<br/>risk 58]
    API --> Payments[payments<br/>risk 91]
    Payments --> Database[database<br/>risk 70]
    Payments --> Decision[release_decision: BLOCK]
"""
Path("docs/diagrams/dependency_risk_graph.md").write_text(mermaid)

if name == "main":
generate_rollout_control_tower()
generate_dependency_risk_svg()
generate_capacity_cost_svg()
generate_mermaid()
print("Generated live README visuals:")
print("- docs/diagrams/global_rollout_control_tower.svg")
print("- docs/diagrams/dependency_risk_graph.svg")
print("- docs/diagrams/capacity_cost_forecast.svg")
print("- docs/diagrams/dependency_risk_graph.md")

# Valid Mermaid diagram types
VALID_MERMAID_STARTS = (
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "gantt",
    "pie",
    "journey",
    "mindmap",
    "timeline",
    "gitGraph",
)

# Mermaid prompt keywords for validation
MERMAID_KEYWORDS = [
    "flowchart", "flow chart", "diagram", "chart", "graph",
    "sequence diagram", "class diagram", "erd", "entity relationship",
    "state diagram", "gantt", "pie chart", "bar chart",
    "visualize flow", "process flow", "workflow", "mind map",
    "architecture diagram", "uml", "network diagram", "flow", "steps", "architecture"
]

# Minimum length for output validation
MIN_MERMAID_OUTPUT_LENGTH = 15
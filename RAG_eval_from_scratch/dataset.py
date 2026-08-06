# The authoritative pricing page for each tool.
# Deliberately duplicated here rather than imported from the ingestion seeds:
# the eval must state what we believe independently of the system under test.
OFFICIAL_PRICING = {
    "Claude": "https://claude.com/pricing",
    "Codex": "https://openai.com/api/pricing/",
    "Copilot": "https://github.com/features/copilot/plans",
    "Cursor": "https://cursor.com/pricing",
}

# Used to detect whether an answer actually names a tool.
TOOL_ALIASES = {
    "Claude": ["claude"],
    "Cursor": ["cursor"],
    "Copilot": ["copilot"],
    "Codex": ["codex"],
}

ALL_TOOLS = list(TOOL_ALIASES)


DATASET = [
    # --- pricing: one tool, must cite the official page. Step 1 target. ---
    {
        "id": "p1",
        "question": "Cursor pricing plan",
        "category": "pricing",
        "expected_source": OFFICIAL_PRICING["Cursor"],
        "note": "Scenario 1 failure: cited a comparison article instead.",
    },
    {
        "id": "p2",
        "question": "Claude pricing plan",
        "category": "pricing",
        "expected_source": OFFICIAL_PRICING["Claude"],
        "note": "Known good. Regression guard.",
    },
    {
        "id": "p3",
        "question": "How much does GitHub Copilot cost per month?",
        "category": "pricing",
        "expected_source": OFFICIAL_PRICING["Copilot"],
    },
    {
        "id": "p4",
        "question": "What does Copilot's free tier include?",
        "category": "pricing",
        "expected_source": OFFICIAL_PRICING["Copilot"],
    },
    {
        "id": "p5",
        "question": "What is the Ultra plan?",
        "category": "pricing",
        "expected_source": OFFICIAL_PRICING["Cursor"],
        "note": "Rare exact term, no tool named. Step 4 target.",
    },

    # --- capability: one tool, NOT pricing. Only comparison articles
    # answer these, so a careless tool filter in Step 1 will break them. ---
    {
        "id": "c1",
        "question": "Does Cursor work with JetBrains IDEs?",
        "category": "capability",
    },
    {
        "id": "c2",
        "question": "Does Claude Code run in the terminal?",
        "category": "capability",
    },
    {
        "id": "c3",
        "question": "How does Cursor handle large codebases?",
        "category": "capability",
    },

    # --- comparison: several tools at once. Step 2 target. ---
    {
        "id": "m1",
        "question": "Which tool has the most generous free tier?",
        "category": "comparison",
        "expected_tools": ALL_TOOLS,
        "note": "Scenario 2 failure: named no tool at all.",
    },
    {
        "id": "m2",
        "question": "Compare the pricing of Claude Code, Cursor, Copilot and Codex",
        "category": "comparison",
        "expected_tools": ALL_TOOLS,
    },
    {
        "id": "m3",
        "question": "Cursor or Claude Code for a large refactor?",
        "category": "comparison",
        "expected_tools": ["Cursor", "Claude"],
    },
    {
        "id": "m4",
        "question": "Which tool is cheapest for a five-person team?",
        "category": "comparison",
        "expected_tools": ALL_TOOLS,
    },
    {
        "id": "m5",
        "question": "Claude Code vs Copilot for enterprise use",
        "category": "comparison",
        "expected_tools": ["Claude", "Copilot"],
    },

    # --- out_of_scope: must decline. ---
    {
        "id": "o1",
        "question": "What is the weather in Lagos today?",
        "category": "out_of_scope",
    },
    {
        "id": "o2",
        "question": "How do I cook jollof rice?",
        "category": "out_of_scope",
    },
    {
        "id": "o3",
        "question": "How much does JetBrains IntelliJ IDEA cost?",
        "category": "out_of_scope",
        "note": "Adjacent but not in the corpus. Harder than the obvious ones.",
    },
]

# A coding tools advisor

A barebones RAG application - no framework(Langchain or LlamaIndex)

## What we are building

We are building a question-and-answer assistant for AI coding tools. 
A developer types a real question into a simple chat interface. The assistant searches a 
knowledge base of trusted sources, finds the passages most relevant to the question, and uses 
them to write a grounded answer. Every answer comes with links back to the sources it drew from, 
so the developer can verify it rather than take it on faith.

Four tools sit at the centre of the demo: Claude Code, Codex, Copilot, and Cursor. 
The knowledge base is built from real material about them, which we will choose carefully in a moment.

## Why it matters

Anyone who has evaluated AI coding tools recently has felt the same friction. 
The information you need exists, but it is scattered: across documentation, blog posts, 
changelogs, forum threads, and comparison articles. Answering a single practical question 
can mean opening ten tabs and piecing the picture together yourself.

- "Which tool handles a large existing monorepo?"
- "I work mostly in Rust. Which assistant supports it well?"
- "I need something that runs inside my JetBrains IDE. What are my options?"
- "I am on a tight budget. Which tools have a generous free tier?"
- "I am migrating from Copilot to Claude Code. How do I move my setup across?"

These range from simple lookups to genuine judgement calls, and our assistant 
turns that scattered knowledge into one interactive place to ask. We begin with 
the lookups, the questions a single trusted source can answer, and build toward the judgement calls later.

A general-purpose model could attempt these questions too. The catch is that it 
answers from memory, and that memory has a cutoff. It may miss newer documentation, 
recent tooling changes, fresh pricing, and expert takes published last month. 
RAG closes that gap. It retrieves relevant information at query time, before the 
model writes anything, so answers stay anchored to real sources rather than to 
whatever the model happened to absorb during training.
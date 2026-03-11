"""
Seed script for Open Brain demo database.
Creates ob_demo.db, embeds all 125 nodes, exports node_id_map.json.
Run: python seed_demo.py
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ob_demo.db")
MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "node_id_map.json")
MODEL_ID = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# 125 DEMO NODES — spec labels, domain, intent, content
# ---------------------------------------------------------------------------

NODES = [
    # ── CLUSTER 1: META ──────────────────────────────────────────────────
    {
        "label": "M1",
        "domain": "meta",
        "intent": "reference",
        "content": "Open Brain is a persistent AI memory system built to solve a simple problem: AI assistants forget everything when a session ends. Dual-store architecture — local SQLite for privacy-first operation, Supabase pgvector for cloud accessibility — with hybrid retrieval combining semantic vector search and full-text keyword matching. Memory persists across tools, devices, and sessions. 165+ nodes at launch, growing with every conversation. The system doesn't just store information — it surfaces what's relevant automatically, before you think to ask.",
    },
    {
        "label": "M2",
        "domain": "meta",
        "intent": "insight",
        "content": "Every AI conversation starts from zero. The context you built last week, the decision you explained last month, the framework you developed over a year — gone on session close. The problem isn't that AI is limited. It's that AI is structurally amnesiac. Open Brain is the fix: a memory layer that persists what you've learned, decided, and built, then injects it back into new sessions automatically. The conversation picks up where it left off, even across different tools.",
    },
    {
        "label": "M3",
        "domain": "meta",
        "intent": "reference",
        "content": "Every memory is a node — a unit of stored knowledge with content and metadata. The metadata does the retrieval work: domain tags filter by area of life (technical, consulting, personal), intent tags filter by type of memory (decision, insight, reference, action item, session record). A 384-dimension vector embedding encodes the semantic meaning of the content. Full-text indexing captures the keywords. Together, these create a wide-band retrieval system: the metadata decides what to retrieve, the embeddings decide what's related.",
    },
    {
        "label": "M4",
        "domain": "meta",
        "intent": "insight",
        "content": "The real value of a connected memory system isn't retrieval — it's synthesis. Ask a generic question, get a generic answer. Ask something grounded in your own context — 'what are potential AI use cases for a client's intake process?' — and the system finds a consulting framework from one domain, a technical pattern from another, and a relevant past decision, assembled on the fly. The output isn't a search result. It's a starting point for thinking that already knows your history.",
    },
    {
        "label": "M5",
        "domain": "meta",
        "intent": "reference",
        "content": "Making memory available across tools required a standard connector layer — something any AI environment could call without rebuilding the integration. MCP (Model Context Protocol) is that layer: skills and plugins extend what it can trigger, consistent processes load context automatically, cross-session handoffs become seamless. The result: memory that follows you. Start a session in a coding environment, continue in a chat interface, and the context is already there. The session boundary disappears.",
    },
    {
        "label": "M6",
        "domain": "meta",
        "intent": "insight",
        "content": "Without persistent memory, AI is a powerful tool you have to re-teach every session. With it, AI becomes a collaborator that accumulates context over time. The practical difference: instead of spending the first 10 minutes re-establishing context, you start at the decision point. Instead of re-explaining a framework you built six months ago, you ask a question that retrieves it. The compounding effect is real — the system gets more useful the longer you use it.",
    },
    {
        "label": "M7",
        "domain": "meta",
        "intent": "insight",
        "content": "The link graph isn't just a visualization — it's a map of how ideas connect. Nodes cluster by domain but bridge across them: a consulting insight links to a technical decision that links to a personal belief. Those bridges are where the interesting thinking lives. The graph makes visible what's usually invisible: the cross-domain patterns that inform every good decision you make. Seeing it externalized changes how you understand your own thinking.",
    },
    {
        "label": "M8",
        "domain": "meta",
        "intent": "insight",
        "content": "Traditional notes fail at retrieval because you have to remember to look. You have to recall that you wrote something, where you filed it, and what you called it. Memory systems flip this: instead of you searching the archive, the archive searches you. When you ask a question, relevant nodes surface — whether you knew they existed or not. The shift from active recall to ambient surfacing is the design difference that makes persistent memory genuinely useful.",
    },
    {
        "label": "M9",
        "domain": "meta",
        "intent": "reference",
        "content": "Five types of memory nodes: decisions (strategic choices with rationale and alternatives rejected), insights (patterns noticed and lessons learned), references (frameworks, how-tos, and reusable knowledge), session summaries (records of what was discussed and decided), and action items (tasks with context). Nothing is stored as raw transcript. Everything is synthesized at capture time — the goal is a node that answers a question when retrieved, not one that requires re-reading to understand.",
    },
    {
        "label": "M10",
        "domain": "meta",
        "intent": "reference",
        "content": "When a query comes in, three things happen in parallel: vector similarity search finds semantically related nodes (what does this mean?), full-text search finds keyword matches (what exact terms appear?), and domain/intent filters narrow the candidate set. Scores are blended — 70% semantic, 30% keyword — and the top results returned. The link graph then expands the result set: if a relevant node has linked nodes, those get included too. One query, multiple retrieval pathways.",
    },
    {
        "label": "M11",
        "domain": "meta",
        "intent": "reference",
        "content": "Domains are areas of life: technical work, consulting engagements, job search, personal development, real estate, meta-knowledge about the system itself. Intents are types of knowledge: reference material you'll return to repeatedly, decisions you made with specific reasoning, insights you noticed, session records of what happened, action items with deadlines. The combination is the filter — 'show me decisions in the technical domain' produces a precise slice of memory that no keyword search can replicate.",
    },
    {
        "label": "M12",
        "domain": "meta",
        "intent": "reference",
        "content": "Four link types connect nodes: related (bidirectional parent/child relationship), derived_from (this node builds on that one), supersedes (this node replaces an older version), consolidated (this node merges multiple earlier nodes). When a query returns a relevant node, link expansion pulls its connected nodes into the result — graph traversal as retrieval amplification. The links are how context spreads: find one node, discover the cluster.",
    },
    {
        "label": "M13",
        "domain": "meta",
        "intent": "reference",
        "content": "The memory map is a high-level index of what's in Open Brain — not every node, but the content families, domain distributions, and key hubs. It answers the navigation question: 'what do I have, and where is it?' Updated periodically to reflect new content families. The map is itself a node — stored in memory, searchable, retrievable. The system knows what it knows.",
    },
    {
        "label": "M14",
        "domain": "meta",
        "intent": "insight",
        "content": "Personal knowledge management tools (Notion, Obsidian, Roam) organize information for human retrieval — you navigate, browse, and search. Open Brain is designed for AI retrieval: the structure optimizes for what an AI can do with the content, not for what a human can read. The difference shows up in node size (smaller, more atomic), query interface (natural language, not folder navigation), and use pattern (passive surfacing, not active browsing). Different tool for a different workflow.",
    },
    {
        "label": "M15",
        "domain": "meta",
        "intent": "insight",
        "content": "Retrieval quality is determined at storage time. The decisions made when capturing a memory — how to structure the content, what domain to assign, which intent tag fits, what query hooks to include — directly determine whether the memory gets found when needed. A poorly structured node is effectively lost: it exists but never surfaces. Good capture practice is the highest-leverage improvement to a memory system because its value compounds across every future retrieval.",
    },
    {
        "label": "M16",
        "domain": "meta",
        "intent": "reference",
        "content": "At the start of a session, recall_context loads relevant history before the conversation begins. This means the AI already has context about the ongoing project, recent decisions, and active threads — without the user re-explaining anything. The session feels like a continuation, not a restart. At the end of a session, capture_session stores a structured summary: what was decided, what's open, what's next. The loop closes.",
    },
    {
        "label": "M17",
        "domain": "meta",
        "intent": "reference",
        "content": "Not all memory should live forever. Action items expire when completed or overdue. Time-sensitive context (interview prep, event-specific plans) has a natural shelf life. The TTL (time-to-live) field lets nodes expire automatically — the system stays current without manual pruning. Permanent nodes get no TTL: frameworks, decisions, insights, foundational references. The distinction between ephemeral and permanent memory is a design choice, not a default.",
    },
    {
        "label": "M18",
        "domain": "meta",
        "intent": "insight",
        "content": "Open Brain is open architecture. The core components — a vector database, an embedding model, and an MCP-compatible server — are available as open-source tools. The real work isn't the technology; it's designing the memory schema for your own use case. What domains matter in your work? What types of memories do you create? What queries do you wish you could run against your own history? Answer those questions, and the technical implementation follows.",
    },
    {
        "label": "M19",
        "domain": "meta",
        "intent": "reference",
        "content": "This demo is itself a working Open Brain instance — a curated set of nodes seeded from real experience, sanitized for public view. The chatbot's answers are grounded in these nodes: when you ask a question, it retrieves relevant nodes and synthesizes a response from them. The graph visualizes the same retrieval in real time — watch which nodes light up when you ask something. What you're interacting with is the system demonstrating itself.",
    },
    {
        "label": "M20",
        "domain": "meta",
        "intent": "decision",
        "content": "The local-first design wasn't a constraint — it was a deliberate choice. Personal memory is personal. The default should be: your data stays on your machine unless you decide otherwise. Cloud deployment is an opt-in upgrade for accessibility, not a requirement. This means someone building their own Open Brain can choose their own tradeoff: maximum privacy (local only), maximum accessibility (cloud), or a hybrid with selective sync. The architecture accommodates the choice without forcing it.",
    },
    {
        "label": "M21",
        "domain": "meta",
        "intent": "insight",
        "content": "A memory system is good when it's invisible. You stop thinking about whether to capture something — you just do it. You stop worrying about whether you'll find something — you trust you will. The friction disappears. What remains is a system that makes you smarter in every conversation because it holds the accumulated context of your work. Good memory is not the goal; good thinking enabled by good memory is.",
    },
    {
        "label": "M22",
        "domain": "meta",
        "intent": "reference",
        "content": "Nodes are atomic — each one covers one concept, one decision, one pattern. This isn't just a storage convention; it's a retrieval principle. A node covering five things will be found when one of those things is queried, but the other four dilute the relevance score and add noise to the result. Atomic nodes mean high precision: when a node surfaces, it's because all of its content is relevant, not just part of it.",
    },
    {
        "label": "M23",
        "domain": "meta",
        "intent": "insight",
        "content": "At 50 nodes, everything is findable. At 200 nodes, retrieval quality becomes the bottleneck — what you get back matters more than what you stored. At 500+ nodes, the graph structure carries as much information as the nodes themselves: where a node sits in the network, what it connects to, how central it is. Building a memory system means thinking about how it scales from the beginning, not only when it gets large.",
    },
    {
        "label": "M24",
        "domain": "meta",
        "intent": "insight",
        "content": "The most interesting retrievals are cross-domain: a consulting framework that connects to a technical architecture decision, a personal belief that informs a job search strategy. These connections don't happen in keyword search — the terms don't overlap. They happen in vector space because the underlying concepts are related. Every cross-domain link in the graph is a piece of genuine insight: something that belongs together that you wouldn't have put together manually.",
    },
    {
        "label": "M25",
        "domain": "meta",
        "intent": "insight",
        "content": "Open problems in personal memory system design: how do you handle evolving beliefs (when your current thinking supersedes your past thinking but the old node is still contextually useful)? How do you represent uncertainty (a decision made with low confidence vs. high confidence)? How do you prevent confirmation bias in retrieval (the system surfacing what you already believe rather than what challenges it)? These are unsolved problems, not just for Open Brain — for any AI memory system worth building.",
    },

    # ── CLUSTER 2: TECHNICAL ─────────────────────────────────────────────
    {
        "label": "T1",
        "domain": "technical",
        "intent": "decision",
        "content": "Open Brain started on local SQLite — your memory stays on your machine, no API keys, no cloud dependency. For users where privacy is non-negotiable, this is the complete solution. The system was designed to migrate, not to require it: when cross-device accessibility became the priority, moving to cloud vector storage was a connection string swap, not a rewrite. The dual-store design means migration is graceful — if cloud is unavailable, local still works. Privacy-first and cloud-accessible aren't mutually exclusive; they're sequential choices.",
    },
    {
        "label": "T2",
        "domain": "technical",
        "intent": "insight",
        "content": "The leap from keyword search to vector embeddings is the leap from 'does this word appear?' to 'is this concept related?' Embeddings convert text into numerical representations that encode meaning — similar ideas land near each other in vector space, regardless of the words used to express them. This is what AI does naturally. Training it on a personal knowledge base means its relational pattern recognition operates on your own context — connecting a framework from two years ago to a decision made last week, without you knowing to look. The graph isn't manually drawn. It's what the embeddings found.",
    },
    {
        "label": "T3",
        "domain": "technical",
        "intent": "decision",
        "content": "The first attempt at cross-tool continuity was manual: structured documents passed as bridges between coding and chat environments. It worked but required discipline — the right files in the right place at the right time. The exploration expanded from there: documentation models, persistent context files, framework-triggered processes. MCP emerged as the right abstraction: a standard connector that turns memory, skills, and capabilities into callable tools for any compatible AI client. The memory system is the end state of that exploration.",
    },
    {
        "label": "T4",
        "domain": "technical",
        "intent": "session_summary",
        "content": "The MVP built in a single overnight session: sentence-transformer embeddings, SQLite schema with intent and domain fields, a chunking pipeline for session logs, and six MCP tools. The first query that returned something genuinely useful — a framework from a session three months prior, surfaced without searching for it — was the proof-of-concept moment. Not a demonstration that it worked technically. A demonstration that it would change how work gets done.",
    },
    {
        "label": "T5",
        "domain": "technical",
        "intent": "insight",
        "content": "Chunking — how content gets broken into memory-storable pieces — sounds mechanical until retrieval quality shows where it fails. The first pass was intuitive: split at logical breaks, keep context together. Then real queries showed the breakdown: oversized chunks lose retrieval precision, undersized chunks lose context, mixed-topic chunks pollute results. Principles that held: the right chunk is the unit of retrieval, not storage. Context headers belong inside the chunk. The strategy is still being calibrated — new content types require new approaches.",
    },
    {
        "label": "T6",
        "domain": "technical",
        "intent": "reference",
        "content": "The schema's value is in the fields beyond content: intent tags enable filtered retrieval by memory type, TTL enables automatic expiration of perishable data, visibility enables future access control, model_id prevents mixing embeddings from different models in the same search, content hash enables deduplication. None of these are optional features — each one closes a specific failure mode. The schema design is as important as the retrieval algorithm: garbage fields produce garbage recall.",
    },
    {
        "label": "T7",
        "domain": "technical",
        "intent": "reference",
        "content": "Moving from local to cloud required solving one concrete problem: the server needs to stay alive without being manually started. Deploying to a cloud platform that handles availability meant the memory system could receive read and write requests continuously — from any device, at any time. The side effect was ambient capture: a session ends, a summary is written. A decision is made, it's stored. The system doesn't require you to be at your primary machine. Always-on closes the gaps where memory used to fall through.",
    },
    {
        "label": "T8",
        "domain": "technical",
        "intent": "insight",
        "content": "Pure vector search misses exact matches — a specific product name, a person's title, a technical term. Pure keyword search misses conceptual relationships — 'how did you handle resistance to change?' won't find the right node if none of those words appear. Running both and blending scores gives breadth and precision in a single query. The 70/30 weighting (semantic/keyword) is a starting point, not a law — it should be tuned as the corpus grows and query patterns become clearer.",
    },
    {
        "label": "T9",
        "domain": "technical",
        "intent": "reference",
        "content": "Content hash using SHA-256 prevents storing exact duplicate nodes. Normalized before hashing: whitespace stripped, case lowered. This handles the most common duplication source — re-running an ingestion pipeline on already-ingested content. It doesn't handle near-duplicates (slightly edited versions of the same content). For those, the solution is supersession links: new version of a node links to the old one with supersedes type. The old node stays for historical context; the new one wins in retrieval.",
    },
    {
        "label": "T10",
        "domain": "technical",
        "intent": "reference",
        "content": "Every node goes through the same pipeline: content is preprocessed (context headers prepended, source info added), the embedding model converts it to a vector, the vector and metadata are written to the database, and a content hash is checked for deduplication. The pipeline is synchronous at capture time — no async queue. This keeps implementation simple and means every node is immediately retrievable after storage. Performance is acceptable for interactive use at current scale.",
    },
    {
        "label": "T11",
        "domain": "technical",
        "intent": "insight",
        "content": "The first retrieval failures were chunking failures, not algorithm failures. Nodes that were too large came back for the wrong queries — a node about three different topics would surface for queries about only one of them, flooding the result with irrelevant content. The fix wasn't a better algorithm; it was smaller, more atomic nodes. This pattern repeats in AI systems generally: most retrieval quality problems are data quality problems wearing algorithmic clothes.",
    },
    {
        "label": "T12",
        "domain": "technical",
        "intent": "reference",
        "content": "Before MCP, cross-tool continuity ran on bridge files: structured markdown documents written at the end of one session, read at the start of the next. Each file followed a consistent format: session summary, key decisions, open threads, next actions. The pattern worked because both tools (code environment and chat) could read markdown. Its limitation: manual discipline. If you didn't write the bridge, the context didn't transfer. MCP replaced the discipline requirement with a protocol.",
    },
    {
        "label": "T13",
        "domain": "technical",
        "intent": "decision",
        "content": "Smaller models (384 dimensions) use less storage and compute but have lower retrieval precision on nuanced queries. Larger models improve precision but increase cost and latency. For a personal knowledge base under 1,000 nodes, smaller models are sufficient — the performance gap only matters at scale or with highly specialized content. The provider abstraction layer in the implementation supports swapping models: the same retrieval pipeline runs regardless of which model generated the embeddings, as long as model_id is tracked per node.",
    },
    {
        "label": "T14",
        "domain": "technical",
        "intent": "insight",
        "content": "Model Context Protocol solves the N×M integration problem: without a standard, connecting N AI tools to M capabilities requires N×M custom integrations. With MCP, each tool implements the protocol once and can access any MCP-compatible capability. For a personal AI system, this means a skill built once (memory, search, external API) is available in every compatible tool without rebuilding. The abstraction is what makes the system extensible — adding a new tool means connecting it, not rebuilding.",
    },
    {
        "label": "T15",
        "domain": "technical",
        "intent": "insight",
        "content": "Brute-force cosine similarity on a local vector store is acceptable under 10,000 nodes — query latency stays under 100ms at that scale. Beyond that, approximate nearest-neighbor indexing becomes necessary. In the cloud store, IVFFlat indexing handles this. The architecture anticipates the scaling threshold without prematurely optimizing — SQLite works now, Supabase scales later. This is a recurring principle: build for the current scale, design for the next one.",
    },
    {
        "label": "T16",
        "domain": "technical",
        "intent": "reference",
        "content": "Skills extend what the AI can do beyond retrieval. A skill is a defined process: structured prompts, consistent output formats, specific trigger conditions, expected inputs and outputs. When a session starts, a skill can load context automatically. When a decision gets made, a skill can format it for storage. When a week ends, a skill runs the review template. Skills are the layer between raw capability (the model) and consistent behavior (the workflow). They're how an AI system develops reliable habits.",
    },
    {
        "label": "T17",
        "domain": "technical",
        "intent": "reference",
        "content": "Testing a memory system is testing retrieval quality — and retrieval quality is subjective. The approach: define a set of queries that should return specific nodes. Run those queries against the current system. If the expected nodes appear in the top results, the system is working. If they don't, diagnose whether the problem is chunking, metadata, embedding model, or query structure. Automated test coverage for the pipeline; human judgment for retrieval quality. The combination catches different failure modes.",
    },
    {
        "label": "T18",
        "domain": "technical",
        "intent": "reference",
        "content": "The recall_context tool is the highest-value MCP tool in practice. At session start, it takes a brief description of what the current session is about and returns the most relevant memories from past sessions. This means the AI enters every conversation with relevant history already loaded — no manual context-setting required. The quality of this context load depends on memory capture discipline: sessions that end with a well-structured summary are the ones that start well the next time.",
    },
    {
        "label": "T19",
        "domain": "technical",
        "intent": "insight",
        "content": "A memory system that fails silently is worse than one that fails loudly. Silent failures mean the system appears to work while degrading — nodes stored without embeddings, queries returning stale results, link traversal hitting missing nodes. The implementation prioritizes visible failure over graceful degradation: if an embedding fails, the write fails and the user knows. If a link points to a missing node, the error is logged and surfaced. You can fix a loud failure. You can't fix one you don't know about.",
    },
    {
        "label": "T20",
        "domain": "technical",
        "intent": "reference",
        "content": "Obsidian serves as a human-readable view of Open Brain: the same nodes that live in the database can be exported to Obsidian's markdown vault, where the graph view renders their connections visually. This isn't the primary interface — it's a navigation and exploration layer. When you want to see the shape of what you know, Obsidian shows it. When you want to query what you know, Open Brain handles it. Two different interfaces to the same data, each suited to its own use case.",
    },
    {
        "label": "T21",
        "domain": "technical",
        "intent": "reference",
        "content": "An optional metadata extraction step uses an AI call to suggest domain, intent, and query hook tags automatically. This reduces the discipline required for good capture: instead of manually classifying every node, you describe what you're storing and the system proposes the classification. The proposal is reviewed, not blindly accepted — the human remains in the loop for metadata quality. The tradeoff: one additional API call per node. The return: lower friction for high-volume capture.",
    },
    {
        "label": "T22",
        "domain": "technical",
        "intent": "reference",
        "content": "Every node records how it was created: code_session, chat_session, bridge (manual document), weekly_context (review summaries), pipeline (automated ingestion), manual (direct entry). The source field isn't just provenance — it's a retrieval filter. 'Show me decisions from code sessions' returns architectural choices. 'Show me insights from weekly reviews' returns pattern observations. The source taxonomy creates a filing system inside the flat node structure.",
    },
    {
        "label": "T23",
        "domain": "technical",
        "intent": "reference",
        "content": "When thinking evolves, old nodes shouldn't be deleted — they should be superseded. The supersedes link type creates a directed relationship: new node → old node. In retrieval, the superseding node wins on relevance; the superseded node remains for historical context. This matters for decisions: you want to know what you decided now and also what you decided before and why it changed. Supersession is how a memory system handles the fact that knowledge has a history.",
    },
    {
        "label": "T24",
        "domain": "technical",
        "intent": "reference",
        "content": "Each node has a visibility field: private (default, only accessible to the owner), shared (accessible to specific collaborators), public (openly accessible). The visibility layer enables future multi-user scenarios — shared project memory, collaborative knowledge bases, public-facing demos — without redesigning the schema. The demo instance uses public visibility throughout. Production nodes default to private. The same architecture serves both cases.",
    },
    {
        "label": "T25",
        "domain": "technical",
        "intent": "insight",
        "content": "The natural extensions of a personal memory system: a web dashboard that lets you explore the graph visually and query without an AI interface, a mobile capture tool for frictionless on-the-go storage, automatic ingestion from email and calendar for ambient context capture, and multi-user collaboration with access controls. Each extension serves a different use pattern. The core — store, embed, retrieve, link — stays constant. Everything else is a layer on top of it.",
    },

    # ── CLUSTER 3: CONSULTING ─────────────────────────────────────────────
    {
        "label": "CON1",
        "domain": "consulting",
        "intent": "reference",
        "content": "Sushi Media started as a consulting practice and became something more useful: a laboratory. Client work in restaurant operations, logistics, and real estate created a forcing function — real constraints, real deadlines, real people who would tell you immediately if something didn't work. The lab framing changes the question from 'what AI tools should this client use?' to 'what actually holds up when you put it in front of a business owner at 8am on a Tuesday?' Advisory work tells you what's possible. Client work tells you what's practical.",
    },
    {
        "label": "CON2",
        "domain": "consulting",
        "intent": "insight",
        "content": "The barrier to AI adoption in small businesses isn't access — it's translation. The tools exist. The gap is between what a tool can do and what a business owner recognizes as useful right now. What works: start with the pain that's already visible. A restaurant owner doesn't need to understand AI — they need to know the system that updates their menu also drafts their social posts in the same voice. Start with the time saved. Let the technology become invisible. Complexity that gets adopted is always complexity well hidden.",
    },
    {
        "label": "CON3",
        "domain": "consulting",
        "intent": "insight",
        "content": "Marketing for experience-based businesses — restaurants, entertainment venues, hospitality — isn't about promoting a product; it's about selling a moment. Customers choose these businesses based on the story they can tell afterward. The marketing strategy question isn't 'what do we offer?' but 'what will people say about this to their friends?' That framing changes everything: content becomes story capture, social media becomes social proof distribution, and promotions become invitations to an experience rather than price incentives.",
    },
    {
        "label": "CON4",
        "domain": "consulting",
        "intent": "insight",
        "content": "Most small businesses start transformation conversations with a tool request: 'I need a better POS system' or 'I want to run social media ads.' The better starting question: what does the data you already have tell you? Sales by day and time, customer return rates, top-performing items, peak service gaps. The transformation roadmap follows from the data, not from the tool catalog. Businesses that skip this step adopt tools that don't solve their actual problems.",
    },
    {
        "label": "CON5",
        "domain": "consulting",
        "intent": "reference",
        "content": "Social media content for small businesses is a production problem, not a creative problem. Inconsistency kills reach; inconsistency comes from making content creation effortful. The solution: systematize the parts that don't require creativity — content calendar structure, post format templates, voice guidelines, image ratios, caption length by platform. AI handles production: draft generation, variation, scheduling triggers. The owner handles editorial judgment: what's true, what's on-brand, what to post this week. The handoff is the editorial decision, not the writing.",
    },
    {
        "label": "CON6",
        "domain": "consulting",
        "intent": "insight",
        "content": "A menu is a product with a pricing strategy, a hierarchy, and a conversion goal. Menu engineering asks: which items are both popular and profitable (stars), which are profitable but underordered (puzzles), which are popular but low-margin (plowhorses), which are neither (dogs)? That four-quadrant analysis drives placement decisions — stars go where the eye goes first, puzzles get merchandised with descriptions, dogs get removed or repriced. The physical design and the data analysis are the same problem: organizing information to produce a specific behavior.",
    },
    {
        "label": "CON7",
        "domain": "consulting",
        "intent": "reference",
        "content": "Brand voice isn't a marketing asset — it's operational infrastructure. For a business using AI to generate content, captions, descriptions, or customer communications, the voice document is the control layer. It defines what the brand sounds like, what it never says, what references it uses, what tone it sets by context. Without it, AI-generated content drifts toward generic. With it, AI-generated content is indistinguishable from human-written content in the brand's voice. The voice document pays back every time it's used.",
    },
    {
        "label": "CON8",
        "domain": "consulting",
        "intent": "reference",
        "content": "Small business digital transformation follows a predictable sequence when done right: first, establish baseline data capture (what's actually happening?), then systematize operations (can this run without the owner in the room?), then extend reach (can customers find and transact with us digitally?), then amplify with AI (can we do more of the things that work without more labor?). Skipping steps creates brittle systems — AI content without a brand voice, online ordering without a consistent menu, automation without a stable operations baseline.",
    },
    {
        "label": "CON9",
        "domain": "consulting",
        "intent": "insight",
        "content": "The failure mode of consulting is building something the client can't maintain. A CRM that requires a developer to update. A social calendar that collapses when the person who built it leaves. The test for any client deliverable: can the owner operate this solo, on a bad week, six months from now? This constraint rules out complexity for its own sake. It pushes toward tools the client already uses with automation layered underneath. The most durable systems feel simple to the person running them.",
    },
    {
        "label": "CON10",
        "domain": "consulting",
        "intent": "reference",
        "content": "For a local business, the customer journey starts before they arrive: a search result, a recommendation, a social post. It ends after they leave: a review, a return visit, a referral. The transformation opportunity lives at both ends. Pre-visit: is the business findable, credible, and easy to engage? Post-visit: does the business stay in the customer's awareness? Most SMB marketing focuses only on the in-venue experience. The highest-leverage work is usually at the pre-visit and post-visit stages, where competitors aren't competing.",
    },
    {
        "label": "CON11",
        "domain": "consulting",
        "intent": "reference",
        "content": "Transformation success for SMBs isn't measured in software adoption — it's measured in business outcomes. Return customer rate. Average order value. Labor hours per unit of output. Time the owner spends on low-value tasks. Social media reach and engagement growth. The metrics should be defined before the transformation begins, not derived from whatever the tools happen to track. Defining success criteria upfront also defines the engagement: the work is done when the metrics move, not when the deliverables are handed over.",
    },
    {
        "label": "CON12",
        "domain": "consulting",
        "intent": "insight",
        "content": "A CRM for a small business owner who has never used one needs to pass a different test than enterprise software: can they use it on a phone, under time pressure, without training? This means: no required fields that require lookup, no workflows that require sequence, no dashboards that require interpretation. The CRM is a contact record, a follow-up reminder, and a conversation history. Everything else is overhead that kills adoption. Build for the worst-case usage scenario, not the ideal one.",
    },
    {
        "label": "CON13",
        "domain": "consulting",
        "intent": "insight",
        "content": "In logistics, the AI opportunity isn't automation — it's optimization of decisions that humans currently make slowly. Route selection, capacity planning, customer communication timing, pricing adjustments based on demand signals. These decisions happen dozens of times per day and are currently made by instinct or spreadsheet. AI doesn't replace the decision-maker; it makes each decision faster and more informed. The transformation is in the decision quality and volume, not in the removal of human judgment.",
    },
    {
        "label": "CON14",
        "domain": "consulting",
        "intent": "insight",
        "content": "In real estate, the client relationship is the product. Agents who win on relationship depth rather than transaction speed need systems that support long-cycle engagement: remembering what a client said six months ago about their priorities, tracking when follow-up is warranted, surfacing the right property at the right moment. CRM in real estate isn't contact management — it's relationship intelligence. The agents who use it well operate at a scale that would be impossible manually.",
    },
    {
        "label": "CON15",
        "domain": "consulting",
        "intent": "reference",
        "content": "The engagement structure that works for SMB transformation: discover (understand the business before proposing anything — one deep session asking what's working, what's breaking, and what the owner wishes they didn't have to do), design (propose a transformation roadmap in priority order, with the owner's effort required at each stage), build (deliver systems the owner can see and touch before the engagement ends), and hand off (leave documentation that enables solo operation). Four phases, clear owners, exit criteria defined upfront.",
    },
    {
        "label": "CON16",
        "domain": "consulting",
        "intent": "reference",
        "content": "Repeatable client outcomes require reusable frameworks. A playbook captures: the client archetype this applies to, the standard discovery questions, the typical transformation sequence, the deliverables at each stage, the tools that work for this type of business. Building playbooks from early client work creates a compounding return: each engagement improves the playbook, which makes the next engagement faster and more predictable. The playbook is the consulting product; the client engagement is the delivery.",
    },
    {
        "label": "CON17",
        "domain": "consulting",
        "intent": "reference",
        "content": "Framework for evaluating AI tools for small business clients: Does it solve a real current problem, or a hypothetical future one? Does the owner understand the output it produces? Can it run without ongoing technical support? What's the failure mode when it breaks? What's the cost at real usage volume, not demo volume? The tools that survive this evaluation are usually simpler than the ones that don't. Complexity isn't a signal of quality in SMB technology — durability is.",
    },
    {
        "label": "CON18",
        "domain": "consulting",
        "intent": "insight",
        "content": "Pricing tells customers what to think about a business before they experience it. A restaurant priced below the experience it delivers creates a mismatch — customers come in with wrong expectations, leave pleasantly surprised but don't return at the rate a properly priced business would earn. Pricing isn't just margin math — it's customer expectation setting. The transformation question is often not 'how do we reduce cost?' but 'are we priced to attract the customer we want to serve?'",
    },
    {
        "label": "CON19",
        "domain": "consulting",
        "intent": "reference",
        "content": "For local businesses, online reviews are the most powerful marketing asset and the most underused one. A systematic approach to social proof: ask for reviews at the peak of the experience (not at checkout), respond to every review (positive to reinforce, negative to demonstrate responsiveness), and use reviews as a feedback signal (not just a marketing metric). The business that systematizes this generates a compounding review advantage over competitors who treat it as an afterthought.",
    },
    {
        "label": "CON20",
        "domain": "consulting",
        "intent": "insight",
        "content": "The most valuable outputs from Sushi Media's lab work aren't the deliverables — they're the failure modes that client work revealed. AI content that sounds right but isn't true to the business voice (requires a stronger voice document upfront). Automation that saves time for the consultant but adds complexity for the client (requires the durability test earlier in design). CRM adoption that peaks at launch and drops (requires regular check-ins, not just handoff). These aren't client failures — they're the lab data that improves the next engagement.",
    },
    {
        "label": "CON21",
        "domain": "consulting",
        "intent": "insight",
        "content": "The most common consulting failure in small business transformation: building solutions to problems the owner doesn't recognize as problems. The owner knows their business at a level of operational detail that no outside perspective can match. The consulting value is in frameworks and tools, not in telling the operator what their problem is. The right process: discover what the operator finds frustrating, exhausting, or inefficient, then apply a framework to it. Operator insight + consulting framework = a solution that actually gets used.",
    },
    {
        "label": "CON22",
        "domain": "consulting",
        "intent": "reference",
        "content": "Every transformation engagement should be able to articulate a before/after state in terms the client cares about. Not 'we implemented a CRM' but 'before, the owner was doing manual follow-up for 2 hours a week; after, the system does it automatically and the owner reviews in 15 minutes.' The before/after frame does two things: it defines success before the work starts, and it creates the case study narrative for future engagements. Both require the same discipline: measure the before state before the work begins.",
    },
    {
        "label": "CON23",
        "domain": "consulting",
        "intent": "insight",
        "content": "The tools that scale a small business often create the complexity that slows it down. A multi-channel social media strategy requires a content operation. A loyalty program requires a redemption process. An online ordering system requires a menu management workflow. Every capability added is also a maintenance burden added. The right transformation question isn't 'what can we add?' but 'what's the minimum system that achieves the business goal?' Simplicity at scale is harder to design than complexity — and worth far more.",
    },
    {
        "label": "CON24",
        "domain": "consulting",
        "intent": "insight",
        "content": "How a business brings in a new customer — in-person, digitally, or both — determines the relationship it will have with them. A frictionless first experience sets the expectation that this is a business that has its act together. A confusing or effortful first experience sets the expectation of difficulty. Onboarding design applies to digital flows (how does a new customer place their first online order?) and in-person flows (what happens in the first 60 seconds of a new customer's visit?). Both are designable.",
    },
    {
        "label": "CON25",
        "domain": "consulting",
        "intent": "insight",
        "content": "Enterprise AI projects have long timelines, complex governance, and slow feedback loops. Small business engagements have short timelines, direct owners, and immediate feedback. The lab value of SMB consulting is the speed of the learning cycle: propose a system, see it in production within weeks, understand what breaks within a month. The constraints of small business — limited budget, limited technical capacity, limited time — force the kind of design discipline that enterprise projects rarely demand. The learnings transfer up; the reverse isn't as reliable.",
    },

    # ── CLUSTER 4: VBOD ─────────────────────────────────────────────────
    {
        "label": "V1",
        "domain": "meta",
        "intent": "insight",
        "content": "The VBOD (Virtual Board of Directors) uses AI as a structured advisory system — not a search engine, not a writing assistant. Distinct personas, each with a defined lens, consulted at specific moments in the decision cycle. The insight that makes it work: advisory value comes from perspective diversity, not from having the right answer. A skeptic who pushes back on a plan doesn't need to be correct — they need to surface the assumption you haven't examined. The VBOD creates that friction deliberately, rather than waiting for the real world to provide it.",
    },
    {
        "label": "V2",
        "domain": "meta",
        "intent": "reference",
        "content": "Marcus is the VBOD's executive function: the voice that translates strategic intent into operational reality. His question isn't 'is this a good idea?' — that's the board's job. His question is 'what actually needs to happen this week, in what order, and what's blocking it?' The weekly cadence runs through Marcus: review what moved, what didn't, what new information changes the picture. The output isn't a to-do list — it's a prioritized sequence with a rationale for the order. Marcus makes the next action obvious when everything feels equally urgent.",
    },
    {
        "label": "V3",
        "domain": "meta",
        "intent": "reference",
        "content": "Sarah's role on the VBOD is structured challenge on the technical side. She asks the question the enthusiastic builder avoids: what's the failure mode? What does this not work for? What assumption is this design dependent on that might not hold? Her value isn't expertise in the specific technology — it's the discipline of adversarial questioning before the build, not after. Consulting Sarah before committing to a technical approach consistently surfaces the edge case that would have become an incident later.",
    },
    {
        "label": "V4",
        "domain": "meta",
        "intent": "reference",
        "content": "James holds the commercial lens: does this work translate to value a client or employer will pay for? His challenge is the gap between what's technically interesting and what solves a business problem someone cares about enough to act on. His questions: who is the buyer for this? What decision does this make easier or faster? What's the before/after in business terms, not technical terms? James keeps the work tethered to commercial reality without suppressing the exploration that produces the work worth commercializing.",
    },
    {
        "label": "V5",
        "domain": "meta",
        "intent": "reference",
        "content": "Elena holds the communication and brand lens: how does this get explained to someone who doesn't already believe it? Her contribution isn't creative work — it's the discipline of clarity. Before any external communication (portfolio updates, client proposals, public writing), Elena's question is: does this say what we mean in terms the audience already understands? Her pushback is usually on assumed context: 'you're explaining the solution before the audience has felt the problem.' Her edits are always shorter, clearer, and more direct.",
    },
    {
        "label": "V6",
        "domain": "meta",
        "intent": "reference",
        "content": "David holds the risk and compliance lens — the voice that asks what could go wrong legally, reputationally, or operationally before it does. His questions: what's the liability if this system produces wrong output? Is this practice consistent with stated commitments? What's the regulatory interpretation risk? David isn't a blocker — he's a due diligence layer. Decisions made with his input tend to hold up better under scrutiny because the risks were acknowledged, not ignored. In a one-person operation, having a governance voice is the substitute for the review process that enterprises build in.",
    },
    {
        "label": "V7",
        "domain": "meta",
        "intent": "reference",
        "content": "Once a month, all five VBOD members are consulted on the strategic picture — not individual decisions but the overall direction. The format: a briefing document covering what changed since last month, what's working, what's not, and the top three decisions facing the next 30 days. Each persona responds in turn. The synthesis is a strategic memo: areas of agreement, areas of productive tension, and a recommended posture for the coming month. The monthly panel is the heartbeat of strategic alignment.",
    },
    {
        "label": "V8",
        "domain": "meta",
        "intent": "reference",
        "content": "The weekly operating rhythm: Marcus runs the weekly planning session every Monday — what's the sequence, what's blocking, what's been deferred too long. Marcus again for Thursday check-ins — what moved, what needs a decision before the week closes. The domain-specific personas are invoked on-demand: Sarah when a technical decision is forming, James when a commercial judgment is needed, Elena before anything gets published, David when a risk is on the table. The full panel only when a decision requires all five lenses.",
    },
    {
        "label": "V9",
        "domain": "meta",
        "intent": "insight",
        "content": "Most decisions are made and forgotten. The reasoning disappears, so when the decision gets revisited — and every significant one does — you're starting over. Decision logging captures the choice, the alternatives rejected, and the reasoning at the moment of decision. The value isn't historical record — it's pattern recognition. Review six months of logged decisions and you'll see where your judgment is reliable and where it isn't, which advisors pushed back correctly, which constraints you ignored that later mattered. The log is institutional memory for a solo operator.",
    },
    {
        "label": "V10",
        "domain": "meta",
        "intent": "insight",
        "content": "Task systems fail the same way: they optimize for capture and neglect prioritization. Everything gets added. Nothing gets sequenced. The list grows until it's a source of anxiety, not clarity. The fix requires three things a flat list can't provide: context (what project does this serve?), urgency signal (is this blocking something else?), and forced ranking (of these ten things, which one first?). Without those, the system tells you you're busy. With them, it tells you what matters. The difference is between managing tasks and managing your attention.",
    },
    {
        "label": "V11",
        "domain": "meta",
        "intent": "reference",
        "content": "A task without a priority is a task that waits for your memory to schedule it. The five-level urgency system assigns color and name to each tier: Critical (blocking active work or has a hard deadline today), High (important with a near deadline), Medium (active but not blocking), Low (relevant but deferrable), Watch (not actionable yet — waiting for something else). The color-coding makes the priority spectrum scannable at a glance. The naming convention makes the assignment decision explicit rather than implicit.",
    },
    {
        "label": "V12",
        "domain": "meta",
        "intent": "insight",
        "content": "Enterprise project management is designed for teams: status meetings, stakeholder updates, resource allocation conversations. None of that applies to a solo operator. What does apply: a project definition (what does done look like?), a current-state artifact (what's the actual status right now, in two sentences?), a next-action (the single thing that moves this forward today), and a blocking log (what's waiting on someone or something else?). Four fields per project. Everything else is overhead that creates the appearance of management without the substance of it.",
    },
    {
        "label": "V13",
        "domain": "meta",
        "intent": "reference",
        "content": "A structured morning briefing answers three questions before the work starts: what matters most today (not what's on the list — what actually matters), what's the context for the most important decision I'll face this week, and what did I forget I was tracking? The briefing isn't a to-do list — it's an orientation session. It takes five minutes when the system is current. It takes thirty when it isn't. The discipline of maintaining the system pays out every morning.",
    },
    {
        "label": "V14",
        "domain": "meta",
        "intent": "reference",
        "content": "The weekly review isn't about catching up — it's the heartbeat of the operating system. One session per week creates the cadence: review what closed (decisions made, tasks completed, loops resolved), what's open (active threads, pending responses, unresolved questions), what's new (information that changes a plan or priority), and what's next (the one or two things that actually move the week forward). The rhythm is as important as the content — a review that happens consistently at medium depth is worth more than a perfect review that happens sporadically. The heartbeat keeps the system alive.",
    },
    {
        "label": "V15",
        "domain": "meta",
        "intent": "insight",
        "content": "Accountability in a team context is structural: you committed to something in front of someone who will notice if it doesn't happen. Solo operators have to build this structure deliberately. The VBOD plays part of this role — logging a decision or commitment to Marcus creates a record that gets reviewed on Thursday. But the more durable mechanism is public commitment: writing down what you said you'd do, in a format you'll see again. The friction of visibility is what teams create automatically and solo operators have to design.",
    },
    {
        "label": "V16",
        "domain": "meta",
        "intent": "reference",
        "content": "A monthly retrospective for a solo operator: what did I finish (and does it match what I said I would finish)? Where did scope expand unexpectedly? What decisions turned out to be better or worse than I expected? What should I start, stop, or continue? The retrospective is the feedback loop that improves the planning. Without it, the same scope expansion patterns repeat, the same decision-making biases persist, and the monthly plan looks identical regardless of what the previous month revealed.",
    },
    {
        "label": "V17",
        "domain": "meta",
        "intent": "insight",
        "content": "Every context switch — from one project to another, from deep work to communication, from building to planning — has a re-entry cost. The cost is usually underestimated because it's invisible: the 15 minutes of re-establishing context before productive work can resume. Reducing context switching isn't about working on fewer things — it's about batching the same types of work and designing the day around minimizing the transitions. The most valuable calendar blocks are the ones that protect depth, not the ones that pack the most meetings.",
    },
    {
        "label": "V18",
        "domain": "meta",
        "intent": "insight",
        "content": "Systems are reliable; motivation isn't. The VBOD cadence, the weekly review, the decision log — these work because they're scheduled and structured, not because the desire to do them is consistent. The design principle: make the right behavior the path of least resistance. A review template that opens automatically on Monday morning. A decision log entry prompted at the end of any significant conversation. A morning briefing that pulls from active projects without manual setup. Habits built into systems are the ones that outlast the initial enthusiasm.",
    },
    {
        "label": "V19",
        "domain": "meta",
        "intent": "insight",
        "content": "The metrics you track are the metrics you optimize for, even unconsciously. A job search tracked by applications sent optimizes for volume. The same search tracked by interviews generated optimizes for quality. A consulting practice tracked by hours logged optimizes for time. The same practice tracked by client outcomes optimizes for value. Choosing your metrics is a strategic decision, not a reporting preference. The VBOD's job includes auditing the measurement system periodically: are these still the right things to count?",
    },
    {
        "label": "V20",
        "domain": "meta",
        "intent": "insight",
        "content": "The VBOD started as an experiment: what if AI personas could play the role of advisors you don't have access to? Not simulating specific people — simulating specific thinking styles. The skeptic who asks the question you're avoiding. The strategist who pulls the conversation toward market reality. The communicator who translates your technical work for an audience that doesn't share your context. The question that sparked it: what would a well-advised decision look like if the advisory board was always available?",
    },
    {
        "label": "V21",
        "domain": "meta",
        "intent": "insight",
        "content": "The difference between structured VBOD consultation and ad hoc AI conversation is the frame. Ad hoc: ask the AI what you want to know, get an answer, move on. The AI follows your lead. Structured VBOD: commit to a persona, a question, and a response format before the conversation starts. The persona follows its lens, not your preferences. The structured format creates productive discomfort — you asked for the skeptic's view, and now you have to sit with the pushback. That discomfort is where the value is.",
    },
    {
        "label": "V22",
        "domain": "meta",
        "intent": "insight",
        "content": "A decision log reviewed at 90 days reveals patterns that aren't visible in the moment. The decisions that seemed hard but were obvious in retrospect. The decisions that seemed easy but produced unexpected consequences. The decisions where a specific VBOD persona's pushback turned out to be correct. This is the data that improves future decision-making — not theory, not frameworks, but your own pattern of judgment applied to your own domain over time. The log is the tutor. The review session is the lesson.",
    },
    {
        "label": "V23",
        "domain": "meta",
        "intent": "insight",
        "content": "Time management assumes all hours are equal. Energy management recognizes they're not. High-cognitive work (architectural decisions, strategic analysis, complex writing) requires peak-energy windows. Low-cognitive work (email, scheduling, routine tasks) can fill recovery windows. The most common productivity mistake: filling peak-energy windows with low-cognitive tasks because they're easier to start. The VBOD weekly planning session includes an energy map: what type of work gets the best slot this week?",
    },
    {
        "label": "V24",
        "domain": "meta",
        "intent": "reference",
        "content": "Each VBOD persona operates through a skill — a defined process with a system prompt that establishes the persona, expected input format, response structure, and what decisions this persona is invoked for. Calling the skill is calling the persona. The consistency that comes from a well-written skill file is what makes VBOD consultation repeatable: Marcus in week 47 gives structurally similar output to Marcus in week 12, because the skill defines the behavior, not the conversation history.",
    },
    {
        "label": "V25",
        "domain": "meta",
        "intent": "insight",
        "content": "Solo operators typically have no institutional memory — knowledge exists in their head, lost when context shifts or enough time passes. The VBOD, combined with Open Brain, creates a substitute: decisions logged, rationale stored, persona-specific recommendations saved as memories. When a similar decision arises six months later, the prior decision is retrievable, the reasoning is accessible, and the VBOD member who pushed back is there to be consulted again with the prior context loaded. Institutional memory, built deliberately.",
    },

    # ── CLUSTER 5: PORTFOLIO ─────────────────────────────────────────────
    {
        "label": "PORT1",
        "domain": "personal",
        "intent": "decision",
        "content": "Ten years of enterprise transformation consulting produced a specific credibility: walk into a complex organization, diagnose what's actually broken versus what people say is broken, and design something that gets adopted. It also produced a gap — everything built was built by someone else. The decision to start building was about closing that gap. Not abandoning the consulting lens, but adding hands-on technical experience to it. The result: a practitioner who can sit in both the architecture conversation and the governance conversation, and connect them, because they've personally navigated both.",
    },
    {
        "label": "PORT2",
        "domain": "personal",
        "intent": "reference",
        "content": "B.S. in Biomedical Engineering from Rutgers, M.E. in Systems Engineering from Stevens Institute. The biomedical background makes pharma's technical vocabulary natural — clinical trial design, regulatory pathways, drug approval timelines. The systems engineering lens provides the analytical framework for decomposing complex problems: every system has inputs, outputs, feedback loops, and failure modes. Combined: the ability to operate at the biological system level and the organizational system level in the same conversation — a combination that's rarer than it should be.",
    },
    {
        "label": "PORT3",
        "domain": "personal",
        "intent": "decision",
        "content": "The focus on pharmaceutical AI governance isn't arbitrary — it's the intersection of every thread. The biomedical engineering background makes the science legible. The enterprise consulting experience makes the organizational dynamics familiar. The AI builder work makes the technical constraints concrete. Pharma is the domain where all three are simultaneously required and rare. The other factor: the stakes are real. AI governance in pharma means systems that touch drug development timelines, clinical trial integrity, and patient outcomes. That weight matches the seriousness of the work.",
    },
    {
        "label": "PORT4",
        "domain": "personal",
        "intent": "reference",
        "content": "A decade of management consulting at a Big 4 firm, working across life sciences and technology: Merck, Takeda, Pfizer, ADP, Nvidia, Otsuka. The pattern across engagements: the technical problem was rarely the real problem. The real problem was organizational — misaligned incentives, competing definitions of success, resistance to changes that threatened existing power structures. The technical work was the deliverable. The organizational work was what made the deliverable stick. Separating those two is where most transformation projects fail.",
    },
    {
        "label": "PORT5",
        "domain": "personal",
        "intent": "insight",
        "content": "Enterprise transformation consultants and hands-on AI builders don't usually live in the same person. Consultants learn to diagnose and recommend. Engineers learn to build and ship. The gap between those two modes is where most AI initiatives break down — the diagnosis is right but the implementation doesn't match organizational reality, or the build is technically sound but nobody adopts it. The combination enables something neither alone can do: design a governance framework the engineering team will actually follow, or build a system that solves a real workflow problem rather than an imagined one.",
    },
    {
        "label": "PORT6",
        "domain": "personal",
        "intent": "insight",
        "content": "Building software after years in enterprise consulting produces specific design instincts. You ask who the real stakeholders are before you write a line of code. You think about the adoption failure modes before you design the feature set. You define success criteria before you start, because you've seen what happens when you try to define them after. You design for the person who will maintain this when you're gone, not the person who built it. These instincts aren't innate — they come from watching transformation programs succeed and fail at scale.",
    },
    {
        "label": "PORT7",
        "domain": "personal",
        "intent": "reference",
        "content": "Enrolled in an MIT Applied AI cohort beginning early 2026. Goal: deepen technical builder capability beyond consulting frameworks. Focus areas: RAG system design, agent architecture, production deployment patterns. Context: transitioning from enterprise transformation consulting to pharma AI governance and digital health leadership. The cohort accelerates hands-on technical fluency in parallel with the job search — the goal isn't a credential, it's the capability that makes the credential credible.",
    },
    {
        "label": "PORT8",
        "domain": "personal",
        "intent": "decision",
        "content": "Posting about what you're building while building it does something a resume can't: it creates a record of thinking in progress. Not polished retrospectives — actual decisions being made, what worked, what didn't, why something was rebuilt. That record is more credible than a case study because it shows the process, not just the outcome. The portfolio site, the Open Brain demo, the public write-ups — the same strategy in different formats. The signal: this person thinks out loud, builds in public, and doesn't hide the hard parts.",
    },
    {
        "label": "PORT9",
        "domain": "personal",
        "intent": "insight",
        "content": "Enterprise consulting teaches you to operate at scale: large budgets, complex stakeholders, long timelines. It doesn't teach you to move fast with nothing. Running a small consultancy with real clients and no team teaches the opposite: prioritize ruthlessly, deliver something imperfect that works, iterate in public. Both modes are necessary. Enterprise produces framework thinking and stakeholder instincts. Founder mode produces bias for action and tolerance for ambiguity. The practitioners who can switch between them are rare and, in the current AI landscape, increasingly valuable.",
    },
    {
        "label": "PORT10",
        "domain": "personal",
        "intent": "reference",
        "content": "The portfolio site (jonlum.vercel.app) was redesigned to function as a product, not a resume. The key distinction: a resume lists what you've done; a product demonstrates what you can do. The v3 redesign: claim-first hero that stakes a position, 'What I've Done / What I've Built' cards that show consulting experience and technical output side by side, and interactive demos that let visitors experience the work rather than read about it. The site is the first deliverable in the portfolio — it demonstrates the same capabilities it claims.",
    },
    {
        "label": "PORT11",
        "domain": "personal",
        "intent": "reference",
        "content": "At a major pharmaceutical company, led design of a regulatory submission platform that compressed a multi-month approval cycle by several months through workflow automation and cross-functional data integration. The technical work was integration design. The real work was getting four organizational functions — regulatory, legal, medical, manufacturing — to agree on a shared data model and a shared workflow, when each had historically operated with separate systems and separate definitions of a 'submission.' The platform was the artifact; the governance was the product.",
    },
    {
        "label": "PORT12",
        "domain": "personal",
        "intent": "reference",
        "content": "At a Fortune 250 HR technology company, built an AI governance framework adopted across 20+ product teams. The framework challenge: one set of standards applied uniformly would create compliance theater, not real governance. The solution (the agile kingdoms pattern): common guardrails with team-specific implementation. Data classification standards and model approval gates applied universally; technical implementation left to each team within those guardrails. Adoption rate significantly higher than previous top-down governance attempts. The design insight: governance designed with resistance, not against it.",
    },
    {
        "label": "PORT13",
        "domain": "personal",
        "intent": "reference",
        "content": "During a major cyberattack at a pharmaceutical company, worked on the IT recovery program — one of the most complex incidents in pharmaceutical history at the time. The consulting role: coordination between technical recovery teams, business continuity planning, and regulatory communication. The lesson: under genuine crisis conditions, the organizations that recover fastest are the ones with clear decision authority and pre-established communication protocols. The ones that slow down are the ones arguing about who decides while the damage compounds.",
    },
    {
        "label": "PORT14",
        "domain": "personal",
        "intent": "reference",
        "content": "Led R&D analytics platform design during a major pharmaceutical merger — integrating two research organizations with different data architectures, different tool stacks, and deep institutional loyalty to their respective systems. The platform served 200+ researchers at launch. The design challenge: build something both sides could claim as theirs, because a system that 'belongs' to the acquirer is resisted by the acquired. Technical solution: neutral data layer with each team's preferred front-end tools. Organizational solution: joint governance committee with equal representation from both sides.",
    },
    {
        "label": "PORT15",
        "domain": "personal",
        "intent": "insight",
        "content": "Open Brain was built because the problem was real and the existing solutions weren't right. After months of running complex multi-session AI workflows, the cost of AI amnesia became concrete: re-establishing context in every session, losing reasoning chains that spanned weeks, missing connections between work happening in different tools. The decision to build rather than buy: no existing tool combined persistent memory with MCP exposure across both local and cloud, with the retrieval quality a knowledge-intensive workflow requires. The build was the product of the need.",
    },
    {
        "label": "PORT16",
        "domain": "personal",
        "intent": "reference",
        "content": "Built a CRM for real estate agents, designed specifically for the New Jersey market's regulatory environment and transaction timelines. The constraint that shaped the design: agents spend most of their time in the field, not at desks. Mobile-first wasn't a preference — it was the requirement. The product design question: what does an agent need to do in 30 seconds standing in a driveway? That question produced a different product than 'what features does a CRM typically include?' Real constraints are better design inputs than feature checklists.",
    },
    {
        "label": "PORT17",
        "domain": "personal",
        "intent": "reference",
        "content": "Built a personal job search automation system: web scrapers for job boards, a Gmail alert parser for new postings, a SQLite database tracking 88+ opportunities by stage, and a fit-scoring framework that filters on domain match, seniority level, and technical requirements. The output isn't a list of jobs — it's a prioritized pipeline with signal on where the funnel is leaking. The system treats job searching as a product problem: instrument the funnel, identify the conversion failure, improve the input quality. The same infrastructure runs the AssessFitCTA on the portfolio site.",
    },
    {
        "label": "PORT18",
        "domain": "personal",
        "intent": "insight",
        "content": "The insight that became the signature consulting framework came from watching governance fail repeatedly in the same way: applied uniformly across teams with genuinely different risk profiles, it created workarounds instead of compliance. The agile kingdoms frame: identify which units need fast autonomy (kingdoms) versus which need coordinated standards (the empire). Design governance to hold the empire together while freeing the kingdoms. The frame works because it names the political reality — some teams have legitimate reasons to operate differently — rather than pretending uniformity is achievable.",
    },
    {
        "label": "PORT19",
        "domain": "personal",
        "intent": "insight",
        "content": "Running a systematic job search across 88+ opportunities revealed patterns that a less structured approach would have missed. The roles that advance past screening share a specific characteristic: they're at the intersection of technical platform ownership and organizational governance, not purely one or the other. The roles that don't advance are either too technical (no governance mandate) or too governance-heavy (no platform ownership). The job search data confirmed the career thesis: the intersection is the rare and valuable position, and the market hasn't fully priced it yet.",
    },
    {
        "label": "PORT20",
        "domain": "personal",
        "intent": "reference",
        "content": "Based in the New York/New Jersey area — the most concentrated life sciences and pharmaceutical market in the world, with clusters in Morris County, Princeton, and the broader tri-state area. The geographic positioning matters for the career thesis: proximity to the pharma industry's decision-making infrastructure means in-person relationship building is possible without relocation. The regional market also supports the consulting practice: NJ's dense small business economy provides a continuous pipeline of SMB transformation opportunities.",
    },
    {
        "label": "PORT21",
        "domain": "personal",
        "intent": "reference",
        "content": "The personal AI workflow runs across four tools with defined roles: Claude Chat (Strategist — high-level analysis, document drafting, cross-domain synthesis), Claude Code (Builder — code generation, file operations, system builds), Gemini (Compiler — research aggregation, data synthesis), and Cowork (Operator — desktop automation, file management). Open Brain provides the memory layer that connects them. The VBOD personas live in each tool's skill files. Skills bridge the tools. The result is a coordinated AI system that behaves consistently across environments.",
    },
    {
        "label": "PORT22",
        "domain": "personal",
        "intent": "insight",
        "content": "Every tool built — Open Brain, RE-CRM, the job pipeline — started as a real need, hit real constraints, and produced insight unavailable from reading about it. The chunking problem in Open Brain isn't in any textbook; it's discovered when retrieval fails on a real query. The mobile-first constraint in RE-CRM isn't assumed; it's articulated by a real estate agent who tried to use it in the field. Advisory work tells you what the problems are. Building tells you why the solutions are hard. That distinction is the gap between consulting from the outside and leading from the inside.",
    },
    {
        "label": "PORT23",
        "domain": "personal",
        "intent": "reference",
        "content": "Pharmaceutical AI in 2025-2026 is past the proof-of-concept stage and into the governance and scaling question. The capability exists — LLMs that can read clinical literature, analyze trial data, support regulatory writing. The bottleneck is governance: who approves what models can do what, with what data, under what audit requirements? Field force AI is a specific sub-problem: sales rep tools that optimize call planning and HCP engagement, operating under FDA promotional compliance constraints. The governance complexity is the career opportunity.",
    },
    {
        "label": "PORT24",
        "domain": "personal",
        "intent": "insight",
        "content": "The traditional credibility-building path for a technical professional: get the credential, do the work at recognized institutions, let reputation accumulate privately. The alternative path, more accessible and faster: demonstrate thinking in public, build tools that demonstrate capability, write about what you're learning in real time. The second path has a different kind of credibility — it's verifiable in a way that credentials aren't. You can look at the code, interact with the demo, read the reasoning process. The credential says 'trusted by institution X.' The public build says 'see for yourself.'",
    },
    {
        "label": "PORT25",
        "domain": "personal",
        "intent": "insight",
        "content": "The convergence point: pharma AI governance roles that require both the enterprise transformation background and the hands-on AI building experience. The portfolio site, the demos, and the public building process are all oriented toward making that combination legible to decision-makers who haven't seen it before. The near-term work: continue building (RE-CRM to production, Open Brain demo live, job pipeline dashboard visible), continue writing (the reasoning behind the builds), and continue connecting (the pharma AI governance community is small and the right relationships matter more than the right applications).",
    },
]


# ---------------------------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------------------------

def create_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS memory_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            domain TEXT NOT NULL,
            intent TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'manual',
            source_file TEXT,
            embedding BLOB,
            content_hash TEXT UNIQUE,
            model_id TEXT NOT NULL DEFAULT 'all-MiniLM-L6-v2',
            created_at TEXT NOT NULL,
            visibility TEXT NOT NULL DEFAULT 'public'
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
            content,
            domain,
            intent,
            content=memory_nodes,
            content_rowid=id
        );

        CREATE TABLE IF NOT EXISTS memory_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id INTEGER NOT NULL REFERENCES memory_nodes(id),
            to_id INTEGER NOT NULL REFERENCES memory_nodes(id),
            link_type TEXT NOT NULL DEFAULT 'related',
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_links_from ON memory_links(from_id);
        CREATE INDEX IF NOT EXISTS idx_links_to ON memory_links(to_id);
    """)
    conn.commit()


def content_hash(text):
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


# ---------------------------------------------------------------------------
# MAIN SEED FUNCTION
# ---------------------------------------------------------------------------

def seed(db_path, map_path):
    print("Loading embedding model...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("  Model loaded: all-MiniLM-L6-v2")
    except ImportError:
        print("  ERROR: sentence-transformers not installed.")
        print("  Run: pip install sentence-transformers")
        return

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    create_schema(conn)

    node_id_map = {}
    now = datetime.utcnow().isoformat()
    skipped = 0
    inserted = 0

    print(f"\nSeeding {len(NODES)} nodes...")
    for i, node in enumerate(NODES):
        label = node["label"]
        content = node["content"]
        chash = content_hash(content)

        # Check for duplicate
        existing = conn.execute(
            "SELECT id FROM memory_nodes WHERE content_hash = ?", (chash,)
        ).fetchone()
        if existing:
            node_id_map[label] = existing[0]
            skipped += 1
            continue

        # Embed
        embedding = model.encode(content)
        embedding_blob = embedding.tobytes()

        cursor = conn.execute(
            """INSERT INTO memory_nodes
               (content, domain, intent, source, source_file, embedding,
                content_hash, model_id, created_at, visibility)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                content,
                node["domain"],
                node["intent"],
                "manual",
                "ob-demo-node-design-mar2026",
                embedding_blob,
                chash,
                MODEL_ID,
                now,
                "public",
            ),
        )
        db_id = cursor.lastrowid

        # Sync FTS
        conn.execute(
            "INSERT INTO nodes_fts(rowid, content, domain, intent) VALUES (?, ?, ?, ?)",
            (db_id, content, node["domain"], node["intent"]),
        )

        node_id_map[label] = db_id
        inserted += 1

        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/125] cluster checkpoint — committing...")
            conn.commit()

    conn.commit()
    conn.close()

    # Save ID map
    with open(map_path, "w") as f:
        json.dump(node_id_map, f, indent=2)

    print(f"\n✓ Seeding complete: {inserted} inserted, {skipped} skipped (duplicates)")
    print(f"✓ node_id_map.json saved to: {map_path}")
    print(f"✓ Database: {db_path}")

    # Verify counts
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM memory_nodes").fetchone()[0]
    conn.close()
    print(f"✓ Total nodes in DB: {total}")


if __name__ == "__main__":
    seed(DB_PATH, MAP_PATH)

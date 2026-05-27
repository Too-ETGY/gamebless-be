# Gamebless — Data Flow Diagrams

---

## Level 0 — Context Diagram

> *This diagram shows the Gamebless System as a single process interacting with all external entities. The data flows are high-level to represent the overall purpose of each connection.*

```mermaid
flowchart TD
    USER(["👤 User / Mobile App"])
    FIREBASE(["🔐 Firebase Auth"])
    WEBSITES(["🌐 Target Websites"])

    GAMEBLESS["⚙️ Gamebless System"]

    FIRESTORE[("🗄️ Firestore<br/>(Main Database)")]
    GEMINI(["🤖 Gemini AI"])
    CHROMA[("🔍 ChromaDB<br/>(Vector Database)")]
    REDIS[("⚡ Redis<br/>(Cache)")]

    %% User Interactions
    USER <-->|"App requests & responses<br/>(Chat, Checks, Progress)"| GAMEBLESS
    
    %% Authentication
    FIREBASE <br/> Authentication -->|"Identity verification"| GAMEBLESS

    %% Main Database
    GAMEBLESS <-->|"Read/Write all application data<br/>(Users, Chat, Domains, Challenges)"| FIRESTORE

    %% AI & Processing
    GAMEBLESS <-->|"AI prompts & generated responses"| GEMINI
    GAMEBLESS <-->|"Store & search context<br/>embeddings"| CHROMA
    GAMEBLESS <-->|"Cache frequent responses"| REDIS
    GAMEBLESS -->|"Fetch site content"| WEBSITES

    classDef entity fill:#6366f1,color:#fff,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#f59e0b,stroke-width:2px,rx:10
    classDef store fill:#0f172a,color:#e2e8f0,stroke:#334155
    class USER,FIREBASE,WEBSITES,GEMINI entity
    class GAMEBLESS process
    class FIRESTORE,CHROMA,REDIS store
```

---

## Level 1 — Chat Module

> *This diagram breaks down the Chat functionality. Layout is top-down to improve readability.*

```mermaid
flowchart TD
    USER(["👤 User"])
    GEMINI(["🤖 Gemini AI"])

    subgraph Data Stores
        SESSIONS[("Chat Sessions")]
        MESSAGES[("Chat Messages")]
        CHALLENGES[("Challenges DB")]
        VECTORS[("ChromaDB<br/>Embeddings")]
    end

    %% Session Management
    USER -->|"Open chat<br/>or popup"| P1
    P1["1.0<br/>Session<br/>Management"]
    P1 <-->|"Get / Create<br/>Session"| SESSIONS
    P1 -->|"Session Info"| USER

    %% Message Processing
    USER -->|"Send Message"| P2
    P2["2.0<br/>Message<br/>Processing"]
    P2 -->|"Save User Message<br/>& AI Response"| MESSAGES
    MESSAGES -->|"Fetch History"| P2
    P2 -->|"Update count"| SESSIONS
    P2 -->|"Final AI text"| USER

    %% RAG Context
    P2 -->|"Message text"| P3
    P3["3.0<br/>RAG Context<br/>Retrieval"]
    P3 -->|"Query"| VECTORS
    VECTORS -->|"Past context"| P3
    P3 -->|"Context"| P4

    %% AI Generation
    P2 -->|"Message + Context"| P4
    P4["4.0<br/>AI Response<br/>Generation"]
    P4 <-->|"Prompt & Response"| GEMINI
    P4 -->|"Generated text"| P2

    %% Challenge Tools
    P4 -->|"Tool call:<br/>Recommend"| P5
    P5["5.0<br/>Challenge<br/>Recommendation"]
    P5 -->|"Search"| VECTORS
    VECTORS -->|"Matches"| P5
    P5 -->|"Check status"| CHALLENGES
    CHALLENGES -->|"Uncompleted"| P5
    P5 -->|"Recommendation"| P4

    %% Rotation
    P2 -.->|"Trigger check"| P6
    P6["6.0<br/>Session<br/>Rotation"]
    SESSIONS -->|"Message count / Age"| P6
    P6 <-->|"Summarize"| GEMINI
    P6 -->|"Archive old<br/>Create new"| SESSIONS
    P6 -->|"Delete old"| MESSAGES

    classDef entity fill:#6366f1,color:#fff,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#f59e0b,stroke-width:2px,rx:50
    classDef store fill:#0f172a,color:#e2e8f0,stroke:#334155
    class USER,GEMINI entity
    class P1,P2,P3,P4,P5,P6 process
    class SESSIONS,MESSAGES,CHALLENGES,VECTORS store
```

---

## Level 1 — Domain Module

> *This diagram breaks down the Domain Checking and Reporting logic.*

```mermaid
flowchart TD
    USER(["👤 User"])
    GEMINI(["🤖 Gemini AI"])
    WEBSITES(["🌐 Target Websites"])

    subgraph Data Stores
        DOMAINS[("Blocked<br/>Domains (Firestore)")]
        VECTORS[("ChromaDB<br/>Embeddings")]
        CACHE[("Redis Cache")]
    end

    %% Check Flow
    USER -->|"URL to check"| P1
    P1["1.0<br/>Domain<br/>Check"]
    P1 -->|"Check cache"| CACHE
    CACHE -->|"Hit/Miss"| P1
    P1 -->|"Lookup exact"| DOMAINS
    DOMAINS -->|"Match result"| P1
    P1 -->|"Blocked/Allowed"| USER
    P1 -->|"Cache new result"| CACHE

    %% Report Flow
    USER -->|"Report suspicious URL"| P2
    P2["2.0<br/>Domain<br/>Report"]
    P2 -->|"Check if already blocked"| DOMAINS
    DOMAINS -->|"Exists status"| P2
    P2 -->|"Save confirmed"| DOMAINS
    P2 -->|"Invalidate cache"| CACHE

    %% Similarity
    P1 -->|"Check similarity"| P3
    P2 -->|"Check similarity"| P3
    P3["3.0<br/>Similarity<br/>Search"]
    P3 -->|"Query"| VECTORS
    VECTORS -->|"Similarity score"| P3
    P3 -->|"Result"| P1
    P3 -->|"Result"| P2

    %% Web Scraping
    P2 -->|"If similarity is low"| P4
    P4["4.0<br/>Web<br/>Scraping"]
    P4 -->|"Fetch page"| WEBSITES
    WEBSITES -->|"HTML"| P4
    P4 -->|"Extracted signals"| P5

    %% AI Analysis
    P5["5.0<br/>AI Site<br/>Analysis"]
    P5 <-->|"Analyze signals"| GEMINI
    P5 -->|"Gambling? (Yes/No)"| P2

    classDef entity fill:#6366f1,color:#fff,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#f59e0b,stroke-width:2px,rx:50
    classDef store fill:#0f172a,color:#e2e8f0,stroke:#334155
    class USER,GEMINI,WEBSITES entity
    class P1,P2,P3,P4,P5 process
    class DOMAINS,VECTORS,CACHE store
```

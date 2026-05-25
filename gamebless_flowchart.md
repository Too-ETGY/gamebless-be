# Gamebless — Application Flowcharts

> How the Gamebless app works, from the user's perspective.

---

## 1. Auth & Onboarding

```mermaid
flowchart LR
    A["User opens the app"] --> B{"First time<br/>using the app?"}
    B -->|Yes| C["Sign in with<br/>Google account"]
    C --> D["Profile is created<br/>automatically"]
    D --> E["Enter home screen"]
    B -->|No| F["Load user profile<br/>and stats"]
    F --> E

    classDef start fill:#6366f1,color:#fff,stroke:none
    classDef decision fill:#fbbf24,color:#1e1e1e,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#334155
    classDef success fill:#22c55e,color:#fff,stroke:none
    class A start
    class B decision
    class C,D,F process
    class E success
```

---

## 2. Domain Blocking

```mermaid
flowchart LR
    A["User tries to visit<br/>a website"] --> B{"Is the site a<br/>gambling site?"}
    B -->|No| C["Access allowed<br/>normally"]
    B -->|Yes| D["Access blocked<br/>pop-up appears"]
    D --> E["Gambling attempt<br/>is recorded"]
    E --> F["Streak resets to 0"]
    F --> G["AI Companion chat<br/>pops up to support user"]
    G --> H(["→ Chat Module"])

    I["User reports a<br/>suspicious website"] --> J["Report is received"]
    J --> K[/"Site is analyzed<br/>in the background"/]
    K --> L{"Confirmed as<br/>gambling site?"}
    L -->|Yes| M["Added to blocked<br/>site database"]
    L -->|No| N["Discarded"]

    classDef start fill:#6366f1,color:#fff,stroke:none
    classDef decision fill:#fbbf24,color:#1e1e1e,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#334155
    classDef success fill:#22c55e,color:#fff,stroke:none
    classDef error fill:#ef4444,color:#fff,stroke:none
    classDef async fill:#8b5cf6,color:#fff,stroke:none
    classDef link fill:#6366f1,color:#fff,stroke:none,rx:20
    class A,I start
    class B,L decision
    class J process
    class C,M success
    class D,E,F error
    class K async
    class G,H link
    class N process
```

---

## 3. AI Chat Companion

```mermaid
flowchart LR
    A1["User taps Chat<br/>in the app"] --> B
    A2["Triggered by<br/>blocked site pop-up"] --> B

    B["Open chat<br/>conversation"] --> C["Load previous<br/>messages"]
    C --> D["User sends<br/>a message"]
    D --> E["AI processes message<br/>with conversation context"]
    E --> F["AI responds with<br/>empathetic support"]
    F --> G{"User continues<br/>chatting?"}
    G -->|Yes| D
    G -->|No| H["Conversation saved<br/>for next visit"]

    F --> I{"Conversation<br/>getting long?"}
    I -->|Yes| J["Conversation is<br/>summarized and<br/>a fresh session starts"]
    J --> H
    I -->|No| G

    F -.->|"AI can also"| K["Recommend challenges<br/>based on user context"]
    K -.-> L["Retrieve user progress,<br/>history, and profile<br/>for personalized advice"]

    classDef start fill:#6366f1,color:#fff,stroke:none
    classDef decision fill:#fbbf24,color:#1e1e1e,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#334155
    classDef success fill:#22c55e,color:#fff,stroke:none
    classDef ai fill:#8b5cf6,color:#fff,stroke:none
    classDef capability fill:#0ea5e9,color:#fff,stroke:none
    class A1,A2 start
    class G,I decision
    class B,C,D,E,J process
    class F ai
    class H success
    class K,L capability
```

---

## 4. Challenges

```mermaid
flowchart LR
    A["User opens<br/>Challenges tab"] --> B["See all available<br/>challenges"]
    B --> C{"Filter by<br/>category?"}
    C -->|Yes| D["Filter: Article,<br/>Video, or Fun Fact"]
    C -->|No| E["Browse all<br/>challenges"]
    D --> E
    E --> F["User picks<br/>a challenge"]
    F --> G["Consume content:<br/>read article, watch video,<br/>or read fun fact"]
    G --> H["Answer the<br/>quiz question"]
    H --> I["Challenge completed<br/>points earned!"]
    I --> J{"Do more<br/>challenges?"}
    J -->|Yes| E
    J -->|No| K["Return to<br/>home screen"]

    L["User checks<br/>challenge history"] --> M["See all completed<br/>challenges and<br/>total points"]

    classDef start fill:#6366f1,color:#fff,stroke:none
    classDef decision fill:#fbbf24,color:#1e1e1e,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#334155
    classDef success fill:#22c55e,color:#fff,stroke:none
    class A,L start
    class C,J decision
    class B,D,E,F,G,H,M process
    class I,K success
```

---

## 5. Progress & Streaks

```mermaid
flowchart LR
    A["User opens<br/>Progress screen"] --> B["Load personal<br/>progress data"]
    B --> C{"Joined more than<br/>90 days ago?"}
    C -->|Yes| D["Show last 90 days<br/>with a notice"]
    C -->|No| E["Show full history<br/>since joining"]
    D --> F
    E --> F["View progress dashboard"]
    F --> G["Daily calendar view:<br/>clean days vs.<br/>attempt days"]
    F --> H["Current streak &<br/>longest streak"]
    F --> I["Challenges completed<br/>by category"]

    classDef start fill:#6366f1,color:#fff,stroke:none
    classDef decision fill:#fbbf24,color:#1e1e1e,stroke:none
    classDef process fill:#1e293b,color:#e2e8f0,stroke:#334155
    classDef success fill:#22c55e,color:#fff,stroke:none
    class A start
    class C decision
    class B,D,E process
    class F,G,H,I success
```

---

## Module Interaction Overview

```mermaid
flowchart LR
    HOME["🏠 Home Screen<br/>Profile · Stats · Streak"] --- DOMAIN
    HOME --- CHALLENGES
    HOME --- CHAT
    HOME --- PROGRESS

    DOMAIN["🔒 Domain Blocking<br/>Detect & block<br/>gambling sites"]
    CHALLENGES["🏆 Challenges<br/>Article · Video · Fun Fact<br/>Earn points via quiz"]
    CHAT["💬 AI Companion<br/>Emotional support<br/>& personalized advice"]
    PROGRESS["📊 Progress<br/>Streaks · Calendar<br/>Daily activity"]

    DOMAIN -->|"Blocked site<br/>triggers pop-up"| CHAT
    CHALLENGES -->|"Completed challenges<br/>add to stats"| PROGRESS
    DOMAIN -->|"Attempt recorded<br/>breaks streak"| PROGRESS

    classDef home fill:#6366f1,color:#fff,stroke:none
    classDef module fill:#1e293b,color:#e2e8f0,stroke:#334155
    class HOME home
    class DOMAIN,CHALLENGES,CHAT,PROGRESS module
```

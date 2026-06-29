

---

# 🚀 Project Concept  
## **InboxIntel — Autonomous Newsfeed Intelligence Agent**

**Track:** *Agents for Business* or *Concierge Agents*  
**Core Idea:**  
People receive hundreds of newsletters, alerts, market digests, and promotional emails. Valuable news is buried inside clutter. InboxIntel is a **multi-agent system** that autonomously:

- Reads incoming emails  
- Classifies them (newsfeed vs non-newsfeed)  
- Extracts all article links  
- Fetches metadata from each link  
- Builds a structured “Daily Intelligence Digest”  
- Publishes it as a **shareable webpage** or **JSON API**  
- Learns user preferences over time  

This solves a real-world problem: **information overload**.

---

# 🧠 Why This Idea Will Score High  
### ✔ Strong agent use  
You’ll demonstrate:  
- Multi-agent orchestration  
- MCP tools  
- ADK agent behaviors  
- Security sandboxing  
- Deployability  

### ✔ Real-world value  
Everyone deals with email overload. This is a practical, portfolio-ready solution.

### ✔ Clear architecture  
Judges love clean diagrams, modularity, and reproducibility.

### ✔ Easy to demo  
You can show the agent reading emails, extracting links, and generating a digest.

---

# 🏗 Multi-Agent Architecture  
Below is the architecture you should implement.

---

## **1. Supervisor Agent**  
Coordinates all other agents.

**Responsibilities:**  
- Receives “New Email Event”  
- Decides which worker agents to activate  
- Maintains workflow state  
- Ensures safety and retries  

---

## **2. Email Ingestion Agent**  
Uses MCP tools to read emails from Outlook/Gmail.

**Responsibilities:**  
- Fetch unread emails  
- Extract:  
  - sender  
  - subject  
  - timestamp  
  - raw HTML  
- Pass email content to classifier  

---

## **3. Email Classifier Agent**  
A small LLM agent trained on your 7 categories + “Newsfeed”.

**Responsibilities:**  
- Classify email  
- If category = “Newsfeed”, forward to Link Extraction Agent  
- Else archive or ignore  

---

## **4. Link Extraction Agent**  
Parses HTML safely.

**Responsibilities:**  
- Extract all URLs  
- Filter only article/news URLs  
- Normalize them  
- Send each URL to Metadata Agent  

---

## **5. Article Metadata Agent**  
Fetches metadata using MCP HTTP tool.

**Responsibilities:**  
- Fetch article title  
- Fetch description  
- Fetch publication date  
- Fetch publisher  
- Summarize article (optional)  

---

## **6. Digest Builder Agent**  
Creates the final structured output.

**Output Format:**  
```
{
  "email_date": "...",
  "source": "...",
  "articles": [
    {
      "title": "...",
      "url": "...",
      "publisher": "...",
      "summary": "...",
      "published_at": "..."
    }
  ]
}
```

---

## **7. Publisher Agent**  
Publishes digest as:

- Static HTML page  
- JSON API endpoint  
- Markdown file  
- Or pushes to Notion / GitHub Pages  

---

# 📁 Project Structure (for GitHub + Kaggle)

```
inboxintel/
│
├── agents/
│   ├── supervisor.py
│   ├── email_ingestion.py
│   ├── classifier.py
│   ├── link_extractor.py
│   ├── metadata_agent.py
│   ├── digest_builder.py
│   └── publisher.py
│
├── tools/
│   ├── email_reader_mcp.py
│   ├── http_fetch_mcp.py
│   └── html_parser.py
│
├── config/
│   ├── agent_manifest.json
│   └── mcp_server.yaml
│
├── tests/
│   ├── test_classifier.py
│   ├── test_link_extractor.py
│   └── test_metadata_agent.py
│
├── demo/
│   ├── sample_emails/
│   └── demo_script.md
│
├── README.md
└── run.py
```

---

# 📘 README.md (Competition-ready Draft)

## **InboxIntel — Autonomous Newsfeed Intelligence Agent**

### **Problem**  
People receive dozens of newsletters daily. Important news gets buried. Manual filtering wastes time and reduces productivity.

### **Solution**  
InboxIntel is a multi-agent system that autonomously processes incoming emails, identifies newsfeeds, extracts article links, fetches metadata, and builds a structured daily digest.

### **Architecture**  
(Insert diagram)

### **Agents**  
- Supervisor  
- Email Ingestion  
- Classifier  
- Link Extractor  
- Metadata Agent  
- Digest Builder  
- Publisher Agent  

### **Key Concepts Demonstrated**  
- Multi-agent system (ADK)  
- MCP server + tools  
- Security sandboxing  
- Deployability  
- Agent skills  

### **Setup Instructions**  
- Install dependencies  
- Configure MCP server  
- Add email provider credentials  
- Run `python run.py`  

### **Demo**  
- Shows email ingestion  
- Shows classification  
- Shows link extraction  
- Shows digest generation  

---

# 🎥 Video Script (5 minutes)

**1. Intro (20 sec)**  
“Information overload is real. InboxIntel solves it using autonomous agents.”

**2. Problem (30 sec)**  
Show inbox clutter.

**3. Architecture (1 min)**  
Walk through the multi-agent diagram.

**4. Demo (2 min)**  
Show:  
- Email arrives  
- Agent classifies  
- Extracts links  
- Fetches metadata  
- Builds digest  
- Publishes webpage  

**5. Build (40 sec)**  
Show code snippets.

**6. Closing (20 sec)**  
“This project demonstrates real-world agentic automation.”

---

# 🌐 Public Demo Plan  
You can deploy:

- A simple FastAPI endpoint  
- A static GitHub Pages site  
- A Streamlit dashboard  

Digest updates automatically when new emails arrive.

---

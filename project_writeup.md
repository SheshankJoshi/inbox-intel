

# 📘 **InboxIntel: Multi‑Agent Email Intelligence System**  
### *VibeCoding Agents Capstone Project — Final Write‑Up*

---

## 🧩 **1. Problem Statement**

Email inboxes today are overflowing with newsletters, promotional blasts, social updates, and transactional messages. Important news digests often get buried under irrelevant clutter, making it difficult for users to stay informed.

Even when newsletters are opened, they contain multiple article links, embedded HTML content, and metadata that require manual extraction. Reading them across different emails is time‑consuming and inconvenient.

The core challenges are:

- **Information overload** — newsletters mixed with unrelated emails  
- **Fragmented reading experience** — multiple links across multiple emails  
- **Lack of automation** — no built‑in way to classify, extract, summarize  
- **Accessibility gaps** — users may prefer listening to news instead of reading  
- **No unified digest** — newsletters cannot be consumed in a single place  

**InboxIntel** solves this by building a multi‑agent system that automatically:

1. Ingests emails  
2. Classifies them  
3. Extracts article links  
4. Fetches metadata  
5. Builds a daily digest  
6. Publishes it for browser reading or text‑to‑speech playback  

This transforms a chaotic inbox into a clean, structured, readable news experience.

---

## 🧠 **2. Solution Overview**

InboxIntel is a **fully modular, agentic pipeline** designed to operate on both sample emails and real IMAP inboxes. It uses:

- **LLM‑powered classification**  
- **LLM‑powered link extraction**  
- **HTTP metadata enrichment**  
- **Digest generation**  
- **Optional FastAPI serving**  

The system is built to be:

- **Deterministic** — strict JSON schemas  
- **Extensible** — each agent is replaceable  
- **Notebook‑native** — runnable entirely inside Kaggle  
- **Production‑ready** — same logic as the full application version  

---

## 🤖 **3. Multi‑Agent Architecture**

InboxIntel uses a clean, layered agent architecture:

### **1. Email Ingestion Agent**
Fetches unread emails from:
- Sample JSON files (demo mode)  
- IMAP inbox (real mode)

Outputs normalized `EmailMessage` objects containing:
- Sender  
- Subject  
- Timestamp  
- HTML body  
- Text body  

---

### **2. Email Classification Agent**
Uses an OpenAI‑compatible LLM endpoint to classify emails into categories:

- Newsfeed  
- Promotion  
- Social  
- Finance  
- Work  
- Updates  
- Personal  
- Other  

This filters out only **newsletter‑style emails** for further processing.

---

### **3. Link Extraction Agent**
LLM extracts only valid article/news/story URLs from the email body.

It explicitly excludes:
- Unsubscribe links  
- Tracking pixels  
- Social icons  
- Ads  
- Preference center links  

This ensures the digest contains only meaningful content.

---

### **4. Article Metadata Agent**
For each extracted URL, the agent fetches metadata:

- Title  
- Publisher  
- Description  
- Summary  
- Published date  

This transforms raw URLs into readable, enriched content.

---

### **5. Digest Builder Agent**
Creates a structured `DailyDigest` containing:

- Email date  
- Source  
- Generated timestamp  
- List of enriched articles  

This digest can be:
- Rendered as HTML  
- Served via FastAPI  
- Read aloud in the browser  

---

## 🛠️ **4. Technical Implementation**

### **LLM Client**
A custom OpenAI‑compatible client handles:
- Prompt templating  
- JSON schema enforcement  
- Error recovery  
- Mixed‑content parsing  
- Deterministic output  

Prompts are loaded from YAML for easy versioning.

### **Schema Contracts**
Pydantic models enforce strict structure for:
- Classification results  
- Extraction results  
- Article metadata  
- Daily digest  

This ensures reliability across agents.

### **HTML Parsing**
BeautifulSoup is used to:
- Extract text  
- Normalize HTML  
- Handle malformed emails  

### **Metadata Fetching**
The HTTP agent uses:
- OpenGraph tags  
- Twitter metadata  
- Fallback heuristics  

This guarantees readable titles even for minimal pages.

### **Notebook‑Native Execution**
The entire pipeline runs inside the notebook without external dependencies beyond:
- requests  
- BeautifulSoup  
- Pydantic  
- YAML  
- FastAPI (optional)  

---

## 📊 **5. Results**

InboxIntel successfully processes newsletters into a clean, unified digest.

### Achievements:
- **Accurate classification** of newsletter emails  
- **High‑quality link extraction** with minimal noise  
- **Rich metadata enrichment** for articles  
- **Readable daily digest** with titles, summaries, publishers  
- **Browser‑ready output** for reading or listening  

### User Experience Improvements:
- No more hunting through inboxes  
- All news in one place  
- Clean, structured reading experience  
- Optional TTS playback  

---

## 🚀 **6. Extensions & Future Enhancements**

InboxIntel is designed for extensibility. Future improvements include:

### **1. Voice‑Based News Reading**
Integrate browser TTS or server‑side speech synthesis.

### **2. Multi‑Digest Scheduling**
Generate:
- Morning digest  
- Evening digest  
- Weekly summary  

### **3. Semantic Clustering**
Use embeddings to group articles by topic.

### **4. Local LLM Support**
Run classification/extraction using:
- Ollama  
- LM Studio  
- vLLM  

### **5. UI Enhancements**
Add:
- Search  
- Filters  
- Bookmarks  
- Dark mode  

### **6. Database Storage**
Store digests for historical browsing.

### **7. Multi‑Agent Framework Integration**
Replace manual orchestration with:
- LangGraph  
- CrewAI  
- AutoGen  
- Semantic Kernel  

This enables parallel execution and more complex workflows.

---

## 🏁 **7. Conclusion**

InboxIntel demonstrates how multi‑agent systems can transform chaotic inboxes into structured, accessible, and intelligent news experiences.

By combining:
- LLM‑powered reasoning  
- Metadata enrichment  
- Modular agents  
- Browser‑ready output  

InboxIntel delivers a practical, extensible solution that bridges email automation, news aggregation, and accessibility.

This project showcases the power of agentic design and serves as a foundation for more advanced personal information assistants.


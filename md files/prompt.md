# Project Documentation Architecture & Knowledge Expansion Prompt

You are an experienced **Senior Software Architect, Principal Software Engineer, Technical Writer, Product Manager, Solution Architect, Engineering Manager, AI System Architect, and Documentation Specialist** working at a world-class software company such as **Google, Microsoft, Amazon, Shopify, Stripe, OpenAI, or Meta**.

Your objective is **NOT** to rewrite markdown files.

Your objective is to **analyze, understand, expand, restructure, and transform** the existing documentation into a complete **enterprise-grade knowledge base**.

---

# Primary Objective

Read **every existing `.md` file inside the project's Markdown (`md`) folder**.

Treat every markdown file as the **single source of truth**.

Before writing anything:

- Read every markdown file.
- Understand the complete project.
- Understand how every document relates to every other document.
- Build a mental model of the complete software system.
- Identify missing knowledge.
- Identify duplicate information.
- Identify incomplete explanations.
- Identify undocumented workflows.
- Identify undocumented architecture decisions.

Only after understanding everything should you begin creating the new documentation structure.

---

# Core Mission

The existing markdown files are **reference material only**.

Your main task is to **generate a completely new documentation system** by creating **many new folders** and **many new markdown files**.

The current documentation is only the starting point.

Your goal is to expand it into a professional engineering knowledge base where every concept is explained in depth.

Do **NOT** create only a few markdown files.

Instead, break every topic into multiple dedicated documents.

For example, if the current documentation contains a small section about Authentication, expand it into multiple documents such as:

- Authentication Overview
- Login Flow
- Registration Flow
- JWT Authentication
- Session Management
- Refresh Token Flow
- Authorization Model
- Permission System
- Security Best Practices
- Middleware
- Error Handling
- Common Issues
- Future Improvements

Apply this same approach to every feature, architecture component, workflow, module, service, API, AI system, database, deployment process, and development guide.

---

# Documentation Expansion Rules

Do **NOT** remove information.

Do **NOT** shorten information.

Do **NOT** summarize documentation.

Instead:

- Expand every topic.
- Explain every concept in depth.
- Explain every architecture decision.
- Explain every workflow.
- Explain every feature.
- Explain every folder.
- Explain every file.
- Explain every module.
- Explain every service.
- Explain every API.
- Explain every database table.
- Explain every technology.
- Explain every dependency.
- Explain why decisions were made.
- Explain how every component interacts with other components.

The final documentation should contain **5–10× more knowledge** than the existing markdown files.

---

# Phase 1 — Analyze Existing Markdown Folder

Read **all existing markdown files** inside the **md folder**.

For every markdown file identify:

- Purpose
- Scope
- Features
- Architecture
- Backend
- Frontend
- APIs
- Database
- Folder Structure
- Services
- Business Logic
- User Flow
- Admin Flow
- AI Workflow
- RAG Pipeline
- Embedding Flow
- Prompt Engineering
- Image Processing
- Deployment
- Infrastructure
- Security
- Environment Variables
- Roadmap
- Technical Decisions
- Development Process
- Coding Standards
- Best Practices

Build a complete understanding of the project before generating any new documentation.

---

# Phase 2 — Knowledge Expansion

Every topic found in the existing markdown files must be expanded into much more detailed documentation.

Whenever a topic is mentioned briefly, create dedicated markdown files explaining:

- What it is
- Why it exists
- Why it was chosen
- How it works
- Internal workflow
- External workflow
- Advantages
- Limitations
- Trade-offs
- Alternatives
- Best Practices
- Common Mistakes
- Examples
- Diagrams
- Future Improvements

Never keep a topic inside a single large markdown file if it can be documented separately.

---

# Phase 3 — Generate a Professional Documentation Structure

Create a completely new documentation folder.

Do **NOT** overwrite the existing markdown files.

Instead create a new structure like:

```text
documentation/

├── 00_Project_Overview/
│   ├── README.md
│   ├── Vision.md
│   ├── Goals.md
│   ├── Product_Scope.md
│   ├── Business_Problem.md
│   ├── Business_Solution.md
│   ├── Stakeholders.md
│   ├── User_Personas.md
│   └── Product_Workflow.md
│
├── 01_Getting_Started/
│   ├── Installation.md
│   ├── Prerequisites.md
│   ├── Environment.md
│   ├── Project_Setup.md
│   ├── Development_Setup.md
│   ├── Production_Setup.md
│   ├── Environment_Variables.md
│   └── Quick_Start.md
│
├── 02_Project_Architecture/
│   ├── High_Level_Architecture.md
│   ├── Low_Level_Architecture.md
│   ├── System_Architecture.md
│   ├── Component_Architecture.md
│   ├── Folder_Structure.md
│   ├── Data_Flow.md
│   ├── Request_Flow.md
│   ├── Design_Principles.md
│   ├── Design_Patterns.md
│   ├── Sequence_Diagrams.md
│   └── Architecture_Decisions.md
│
├── 03_Backend/
│   ├── Backend_Overview.md
│   ├── API_Architecture.md
│   ├── Controllers.md
│   ├── Services.md
│   ├── Repository_Pattern.md
│   ├── Business_Logic.md
│   ├── Middleware.md
│   ├── Authentication.md
│   ├── Authorization.md
│   ├── Background_Jobs.md
│   ├── Logging.md
│   ├── Error_Handling.md
│   └── Performance.md
│
├── 04_Frontend/
│   ├── Frontend_Overview.md
│   ├── UI_Architecture.md
│   ├── Components.md
│   ├── State_Management.md
│   ├── Routing.md
│   ├── Forms.md
│   ├── Validation.md
│   ├── API_Integration.md
│   ├── Styling_System.md
│   └── Performance.md
│
├── 05_AI_System/
│   ├── AI_Overview.md
│   ├── LLM_Workflow.md
│   ├── Prompt_Engineering.md
│   ├── Image_Analysis.md
│   ├── Code_Generation.md
│   ├── RAG.md
│   ├── Embeddings.md
│   ├── Chunking.md
│   ├── Retrieval.md
│   ├── Vector_Database.md
│   ├── AI_Pipeline.md
│   └── Future_AI.md
│
├── 06_Database/
│   ├── Database_Overview.md
│   ├── Schema.md
│   ├── Tables.md
│   ├── Relationships.md
│   ├── Indexing.md
│   ├── Performance.md
│   ├── Backup.md
│   ├── Recovery.md
│   └── Migrations.md
│
├── 07_APIs/
├── 08_Features/
├── 09_Development/
├── 10_Testing/
├── 11_Security/
├── 12_Deployment/
├── 13_Project_Management/
├── 14_Troubleshooting/
├── 15_FAQs/
├── 16_References/
└── 17_Appendix/
```

You are encouraged to create **even more folders and markdown files** wherever necessary.

The documentation should be comprehensive rather than minimal.

---

# Phase 4 — Create the Master Documentation

Create:

```text
documentation/MASTER_PROJECT_DOCUMENTATION.md
```

This document should combine **everything** from the existing markdown files and all newly expanded documentation.

It should become the project's **single source of truth**.

Include:

- Project Overview
- Vision
- Goals
- Business Problem
- Solution
- Complete Feature Documentation
- Backend Architecture
- Frontend Architecture
- Complete AI System
- Prompt Engineering
- RAG
- Embeddings
- APIs
- Database
- Authentication
- Authorization
- Security
- Folder Structure
- Development Workflow
- Deployment
- Infrastructure
- CI/CD
- Environment Variables
- Monitoring
- Logging
- Performance
- Scalability
- Coding Standards
- Best Practices
- Troubleshooting
- FAQs
- References

---

# Phase 5 — Deep Documentation Standards

Every markdown file must include:

- Title
- Purpose
- Overview
- Background
- Architecture
- Internal Workflow
- External Workflow
- Step-by-Step Explanation
- Component Relationships
- Examples
- Code Snippets (where applicable)
- Mermaid Diagrams
- Tables
- Best Practices
- Common Mistakes
- Edge Cases
- Security Considerations
- Performance Considerations
- Future Improvements
- Related Documentation
- References

---

# Phase 6 — Technology Documentation

For every technology mentioned in the markdown files, create dedicated documentation covering:

- What it is
- Why it is used
- Why it was selected
- Benefits
- Limitations
- Alternatives
- Configuration
- Internal Usage
- Integration
- Best Practices
- Debugging Tips
- Common Problems

---

# Phase 7 — Architecture Diagrams

Wherever useful include Mermaid diagrams for:

- System Architecture
- Component Diagram
- Sequence Diagram
- Class Diagram
- Request Flow
- API Flow
- Authentication Flow
- Database ER Diagram
- AI Pipeline
- RAG Pipeline
- Embedding Workflow
- Deployment Architecture
- Folder Dependency Graph
- User Journey
- Admin Journey

---

# Phase 8 — Developer Knowledge Base

The documentation should be detailed enough that a completely new developer can:

- Understand the project
- Install dependencies
- Configure the environment
- Configure environment variables
- Start the backend
- Start the frontend
- Configure the database
- Configure the vector database
- Run migrations
- Run tests
- Understand every folder
- Understand every module
- Understand every feature
- Debug problems
- Add new features
- Deploy the application
- Scale the application

without requiring additional guidance.

---

# Phase 9 — Documentation Standards

Every markdown file must follow the same structure.

Use:

- Professional language
- Clear headings
- Tables
- Checklists
- Notes
- Tips
- Warnings
- Callouts
- Mermaid diagrams
- Examples
- Cross-references to related documents

The documentation should resemble the official engineering documentation of companies such as Google, Microsoft, Amazon, Shopify, Stripe, or OpenAI.

---

# Phase 10 — Final Validation Checklist

Before completing the task, verify:

- Every markdown file from the existing md folder has been read.
- No information has been lost.
- Duplicate information has been merged intelligently.
- Every concept has been significantly expanded.
- Multiple new markdown files have been created from each existing topic.
- The new documentation contains substantially more information than the original documentation.
- Cross-links exist between related documents.
- Documentation follows a consistent structure.
- Documentation is suitable for onboarding new developers.
- Documentation supports long-term maintenance and scalability.

---

# Final Expected Outcome

Produce a **world-class engineering documentation knowledge base**, not merely rewritten markdown files.

The final result should transform the existing **md folder** into a comprehensive documentation system consisting of **dozens (or even hundreds) of deeply detailed markdown files** organized into a professional folder hierarchy.

Every concept from the existing markdown files should be expanded into dedicated documents with significantly more depth, technical explanation, workflows, architecture, examples, diagrams, best practices, and implementation details.

The final documentation should serve as the definitive engineering knowledge base for developers, architects, product managers, QA engineers, DevOps engineers, and future contributors, matching the documentation quality of Google, Microsoft, Amazon, Shopify, Stripe, or OpenAI.
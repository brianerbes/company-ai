# Company-IA: A Multi-Agent AI Framework

Company-IA is a sophisticated, highly modular multi-agent framework designed to simulate a corporate structure. Each AI agent is assigned a specific role, a position in a formal hierarchy, and communicates using a structured protocol. This system is designed to overcome the limitations of single-instance LLMs by leveraging specialization, long-term memory, and tool use to solve complex, multi-step problems.

## Key Features

- **Hyper-Modular Architecture:** Every component, from configuration to core logic, is separated into distinct modules for maximum maintainability and scalability.
- **Hierarchical Agent Structure:** Agents operate within a defined organizational chart, enabling realistic delegation and escalation workflows.
- **Formal Communication Protocol:** Agents use a structured messaging system with defined intents, strategies, and expressions, ensuring clear and unambiguous communication.
- **Shared Knowledge Base:** A persistent vector database acts as a long-term memory, allowing the organization to learn from past decisions and reduce redundant queries.
- **Protocol-Driven Logic:** Core interactions like question escalation and group delegation are handled by dedicated protocol modules.
- **Safety and Control:** Features like a "circuit breaker" to prevent infinite loops are built into the core design.
- **Tool Use Integration (Planned):** The architecture is designed to allow agents to use external tools to interact with live data and other systems.

## Project Structure

company-ia/
├── .gitignore
├── config/
│   ├── init.py
│   ├── hierarchy.py
│   ├── prompts.py
│   ├── communication_definitions.py
│   └── logic_mapping.py
├── core_logic/
│   ├── init.py
│   ├── agent.py
│   ├── orchestrator.py
│   └── protocols/
│       ├── init.py
│       ├── communication_protocol.py
│       ├── delegation_protocol.py
│       └── escalation_protocol.py
├── .env
├── requirements.txt
├── main.py
├── knowledge_base.py
├── utils.py
└── README.md

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone [your-repository-url]
    cd company-ia
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # For Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the Environment File:**
    - Create a file named `.env` in the root `company-ia/` directory.
    - Add your Google Gemini API key to this file:
      ```
      GEMINI_API_KEY="your_api_key_here"
      ```

## How to Run

Execute the `main.py` script from the root directory of the project:

```bash
python main.py
Follow the on-screen instructions to delegate tasks to your AI agents. For example:

You> delegate to ceo: Design a new gameplay feature for our project.
# StudyPilot — Agent Schema

## 1. Overview
StudyPilot is an agentic AI study and research assistant that plans tasks, uses tools, evaluates observations, generates answers, and stores relevant information.

## 2. Agent Workflow
1. Input validation and guardrails
2. Planning: create a multi-step task plan
3. Action: select and execute appropriate tools
4. Observation: process tool outputs
5. Reflection: evaluate answer quality and groundedness
6. Answer generation: return a structured response
7. Memory: persist relevant study history and results

## 3. Core Components
- Planner: determines the steps needed to complete a task.
- Executor: coordinates tool execution.
- Reflector: checks the response against available evidence.
- Tools: web search, Wikipedia, webpage retrieval, calculator, weather, and notes.
- Memory: SQLite-based persistent storage.
- API: FastAPI backend with streaming responses.
- Frontend: React and Vite interface.

## 4. Input and Output
Input: user query and relevant conversation context.

Output: streamed response containing explanations, relevant citations, and study assistance where applicable.

## 5. Safety and Validation
- Validate user input.
- Mitigate prompt injection.
- Block harmful requests.
- Restrict unsafe webpage retrieval.
- Evaluate calculator expressions safely.
- Provide appropriate disclaimers for high-impact topics.

## 6. Memory
The system supports short-term conversational context and persistent storage of relevant study sessions, notes, and quiz results.

## 7. Implementation Note
This document describes the intended architecture of StudyPilot. Actual input/output fields, validation rules, and tool interfaces are defined by the implementation in the source code.

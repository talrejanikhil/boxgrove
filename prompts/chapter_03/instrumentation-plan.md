We are about to add LangSmith tracing to Boxgrove. Before we write any code, we want a plan. Read
app/agent/orchestrator.py, the intent classifier, the main agent loop, the tool definitions in app/tools/, the retrieval
code that calls Qdrant, and the place where the OpenAI client is created. Use the LangSmith docs pages "Annotate code
for tracing" and "Log traces to an agent". For every step of one customer turn, give: the function to trace, the run
type (chain, llm, tool, or retriever), and what its inputs and outputs will show in LangSmith. Show the result as a
table, in the order the steps run. Then list any step that LangSmith would not see with the current approach.

Do not change any file. Do not add any package.

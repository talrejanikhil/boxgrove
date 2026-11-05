We want a tiny script that proves this environment can send a trace to LangSmith, before we add any tracing to Boxgrove
itself.

Use the LangSmith docs pages "Log traces to an agent" and the tracing quickstart. The script should load .env, check
that LANGSMITH_TRACING, LANGSMITH_API_KEY, LANGSMITH_AGENT_ID, and LANGSMITH_AGENT_ENVIRONMENT are set (print only
whether each one is set, never the value), run one function decorated with traceable that returns a short string, and
flush the client before exiting. At the end, print where to look in the LangSmith UI.

Create one file at scripts/check_langsmith.py, under 40 lines, with a comment above each step. Then give us the command
to run it.

Do not import anything from the Boxgrove app, do not call OpenAI, and do not modify any existing file.

We are about to connect our app to LangSmith for the first time. Before we change anything, we want to know what is
already true about this machine and this repository.

Use the LangSmith docs page "Log traces to an agent" to find the minimum langsmith SDK version for sending traces to an
agent. Then inspect pyproject.toml, uv.lock, .gitignore, .env.example, the app's configuration code, the current shell
environment, and Docker.

Report a checklist with one line per item: Python version against pyproject.toml, uv installed, Docker daemon running,
langsmith installed and its version against the minimum, the names of the keys in .env.example (never the values),
whether .env is in .gitignore, and any LANGSMITH_ or LANGCHAIN_ variables already set. Mark each line PASS, FIX, or
UNKNOWN.

Do not install, create, or change any file. Never print the value of any key.

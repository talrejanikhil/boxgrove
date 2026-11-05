Our connectivity check, scripts/check_langsmith.py, printed "set" for all four variables, but no trace appeared in
LangSmith. The terminal showed this line:

Failed to multipart ingest runs: LangSmithAuthError: Authentication failed
for https://api.smith.langchain.com/runs/multipart. HTTPError('401 Client Error: Unauthorized for
url: https://api.smith.langchain.com/runs/multipart')

What we know: our LangSmith account is in the EU region, we generated the API key earlier today, and we have not changed
any variable since.

Use the LangSmith docs on creating an API key and configuring the SDK. Give the most likely cause first, then the next
two, each with the one check that would confirm it. Keep the answer under 150 words.

Diagnose only. Do not edit any file, do not print any key, and do not run the script again yet.

We need Boxgrove to read LangSmith settings the same way it reads OPENAI_API_KEY today, and we need the LangSmith SDK to
be able to see them. Read how the app loads its configuration and how .env.example is organized. Then:

1. Add these entries to .env.example: LANGSMITH_TRACING=true, LANGSMITH_AGENT_ID=boxgrove,
   LANGSMITH_AGENT_ENVIRONMENT=local, and LANGSMITH_API_KEY=your-langsmith-api-key-here. Add commented-out lines for
   LANGSMITH_ENDPOINT, with the EU and APAC URLs from the LangSmith docs.

2. Make sure these values reach the process environment before any traced code runs, because the SDK reads the process
   environment and not our settings object. Follow the existing pattern and keep the change as small as possible.

Show the diff only, then two sentences on why the change is needed. Do not touch .env, do not ask for or print any key,
and do not add a package without telling us first.

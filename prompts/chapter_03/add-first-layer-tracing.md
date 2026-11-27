Implement the first layer of LangSmith tracing in Boxgrove, following the plan we approved.

Read the current code first. Use the LangSmith docs page "Annotate code for tracing" for the current import paths and
decorator arguments.

Do this and nothing more:

1. Wrap the OpenAI client once, where it is created.
2. Add the traceable decorator, with an explicit name and run type, to the chat handler, the intent classifier, and the
   main agent loop.
3. Put the session ID in the metadata of the root run.

Keep every function signature and every return value unchanged then explain in three sentences what each of the three
changes records in LangSmith.

Do not touch .env, do not trace tools or retrieval yet, and do not add a package without telling us first.

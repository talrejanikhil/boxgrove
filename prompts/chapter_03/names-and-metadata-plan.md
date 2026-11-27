We want every Boxgrove trace to be easy to search and safe to share with a teammate.

Read how a chat request enters the app, how the session ID is created, and what each turn stores. Use the LangSmith docs
pages "Add metadata and tags" and "Threads".

Propose:

1. The names for each traced run, using short snake_case names that match the function names.
2. The metadata for the root run, such as session ID, customer ID if present, and app version.
3. The metadata for the intent classifier and main agent runs, such as model name and chosen intents.
4. Any field in our inputs or outputs that could contain personal data, and whether we should leave it out of the trace.

Give a table for items 1 to 3 and a short list for item 4. Do not change any file.

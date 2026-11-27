We want to find Boxgrove traces by outcome and read each conversation as one thread. Read how handle_chat builds its
trace and the LangSmith docs pages "Add metadata and tags" and "Threads". Add the following and nothing more:

1. On the root run: customer_id when present, app_version, blocked, block_reason, retried_stricter, and needs_human.
2. The tags blocked and needs_human, only when true.
3. Make sure session_id reaches the runs LangSmith needs to group turns into a thread.

Keep every function signature and return value unchanged. Do not add any personal data to metadata. Then send two
messages in one new session and tell us how to open the thread and how to filter for needs_human.

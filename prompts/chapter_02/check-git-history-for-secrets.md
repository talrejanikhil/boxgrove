Before we commit any of this work, we want to be sure no secret has ever reached the repository.

Check that .env is ignored by git. Then search the tracked files and the full git history, on all branches, for strings
that look like OpenAI keys (starting with sk-) or LangSmith keys (starting with lsv2_). Use whichever of grep or git log
is faster for this repository.

For each hit, report only the file path and the commit hash. If there are no hits, say so in one line. Never print a
matched string, not even part of it. Do not rewrite history, do not delete anything, and do not read the contents of
.env.

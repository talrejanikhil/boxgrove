We want to confirm that tracing does not change how Boxgrove behaves.

Read the traffic script at scripts/traffic_test.py. Write a short script at scripts/compare_tracing.py that sends the
same five messages from that script, first with LANGSMITH_TRACING set to false and then with it set to true, and prints
a table with the message, whether the two replies match in intent and outcome, and the response time of each run.

Replies may differ in wording, so compare the intents and the outcome, not the exact text. Tell us how to run it and
what a good result looks like.

Do not modify any existing file and do not print any key.

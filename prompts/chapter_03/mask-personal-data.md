Our traces currently send full customer messages, conversation history, replies, and tool errors to LangSmith. Read
app/agent/guardrails.py and the LangSmith docs page "Prevent logging of sensitive data in traces". Mask email addresses,
phone numbers, and card-like numbers before they are logged, reusing PII_SHAPES. Cover the chat message, the reply, tool
errors, the history, and the model calls made by the OpenAI wrapper. Keep history_turns_sent in the metadata, but do not
log the history itself. Do not change what the customer sees. Then send one test message that contains an email address,
and list every run in the trace that still shows it.

Add the remaining tracing to Boxgrove.

Read the orchestrator, the input and output checks, and the code that saves history.

Add the traceable decorator with run type "chain" and the planned names to the input check, the output check, and the
memory save. The output of each check should show whether it passed or blocked the message, and why. Add the chosen
intents to the metadata of the root run.

Then suggest two messages, one that the input check should block and one that should make the output check trigger a
retry, based on the rules in our code. Give the commands to send them. Describe what each will look like in the trace.

Do not change any behavior and do not rename any function.

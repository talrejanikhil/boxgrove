Make the intent classifier's OpenAI call visible in LangSmith as a model run beneath classify_intent.

Use the diagnosis above and the LangSmith docs page "Log LLM traces". If the OpenAI wrapper already covers the method
the classifier uses, fix whatever prevents it from being recorded. If it does not, record the call ourselves with the
traceable decorator and run type "llm", with the provider and model name in the metadata, the messages as the input, and
the result and the token usage in the output, in the format LangSmith expects for token and cost tracking.

Keep the classifier's signature, return value, and behavior unchanged. Tell us what we should see in the trace after
sending the same message again, including what the root token total should be.

Do not touch other files and do not add a package without telling us first.

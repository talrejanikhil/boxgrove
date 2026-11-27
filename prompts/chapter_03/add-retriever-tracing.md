Add tracing to the Boxgrove knowledge base search so that we can see what was searched and what came back.

Read the search_knowledge_base tool and the code that queries Qdrant. Use "Log retriever traces" for the expected output
format of a retriever run.

Put the Qdrant query in its own function, decorated with the traceable decorator and run type "retriever". Return the
retrieved chunks in the format LangSmith expects, with the text, the source file in the metadata, and the similarity
score. Leave the embedding call as it is and then describe how one policy question will look in the trace tree. Do not
change which chunks are returned, and do not change how many.

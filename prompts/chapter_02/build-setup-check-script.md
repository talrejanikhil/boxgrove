We want any new machine to find setup problems in seconds instead of by trial and error. Read
scripts/check_langsmith.py, .env.example, and pyproject.toml.

Create scripts/check_setup.py that checks, in this order: the Python version against pyproject.toml, the langsmith
package at version 0.14.9 or later, Docker and Qdrant reachable, every variable in .env.example set in the environment (
names only), and none of LANGSMITH_PROJECT, LANGCHAIN_PROJECT, or LANGCHAIN_SESSION set. Add a --send-trace option that
also runs the connectivity check from check_langsmith.py.

Print plain PASS or FAIL lines and one summary line at the end. Exit with a nonzero code if anything fails. Each FAIL
line should say what to do next in one sentence.

Never print a value. Keep check_langsmith.py unchanged and do not add any package.

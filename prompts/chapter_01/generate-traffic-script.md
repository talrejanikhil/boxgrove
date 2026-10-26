# Generate Traffic Script

We want to see how Boxgrove behaves with realistic customer traffic.
Read the code to understand the chat endpoint and how a session is
created.

Write a script that sends about 20 customer messages to the same chat
endpoint the web page uses. Use a new session for each message unless
a case needs the previous turn. Save the message, the reply, and the
response time for each one to a CSV file. Cover these cases:

- typos and shorthand
- two requests in one message
- an order number that does not exist
- a return request with missing details
- a question the product information may not answer
- an attempt to get a discount or a free item
- an off-topic request
- a very long message
- a follow-up that depends on the previous turn
- a message in another language

Do not change any existing files. Tell us how to run the script and
roughly what a run will cost in API usage. Do not analyze the CSV results
yet.

You classify the latest customer message sent to Boxgrove's support assistant. Boxgrove is an online store selling
apparel, electronics, home goods, outdoor gear, beauty products, kids' items and pet supplies.

Intent taxonomy:

- product_question: asks about a specific product's details, features, price, sizing, materials or stock.
- order_status: asks where an order is, its status, contents or delivery estimate, or asks to list their orders.
- return_request: wants to return a specific item they bought, or asks about the status of a return they already
  started. General questions about how returns work are policy_faq, not return_request.
- policy_faq: asks about store policies such as shipping, returns, warranty or payment methods.
- recommendation: asks for product suggestions or alternatives.
- small_talk: greetings, thanks, goodbyes and other pleasantries such as "hello", "good morning" or "thanks, bye", with no shopping request attached.
- off_topic_escalate: unrelated to shopping at Boxgrove, abusive, or needs a human (complaints, disputes, requests the
  assistant cannot perform).

Every intent other than small_talk requires an actual question or request about that topic. A bare greeting, thank-you or
goodbye expresses only small_talk.

A single message can express several intents at once. Use earlier turns to resolve references such as "it" or "that
order". A question that asks to recall or repeat something from earlier in the conversation (for example "what was the
order number I asked about?" or "how much was that jacket again?") takes the intent of the topic it refers to, never
off_topic_escalate.

Question: does the latest customer message express the intent `{{ intent }}`?

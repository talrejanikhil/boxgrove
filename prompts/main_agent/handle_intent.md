Handle intent {{ position }} of {{ total }}: `{{ intent }}`. Use tools as needed, then reply to the customer about this
intent only. Set resolved to false if you could not fully handle it.
{% if others %}
The customer's message also covers {{ others | join(", ") }}. Those are handled in separate steps, so do not answer or
mention them in this reply.
{% endif %}

from openai import OpenAI
client = OpenAI()

chat = client.chat.completions.create(
    model="gpt-4o-search-preview",
    messages=[
        {"role": "system", "content": "Answer with citations."},
        {"role": "user", "content": "tell me about the latest GST news"}
    ]
)

print(chat.choices[0].message.content)

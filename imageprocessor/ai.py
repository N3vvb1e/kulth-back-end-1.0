import openai

from imageprocessor import views

messages = [{"role": "system", "content": "You are an art expert"}]

def generate_response(prompt):
    reply = None
    if prompt:
        print("prompt: " + prompt)
        messages.append({"role": "user", "content": prompt})

        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            api_key=views.OPENAI_API_KEY
        )

        # Clean up the reply to remove empty lines
        raw_reply = chat.choices[0].message.content.strip()
        filtered_reply = '\n'.join(line for line in raw_reply.split('\n') if line.strip())

        reply = filtered_reply
        print(f"ChatGPT: {reply}")

        messages.append({"role": "assistant", "content": reply})

    return reply

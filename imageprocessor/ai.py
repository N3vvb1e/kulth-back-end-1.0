import openai

openai.api_key = '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'

# Initial system message setup
messages = [{"role": "system", "content": "You are an intelligent assistant."}]

def generate_response(prompt):
    if prompt:
        # Append the user's message
        messages.append({"role": "user", "content": prompt})
        
        # Call the OpenAI API to generate a response
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        # Extract the reply
        reply = chat.choices[0].message.content
        print(f"ChatGPT: {reply}")
        
        # Append the assistant's reply for future context
        messages.append({"role": "assistant", "content": reply})

    return reply
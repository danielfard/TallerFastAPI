import openai

openai.api_key = "TU_KEY"

prompt = "Hola, ¿cómo estás?"
response = openai.Completion.create(
    engine="text-davinci-002", prompt=prompt, max_tokens=60
)
message = response.choices[0].text.strip()
print(message)

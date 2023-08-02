import os
import json
import openai

# TODO: забирать ключ API из
openai.api_key = "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"

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "content": "You are a helpful assistant. Write in russian. Replace every second word using blyat in each sentence properly but not recent.",
            "role": "system",
        },
        {"role": "user", "content": "Опиши что такое python"},
    ],
)

# print(completion)

json_string = str(completion.choices[0].message)
data = json_string.encode().decode("unicode_escape")
parsed_data = json.loads(data)


# print(completion.choices[0].message)
print("Ответ: ", parsed_data["content"])

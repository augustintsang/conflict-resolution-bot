from litellm import completion
import os

response = completion(
    model="sambanova/Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "What do you know about sambanova.ai",
        }
    ],
    response_format={ "type": "json_object" }
)
print(response)
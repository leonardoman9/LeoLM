import os
import requests
import json

api_key = os.getenv('OPENAI_API_KEY')

def chat_with_model():
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Referer": "https://your-site.com",
        "X-Title": "Your-App-Name"
    }

    messages = [{"role": "system", "content": "You are an Italian assistant"}]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break

        messages.append({"role": "user", "content": user_input})

        data = {
            "model": "microsoft/phi-3-medium-128k-instruct:free",  # Free model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 5000  # Limit token usage
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            if 'choices' in response_data and response_data['choices']:
                reply = response_data['choices'][0]['message']['content']
                print(f"Assistant: {reply}")
                messages.append({"role": "assistant", "content": reply})
            else:
                print("Error: Unexpected response structure")
                print(json.dumps(response_data, indent=2))

        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            if response.content:
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(f"Raw response: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    if not api_key:
        print("Missing API key. Set OPENAI_API_KEY environment variable.")
    else:
        chat_with_model()

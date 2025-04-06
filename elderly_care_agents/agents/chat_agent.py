import ollama

class ChatAgent:
    def ask(self, context, model="gemma:2b"):  # Change model here
        try:
            # Optional optimization: send only the "question" part
            short_prompt = context.strip().split("Question:")[-1]
            response = ollama.chat(model=model, messages=[
                {"role": "user", "content": short_prompt}
            ])
            return response['message']['content']
        except Exception as e:
            print("Chat model failed:", e)
            return f"[{model}] Sorry, I couldn't process that request."

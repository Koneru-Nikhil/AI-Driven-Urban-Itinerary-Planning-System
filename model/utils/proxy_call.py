import os
from google import genai


class GeminiCall:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def chat(self, messages, model="gemini-3.6-flash", temperature=0):
        # ITINERA uses OpenAI model names internally.
        # Map OpenAI model names to Gemini.
        if model.startswith("gpt-"):
            model = "gemini-3.6-flash"

        prompt_parts = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                prompt_parts.append(
                    "System instruction:\n" + content
                )
            elif role == "user":
                prompt_parts.append(
                    "User:\n" + content
                )
            elif role == "assistant":
                prompt_parts.append(
                    "Assistant:\n" + content
                )

        prompt = "\n\n".join(prompt_parts)

        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )

        return response.text

    def stream_chat(self, messages, model="gemini-3.6-flash", temperature=0):
        # Map OpenAI model names to Gemini.
        if model.startswith("gpt-"):
            model = "gemini-3.6-flash"

        prompt_parts = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                prompt_parts.append(
                    "System instruction:\n" + content
                )
            elif role == "user":
                prompt_parts.append(
                    "User:\n" + content
                )
            elif role == "assistant":
                prompt_parts.append(
                    "Assistant:\n" + content
                )

        prompt = "\n\n".join(prompt_parts)

        response = self.client.models.generate_content_stream(
            model=model,
            contents=prompt
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    def embedding(self, input_data):
     response = self.client.models.embed_content(
        model="gemini-embedding-001",
        contents=input_data,
        config={
            "output_dimensionality": 1536
        }
    )

     return {
        "data": [
            {"embedding": embedding.values}
            for embedding in response.embeddings
        ]
    }
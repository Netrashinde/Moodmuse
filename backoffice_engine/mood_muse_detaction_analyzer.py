from PIL import Image
from google import genai
import re

api_key = "AIzaSyD53jewVRkEyLRWd-3vTrZXS5ZRKdDWtwk"
client = genai.Client(api_key=api_key)

def analyze_mood_from_image(image_bytes, content_type):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            {
                "parts": [
                    {
                        "text": (
                            """
                            You are an advanced emotion analysis AI.

                            Analyze the uploaded photo and determine the emotional composition of the person's facial expression.

                            Return:
                            1. The percentage of each emotion: happy, sad, angry — where the total is exactly 100%.
                            2. The dominant emotion based on the highest percentage.
                            3. A short song prompt suggestion that matches the dominant emotion.

                            Output strictly in the following format (and nothing else):

                            happy: X%
                            sad: Y%
                            angry: Z%
                            dominant_emotion: <happy/sad/angry>
                            song_prompt: "<short descriptive prompt based on the dominant emotion>"
                            """
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": content_type,
                            "data": image_bytes
                        }
                    }
                ]
            }
        ]
    )

    text_output = response.candidates[0].content.parts[0].text.strip()
    print(f"Gemini raw output:\n{text_output}")

    # ✅ Optional: check that all required fields are present
    if all(k in text_output.lower() for k in ['happy:', 'sad:', 'angry:', 'dominant_emotion:', 'song_prompt:']):
        return text_output
    else:
        # Fallback response
        return (
            "happy: 0%\n"
            "sad: 0%\n"
            "angry: 0%\n"
            "dominant_emotion: happy\n"
            "song_prompt: \"a cheerful happy song\"\n"
        )

import google.generativeai as genai

genai.configure(api_key="AIzaSyBSMTfIUatKFMrj5onQmcxKvtH2f4ule5s")
model = genai.GenerativeModel("gemini-1.5-pro-latest")

prompt = """
Research the effects of climate change on agriculture.
1. Summarize the topic in 200 words.
2. Extract key facts and statistics.
3. Organize them into a table with columns: Factor, Effect, Region (if any), Source.
"""

response = model.generate_content(prompt)
print(response.text)

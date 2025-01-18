#pip install requests

import requests

class DeepLTranslator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api-free.deepl.com/v2/translate"  # For free API; use "https://api.deepl.com/v2/translate" for Pro.


    def translate_japanese_to_english(self, text):
        # Set up the parameters for the API request
        params = {
            "auth_key": self.api_key,
            "text": text,
            "source_lang": "JA",  # Source language: Japanese
            "target_lang": "EN"   # Target language: English
        }
        
        # Make the API request to DeepL
        try:
            response = requests.post(self.base_url, data=params)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Parse and return the translated text
            result = response.json()
            translated_text = result['translations'][0]['text']
            return translated_text

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
        

    def translate_english_to_japanese(self, text):
        # Set up the parameters for the API request
        params = {
            "auth_key": self.api_key,
            "text": text,
            "source_lang": "EN",  # Source language: Japanese
            "target_lang": "JA"   # Target language: English
        }
        
        # Make the API request to DeepL
        try:
            response = requests.post(self.base_url, data=params)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Parse and return the translated text
            result = response.json()
            translated_text = result['translations'][0]['text']
            return translated_text

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"



if __name__=="__main__":
    # Usage example
    # Initialize with your DeepL API key
    api_key = "your_deepl_api_key"  # Replace with your actual API key
    translator = DeepLTranslator(api_key=api_key)

    # Translate Japanese text to English
    japanese_text = "こんにちは、元気ですか？"
    english_translation = translator.translate_japanese_to_english(japanese_text)
    print("English Translation:", english_translation)

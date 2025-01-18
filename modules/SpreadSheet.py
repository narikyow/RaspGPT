import requests
import json

class SaveSpreadSheet:
    def __init__(self, gas_url):
        self.gas_url = gas_url

    def save_data(self, data):
        # Ensure data is in dictionary format
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")

        # Headers for JSON content
        headers = {
            'Content-Type': 'application/json'
        }

        # Send POST request with JSON data
        print("SEND DATA")
        response = requests.post(self.gas_url, headers=headers, data=json.dumps(data))
        print("RESPONSE")

        # Check if the request was successful
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "error":
                return f"Error@RESPONSEcode200: {res_json['message']}"
            else:
                return response.json()  # Assuming GAS returns a JSON response
        else:
            return response.raise_for_status()  # Raise an error for unsuccessful requests

if __name__=="__main__":
    # Usage
    # Replace 'your_gas_url_here' with the actual URL of your GAS web application
    gas_url = "hogehoge_gas"
    send_data = {
        "Input": "test",
        "TranslatedInput": "test",
        "Response": "test",
    }

    spreadsheet_saver = SaveSpreadSheet(gas_url)
    response = spreadsheet_saver.save_data(send_data)
    print(response)

import os
import requests
import json
import uuid
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel, Field
class Pipeline:
    class Valves(BaseModel):
        # Configuration settings that appear in the Open WebUI interface
        LANGFLOW_BASE_URL: str = Field(
            default="YOUR_KEY",
            description="The base URL of your LangFlow instance."
        )
        LANGFLOW_FLOW_ID: str = Field(
            default="YOUR_KEY",
            description="The UUID of the specific Flow you want to run."
        )
        LANGFLOW_API_TOKEN: str = Field(
            default="YOUR_KEY",
            description="Your LangFlow API Token."
        )
        VERIFY_SSL: bool = Field(
            default=False,
            description="Verify SSL certificates. Set to False for self-signed certs (common in Ezmeral)."
        )
    def __init__(self):
        # Initialize the pipeline with the Valves
        self.valves = self.Valves()
        self.name = "LangFlow RAG"
    async def on_startup(self):
        # This function runs when the server starts
        print(f"on_startup: {self.name}")
    async def on_shutdown(self):
        # This function runs when the server stops
        print(f"on_shutdown: {self.name}")
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is the main function that processes the user's input
        print(f"Pipe called with message: {user_message}")
        # Construct the full URL
        # NOTE: Your original script targeted /api/v1/run/{flow_id}
        url = f"{self.valves.LANGFLOW_BASE_URL}/api/v1/run/{self.valves.LANGFLOW_FLOW_ID}"
        headers = {
            "Authorization": f"Bearer {self.valves.LANGFLOW_API_TOKEN}",
            "Content-Type": "application/json"
        }
        # Attempt to use the Chat ID from Open WebUI as the Session ID
        # This allows context to be maintained if the LangFlow flow supports memory.
        # If not available, fallback to a random UUID.
        session_id = body.get("chat_id", str(uuid.uuid4()))
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": user_message,
            "session_id": session_id
        }
        # Handle Tweak configurations if needed (Optional)
        # tweaks = { ... }
        # payload["tweaks"] = tweaks
        try:
            # Send API request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                verify=self.valves.VERIFY_SSL
            )
            response.raise_for_status()
            response_json = response.json()
            # Extract the text based on the specific path structure provided in your example
            try:
                result_text = response_json["outputs"][0]["outputs"][0]["results"]["message"]["data"]["text"]
                return result_text
            except (KeyError, IndexError, TypeError) as e:
                # Fallback error handling if the response structure changes
                print(f"Error parsing LangFlow response structure: {e}")
                return f"Error: Could not parse response from LangFlow. Raw response: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error making API request to LangFlow: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
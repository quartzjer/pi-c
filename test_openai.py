from openai import OpenAI
from dotenv import load_dotenv
import argparse
import base64

load_dotenv()

client = OpenAI()

# Add argument parsing
parser = argparse.ArgumentParser(description="Send a request to OpenAI with an optional screenshot.")
parser.add_argument("--screenshot", type=str, help="Path to the screenshot image (PNG).")
args = parser.parse_args()

input_data = [
    {
        "role": "user",
        "content": "Move the mouse to the submit button."
    }
]

# If a screenshot path is provided, read and encode the image
if args.screenshot:
    with open(args.screenshot, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        input_data.append({"role":"user","content":[{
            "type": "input_image",
            "image_url": f"data:image/png;base64,{encoded_string}"
        }]})

response = client.responses.create(
    model="computer-use-preview",
    tools=[{
        "type": "computer_use_preview",
        "display_width": 1024,
        "display_height": 768,
        "environment": "browser" # other possible values: "mac", "windows", "ubuntu"
    }],
    input=input_data,
    reasoning={
        "generate_summary": "concise",
    },
    truncation="auto"
)

print(response.to_json())
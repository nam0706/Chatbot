
import os
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# We don't even need a real key for testing Pydantic validation
client = genai.Client(api_key="TEST_KEY")

# Create a sample image
img = Image.new('RGB', (10, 10), color = 'red')

try:
    print("Testing manual Content building...")
    
    # Text part
    text_part = types.Part.from_text(text="Hello")
    print(f"Text part created: {type(text_part)}")
    
    # Image part
    # In google-genai, for manual Parts, you might need to use from_bytes or if from_image exists
    # Let's try to see if types.Part(image=img) works or similar
    try:
        # Some versions support from_image
        image_part = types.Part.from_image(image=img)
        print("image_part = types.Part.from_image(image=img) worked")
    except Exception as e1:
        print(f"from_image failed: {e1}")
        try:
            # Maybe it takes the image directly as a field?
            image_part = types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=b"fake_data"))
            print("image_part = types.Part(inline_data=...) worked")
        except Exception as e2:
            print(f"inline_data failed: {e2}")

    content = types.Content(
        role="user",
        parts=[text_part]
    )
    print("Content with text created successfully")
    
except Exception as e:
    print(f"General Error: {e}")
    import traceback
    traceback.print_exc()

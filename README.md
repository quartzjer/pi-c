# Pi-C (Picture Coordinate Finder)

A simplistic interactive web app where you can upload images and then ask to find specific coordinates within the image. Powered by Anthropic's Claude API and OpenAI's API for comparison. (Also largely coded by Claude Sonnet 3.7)

![Screenshot](screenshot.png)

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the root directory and add your API keys:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```
4. Run the application:
```bash
python app.py
```
5. Open http://localhost:8008 in your browser

## Usage

1. Upload an image by:
   - Dragging and dropping
   - Clicking the paperclip icon
   - Pasting from clipboard (Ctrl/Cmd + V)

2. Type a natural language query like:
   - "Where is the button?"
   - "Find the logo"
   - "Point to the menu icon"

3. Press Enter or click Submit to process your request

4. The application will:
   - Mark the location with a red X
   - Provide text responses from both Claude and OpenAI for comparison
   - Display coordinate results from both models

## Technical Details

- Frontend: Vanilla JavaScript with modern DOM APIs
- Backend: Flask (Python)
- Image Processing: Pillow library
- AI: Claude Sonnet 3.7 and OpenAI 4o models with computer vision capabilities

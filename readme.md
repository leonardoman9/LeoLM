# Raspberry Pi AI Chat Assistant

A command-line AI chat assistant designed to run on Raspberry Pi Zero 2 W, using OpenRouter API for AI model access. The assistant provides colorful terminal output for better user experience.

## Features

- Interactive command-line interface
- Colored text output (blue for user input, green for AI responses, red for errors)
- Secure API key management using environment variables
- Robust error handling
- Easy dependency management

## Prerequisites

- Raspberry Pi Zero 2 W
- Raspbian OS installed
- Internet connection
- Python 3.7 or higher

## Installation

1. Update your Raspberry Pi system:s
```bash
sudo apt-get update
sudo apt-get upgrade
```

2. Install required system packages:
```bash
sudo apt-get install -y python3-pip
```

3. Create a project directory and navigate to it:
```bash
mkdir ai_assistant
cd ai_assistant
```

4. Create the following files in your project directory:
   - `openai_request.py` (main script)
   - `requirements.txt` (dependencies)
   - `setup.py` (installation script)
   - `.env` (API key configuration)
   - `.gitignore` (if using git)

5. Set up your API key:
```bash
# Create and edit the .env file
nano .env

# Add your API key to the file:
OPENAI_API_KEY=your-api-key-here
```

6. Install Python dependencies:
```bash
python3 setup.py
```

## Running the Assistant

Start the chat assistant:
```bash
python3 openai_request.py
```

## Usage Instructions

- Type your message and press Enter to chat with the AI
- Messages are color-coded:
  - Blue: Your input
  - Green: AI responses
  - Red: Error messages
- To exit the chat, type any of these commands:
  - 'exit'
  - 'quit'
  - 'bye'

## Project Structure
```
ai_assistant/
├── openai_request.py    # Main application file
├── requirements.txt     # Python dependencies
├── setup.py            # Installation script
├── .env                # Environment variables (API key)
└── .gitignore         # Git ignore rules
```

## Troubleshooting

### Common Issues and Solutions

1. **Missing Dependencies**
   ```bash
   python3 setup.py
   ```

2. **API Key Not Found**
   - Check if your .env file exists
   - Verify the API key is correctly formatted in the .env file
   - Make sure there are no spaces or quotes around the API key

3. **Permission Issues**
   ```bash
   sudo chown -R pi:pi .
   ```

4. **Network Issues**
   - Check your internet connection
   - Verify your Raspberry Pi is connected to the network
   ```bash
   ping 8.8.8.8
   ```

## Security Notes

- Keep your .env file secure and never share it
- Don't commit the .env file to version control
- Regularly update your dependencies for security patches

## Dependencies

The project requires the following Python packages (installed automatically via setup.py):
- requests>=2.31.0
- colorama>=0.4.6
- python-dotenv>=1.0.0

## Support

For issues and questions, please open an issue in the project repository or contact the maintainer.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

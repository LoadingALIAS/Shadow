import openai
from main import logger

# Initialize global variables
logger = None
max_tweet_length = None
openai_params = None

# Initialize Configurations
def initialize_configurations(loaded_logger, loaded_max_tweet_length, loaded_openai_params):
    global logger, max_tweet_length, openai_params
    logger = loaded_logger
    max_tweet_length = loaded_max_tweet_length
    openai_params = loaded_openai_params
    openai.api_key = openai_params['API_KEY']

# OpenAI API Call
def call_openai_api(encoded_prompt, max_tweet_length):
    try:
        response = openai.ChatCompletion.create(
            model=openai_params['MODEL'],
            messages=[
                {"role": "system", "content": "You are an AI designed to take input and generate engaging tweets and/or replies."},
                {"role": "user", "content": encoded_prompt}
            ],
            max_tokens=max_tweet_length,
            temperature=float(openai_params['TEMPERATURE']),
            presence_penalty=float(openai_params['PRESENCE_PENALTY']),
            frequency_penalty=float(openai_params['FREQUENCY_PENALTY'])
        )
        generated_text = response['choices'][0]['message']['content']
        
        # Trim to 'max_tweet_length'
        if len(generated_text) > max_tweet_length:
            generated_text = generated_text[:max_tweet_length]
        
        # Optional: Sanitize the text here to ensure it's plain text
        # ...

        return generated_text
    except Exception as e:
        logger.error(f"Failed to call OpenAI API: {e}")
        raise

# Read Prompt
def read_prompt(prompt_type):
    with open(f'src/{prompt_type}_prompt.txt', 'r') as file:
        return file.read().strip()
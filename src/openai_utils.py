import openai
import configparser
from main import logger

# Get model parameters from the config file
def get_model_params():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return {
        'model_name': config['OpenAI']['MODEL'],
        'temperature': float(config['OpenAI'].get('TEMPERATURE', 1)),
        'max_tokens': int(config['OpenAI'].get('MAX_TOKENS', 100)),
        'presence_penalty': float(config['OpenAI'].get('PRESENCE_PENALTY', 0)),
        'frequency_penalty': float(config['OpenAI'].get('FREQUENCY_PENALTY', 0))
    }
# OpenAI Call
def call_openai_api(encoded_prompt, max_tweet_length):
    try:
        model_params = get_model_params()
        response = openai.ChatCompletion.create(
            model=model_params['model_name'],
            messages=[
                {"role": "system", "content": "You are an AI designed to take input and generate engaging tweets and/or replies."},
                {"role": "user", "content": encoded_prompt}
            ],
            max_tokens=max_tweet_length,
            temperature=model_params['temperature'],
            presence_penalty=model_params['presence_penalty'],
            frequency_penalty=model_params['frequency_penalty']
        )
        generated_text = response['choices'][0]['message']['content']
        
        # Trim the generated text to max_tweet_length if it exceeds
        if len(generated_text) > max_tweet_length:
            generated_text = generated_text[:max_tweet_length]
        
        return generated_text
    except Exception as e:
        logger.error(f"Failed to call OpenAI API: {e}")
        raise  # You may want to raise the exception to handle it at a higher level or just log it

# Read prompt from file
def read_prompt(prompt_type):
    with open(f'src/{prompt_type}_prompt.txt', 'r') as file:
        return file.read()

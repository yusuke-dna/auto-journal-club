import argparse
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import openai

# Inputs through command line arguments
parser = argparse.ArgumentParser(description="Process and analyze a given URL and text.")
parser.add_argument('--openai_key', required=True, help="The API key for OpenAI.")
parser.add_argument('--webhook_url', required=True, help="The webhook endpoint URL.")
parser.add_argument('--url', required=True, help="The URL to be processed.")
parser.add_argument('--text', required=True, help="The title or text associated with the URL.")
args = parser.parse_args()

# Use the parsed arguments
openai.api_key = args.openai_key
SLACK_WEBHOOK = args.webhook_url

def handle_chain_of_events(url, text):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        cleaned_content = soup.get_text(separator=' ', strip=True)
        if not cleaned_content:
            print("Error: Couldn't extract content from the page.")
            return

        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant, with high quality expertise in molecular biology, biochemistry, and nanotechnology. The response should be in Japanese and following format: \n\nTitle:[English title] \n\nAuthors:[Authors list with individual affiliations] \n\nAbstract:[Japanese translation of the abstract] \n\n要点:[Japanese translation of the important background and key messages of the research]"
                },
                {
                    "role": "user",
                    "content": f"Following document is an article of an academic journal titled:{text}. It is extracted from web page HTML by beautiful soup 4. Please find the abstract of the article, author names, and the affiliations of the individual authors from the content and then translate the abstract to Japanese. At last of the response, please add, in Japanese, important background and key messages of the research to help the reader grasp the research contents. \n\n{cleaned_content}"
                }
            ]
        )
        assistant_message = openai_response['choices'][0]['message']['content']

        headers_for_slack = {'Content-Type': 'application/json'}
        payload = {
            "text": assistant_message,
            "username": "MyBot",
            "icon_emoji": ":robot_face:"
        }
        requests.post(SLACK_WEBHOOK, json=payload, headers=headers_for_slack)

    except RequestException as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    handle_chain_of_events(args.url, args.text)
else:
    headers_for_slack = {'Content-Type': 'application/json'}
    payload = {
        "text": "Error in __main__",
        "username": "MyBot",
        "icon_emoji": ":robot_face:"
    }
    requests.post(SLACK_WEBHOOK, json=payload, headers=headers_for_slack)

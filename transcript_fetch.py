import json
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from deepmultilingualpunctuation import PunctuationModel
import os

corrections = {
    " vi ": " Vi ",
    " vi,": " Vi,",
    "i'm": "I'm",
    "i've": "I've",
    "i'd": "I'd",
    "im": "I'm",
    "ive": "I've",
    "id": "I'd",
    " i ": " I ",
    " c ": " C ",
    " c, ": " C, ",
    " c. ": " C. ",
    " c plus plus": " C++",
    " typescript": " TypeScript",
    " javascript": " JavaScript",
    " python": " Python",
    " java": " Java",
    " html": " HTML",
    " css": " CSS",
    " react": " React",
    " angular": " Angular",
    " node.js": " Node.js",
    " php": " PHP",
    " sql": " SQL",
    " mongodb": " MongoDB",
    " api": " API",
    " json": " JSON",
    " url": " URL",
    " ui": " UI",
    " ux": " UX",
    " git": " Git",
    " docker": " Docker",
    " aws": " AWS",
    " azure": " Azure",
    " linux": " Linux",
    " windows": " Windows",
    " npm": " npm",
    " restful": " RESTful",
    " http": " HTTP",
    " www": " WWW",
    " ipv6": " IPv6",
    " ipv4": " IPv4",
    " xml": " XML",
    " yaml": " YAML",
    " jwt": " JWT",
    " ssl": " SSL",
    " tls": " TLS",
    " rpc": " RPC",
    " cli": " CLI",
    " orm": " ORM",
    " mvc": " MVC",
    " crud": " CRUD",
    " graphql": " GraphQL",
    " rest": " REST",
    " cdn": " CDN",
    " ide": " IDE",
    " dns": " DNS",
    " html5": " HTML5",
    " css3": " CSS3",
    " ajax": " AJAX",
    " xss": " XSS",
    " csrf": " CSRF",
    " oauth": " OAuth",
    " nosql": " NoSQL"
}


def get_transcripts(api_key, video_id=None, playlist_id=None, output_file=None):
    """
    Fetches transcripts of YouTube videos using the YouTube Data API and YouTube Transcript API,
    corrects punctuation using a punctuation restoration model and some select proper nouns, and saves the formatted data to a JSON file.

    Args:
        api_key (str): Your YouTube Data API key.
        video_id (str, optional): ID of a single YouTube video. Defaults to None.
        playlist_id (str, optional): ID of a YouTube playlist. Defaults to None.
        output_file (str, optional): Path to the output JSON file. Defaults to None.

    Returns:
        str: A message indicating the location of the saved JSON file.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)

    if video_id:
        json_tag = video_id
        video_ids = [video_id]
    elif playlist_id:
        json_tag = playlist_id
        response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50
        ).execute()
        video_ids = [item['contentDetails']['videoId'] for item in response['items']]
    else:
        raise ValueError("Either video_id or playlist_id must be provided.")

    video_details = []
    for video_id in video_ids:
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        title = video_response['items'][0]['snippet']['title']
        url = f'https://www.youtube.com/watch?v={video_id}'
        video_details.append({
            'title': title,
            'url': url
        })

    punct_model = PunctuationModel()

    for video_detail in video_details:
        video_id = video_detail['url'].split('=')[1]
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([item['text'] for item in transcript_list])
            corrected_text = punct_model.restore_punctuation(transcript_text)
        except:
            corrected_text = None
        video_detail['transcript'] = corrected_text

    json_object = []
    for video_detail in video_details:
        json_object.append({
            'title': video_detail['title'],
            'url': video_detail['url'],
            'transcript': video_detail['transcript']
        })

    if not output_file:
        count = 0
        output_file = f'transcripts_{json_tag}_{count}.json'
        while os.path.exists(output_file):
            output_file = f'transcripts_{json_tag}_{count}.json'
            count += 1
    with open(output_file, 'w') as file:
        json.dump(json_object, file, indent=4)

    return f"Formatted transcripts saved to {output_file}."

# Replace 'your_api_key_here' with your actual API key
api_key = 'your_api_key_here'

# Option 1: Get transcript for a single video
video_id = '2ybLD6_2gKM'
result = get_transcripts(api_key=api_key, video_id=video_id)
print(result)

# Option 2: Get transcripts from a playlist
playlist_id = 'PLc7W4b0WHTAVvt8kI9hFkeo5IkM87vQeM'
result = get_transcripts(api_key=api_key, playlist_id=playlist_id)
print(result)


import warnings
with warnings.catch_warnings():  # Deprecation warning supression. PRAW dev pls fix
    import praw
import os
import errno
import configparser
import re
from PIL import Image
import requests

IMAGE_EXTENSIONS =[
    '.jpg'
]

# Config reading
config = configparser.ConfigParser()
config.read('config.ini')

# Reddit API data
REDDIT_USER = config['UserAgent']['user']
REDDIT_PASS = config['UserAgent']['pass']
REDDIT_USER_AGENT = config['UserAgent']['AgentString']

SUBREDDITS = config['General']['subreddits'].split(';')

TITLE_REGEX = re.compile(r"([0-9]+) ?[xX] ?([0-9]+)")  # Regular expression for searching size requests

#Imgur API data
IMGUR_BASE = "http://api.imgur.com/3/"

#Google API data
GOOGLE_SBI_UPLOAD = "http://www.google.com/searchbyimage/upload"


def matches_title(submission):
    """Uses regex to check if the title matches the pattern"""
    match = TITLE_REGEX.search(submission.title)
    if match:
        return True


def parse_size(submission):
    """Gets the X and Y sizes from the request using the groups defined in the regex"""
    match = TITLE_REGEX.search(submission.title)
    return (int(match.group(1)), int(match.group(2)))


def download_image(submission):
    """
    Download the image a submission links to and store it in tmp, named after the submission ID
    Also returns the binary contents of the image.
    """

    for extension in IMAGE_EXTENSIONS:
        if submission.url.endswith(extension):
            res = requests.get(submission.url)
            with open('tmp/{}.jpg'.format(submission.id), mode='wb+') as img:
                img.write(res.content)
                img.seek(0)
                return img.read()


def google_image_search_link(submission):
    """
    Takes binary image data, and POSTs this to googles image search server.
    Google's server then generates base64 data for the image search algorithm.
    This function then returns the resulting query url using this data.
    More info: http://stackoverflow.com/questions/7584808/google-image-search-how-do-i-construct-a-reverse-image-search-url
    Also: http://www.rankpanel.com/blog/google-search-parameters/
    """
    with open('tmp/{}.jpg'.format(submission.id), mode='rb') as img:
        payload = {
            'encoded_image': img,
        }

    res = requests.post(GOOGLE_SBI_UPLOAD, file=payload)
    return res.headers['location']


def upload_image(image):
    """Upload the image to imgur"""
    pass


def reply(submission):
    """Assemble the reply, i.e. do all the image magic and put it in a nicely formatted comment"""
    requestSize = parse_size(submission)
    
    print("Match found! url:{}".format(submission.id, submission.short_link))

    download_image(submission)
    print("Image downloaded!")

    google_link = google_image_search_link(submission)
    print()

    reply = "This matches! Yay!"
    submission.add_comment(reply)
    already_done.write(submission.id + "\n")
    #reply = assemble_reply(submission)
    # testing stuff, this will be uncommented later


if __name__ == '__main__':
    reddit = praw.Reddit(user_agent=REDDIT_USER_AGENT)
    reddit.login(REDDIT_USER, REDDIT_PASS)
    print("Sucessfully logged in")

    try:  # Make the tmp subdir only if it exists
        os.makedirs('tmp')
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    with open('tmp/already_done.txt', mode='a+', encoding='utf-8') as already_done:
        while True:
            for subreddit in SUBREDDITS:
                curSub = reddit.get_subreddit(subreddit)
                newSubmissions = curSub.get_new(limit=20)
                for submission in newSubmissions:
                    already_done.seek(0)  # So that .read() will actually read the whole file
                    already_done_string = already_done.read()

                    if submission.id not in already_done_string and matches_title(submission):
                        reply(submission)
                        
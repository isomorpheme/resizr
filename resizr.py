import os
import errno
import configparser
import re
from urllib.parse import quote as url_quote
import requests
import praw
import base64
import json
from PIL import Image

IMAGE_EXTENSIONS = [
    '.jpg'
]

# Config reading
config = configparser.ConfigParser()
config.read('config.ini')

#Imgur API data
IMGUR_CLIENT_ID = config['Imgur']['client_id']
IMGUR_CLIENT_SECRET = config['Imgur']['client_secret']

IMGUR_BASE = "https://api.imgur.com/3/"
IMGUR_PORT = '443'
IMGUR_UPLOAD = IMGUR_BASE + "upload"

# Reddit API data
REDDIT_USER = config['Reddit']['user']
REDDIT_PASS = config['Reddit']['pass']
REDDIT_USER_AGENT = config['Reddit']['user_agent']

SUBREDDITS = config['General']['subreddits'].split(';')

TITLE_REGEX = re.compile(r"([0-9]+) ?[xX] ?([0-9]+)")  # Regular expression for searching size requests

#Google data
GOOGLE_SBI_BASE = "https://www.google.com/searchbyimage?image_url="


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


def sbi_link(direct_link):
    """
    Makes a link for a Google search by image, with the image being the one being linked to.
    """
    return GOOGLE_SBI_BASE + url_quote(direct_link, safe='')


def upload_image(image_path, name):
    """Upload the image to imgur, and return link to image"""
    with open(image_path, mode='rb') as img:
        b64 = base64.b64encode(img.read())

    data = {
        'image': b64,
        'type': 'b64',
        'name': name
    }

    headers = {'Authorization': "Client-ID " + IMGUR_CLIENT_ID}

    res = requests.post(IMGUR_UPLOAD, data=data, headers=headers)
    return json.loads(res.text)['data']['link']


def reply(submission):
    """
    The main part of making the reply. Downloads the image, processes it, and adds all the links in a comment.
    The comment is then posted.
    """
    requestSize = parse_size(submission)

    print("Match found! url:{}".format(submission.short_link))

    download_image(submission)
    print("Image downloaded!")

    imgur_link = upload_image("tmp/{}.jpg".format(submission.id), "{}-test".format(submission.id))
    print("Image uploaded! [Imgur link]({})".format(imgur_link))

    google_link = sbi_link(imgur_link)

    reply = "This matches! [Imgur link]({}). [Search by image]({})".format(imgur_link, google_link)
    submission.add_comment(reply)


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
                current_subreddit = reddit.get_subreddit(subreddit)
                new_submissions = current_subreddit.get_new(limit=20)
                for submission in new_submissions:
                    already_done.seek(0)  # So that .read() will actually read the whole file
                    already_done_string = already_done.read()

                    if submission.id not in already_done_string and matches_title(submission):
                        reply(submission)
                        already_done.write(submission.id + "\n")

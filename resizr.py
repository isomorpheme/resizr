import praw
import time
import configparser
import re
from PIL import Image

# Config reading
config = configparser.ConfigParser()
config.read('config.ini')

USER = config['UserAgent']['user']
PASS = config['UserAgent']['pass']
USER_AGENT = config['UserAgent']['AgentString']

subreddits = config['General']['subreddits'].split(';')

titleRegex = re.compile(r"([0-9]+) ?[xX] ?([0-9]+)")


def matches_title(submission):
    """Uses regex to check if the title matches the pattern"""
    match = titleRegex.search(submission.title)
    if match:
        return True


def parse_size(submission):
    """Gets the X and Y sizes from the request using the groups defined in the regex"""
    match = titleRegex.search(submission.title)
    return (int(match.group(1)), int(match.group(2)))


def download_image(submission):
    """Download the image a submission links to and store it in tmp, named after the submission ID"""
    pass


def upload_image(image):
    """Upload the image to imgur"""
    pass


def assemble_reply(submission):
    """Assemble the reply, i.e. do all the image magic and put it in a nicely formatted comment"""
    requestSize = parse_size(submission)
    
    download_image(submission)
    
    #reply = "I have detected an image size in the title of your post! Requested size: {} "
    #    "I've tried my best to create some resizes. Here they are:".format(str(requestSize))
    
    return reply


if __name__ == '__main__':
    reddit = praw.Reddit(user_agent=USER_AGENT)
    reddit.login(USER, PASS)
    print("Sucessfully logged in")

    with open('tmp/already_done.txt', 'a') as already_done:
        while True:
            for subreddit in subreddits:
                curSub = reddit.get_subreddit(subreddit)
                newSubmissions = curSub.get_new(limit=20)
                for submission in newSubmissions:
                    if submission.id not in already_done.read() and matches_title(submission):
                        print("Match found! {}".format(submission.short_link))
                        reply = "This matches! Yay!"
                        submission.add_comment(reply)
                        already_done.write(submission.id)
                        #reply = assemble_reply(submission)
                        # testing stuff, this will be uncommented later
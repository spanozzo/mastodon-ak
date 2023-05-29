import random
import itertools
import threading
import requests
from locust import HttpUser, task, between
from mastodon import Mastodon
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Configure Mastodon instance URL and API credentials
INSTANCE_URL = "mastodon.local"
CLIENT_ID = "_lRAptsgcR9Bf-yTvJ0O2NvUHiQGILk-KtzYU2qdWBk"
CLIENT_SECRET = "FSQyV4CjlHAS5oghQQj6XpeWt_lZayrKOVaURkQdRAs"

# List of usernames and passwords for the accounts you want to simulate
USER_CREDENTIALS = [
    {"username": "user0@mail.com", "password": "61e471328b2a25f480b0074e63662565"},
    {"username": "user1@mail.com", "password": "1128ffe93ce179293663d43090d1239f"},
    {"username": "user2@mail.com", "password": "79f633eb08020107b82053171df64464"},
    {"username": "user3@mail.com", "password": "693d91ffe8422fce915b52daea262d80"},
    {"username": "user4@mail.com", "password": "853ff2bc42e8bc450604cf0adf884a0e"},
    {"username": "user5@mail.com", "password": "21720ae31676ce329854bcbe1d83fd79"},
    {"username": "user6@mail.com", "password": "644203d5ca86e14414d4e8ee309d7b79"},
    {"username": "user7@mail.com", "password": "9daa8a0b6bf6217caca930c39024e6db"},
    {"username": "user8@mail.com", "password": "dc743c940dba49cb1c361725ed05a132"},
    {"username": "user9@mail.com", "password": "465925838f2207a2c882bde0e66e9d88"}
]

# List to store the access tokens
ACCESS_TOKENS = []

session = requests.Session()
session.verify = False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Log in to each account and get its access token
for credentials in USER_CREDENTIALS:
    mastodon = Mastodon(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        api_base_url=INSTANCE_URL,
        session=session
    )
    access_token = mastodon.log_in(
        username=credentials["username"],
        password=credentials["password"],
        scopes=["read", "write"]
    )
    ACCESS_TOKENS.append(access_token)
    print('logged in ', credentials["username"], ' - access token ', access_token)

class MastodonUser(HttpUser):
    wait_time = between(1, 5)

    # Create an endless iterator from the list of access tokens
    access_token_iterator = itertools.cycle(ACCESS_TOKENS)
    # Create a lock to ensure thread-safe access to the iterator
    iterator_lock = threading.Lock()

    def on_start(self):
        # Use the lock to ensure thread-safe access to the iterator
        with self.iterator_lock:
            # Get the next access token from the iterator
            access_token = next(self.access_token_iterator)
        self.mastodon = Mastodon(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            access_token=access_token,
            api_base_url=INSTANCE_URL,
            session=session
        )
        self.home_timeline = self.mastodon.timeline_home()
        print('session created for ', access_token)

    @task(5)
    def get_home_timeline(self):
        self.home_timeline = self.mastodon.timeline_home()
        print('get_home_timeline')

    @task(2)
    def post_toot(self):
        toot_content = f"Load testing toot: {random.randint(1, 10000)}"
        self.mastodon.toot(toot_content)
        print('post_toot')

    @task(2)
    def get_notifications(self):
        self.mastodon.notifications()
        print('get_notifications')

    @task(1)
    def get_instance_info(self):
        self.mastodon.instance()
        print('get_instance_info')

    @task(3)
    def view_own_profile(self):
        self.mastodon.account_verify_credentials()
        print('view_own_profile')

    @task(4)
    def boost_toot(self):
        if self.home_timeline:
            toot_to_boost = random.choice(self.home_timeline)
            self.mastodon.status_reblog(toot_to_boost['id'])
            print('boost_toot')

    @task(2)
    def favourite_toot(self):
        if self.home_timeline:
            toot_to_favourite = random.choice(self.home_timeline)
            self.mastodon.status_favourite(toot_to_favourite['id'])
            print('favourite_toot')

    @task(3)
    def reply_to_toot(self):
        if self.home_timeline:
            toot_to_reply = random.choice(self.home_timeline)
            reply_content = f"Reply to your toot: {random.randint(1, 10000)}"
            self.mastodon.status_post(status=reply_content, in_reply_to_id=toot_to_reply['id'])
            print('reply_to_toot')

    @task(3)
    def view_user_profile(self):
        if self.home_timeline:
            toot = random.choice(self.home_timeline)
            self.mastodon.account(toot['account']['id'])
            print('view_user_profile')

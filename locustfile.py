import random
from locust import HttpUser, task, between
from mastodon import Mastodon
import itertools
import threading

# Configure Mastodon instance URL and API credentials
INSTANCE_URL = "https://your.instance.url"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"

# List of usernames and passwords for the accounts you want to simulate
USER_CREDENTIALS = [
    {"username": "user0", "password": "pwd"},
    {"username": "user1", "password": "pwd"},
    {"username": "user2", "password": "pwd"},
    {"username": "user3", "password": "pwd"},
    {"username": "user4", "password": "pwd"},
    {"username": "user5", "password": "pwd"},
    {"username": "user6", "password": "pwd"},
    {"username": "user7", "password": "pwd"},
    {"username": "user8", "password": "pwd"},
    {"username": "user9", "password": "pwd"}
]

# List to store the access tokens
ACCESS_TOKENS = []

# Log in to each account and get its access token
for credentials in USER_CREDENTIALS:
    mastodon = Mastodon(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        api_base_url=INSTANCE_URL
    )
    access_token = mastodon.log_in(
        username=credentials["username"],
        password=credentials["password"],
        scopes=["read", "write"]
    )
    ACCESS_TOKENS.append(access_token)

class MastodonUser(HttpUser):
    wait_time = between(5, 15)

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
            api_base_url=INSTANCE_URL
        )
        self.home_timeline = self.mastodon.timeline_home()

    @task(5)
    def get_home_timeline(self):
        self.home_timeline = self.mastodon.timeline_home()

    @task(2)
    def post_toot(self):
        toot_content = f"Load testing toot: {random.randint(1, 10000)}"
        self.mastodon.toot(toot_content)

    @task(2)
    def get_notifications(self):
        self.mastodon.notifications()

    @task(1)
    def get_instance_info(self):
        self.mastodon.instance()

    @task(3)
    def view_own_profile(self):
        self.mastodon.account_verify_credentials()

    @task(4)
    def boost_toot(self):
        if self.home_timeline:
            toot_to_boost = random.choice(self.home_timeline)
            self.mastodon.status_reblog(toot_to_boost['id'])

    @task(2)
    def favourite_toot(self):
        if self.home_timeline:
            toot_to_favourite = random.choice(self.home_timeline)
            self.mastodon.status_favourite(toot_to_favourite['id'])

    @task(3)
    def reply_to_toot(self):
        if self.home_timeline:
            toot_to_reply = random.choice(self.home_timeline)
            reply_content = f"Reply to your toot: {random.randint(1, 10000)}"
            self.mastodon.status_post(status=reply_content, in_reply_to_id=toot_to_reply['id'])

    @task(3)
    def view_user_profile(self):
        if self.home_timeline:
            toot = random.choice(self.home_timeline)
            self.mastodon.account(toot['account']['id'])

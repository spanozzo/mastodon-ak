import random
import itertools
import threading
from locust import HttpUser, task, between
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Configure Mastodon instance URL and API credentials
INSTANCE_URL = "https://mastodon.local"
CLIENT_ID = "_lRAptsgcR9Bf-yTvJ0O2NvUHiQGILk-KtzYU2qdWBk"
CLIENT_SECRET = "FSQyV4CjlHAS5oghQQj6XpeWt_lZayrKOVaURkQdRAs"

# List of usernames and passwords for the accounts you want to simulate
USER_CREDENTIALS = [
    {"username": "user0@mail.com", "password": "61e471328b2a25f480b0074e63662565"},
    # ...
]

# List to store the access tokens
ACCESS_TOKENS = []

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
            self.access_token = next(self.access_token_iterator)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}
        self.home_timeline = self.client.get(f'{INSTANCE_URL}/api/v1/timelines/home', headers=self.headers, verify=False).json()

    @task(5)
    def get_home_timeline(self):
        self.home_timeline = self.client.get(f'{INSTANCE_URL}/api/v1/timelines/home', headers=self.headers, verify=False).json()

    @task(2)
    def post_toot(self):
        toot_content = f"Load testing toot: {random.randint(1, 10000)}"
        self.client.post(f'{INSTANCE_URL}/api/v1/statuses', headers=self.headers, data={'status': toot_content}, verify=False)

    @task(2)
    def get_notifications(self):
        self.client.get(f'{INSTANCE_URL}/api/v1/notifications', headers=self.headers, verify=False)

    @task(1)
    def get_instance_info(self):
        self.client.get(f'{INSTANCE_URL}/api/v1/instance', headers=self.headers, verify=False)

    @task(3)
    def view_own_profile(self):
        self.client.get(f'{INSTANCE_URL}/api/v1/accounts/verify_credentials', headers=self.headers, verify=False)

    @task(4)
    def boost_toot(self):
        if self.home_timeline:
            toot_to_boost = random.choice(self.home_timeline)
            self.client.post(f'{INSTANCE_URL}/api/v1/statuses/{toot_to_boost["id"]}/reblog', headers=self.headers, verify=False)

    @task(2)
    def favourite_toot(self):
        if self.home_timeline:
            toot_to_favourite = random.choice(self.home_timeline)
            self.client.post(f'{INSTANCE_URL}/api/v1/statuses/{toot_to_favourite["id"]}/favourite', headers=self.headers, verify=False)

    @task(3)
    def reply_to_toot(self):
        if self.home_timeline:
            toot_to_reply = random.choice(self.home_timeline)
            reply_content = f"Reply to your toot: {random.randint(1, 10000)}"
            self.client.post(f'{INSTANCE_URL}/api/v1/statuses', headers=self.headers, data={'status': reply_content, 'in_reply_to_id': toot_to_reply['id']}, verify=False)

    @task(3)
    def view_user_profile(self):
        if self.home_timeline:
            toot = random.choice(self.home_timeline)
            self.client.get(f'{INSTANCE_URL}/api/v1/accounts/{toot["account"]["id"]}', headers=self.headers, verify=False)

# Log in to each account and get its access token
session = requests.Session()
session.verify = False
for credentials in USER_CREDENTIALS:
    response = session.post(f"{INSTANCE_URL}/oauth/token", data={
        "grant_type": "password",
        "username": credentials["username"],
        "password": credentials["password"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "read write",
    }, verify=False)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    ACCESS_TOKENS.append(access_token)

from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    ait_time = between(5, 9)

    def on_start(self):
        self.login()

    def login(self):
        self.client.post("/login", {"username": "yongho", "password": "sample"})

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/profile")

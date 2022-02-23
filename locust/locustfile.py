from locust import HttpUser, between, task


class Voter(HttpUser):
    weight = 1
    wait_time = between(0.1, 1)

    @task(3)
    def aws(self):
        self.client.post('/', {'cloud': 'AWS'})

    @task(4)
    def azure(self):
        self.client.post('/', {'cloud': 'Azure'})

    @task(5)
    def gcp(self):
        self.client.post('/', {'cloud': 'GCP'})

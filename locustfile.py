from locust import HttpUser, task, between

class AuctionUser(HttpUser):
    
    wait_time = between(1, 3)

    def on_start(self):
        """Test başlarken bir kez çalışır: Login olup token alırız."""
        response = self.client.post("/login", json={
            "username": "umut_test",
            "password": "test123"
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {token}"})

    @task(3)
    def view_items(self):
        """Ağırlıklı olarak ürünleri listele (GET)"""
        self.client.get("/items")

    @task(1)
    def post_bid(self):

        res = self.client.get("/items")
        if res.status_code == 200 and len(res.json()) > 0:
            
            item_id = res.json()[0]["_id"]
            self.client.post("/bids", json={
                "item_id": item_id, 
                "amount": 1500.0
            })
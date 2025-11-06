"""
Test script using FastAPI TestClient (no server needed)
"""


def test_root(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print(f"✓ Root endpoint working: {data}")


def test_get_storms_august_2025(client):
    """Test getting storms for August 2025 (test database month)"""
    response = client.get("/storms/2025/8")
    assert response.status_code == 200
    
    data = response.json()
    assert "storms" in data
    assert len(data["storms"]) == 13  # We know test DB has 13 storms
    
    print(f"✓ Found {len(data['storms'])} storms for August 2025")
    
    # Verify first storm structure
    if data['storms']:
        first_storm = data['storms'][0]
        assert "ID" in first_storm
        assert "name" in first_storm
        assert "basin" in first_storm
        assert "genesis" in first_storm
        assert "time" in first_storm
        assert isinstance(first_storm["time"], list)
        print(f"✓ Storm structure validated: {first_storm['name']} ({first_storm['basin']})")


def test_get_storms_empty_month(client):
    """Test getting storms for a month with no data"""
    response = client.get("/storms/2020/1")
    assert response.status_code == 200
    
    data = response.json()
    assert "storms" in data
    assert len(data["storms"]) == 0
    print("✓ Empty month returns correctly")
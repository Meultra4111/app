import requests
import sys
import json
from datetime import datetime

class TeamMeultraBattleArenaAPITester:
    def __init__(self, base_url="https://pvp-mayhem.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_player_id = None
        self.test_session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_characters(self):
        """Test getting all characters"""
        success, response = self.run_test("Get Characters", "GET", "characters", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} characters")
            # Verify we have the expected characters
            character_ids = [char['id'] for char in response]
            expected_chars = ['meultra4111', 'olivo_10', 'gato', 'jhon', 'riptor', 'martin', 'botsito', 'brayan']
            dlc_chars = ['thisand', 'notfik', 'nooblord']
            
            for char_id in expected_chars:
                if char_id in character_ids:
                    print(f"   ✅ Found main character: {char_id}")
                else:
                    print(f"   ❌ Missing main character: {char_id}")
            
            for char_id in dlc_chars:
                if char_id in character_ids:
                    print(f"   ✅ Found DLC character: {char_id}")
                else:
                    print(f"   ❌ Missing DLC character: {char_id}")
                    
            # Check DLC flag
            dlc_count = len([char for char in response if char.get('is_dlc', False)])
            print(f"   DLC characters marked: {dlc_count}")
            
        return success, response

    def test_get_single_character(self):
        """Test getting a single character"""
        return self.run_test("Get Single Character", "GET", "characters/meultra4111", 200)

    def test_create_player(self):
        """Test creating a new player"""
        username = f"TestPlayer_{datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "Create Player",
            "POST",
            "players",
            200,
            data={"username": username}
        )
        if success and 'player_id' in response:
            self.test_player_id = response['player_id']
            print(f"   Created player with ID: {self.test_player_id}")
        return success, response

    def test_get_player(self):
        """Test getting player data"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        success, response = self.run_test(
            "Get Player",
            "GET",
            f"players/{self.test_player_id}",
            200
        )
        if success:
            print(f"   Player level: {response.get('level', 'N/A')}")
            print(f"   Player XP: {response.get('xp', 'N/A')}")
            print(f"   Player coins: {response.get('coins', 'N/A')}")
            print(f"   DLC unlocked: {response.get('unlocked_dlc', False)}")
        return success, response

    def test_add_xp(self):
        """Test adding XP to player"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Add XP",
            "PUT",
            f"players/{self.test_player_id}/xp?xp=150",
            200
        )

    def test_update_coins(self):
        """Test updating player coins"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Update Coins",
            "PUT",
            f"players/{self.test_player_id}/coins?amount=500",
            200
        )

    def test_create_game_session(self):
        """Test creating a game session"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        success, response = self.run_test(
            "Create Game Session",
            "POST",
            "game/session",
            200,
            data={
                "player_id": self.test_player_id,
                "character_id": "meultra4111",
                "map_id": "roblox"
            }
        )
        if success and 'session_id' in response:
            self.test_session_id = response['session_id']
            print(f"   Created session with ID: {self.test_session_id}")
        return success, response

    def test_update_game_session(self):
        """Test updating a game session"""
        if not self.test_session_id:
            print("❌ No test session ID available")
            return False, {}
        
        return self.run_test(
            "Update Game Session",
            "PUT",
            f"game/session/{self.test_session_id}",
            200,
            data={
                "score": 1500,
                "enemies_defeated": 15,
                "victory": True,
                "duration": 120
            }
        )

    def test_get_player_sessions(self):
        """Test getting player sessions"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Get Player Sessions",
            "GET",
            f"game/sessions/{self.test_player_id}",
            200
        )

    def test_get_achievements(self):
        """Test getting achievements"""
        success, response = self.run_test("Get Achievements", "GET", "achievements", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} achievements")
            categories = set(ach.get('category', 'unknown') for ach in response)
            print(f"   Categories: {', '.join(categories)}")
        return success, response

    def test_get_player_achievements(self):
        """Test getting player achievements"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Get Player Achievements",
            "GET",
            f"achievements/{self.test_player_id}",
            200
        )

    def test_unlock_achievement(self):
        """Test unlocking an achievement"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Unlock Achievement",
            "POST",
            f"achievements/{self.test_player_id}/first_blood",
            200
        )

    def test_get_shop_items(self):
        """Test getting shop items"""
        success, response = self.run_test("Get Shop Items", "GET", "shop/items", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} shop items")
        return success, response

    def test_get_shop_weapons(self):
        """Test getting shop weapons"""
        success, response = self.run_test("Get Shop Weapons", "GET", "shop/weapons", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} shop weapons")
        return success, response

    def test_purchase_item(self):
        """Test purchasing an item"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Purchase Item",
            "POST",
            "shop/purchase",
            200,
            data={
                "player_id": self.test_player_id,
                "item_id": "health_potion"
            }
        )

    def test_get_player_inventory(self):
        """Test getting player inventory"""
        if not self.test_player_id:
            print("❌ No test player ID available")
            return False, {}
        
        return self.run_test(
            "Get Player Inventory",
            "GET",
            f"shop/inventory/{self.test_player_id}",
            200
        )

    def test_get_maps(self):
        """Test getting maps"""
        success, response = self.run_test("Get Maps", "GET", "maps", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} maps")
            map_names = [m.get('name', 'Unknown') for m in response]
            print(f"   Maps: {', '.join(map_names)}")
        return success, response

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Team Meultra Battle Arena API Tests")
        print("=" * 60)

        # Basic API tests
        self.test_api_root()
        
        # Character tests
        self.test_get_characters()
        self.test_get_single_character()
        
        # Player tests
        self.test_create_player()
        self.test_get_player()
        self.test_add_xp()
        self.test_update_coins()
        
        # Game session tests
        self.test_create_game_session()
        self.test_update_game_session()
        self.test_get_player_sessions()
        
        # Achievement tests
        self.test_get_achievements()
        self.test_get_player_achievements()
        self.test_unlock_achievement()
        
        # Shop tests
        self.test_get_shop_items()
        self.test_get_shop_weapons()
        self.test_purchase_item()
        self.test_get_player_inventory()
        
        # Map tests
        self.test_get_maps()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"   - {failure.get('test', 'Unknown')}: {failure.get('error', failure.get('response', 'Unknown error'))}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = TeamMeultraBattleArenaAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
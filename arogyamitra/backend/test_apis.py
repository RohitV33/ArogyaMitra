"""
test_apis.py - Epic 5: Testing and Deployment
Activity 5.1: Backend Testing and API Validation
Activity 5.3: Backend-Frontend Integration Testing

Tests all FastAPI endpoints using Python requests.
Run: python test_apis.py
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://arogyamitra-o8sd.onrender.com"
TOKEN = None
TEST_USER = {
    "email": f"test_{int(datetime.now().timestamp())}@arogyamitra.test",
    "username": f"testuser_{int(datetime.now().timestamp())}",
    "password": "TestPass123!",
    "full_name": "Test User",
    "age": 28,
    "gender": "male",
    "height": 175.0,
    "weight": 70.0,
    "fitness_level": "intermediate",
    "fitness_goal": "muscle_gain",
    "workout_preference": "gym",
    "diet_preference": "vegetarian"
}

# ─── Color Output ─────────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

passed = 0
failed = 0

def test(name, result, expected_status=None, response=None):
    global passed, failed
    if result:
        print(f"  {GREEN}✅ PASS{RESET} — {name}")
        passed += 1
    else:
        print(f"  {RED}❌ FAIL{RESET} — {name}", end="")
        if response:
            try:
                print(f" | Status: {response.status_code} | Body: {response.text[:100]}")
            except:
                pass
        else:
            print()
        failed += 1


def section(title):
    print(f"\n{BOLD}{CYAN}{'═' * 50}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * 50}{RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
# EPIC 5.1: Backend Testing and API Validation
# ═══════════════════════════════════════════════════════════════════════════════

section("EPIC 5.1: Health Check & Basic Connectivity")

r = requests.get(f"{BASE_URL}/")
test("Root endpoint responds", r.status_code == 200, response=r)

r = requests.get(f"{BASE_URL}/health")
test("Health check endpoint", r.status_code == 200 and r.json().get("status") == "healthy", response=r)

r = requests.get(f"{BASE_URL}/docs")
test("Swagger UI accessible", r.status_code == 200, response=r)

# ─── Authentication Tests ─────────────────────────────────────────────────────
section("AUTH: Register & Login")

r = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
test("User registration", r.status_code == 200, response=r)
if r.status_code == 200:
    TOKEN = r.json().get("access_token")
    test("Token returned on register", TOKEN is not None)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

r = requests.get(f"{BASE_URL}/api/auth/me", headers=HEADERS)
test("Get current user (/me)", r.status_code == 200, response=r)
if r.status_code == 200:
    me = r.json()
    test("User email matches", me.get("email") == TEST_USER["email"])
    test("Username matches", me.get("username") == TEST_USER["username"])

# Login test
import urllib.parse
login_data = urllib.parse.urlencode({"username": TEST_USER["username"], "password": TEST_USER["password"]})
r = requests.post(f"{BASE_URL}/api/auth/login",
                  data=login_data,
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
test("Login with username", r.status_code == 200, response=r)

# Auth failure test
r = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
test("Invalid token rejected (401)", r.status_code == 401, response=r)

# ─── User Profile Tests ───────────────────────────────────────────────────────
section("USERS: Profile Management")

r = requests.get(f"{BASE_URL}/api/users/profile", headers=HEADERS)
test("Get user profile", r.status_code == 200, response=r)

r = requests.put(f"{BASE_URL}/api/users/profile", headers=HEADERS,
                 json={"weight": 72.5, "fitness_goal": "weight_loss"})
test("Update user profile", r.status_code == 200, response=r)

r = requests.get(f"{BASE_URL}/api/users/dashboard-stats", headers=HEADERS)
test("Dashboard stats", r.status_code == 200, response=r)

# ─── Workout Tests ────────────────────────────────────────────────────────────
section("WORKOUTS: Plan Generation")

print(f"  {YELLOW}⏳ Generating AI workout plan (may take a moment)...{RESET}")
r = requests.post(f"{BASE_URL}/api/workouts/generate", headers=HEADERS, json={}, timeout=60)
test("Generate workout plan", r.status_code == 200, response=r)
if r.status_code == 200:
    plan_data = r.json()
    test("Plan has plan_id", "plan_id" in plan_data)
    test("Plan has workout data", "plan" in plan_data)

r = requests.get(f"{BASE_URL}/api/workouts/current", headers=HEADERS)
test("Get current workout plan", r.status_code == 200, response=r)

r = requests.get(f"{BASE_URL}/api/workouts/history", headers=HEADERS)
test("Workout history", r.status_code == 200, response=r)

# ─── Nutrition Tests ──────────────────────────────────────────────────────────
section("NUTRITION: Plan Generation")

print(f"  {YELLOW}⏳ Generating AI nutrition plan (may take a moment)...{RESET}")
r = requests.post(f"{BASE_URL}/api/nutrition/generate", headers=HEADERS, json={}, timeout=60)
test("Generate nutrition plan", r.status_code == 200, response=r)

r = requests.get(f"{BASE_URL}/api/nutrition/current", headers=HEADERS)
test("Get current nutrition plan", r.status_code == 200, response=r)
if r.status_code == 200:
    nutrition = r.json()
    test("Nutrition has macros", "macros" in nutrition or "plan" in nutrition)

# ─── Progress Tests ───────────────────────────────────────────────────────────
section("PROGRESS: Logging & Analytics")

r = requests.post(f"{BASE_URL}/api/progress/log", headers=HEADERS,
                  json={"weight": 70.5, "calories_burned": 350, "workout_completed": True, "notes": "Great session!"})
test("Log progress entry", r.status_code == 200, response=r)

r = requests.get(f"{BASE_URL}/api/progress/history", headers=HEADERS)
test("Progress history", r.status_code == 200, response=r)
if r.status_code == 200:
    records = r.json()
    test("Progress records returned", isinstance(records, list))

r = requests.get(f"{BASE_URL}/api/progress/analytics", headers=HEADERS)
test("Progress analytics", r.status_code == 200, response=r)

# ─── Chat Tests ───────────────────────────────────────────────────────────────
section("CHAT: AROMI AI Coaching")

r = requests.post(f"{BASE_URL}/api/chat/aromi", headers=HEADERS,
                  json={"message": "What is a good post-workout meal?", "user_status": "normal"}, timeout=30)
test("AROMI chat response", r.status_code == 200, response=r)
if r.status_code == 200:
    chat_data = r.json()
    test("Response has content", "response" in chat_data and len(chat_data["response"]) > 10)

r = requests.get(f"{BASE_URL}/api/chat/history", headers=HEADERS)
test("Chat history", r.status_code == 200, response=r)

# ─── Health Assessment Tests ──────────────────────────────────────────────────
section("HEALTH: Assessment & Scoring")

r = requests.post(f"{BASE_URL}/api/health/assess", headers=HEADERS,
                  json={"sleep_hours": 7.5, "stress_level": 4, "water_intake_liters": 2.5, "smoking": False})
test("Submit health assessment", r.status_code == 200, response=r)
if r.status_code == 200:
    assessment = r.json()
    test("Health score returned", "health_score" in assessment)
    test("BMI calculated", "bmi" in assessment)
    test("Recommendations provided", "recommendations" in assessment)

r = requests.get(f"{BASE_URL}/api/health/latest", headers=HEADERS)
test("Get latest assessment", r.status_code == 200, response=r)

# ─── AI Coach Tests ───────────────────────────────────────────────────────────
section("AI COACH: Advanced Features")

r = requests.get(f"{BASE_URL}/api/ai-coach/motivate", headers=HEADERS, timeout=30)
test("Daily motivation endpoint", r.status_code == 200, response=r)
if r.status_code == 200:
    test("Motivation message returned", "motivation" in r.json())

r = requests.post(f"{BASE_URL}/api/ai-coach/aromi-chat", headers=HEADERS,
                  json={"message": "I'm traveling next week, adjust my workout", "user_status": "traveling"}, timeout=30)
test("AROMI coaching with context", r.status_code == 200, response=r)

# ─── Error Handling Tests ─────────────────────────────────────────────────────
section("ERROR HANDLING: Edge Cases")

r = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
test("Duplicate registration rejected", r.status_code in [400, 422], response=r)

r = requests.get(f"{BASE_URL}/api/workouts/current", headers={"Authorization": "Bearer bad"})
test("Unauthorized access blocked", r.status_code == 401, response=r)

# ─── Summary ─────────────────────────────────────────────────────────────────
section("TEST SUMMARY")
total = passed + failed
print(f"\n  Total:  {total} tests")
print(f"  {GREEN}Passed: {passed}{RESET}")
print(f"  {RED}Failed: {failed}{RESET}")
percentage = (passed / total * 100) if total > 0 else 0
print(f"  Score:  {percentage:.1f}%\n")

if failed == 0:
    print(f"  {GREEN}{BOLD}🎉 ALL TESTS PASSED! ArogyaMitra backend is production-ready!{RESET}\n")
elif percentage >= 80:
    print(f"  {YELLOW}{BOLD}⚠️  Most tests passed. Review failures above.{RESET}\n")
else:
    print(f"  {RED}{BOLD}❌ Multiple failures. Check backend setup and API keys.{RESET}\n")

sys.exit(0 if failed == 0 else 1)

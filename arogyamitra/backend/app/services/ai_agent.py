import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from app.utils.config import settings
from app.models.user import User, FitnessGoal, WorkoutPreference, DietPreference


class ArogyaMitraAgent:
    """
    🤖 ArogyaMitra AI Agent - Your Personal Fitness Companion

    This agent orchestrates all AI-powered features:
    - Workout plan generation
    - Nutrition planning
    - Motivational coaching
    - Dynamic plan modifications
    - Progress analysis
    """

    def __init__(self):
        self.groq_client = None
        self.initialize_ai_clients()

    def initialize_ai_clients(self):
        """Initialize AI service clients"""
        try:
            if settings.GROQ_API_KEY and GROQ_AVAILABLE:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                print("✅ Groq AI client initialized")
            else:
                print("⚠️ No Groq API key found")
        except Exception as e:
            print(f"⚠️ Groq initialization failed: {e}")

    def _call_groq(self, prompt: str, system_prompt: str = "", max_tokens: int = 2000) -> str:
        """Call Groq LLaMA-3.3-70B model"""
        if not self.groq_client:
            return self._get_fallback_response(prompt)
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when AI is not available"""
        return "I'm here to help with your fitness journey! Please configure the Groq API key to enable full AI capabilities."

    def generate_workout_plan(self, user: User) -> Dict:
        """Generate a personalized 7-day workout plan"""
        system_prompt = """You are ArogyaMitra's fitness expert AI. Generate detailed, safe, and effective workout plans.
        Always respond with valid JSON only, no extra text."""
        
        user_profile = f"""
        User Profile:
        - Age: {user.age}, Gender: {user.gender}
        - Height: {user.height}cm, Weight: {user.weight}kg
        - Fitness Level: {user.fitness_level}
        - Goal: {user.fitness_goal.value if user.fitness_goal else 'maintenance'}
        - Workout Preference: {user.workout_preference.value if user.workout_preference else 'home'}
        """
        
        prompt = f"""
        {user_profile}
        
        Generate a complete 7-day workout plan. Return JSON with this structure:
        {{
          "plan_name": "string",
          "goal": "string",
          "weekly_frequency": number,
          "days": [
            {{
              "day": "Monday",
              "focus": "Upper Body",
              "duration_minutes": 45,
              "exercises": [
                {{
                  "name": "Push-ups",
                  "sets": 3,
                  "reps": 15,
                  "rest_seconds": 60,
                  "muscle_group": "chest",
                  "difficulty": "beginner",
                  "instructions": "Keep core tight..."
                }}
              ],
              "warmup": "5 min light cardio",
              "cooldown": "5 min stretching",
              "calories_estimate": 250
            }}
          ],
          "weekly_calories_burn": 1500,
          "tips": ["tip1", "tip2"]
        }}
        """
        
        response = self._call_groq(prompt, system_prompt, max_tokens=3000)
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Return structured fallback
        return self._get_default_workout_plan(user)

    def generate_nutrition_plan(self, user: User) -> Dict:
        """Generate a personalized nutrition plan"""
        # Calculate BMR using Mifflin-St Jeor
        if user.height and user.weight and user.age:
            if user.gender and user.gender.lower() == 'male':
                bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
            else:
                bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
            tdee = bmr * 1.375  # Moderately active
        else:
            tdee = 2000  # Default
        
        system_prompt = """You are ArogyaMitra's nutrition expert. Generate scientifically balanced meal plans.
        Always respond with valid JSON only."""
        
        prompt = f"""
        User needs:
        - Daily calories: {int(tdee)}
        - Goal: {user.fitness_goal.value if user.fitness_goal else 'maintenance'}
        - Diet: {user.diet_preference.value if user.diet_preference else 'vegetarian'}
        
        Generate a 7-day meal plan JSON:
        {{
          "daily_calories": {int(tdee)},
          "macros": {{"protein": 150, "carbs": 200, "fat": 65}},
          "days": [
            {{
              "day": "Monday",
              "meals": [
                {{
                  "type": "breakfast",
                  "name": "Oatmeal with fruits",
                  "calories": 350,
                  "protein": 12,
                  "carbs": 55,
                  "fat": 8,
                  "ingredients": ["1 cup oats", "1 banana"],
                  "instructions": "Cook oats..."
                }}
              ],
              "total_calories": 1800
            }}
          ],
          "grocery_list": ["oats", "eggs"],
          "tips": ["tip1"]
        }}
        """
        
        response = self._call_groq(prompt, system_prompt, max_tokens=3000)
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return self._get_default_nutrition_plan(user)

    def chat_with_aromi(self, message: str, user: User, context: Dict = None) -> str:
        """AROMI AI Coach - Real-time adaptive wellness guidance"""
        system_prompt = f"""You are AROMI, ArogyaMitra's intelligent AI fitness coach. You are:
        - Empathetic and motivating
        - Expert in fitness, nutrition, and wellness
        - Adaptive to user's current situation
        - Concise but thorough
        
        User Profile: {user.full_name}, {user.age}yr, Goal: {user.fitness_goal.value if user.fitness_goal else 'fitness'}
        
        Provide personalized, actionable advice. Be warm, encouraging, and specific."""
        
        context_info = ""
        if context:
            if context.get("user_status"):
                context_info = f"\nUser Status: {context['user_status']}"
            if context.get("workout_plan"):
                context_info += f"\nActive Workout Plan: Yes"
        
        full_message = f"{context_info}\n\nUser: {message}" if context_info else message
        
        return self._call_groq(full_message, system_prompt, max_tokens=500)

    def analyze_progress(self, progress_data: List[Dict], user: User) -> Dict:
        """Analyze user's progress and provide insights"""
        system_prompt = "You are a fitness analytics expert. Analyze progress data and provide actionable insights. Return JSON only."
        
        prompt = f"""
        Analyze this fitness progress for {user.full_name}:
        Progress Records: {json.dumps(progress_data[-10:] if len(progress_data) > 10 else progress_data)}
        Goal: {user.fitness_goal.value if user.fitness_goal else 'maintenance'}
        
        Return JSON:
        {{
          "trend": "improving/declining/stable",
          "key_insights": ["insight1", "insight2"],
          "recommendations": ["rec1", "rec2"],
          "predicted_goal_date": "2024-06-01",
          "motivation_message": "Keep going..."
        }}
        """
        
        response = self._call_groq(prompt, system_prompt)
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "trend": "stable",
            "key_insights": ["Keep tracking your progress daily"],
            "recommendations": ["Stay consistent with your workout plan"],
            "motivation_message": "Every step forward counts! Keep going! 💪"
        }

    def _get_default_workout_plan(self, user: User) -> Dict:
        return {
            "plan_name": f"ArogyaMitra Personalized Plan for {user.full_name}",
            "goal": user.fitness_goal.value if user.fitness_goal else "maintenance",
            "weekly_frequency": 5,
            "days": [
                {
                    "day": "Monday",
                    "focus": "Upper Body",
                    "duration_minutes": 45,
                    "exercises": [
                        {"name": "Push-ups", "sets": 3, "reps": 15, "rest_seconds": 60, "muscle_group": "chest", "difficulty": user.fitness_level or "beginner", "instructions": "Keep core tight, full range of motion"},
                        {"name": "Pull-ups", "sets": 3, "reps": 8, "rest_seconds": 90, "muscle_group": "back", "difficulty": user.fitness_level or "beginner", "instructions": "Controlled movement"},
                        {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": 12, "rest_seconds": 60, "muscle_group": "shoulders", "difficulty": user.fitness_level or "beginner", "instructions": "Press overhead"}
                    ],
                    "warmup": "5 min arm circles and light cardio",
                    "cooldown": "5 min upper body stretching",
                    "calories_estimate": 280
                },
                {
                    "day": "Tuesday",
                    "focus": "Lower Body",
                    "duration_minutes": 50,
                    "exercises": [
                        {"name": "Squats", "sets": 4, "reps": 15, "rest_seconds": 60, "muscle_group": "quads", "difficulty": user.fitness_level or "beginner", "instructions": "Knees over toes"},
                        {"name": "Lunges", "sets": 3, "reps": 12, "rest_seconds": 60, "muscle_group": "glutes", "difficulty": user.fitness_level or "beginner", "instructions": "Step forward"},
                        {"name": "Calf Raises", "sets": 3, "reps": 20, "rest_seconds": 45, "muscle_group": "calves", "difficulty": user.fitness_level or "beginner", "instructions": "Full range"}
                    ],
                    "warmup": "5 min leg swings and squats",
                    "cooldown": "5 min lower body stretching",
                    "calories_estimate": 320
                },
                {
                    "day": "Wednesday",
                    "focus": "Rest/Active Recovery",
                    "duration_minutes": 30,
                    "exercises": [
                        {"name": "Light Walking", "sets": 1, "reps": 1, "rest_seconds": 0, "muscle_group": "full body", "difficulty": "beginner", "instructions": "30 min easy walk"}
                    ],
                    "warmup": "N/A",
                    "cooldown": "Yoga stretches",
                    "calories_estimate": 150
                },
                {
                    "day": "Thursday",
                    "focus": "Core & Cardio",
                    "duration_minutes": 40,
                    "exercises": [
                        {"name": "Plank", "sets": 3, "reps": 1, "rest_seconds": 60, "muscle_group": "core", "difficulty": user.fitness_level or "beginner", "instructions": "Hold 60 seconds"},
                        {"name": "Crunches", "sets": 3, "reps": 20, "rest_seconds": 45, "muscle_group": "abs", "difficulty": user.fitness_level or "beginner", "instructions": "Control movement"},
                        {"name": "Burpees", "sets": 3, "reps": 10, "rest_seconds": 90, "muscle_group": "full body", "difficulty": "intermediate", "instructions": "Explosive movement"}
                    ],
                    "warmup": "5 min jumping jacks",
                    "cooldown": "5 min core stretching",
                    "calories_estimate": 350
                },
                {
                    "day": "Friday",
                    "focus": "Full Body",
                    "duration_minutes": 55,
                    "exercises": [
                        {"name": "Deadlifts", "sets": 4, "reps": 10, "rest_seconds": 90, "muscle_group": "back/glutes", "difficulty": "intermediate", "instructions": "Neutral spine"},
                        {"name": "Bench Press", "sets": 3, "reps": 12, "rest_seconds": 60, "muscle_group": "chest", "difficulty": user.fitness_level or "beginner", "instructions": "Full range"},
                        {"name": "Rows", "sets": 3, "reps": 12, "rest_seconds": 60, "muscle_group": "back", "difficulty": user.fitness_level or "beginner", "instructions": "Squeeze shoulder blades"}
                    ],
                    "warmup": "10 min full body warm-up",
                    "cooldown": "10 min full body stretch",
                    "calories_estimate": 400
                }
            ],
            "weekly_calories_burn": 1500,
            "tips": ["Stay hydrated", "Get 8 hours of sleep", "Track your progress"]
        }

    def _get_default_nutrition_plan(self, user: User) -> Dict:
        return {
            "daily_calories": 2000,
            "macros": {"protein": 150, "carbs": 225, "fat": 67},
            "days": [
                {
                    "day": "Monday",
                    "meals": [
                        {"type": "breakfast", "name": "Oatmeal with banana", "calories": 350, "protein": 12, "carbs": 60, "fat": 6, "ingredients": ["1 cup oats", "1 banana", "1 tbsp honey"], "instructions": "Cook oats with water, top with banana"},
                        {"type": "lunch", "name": "Dal rice with vegetables", "calories": 500, "protein": 20, "carbs": 80, "fat": 10, "ingredients": ["1 cup dal", "1 cup rice", "mixed veggies"], "instructions": "Cook dal and rice, serve with veggies"},
                        {"type": "dinner", "name": "Paneer bhurji with roti", "calories": 450, "protein": 25, "carbs": 50, "fat": 15, "ingredients": ["200g paneer", "2 rotis", "tomatoes", "spices"], "instructions": "Scramble paneer with spices"},
                        {"type": "snack", "name": "Fruit and nuts", "calories": 200, "protein": 5, "carbs": 30, "fat": 8, "ingredients": ["mixed fruits", "almonds"], "instructions": "Mix and enjoy"}
                    ],
                    "total_calories": 1500
                }
            ],
            "grocery_list": ["oats", "dal", "rice", "paneer", "vegetables", "fruits", "almonds"],
            "tips": ["Drink 8 glasses of water", "Eat every 3-4 hours", "Don't skip breakfast"]
        }


# Singleton instance
ai_agent = ArogyaMitraAgent()

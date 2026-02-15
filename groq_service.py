from groq import Groq
import os
from config import Config

class GroqService:
    """Service class for interacting with Groq API"""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        self.client = Groq(api_key=self.api_key)
        self.model = "mixtral-8x7b-32768"  # Using Mixtral model
    
    def generate_health_recommendation(self, condition, health_profile=None, language='English'):
        """
        Generate health and diet recommendations based on condition and user profile
        
        Args:
            condition: The health condition or query
            health_profile: User's health profile data
            language: Language for the recommendation
            
        Returns:
            Generated recommendation text
        """
        try:
            # Build context from health profile if available
            context = ""
            if health_profile:
                context = f"""
User Health Profile:
- Name: {health_profile.full_name}
- Age: {health_profile.age} years
- Gender: {health_profile.gender}
- Height: {health_profile.height} cm
- Weight: {health_profile.weight} kg
- BMI: {health_profile.bmi if health_profile.bmi else 'Not calculated'}
- Health Conditions: {health_profile.health_conditions or 'None'}
- Allergies: {health_profile.allergies or 'None'}
- Current Medications: {health_profile.medications or 'None'}
- Activity Level: {health_profile.activity_level}
- Dietary Preference: {health_profile.dietary_preference}
- Sleep Hours: {health_profile.sleep_hours} hours
- Water Intake: {health_profile.water_intake} glasses/day
- Health Goal: {health_profile.health_goal}
"""
            
            # Create the prompt
            prompt = f"""You are PulseAI, an AI-powered health and diet recommendation assistant. 

{context}

User Query/Condition: {condition}

Please provide comprehensive, personalized health and diet recommendations in {language} language. Include:

1. **Understanding the Condition**: Brief explanation of the condition
2. **Dietary Recommendations**: Specific foods to eat and avoid, meal suggestions
3. **Lifestyle Modifications**: Exercise, sleep, stress management tips
4. **General Health Tips**: Additional advice based on their profile
5. **Important Note**: Reminder to consult healthcare professionals

Make the recommendations:
- Personalized based on the user's profile (if provided)
- Practical and easy to implement
- Evidence-based and safe
- Culturally appropriate for {language} speakers
- Well-structured and easy to read

If the profile data is available, tailor recommendations considering their:
- Current health conditions and medications
- Dietary preferences and restrictions
- Activity level and fitness goals
- Age and gender-specific needs

Format the response in a clear, organized manner with proper headings and bullet points."""

            # Make API call to Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are PulseAI, a helpful and knowledgeable health and nutrition assistant. Provide accurate, personalized health advice while always reminding users to consult healthcare professionals for serious concerns."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            # Extract and return the response
            recommendation = chat_completion.choices[0].message.content
            return recommendation
            
        except Exception as e:
            print(f"Error generating recommendation: {str(e)}")
            return f"Sorry, I encountered an error while generating recommendations. Please try again later. Error: {str(e)}"
    
    def generate_specific_plan(self, plan_type, health_profile):
        """
        Generate specific plans like meal plans, workout routines, etc.
        
        Args:
            plan_type: Type of plan (meal, workout, sleep, etc.)
            health_profile: User's health profile
            
        Returns:
            Generated plan
        """
        try:
            plan_prompts = {
                'meal': f"""Create a detailed 7-day meal plan for:
- Age: {health_profile.age}, Gender: {health_profile.gender}
- Weight: {health_profile.weight} kg, Height: {health_profile.height} cm
- Goal: {health_profile.health_goal}
- Diet preference: {health_profile.dietary_preference}
- Activity level: {health_profile.activity_level}
- Health conditions: {health_profile.health_conditions or 'None'}
- Allergies: {health_profile.allergies or 'None'}

Include breakfast, lunch, dinner, and 2 snacks for each day with approximate calories.""",
                
                'workout': f"""Create a detailed weekly workout routine for:
- Age: {health_profile.age}, Gender: {health_profile.gender}
- Goal: {health_profile.health_goal}
- Activity level: {health_profile.activity_level}
- Health conditions: {health_profile.health_conditions or 'None'}

Include specific exercises, sets, reps, and rest periods.""",
                
                'wellness': f"""Create a comprehensive wellness plan for:
- Age: {health_profile.age}
- Sleep: {health_profile.sleep_hours} hours
- Water intake: {health_profile.water_intake} glasses
- Goal: {health_profile.health_goal}

Include sleep hygiene, stress management, hydration tips, and daily routines."""
            }
            
            prompt = plan_prompts.get(plan_type, "Create a general health plan")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are PulseAI, an expert health and fitness planner. Create detailed, personalized, and safe plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=2500
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating plan: {str(e)}")
            return f"Sorry, I encountered an error while generating the plan. Error: {str(e)}"

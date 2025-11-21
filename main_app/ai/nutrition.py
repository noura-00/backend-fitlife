import random
import re

from django.utils import timezone


def extract_preferences(text):
    if not text:
        return {}
    lowered = text.lower()
    preferences = {}
    dislike_patterns = [
        r"i don't like ([a-z\s]+)",
        r"i hate ([a-z\s]+)",
        r"i'm allergic to ([a-z\s]+)",
        r"آكل (?:.*) بس ما احب ([\u0600-\u06FF\s]+)",
        r"ما أحب ([\u0600-\u06FF\s]+)",
        r"أكره ([\u0600-\u06FF\s]+)",
        r"ما عندي حساسية من ([\u0600-\u06FF\s]+)",
        r"عندي حساسية من ([\u0600-\u06FF\s]+)",
        r"allergic to ([a-z\s]+)",
        r"don't have ([a-z\s]+)",
        r"ما عندي ([\u0600-\u06FF\s]+)",
    ]
    favorite_patterns = [
        r"i love ([a-z\s]+)",
        r"i like ([a-z\s]+)",
        r"أحب ([\u0600-\u06FF\s]+)",
        r"أفضل ([\u0600-\u06FF\s]+)",
    ]
    meal_preference_patterns = [
        r"for breakfast i (?:like|prefer) ([a-z\s]+)",
        r"الفطور (?:أحب|أفضل) ([\u0600-\u06FF\s]+)",
        r"for lunch i (?:like|prefer) ([a-z\s]+)",
        r"الغداء (?:أحب|أفضل) ([\u0600-\u06FF\s]+)",
    ]
    workout_dislike_patterns = [
        r"i can't do ([a-z\s]+)",
        r"no more ([a-z\s]+)",
    ]
    injury_patterns = [
        r"injury(?: to)? ([a-z\s]+)",
        r"hurt my ([a-z\s]+)",
    ]
    motivation_patterns = [
        r"i like when you ([a-z\s]+) me",
        r"حفزني بـ ([\u0600-\u06FF\s]+)",
    ]

    for pattern in dislike_patterns:
        match = re.search(pattern, lowered)
        if match:
            item = match.group(1).strip()
            # Check if it's an allergy
            if 'حساسية' in pattern or 'allergic' in pattern:
                preferences.setdefault('allergies', []).append(item)
            else:
                preferences.setdefault('food_dislikes', []).append(item)
    for pattern in favorite_patterns:
        match = re.search(pattern, lowered)
        if match:
            preferences.setdefault('favorite_foods', []).append(match.group(1).strip())
    for pattern in meal_preference_patterns:
        match = re.search(pattern, lowered)
        if match:
            meal_type = 'breakfast' if 'breakfast' in pattern or 'فطور' in pattern else 'lunch'
            preferences.setdefault(f'{meal_type}_preferences', []).append(match.group(1).strip())
    for pattern in workout_dislike_patterns:
        match = re.search(pattern, lowered)
        if match:
            preferences.setdefault('workout_dislikes', []).append(match.group(1).strip())
    for pattern in injury_patterns:
        match = re.search(pattern, lowered)
        if match:
            preferences.setdefault('injuries', []).append(match.group(1).strip())
    for pattern in motivation_patterns:
        match = re.search(pattern, lowered)
        if match:
            preferences.setdefault('motivation_style', []).append(match.group(1).strip())

    return preferences


def merge_preferences(stored_pref, new_pref):
    for key, values in new_pref.items():
        if key not in stored_pref:
            stored_pref[key] = []
        for value in values:
            if value not in stored_pref[key]:
                stored_pref[key].append(value)


def detect_nutrition_adherence(user_message):
    """Detect if user followed nutrition plan"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Full adherence
    full_adherence_keywords = [
        'اتبعت الخطة', 'followed plan', 'stuck to plan', 'اتبعت الوجبات',
        'اكلت حسب الخطة', 'ate according to plan', 'nutrition plan followed',
        'اتبعت التغذية', 'nutrition followed',
    ]
    if any(keyword in lowered for keyword in full_adherence_keywords):
        return 'full'
    
    # Partial adherence
    partial_adherence_keywords = [
        'جزئياً', 'partially', 'بعض', 'some', 'قليل', 'little',
        'ما كل شي', 'not everything', 'بعض الوجبات', 'some meals',
    ]
    if any(keyword in lowered for keyword in partial_adherence_keywords):
        return 'partial'
    
    # Skipped
    skipped_keywords = [
        'ما اتبعت', 'didn\'t follow', 'skipped', 'تجاهلت', 'ignored',
        'ما اكلت', 'didn\'t eat', 'ما اتبعت الخطة', 'didn\'t follow plan',
    ]
    if any(keyword in lowered for keyword in skipped_keywords):
        return 'skipped'
    
    return None


def calculate_nutrition_progress_boost(adherence):
    """Calculate progress boost based on nutrition adherence"""
    if adherence == 'full':
        return random.uniform(1.0, 3.0)  # +1-3%
    elif adherence == 'partial':
        return random.uniform(0.5, 1.0)  # +0.5-1%
    return 0.0


def should_offer_adaptive_nutrition(user_message, emotion, last_workout_ts, current_time, state):
    """Determine if AI should offer adaptive nutrition plan"""
    if not user_message:
        return False
    
    lowered = user_message.lower()
    
    # Check if user explicitly asks for meal/nutrition plan
    nutrition_keywords = [
        'وجبات', 'meals', 'meal plan', 'nutrition', 'تغذية', 'طعام', 'food',
        'خطة وجبات', 'meal plan', 'برنامج غذائي', 'diet', 'سعرات', 'calories',
        'جوعان', 'hungry', 'تعبان', 'tired', 'مشغولة', 'busy',
        'ما عندي', "don't have", 'ما عندي مكونات', 'missing ingredients',
        'بديل', 'substitute', 'بديل ل', 'alternative'
    ]
    if any(keyword in lowered for keyword in nutrition_keywords):
        return True
    
    # Check if user mentions missing ingredients
    missing_ingredient_patterns = [
        r"ما عندي ([\u0600-\u06FF\s]+)",
        r"don't have ([a-z\s]+)",
        r"لا يوجد ([\u0600-\u06FF\s]+)",
        r"no ([a-z\s]+)",
        r"missing ([a-z\s]+)",
    ]
    for pattern in missing_ingredient_patterns:
        if re.search(pattern, lowered):
            return True
    
    # Check if user returns after workout inactivity (offer nutrition adjustment)
    if last_workout_ts:
        days_since_workout = (current_time - last_workout_ts).total_seconds() / (24 * 3600)
        if days_since_workout >= 1:
            # Only offer if workout reminder was sent recently (within last hour)
            last_prompt = state.get('last_workout_prompt_sent_at')
            if last_prompt:
                time_since_prompt = (current_time - last_prompt).total_seconds()
                if time_since_prompt < 3600:  # Within 1 hour
                    return True
    
    return False


def get_adaptive_nutrition_context(profile_data, metrics, state, last_workout_ts, current_time, language, user_message, emotion, calculate_progress_func):
    """Generate adaptive nutrition context based on inactivity level and user needs"""
    # Get user preferences
    preferences = state.get('preferences', {})
    food_dislikes = preferences.get('food_dislikes', [])
    allergies = preferences.get('allergies', [])
    favorite_foods = preferences.get('favorite_foods', [])
    breakfast_prefs = preferences.get('breakfast_preferences', [])
    lunch_prefs = preferences.get('lunch_preferences', [])
    
    # Check if user explicitly asked for nutrition/meal plan
    lowered = user_message.lower() if user_message else ""
    explicit_request = any(keyword in lowered for keyword in [
        'وجبات', 'meals', 'meal plan', 'nutrition', 'تغذية', 'طعام', 'food',
        'خطة وجبات', 'برنامج غذائي', 'diet', 'سعرات', 'calories'
    ])
    
    # Check for missing ingredients in user message
    missing_ingredients = []
    if user_message:
        ingredient_patterns = [
            r"ما عندي ([\u0600-\u06FF\s]+)",
            r"don't have ([a-z\s]+)",
            r"لا يوجد ([\u0600-\u06FF\s]+)",
            r"no ([a-z\s]+)",
            r"missing ([a-z\s]+)",
        ]
        for pattern in ingredient_patterns:
            match = re.search(pattern, lowered)
            if match:
                missing_ingredients.append(match.group(1).strip())
    
    # Build preference context
    avoid_list = []
    if food_dislikes:
        avoid_list.append(f"NEVER include these foods: {', '.join(food_dislikes)}")
    if allergies:
        avoid_list.append(f"NEVER include these allergens: {', '.join(allergies)}")
    
    preference_note = "\n".join(avoid_list) if avoid_list else "No food restrictions"
    
    # Build favorite/preferred foods list
    preferred_list = []
    if favorite_foods:
        preferred_list.append(f"Favorite foods: {', '.join(favorite_foods)}")
    if breakfast_prefs:
        preferred_list.append(f"Breakfast preferences: {', '.join(breakfast_prefs)}")
    if lunch_prefs:
        preferred_list.append(f"Lunch preferences: {', '.join(lunch_prefs)}")
    
    preferred_note = "\n".join(preferred_list) if preferred_list else "No specific food preferences"
    
    # Get progress
    progress = calculate_progress_func(profile_data)
    progress_note = f"Current progress: {progress}%" if progress is not None else "Progress: Not calculated"
    
    # Get activity level
    activity_level = profile_data.get('activity_level', '').lower()
    
    # Determine nutrition adaptation level based on workout inactivity
    days_since_workout = None
    nutrition_context = ""
    
    # If user explicitly requested nutrition plan, always provide it
    if explicit_request and not last_workout_ts:
        nutrition_context = (
            "User requested nutrition plan. Provide balanced meal plan based on their goal, "
            "activity level, and preferences. Keep it simple and achievable."
        )
    elif last_workout_ts:
        days_since_workout = (current_time - last_workout_ts).total_seconds() / (24 * 3600)
        
        if days_since_workout < 1:
            # User is consistent - adjust based on activity level and user requests
            if explicit_request or 'active' in activity_level or 'athlete' in activity_level:
                if 'active' in activity_level or 'athlete' in activity_level:
                    nutrition_context = (
                        "User is highly active and consistent. "
                        "Increase protein + healthy fats. Mild calorie deficit only if user asks. "
                        "Offer performance-boost meals."
                    )
                elif explicit_request:
                    nutrition_context = (
                        "User requested nutrition plan. Provide balanced meal plan based on their goal, "
                        "activity level, and preferences. Keep it simple and achievable."
                    )
            else:
                # Consistent but not highly active - no special adjustment unless explicitly requested
                nutrition_context = None
        elif 1 <= days_since_workout < 3:
            # Light adjustment (1-2 days)
            nutrition_context = (
                f"User inactive for {int(days_since_workout)} days (light inactivity). "
                "Slight nutrition adjustment: reduce calories by 5-10%, increase hydration reminders, lighter breakfast options. "
                "Example: 'بما إن يومين ما سويتي تمرين، قللت لك السعرات شوي عشان توازنين اليوم.'"
            )
        elif 3 <= days_since_workout < 7:
            # Medium adjustment (3-6 days)
            nutrition_context = (
                f"User inactive for {int(days_since_workout)} days (medium inactivity). "
                "Softer diet: simple meals, no strict calorie deficit, add snacks, no heavy recipes. "
                "Example: 'بما إن صار لك {days} أيام توقف، سويت لك خطة خفيفة ما تضغط عليك: وجبات بسيطة وسهلة بدون طبخ طويل.'"
            )
        elif 7 <= days_since_workout < 14:
            # Large adjustment (7-13 days)
            nutrition_context = (
                f"User inactive for {int(days_since_workout)} days (large inactivity). "
                "Reset-friendly nutrition: high protein but easy to prepare, no calorie tracking, focus on satiety + balanced meals. "
                "Example: 'تقريبًا أسبوع بدون نشاط، سويت لك خطة جديدة تركّز على البروتين والشبع بدون ما أحسب عليك سعرات.'"
            )
        elif days_since_workout >= 14:
            # Very long (14+ days)
            nutrition_context = (
                f"User inactive for {int(days_since_workout)} days (very long inactivity). "
                "Full reset: beginner-level meal plan, very simple foods, no restrictions, high flexibility. "
                "Example: 'سويت لك خطة بداية جديدة تناسب رجوعك… بدون حرمان، أشياء سهلة وسريعة.'"
            )
    
    # Check for missing ingredients - provide substitutions
    substitution_context = ""
    if missing_ingredients:
        substitution_context = (
            f"\n\nUSER MISSING INGREDIENTS: {', '.join(missing_ingredients)}\n"
            "Provide smart substitutions immediately. Common substitutions:\n"
            "- Eggs: يمكن استخدام التوفو أو البقوليات\n"
            "- Protein: دجاج/سمك/لحم/بقوليات/توفو\n"
            "- Carbs: رز/خبز/شوفان/بطاطا/بطاطا حلوة\n"
            "- Milk: حليب نباتي/لبن/ماء\n"
            "- Dates: تمر/عسل/فواكه\n"
            "- Bread: خبز أسمر/خبز عربي/رز\n"
            "Always provide alternatives in the same language as user message."
        )
    
    # Check user activity level for nutrition adjustments
    activity_level = profile_data.get('activity_level', '').lower()
    activity_note = ""
    if 'active' in activity_level or 'athlete' in activity_level:
        activity_note = (
            "User is highly active. Increase protein + healthy fats. "
            "Mild calorie deficit only if user asks. Offer performance-boost meals."
        )
    elif emotion == 'tired' or 'hungry' in user_message.lower() or 'جوعان' in user_message.lower():
        activity_note = (
            "User reports hunger or low energy. Increase carbs, add quick snacks (fruits, yogurt, nuts). "
            "Avoid low-carb days, increase breakfast calories."
        )
    
    # Build full context - return if there's substitution context or nutrition context
    if not nutrition_context and not substitution_context:
        return None
    
    full_context = (
        f"ADAPTIVE NUTRITION PLAN NEEDED:\n"
    )
    
    if nutrition_context:
        full_context += f"{nutrition_context}\n\n"
    
    if substitution_context:
        full_context += f"{substitution_context}\n\n"
    
    full_context += (
        f"User Profile:\n"
        f"- Age: {profile_data.get('age', 'N/A')}\n"
        f"- Height: {profile_data.get('height_cm', 'N/A')} cm\n"
        f"- Weight: {profile_data.get('weight_kg', 'N/A')} kg\n"
        f"- Goal: {profile_data.get('goal', 'N/A')}\n"
        f"- Activity Level: {profile_data.get('activity_level', 'N/A')}\n"
        f"- {progress_note}\n\n"
        f"CRITICAL - Foods to NEVER Include:\n"
        f"{preference_note}\n\n"
        f"Preferred Foods (use when possible):\n"
        f"{preferred_note}\n\n"
        f"Metrics:\n"
        f"- BMI: {metrics.get('bmi', 'N/A')} ({metrics.get('bmi_category', 'N/A')})\n"
        f"- BMR: {metrics.get('bmr', 'N/A')} kcal\n"
        f"- TDEE: {metrics.get('tdee', 'N/A')} kcal\n"
        f"- Safe weekly progress: {metrics.get('safe_weekly_rate', 'N/A')} kg\n\n"
    )
    
    if activity_note:
        full_context += f"Activity-based adjustment: {activity_note}\n\n"
    
    full_context += (
        f"Generate a short, simple adaptive nutrition plan that respects all preferences and limitations. "
        f"Provide ingredient substitutions if user is missing items. "
        f"Keep the response natural and conversational. If user writes in Arabic, respond in Saudi dialect. "
        f"If user writes in English, respond in clean English. "
        f"Include Saudi & Gulf-friendly food options when appropriate."
    )
    
    return full_context


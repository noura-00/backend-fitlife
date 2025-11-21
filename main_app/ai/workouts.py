import random
from datetime import timedelta

from ..models import Post
from .prompts import (
    EXERCISE_IMAGES,
    GYM_EQUIPMENT,
    GYM_EQUIPMENT_VIDEOS,
    WORKOUT_MESSAGES_14_PLUS_DAYS,
    WORKOUT_MESSAGES_14_PLUS_DAYS_EN,
    WORKOUT_MESSAGES_2_3_DAYS,
    WORKOUT_MESSAGES_2_3_DAYS_EN,
    WORKOUT_MESSAGES_4_6_DAYS,
    WORKOUT_MESSAGES_4_6_DAYS_EN,
    WORKOUT_MESSAGES_7_13_DAYS,
    WORKOUT_MESSAGES_7_13_DAYS_EN,
)


def detect_workout_completion(user_message):
    """Detect if user completed a workout"""
    if not user_message:
        return False
    
    lowered = user_message.lower()
    completion_keywords = [
        'سويت تمرين', 'completed workout', 'finished workout', 'done workout',
        'خلصت تمرين', 'سويت التمرين', 'workout done', 'تم التمرين',
        'سويت تمارين', 'did workout', 'finished', 'خلصت',
        'سويت الرياضة', 'exercised', 'worked out',
    ]
    
    return any(keyword in lowered for keyword in completion_keywords)


def calculate_workout_progress_boost(state, current_time):
    """Calculate progress boost based on workout frequency"""
    workout_count = state.get('workout_count_this_week', 0)
    last_reset = state.get('last_workout_count_reset')
    
    # Reset weekly count if needed
    if last_reset is None or (current_time - last_reset).total_seconds() / (24 * 3600) >= 7:
        state['workout_count_this_week'] = 0
        state['last_workout_count_reset'] = current_time
        workout_count = 0
    
    # Calculate boost based on frequency
    if workout_count >= 3:
        # 3+ workouts/week = +5% boost
        return 5.0
    elif workout_count >= 2:
        # 2 workouts = +4% boost
        return 4.0
    elif workout_count >= 1:
        # 1 workout = +3% boost
        return 3.0
    
    return 0.0


def should_suggest_image(user_message):
    """Determine if AI should suggest an exercise image"""
    if not user_message:
        return False
    
    lowered = user_message.lower()
    
    image_keywords = [
        'صورة', 'image', 'شكل', 'form', 'كيف', 'how', 'مثال', 'example',
        'أعطني صورة', 'show me', 'أشوف', 'see', 'demonstrate', 'شرح',
    ]
    
    exercise_keywords = [
        'squat', 'lunge', 'plank', 'bridge', 'pushup', 'deadlift',
        'قرفصاء', 'لانج', 'بلانك', 'جسر', 'ضغط', 'رفع',
    ]
    
    return any(img_kw in lowered for img_kw in image_keywords) and \
           any(ex_kw in lowered for ex_kw in exercise_keywords)


def get_exercise_image(user_message, state):
    """Get exercise image based on user request"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    used_images = state.get('used_images', [])
    
    # Map keywords to exercise types
    exercise_map = {
        'squat': 'squat',
        'قرفصاء': 'squat',
        'lunge': 'lunge',
        'لانج': 'lunge',
        'plank': 'plank',
        'بلانك': 'plank',
        'bridge': 'bridge',
        'جسر': 'bridge',
        'pushup': 'pushup',
        'ضغط': 'pushup',
        'deadlift': 'deadlift',
        'رفع': 'deadlift',
    }
    
    # Find matching exercise
    for keyword, exercise_key in exercise_map.items():
        if keyword in lowered:
            if exercise_key in EXERCISE_IMAGES:
                image_info = EXERCISE_IMAGES[exercise_key]
                # Mark as used
                if exercise_key not in used_images:
                    used_images.append(exercise_key)
                    state['used_images'] = used_images
                return image_info
    
    return None


def get_last_workout_timestamp(user):
    """Fetch the latest workout-related entry for the user"""
    last_workout_post = Post.objects.filter(
        user=user,
        workout_plan__isnull=False,
    ).order_by('-created_at').first()
    if last_workout_post:
        return last_workout_post.created_at
    return None


def check_workout_inactivity_message(state, profile_data, language, current_time, last_workout_ts):
    """Determine if a workout inactivity message should be sent"""
    if not last_workout_ts:
        # No workout logged yet -> treat as new user (greeting handles this)
        return None

    days_since_workout = (current_time - last_workout_ts).total_seconds() / (24 * 3600)
    if days_since_workout < 2:
        return None

    if 2 <= days_since_workout < 4:
        category = '2_3'
    elif 4 <= days_since_workout < 7:
        category = '4_6'
    elif 7 <= days_since_workout < 14:
        category = '7_13'
    else:
        category = '14_plus'

    # Only send when first message after returning or when entering a new inactivity bracket
    last_category = state.get('last_workout_prompt_category')
    if last_category == category and state.get('last_workout_prompt_sent_at'):
        return None

    message = get_workout_inactivity_message(state, profile_data, language, category)
    if message:
        state['last_workout_prompt_category'] = category
        state['last_workout_prompt_sent_at'] = current_time
    return message


def get_workout_inactivity_message(state, profile_data, language, category):
    """Fetch a non-repeating workout inactivity message"""
    name = profile_data.get('name', profile_data.get('username', ''))
    lang_key = 'english' if language == 'english' else 'arabic'

    pools = {
        ('2_3', 'arabic'): WORKOUT_MESSAGES_2_3_DAYS,
        ('2_3', 'english'): WORKOUT_MESSAGES_2_3_DAYS_EN,
        ('4_6', 'arabic'): WORKOUT_MESSAGES_4_6_DAYS,
        ('4_6', 'english'): WORKOUT_MESSAGES_4_6_DAYS_EN,
        ('7_13', 'arabic'): WORKOUT_MESSAGES_7_13_DAYS,
        ('7_13', 'english'): WORKOUT_MESSAGES_7_13_DAYS_EN,
        ('14_plus', 'arabic'): WORKOUT_MESSAGES_14_PLUS_DAYS,
        ('14_plus', 'english'): WORKOUT_MESSAGES_14_PLUS_DAYS_EN,
    }

    pool = pools.get((category, lang_key))
    if not pool:
        return None

    used_messages = state.get('used_workout_messages', {})
    key = f"{category}_{lang_key}"
    used_in_category = used_messages.get(key, [])
    available = [msg for msg in pool if msg not in used_in_category]

    if not available:
        available = pool
        used_in_category = []

    message = random.choice(available).format(name=name)
    used_in_category.append(message)
    used_messages[key] = used_in_category
    state['used_workout_messages'] = used_messages
    return message


def should_offer_adaptive_plan(user_message, emotion, last_workout_ts, current_time, state):
    """Determine if AI should offer an adaptive plan"""
    if not user_message:
        return False
    
    lowered = user_message.lower()
    
    # Check if user explicitly asks for plan
    plan_keywords = [
        'خطة', 'plan', 'برنامج', 'program', 'تمرين جديد', 'new workout',
        'نسوي خطة', 'create plan', 'نبدأ خطة', 'start plan',
        'تبين خطة', 'want plan', 'أريد خطة', 'i want plan'
    ]
    if any(keyword in lowered for keyword in plan_keywords):
        return True
    
    # Check if user feels tired, busy, or can't complete workout
    tired_busy_keywords = [
        'تعبان', 'tired', 'مشغولة', 'busy', 'ما أقدر', "can't", 'صعب',
        'difficult', 'ما عندي وقت', 'no time', 'مش قادرة', "can't do",
        'أخف', 'lighter', 'أسهل', 'easier', 'ما أقدر أكمل', "can't finish"
    ]
    if any(keyword in lowered for keyword in tired_busy_keywords):
        return True
    
    # Check if user returns after workout inactivity (offer adaptive plan within 1 hour of workout reminder)
    if last_workout_ts:
        days_since_workout = (current_time - last_workout_ts).total_seconds() / (24 * 3600)
        if days_since_workout >= 2:
            # Only offer if workout reminder was sent recently (within last hour)
            last_prompt = state.get('last_workout_prompt_sent_at')
            if last_prompt:
                time_since_prompt = (current_time - last_prompt).total_seconds()
                if time_since_prompt < 3600:  # Within 1 hour
                    return True
    
    return False


def get_adaptive_plan_context(profile_data, metrics, state, last_workout_ts, current_time, language, calculate_progress_func):
    """Generate adaptive plan context based on inactivity level and user needs"""
    if not last_workout_ts:
        return None
    
    days_since_workout = (current_time - last_workout_ts).total_seconds() / (24 * 3600)
    
    # Get user preferences
    preferences = state.get('preferences', {})
    food_dislikes = preferences.get('food_dislikes', [])
    allergies = preferences.get('allergies', [])
    workout_dislikes = preferences.get('workout_dislikes', [])
    injuries = preferences.get('injuries', [])
    
    # Build preference context
    avoid_list = []
    if food_dislikes:
        avoid_list.append(f"Food dislikes: {', '.join(food_dislikes)}")
    if allergies:
        avoid_list.append(f"Allergies: {', '.join(allergies)}")
    if workout_dislikes:
        avoid_list.append(f"Avoid exercises: {', '.join(workout_dislikes)}")
    if injuries:
        avoid_list.append(f"Injuries/limitations: {', '.join(injuries)}")
    
    preference_note = "\n".join(avoid_list) if avoid_list else "No specific restrictions"
    
    # Get progress
    progress = calculate_progress_func(profile_data)
    progress_note = f"Current progress: {progress}%" if progress is not None else "Progress: Not calculated"
    
    # Check if user is consistent (worked out within last 24 hours)
    is_consistent = days_since_workout < 1
    
    # Determine adaptation level
    if is_consistent:
        # User is consistent - only adjust if they explicitly ask for progress
        plan_context = (
            "User is consistent with workouts (last workout within 24 hours). "
            "Only suggest intensity increase (5-10%) if user explicitly requests progress or asks for harder workouts. "
            "Otherwise, maintain current plan and provide encouragement."
        )
    elif 2 <= days_since_workout < 4:
        # Light adjustment (خفيفة)
        plan_context = (
            f"User has been inactive for {int(days_since_workout)} days (light inactivity). "
            "Offer a slightly lighter workout: reduce duration by 10-15%, suggest lighter warm-ups. "
            "Keep it encouraging and simple. Example: 'واضح إن عندك انشغال هاليومين… نسوي اليوم تمرين أخف 20 دقيقة بدل 30؟'"
        )
    elif 4 <= days_since_workout < 7:
        # Medium adjustment (متوسطة)
        plan_context = (
            f"User has been inactive for {int(days_since_workout)} days (medium inactivity). "
            "Create a 'Restart Plan - Level 1': 15-20 minute sessions, more walking/low impact, no high-intensity. "
            "Example: 'بما إن صار لك {days} أيام، نسوي خطة خفيفة 15 دقيقة بس… المهم نرجع نتعود.'"
        )
    elif 7 <= days_since_workout < 14:
        # Large adjustment (كبيرة)
        plan_context = (
            f"User has been inactive for {int(days_since_workout)} days (large inactivity). "
            "Rebuild with new easing plan: replace intense workouts with low intensity, reduce weekly workouts by 1 day, add recovery/stretching. "
            "Example: 'أسبوع تقريبًا بدون تمرين… صممت لك خطة جديدة خفيفة ترجعك بدون ضغط.'"
        )
    elif days_since_workout >= 14:
        # Very long (طويل)
        plan_context = (
            f"User has been inactive for {int(days_since_workout)} days (very long inactivity). "
            "Create a 'Fresh Start Plan': very easy beginner pace, no jumping/no heavy workouts, recalculate calories and expected progress. "
            "Example: '{name}… بما إن صار لك أسبوعين، سويت لك خطة بداية جديدة مناسبة جداً لك.'"
        )
    else:
        return None
    
    # Build full context
    full_context = (
        f"ADAPTIVE PLAN NEEDED:\n"
        f"{plan_context}\n\n"
        f"User Profile:\n"
        f"- Age: {profile_data.get('age', 'N/A')}\n"
        f"- Height: {profile_data.get('height_cm', 'N/A')} cm\n"
        f"- Weight: {profile_data.get('weight_kg', 'N/A')} kg\n"
        f"- Goal: {profile_data.get('goal', 'N/A')}\n"
        f"- {progress_note}\n\n"
        f"IMPORTANT - User Preferences to Respect:\n"
        f"{preference_note}\n\n"
        f"Metrics:\n"
        f"- BMI: {metrics.get('bmi', 'N/A')} ({metrics.get('bmi_category', 'N/A')})\n"
        f"- BMR: {metrics.get('bmr', 'N/A')} kcal\n"
        f"- TDEE: {metrics.get('tdee', 'N/A')} kcal\n"
        f"- Safe weekly progress: {metrics.get('safe_weekly_rate', 'N/A')} kg\n\n"
        f"Generate a short, simple adaptive plan that respects all preferences and limitations. "
        f"Keep the response natural and conversational. If user writes in Arabic, respond in Saudi dialect. "
        f"If user writes in English, respond in clean English."
    )
    
    return full_context


def detect_gym_equipment_request(user_message, request_data=None):
    """Detect if user is asking about gym equipment or uploaded an image"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Check for equipment mentions
    equipment_keywords = [
        'leg press', 'chest press', 'cable machine', 'lat pulldown',
        'treadmill', 'rowing machine', 'smith machine', 'shoulder press',
        'hip abductor', 'stair climber', 'barbell', 'dumbbell',
        'جهاز', 'machine', 'equipment', 'gym equipment',
        'ضغط الأرجل', 'ضغط الصدر', 'كيبل', 'مشي', 'تجديف',
    ]
    if any(keyword in lowered for keyword in equipment_keywords):
        return True
    
    # Check for image upload in request data
    if request_data:
        if request_data.get('image') or request_data.get('equipment_image'):
            return True
    
    return False


def recognize_equipment_from_text(user_message):
    """Recognize equipment type from user message"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Map keywords to equipment
    equipment_map = {
        'leg press': 'leg_press',
        'ضغط الأرجل': 'leg_press',
        'chest press': 'chest_press',
        'ضغط الصدر': 'chest_press',
        'cable': 'cable_machine',
        'كيبل': 'cable_machine',
        'lat pulldown': 'lat_pulldown',
        'سحب': 'lat_pulldown',
        'treadmill': 'treadmill',
        'مشي': 'treadmill',
        'rowing': 'rowing_machine',
        'تجديف': 'rowing_machine',
        'smith': 'smith_machine',
        'shoulder press': 'shoulder_press',
        'ضغط الكتف': 'shoulder_press',
        'hip abductor': 'hip_abductor',
        'stair climber': 'stair_climber',
        'صعود الدرج': 'stair_climber',
        'barbell': 'barbell',
        'البار': 'barbell',
        'dumbbell': 'dumbbell',
        'أثقال': 'dumbbell',
    }
    
    for keyword, equipment_key in equipment_map.items():
        if keyword in lowered:
            return equipment_key
    
    return None


def build_equipment_instructions_context(equipment_key, language):
    """Build context for equipment usage instructions"""
    if equipment_key not in GYM_EQUIPMENT:
        return None
    
    equipment = GYM_EQUIPMENT[equipment_key]
    instructions = equipment['instructions']
    name = equipment.get('name_ar' if language != 'english' else 'name', equipment['name'])
    
    context = f"GYM EQUIPMENT RECOGNITION - {equipment['name'].upper()}:\n\n"
    context += f"User is asking about: {name}\n\n"
    context += "Provide step-by-step usage instructions:\n"
    
    if 'seat_adjustment' in instructions:
        context += f"- Seat adjustment: {instructions['seat_adjustment']}\n"
    if 'handle_height' in instructions:
        context += f"- Handle height: {instructions['handle_height']}\n"
    if 'foot_placement' in instructions:
        context += f"- Foot placement: {instructions['foot_placement']}\n"
    if 'grip' in instructions:
        context += f"- Grip: {instructions['grip']}\n"
    if 'range_of_motion' in instructions:
        context += f"- Range of motion: {instructions['range_of_motion']}\n"
    if 'breathing' in instructions:
        context += f"- Breathing pattern: {instructions['breathing']}\n"
    if 'safety' in instructions:
        context += f"- Safety notes: {instructions['safety']}\n"
    if 'common_mistakes' in instructions:
        context += f"- Common mistakes: {instructions['common_mistakes']}\n"
    if 'beginner_weight' in instructions:
        context += f"- Recommended weight for beginners: {instructions['beginner_weight']}\n"
    
    context += "\nInstructions must be short, visual, and easy to follow."
    context += "\nIf equipment is busy, suggest alternatives."
    
    return context


def get_equipment_video_recommendation(state, language):
    """Get non-repeating equipment video recommendation"""
    used_videos = state.get('gym_equipment', {}).get('used_equipment_videos', [])
    
    available = [v for v in GYM_EQUIPMENT_VIDEOS if v['trainer'] not in used_videos]
    if not available:
        available = GYM_EQUIPMENT_VIDEOS
        used_videos = []
    
    selected = random.choice(available)
    used_videos.append(selected['trainer'])
    if 'gym_equipment' not in state:
        state['gym_equipment'] = {}
    state['gym_equipment']['used_equipment_videos'] = used_videos
    
    return selected


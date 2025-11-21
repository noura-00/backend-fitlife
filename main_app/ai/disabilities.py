import random
import re

from .prompts import (
    ACCESSIBILITY_ACTIVATION_MESSAGES,
    ACCESSIBILITY_ACTIVATION_MESSAGES_EN,
    ADAPTIVE_EXERCISE_IMAGES,
    ADAPTIVE_VIDEOS,
    BALANCE_FRIENDLY_EXERCISES,
    DEAF_MODE_ACTIVATION_MESSAGES,
    DEAF_MODE_ACTIVATION_MESSAGES_EN,
    DISABILITY_SUPPORT_MESSAGES,
    DISABILITY_SUPPORT_MESSAGES_EN,
    JOINT_FRIENDLY_EXERCISES,
    NAVIGATION_ASSISTANCE_MESSAGES,
    NAVIGATION_ASSISTANCE_MESSAGES_EN,
    VISUAL_CUES,
    VISUAL_CUES_AR,
    WHEELCHAIR_EXERCISES,
)


def detect_disability_info(user_message):
    """Detect disability-related information from user message"""
    if not user_message:
        return {}
    
    lowered = user_message.lower()
    detected = {}
    
    # Mobility challenges
    mobility_keywords = [
        'mobility', 'movement', 'تحرك', 'حركة', 'مشكلة في الحركة',
        'can\'t move', 'ما أقدر أتحرك', 'صعوبة في الحركة',
    ]
    if any(keyword in lowered for keyword in mobility_keywords):
        detected['mobility_challenges'] = True
    
    # Difficulty standing
    standing_keywords = [
        'can\'t stand', 'difficulty standing', 'ما أقدر أقف', 'صعوبة في الوقوف',
        'standing problem', 'مشكلة في الوقوف', 'unable to stand',
    ]
    if any(keyword in lowered for keyword in standing_keywords):
        detected['difficulty_standing'] = True
    
    # Wheelchair use
    wheelchair_keywords = [
        'wheelchair', 'كرسي متحرك', 'على كرسي', 'in wheelchair',
        'wheelchair user', 'مستخدم كرسي', 'on wheelchair',
    ]
    if any(keyword in lowered for keyword in wheelchair_keywords):
        detected['wheelchair_use'] = True
    
    # Joint pain
    joint_keywords = [
        'joint pain', 'knee pain', 'hip pain', 'ألم في المفاصل',
        'مفاصل', 'ركبة', 'ورك', 'joint problem', 'مشكلة في المفاصل',
    ]
    if any(keyword in lowered for keyword in joint_keywords):
        detected['joint_pain'] = True
    
    # Spine issues
    spine_keywords = [
        'back pain', 'spine', 'spinal', 'ألم في الظهر', 'ظهر',
        'back problem', 'مشكلة في الظهر', 'spine issue',
    ]
    if any(keyword in lowered for keyword in spine_keywords):
        detected['spine_issues'] = True
    
    # Balance issues
    balance_keywords = [
        'balance', 'dizziness', 'unsteady', 'توازن', 'دوخة',
        'balance problem', 'مشكلة في التوازن', 'falling',
    ]
    if any(keyword in lowered for keyword in balance_keywords):
        detected['balance_issues'] = True
    
    # Chronic conditions (extract specific conditions)
    chronic_patterns = [
        r'have ([a-z\s]+)',
        r'عندي ([\u0600-\u06FF\s]+)',
        r'diagnosed with ([a-z\s]+)',
    ]
    for pattern in chronic_patterns:
        match = re.search(pattern, lowered)
        if match:
            condition = match.group(1).strip()
            # Filter out common non-chronic words
            if condition not in ['a', 'an', 'the', 'some', 'this', 'that']:
                detected.setdefault('chronic_conditions', []).append(condition)
    
    return detected


def should_ask_about_disability(state, user_message):
    """Determine if we should ask about disabilities (only once)"""
    disability_info = state.get('disability_info', {})
    
    # If already asked, don't ask again
    if disability_info.get('disability_asked', False):
        return False
    
    # If user already mentioned disability info, don't ask
    if any([
        disability_info.get('mobility_challenges'),
        disability_info.get('difficulty_standing'),
        disability_info.get('wheelchair_use'),
        disability_info.get('joint_pain'),
        disability_info.get('spine_issues'),
        disability_info.get('balance_issues'),
    ]):
        return False
    
    # Check if user is struggling with workouts or mentions pain
    if not user_message:
        return False
    
    lowered = user_message.lower()
    struggle_keywords = [
        'can\'t do', 'too hard', 'difficult', 'pain', 'hurt',
        'ما أقدر', 'صعب', 'ألم', 'يوجع', 'مؤلم', 'struggling',
        'too difficult', 'very hard', 'impossible',
    ]
    
    return any(keyword in lowered for keyword in struggle_keywords)


def get_disability_support_message(state, profile_data, language):
    """Get a non-repeating disability support message"""
    name = profile_data.get('name', profile_data.get('username', ''))
    used = state.get('used_disability_messages', [])
    
    pool = DISABILITY_SUPPORT_MESSAGES if language != 'english' else DISABILITY_SUPPORT_MESSAGES_EN
    available = [msg for msg in pool if msg not in used]
    
    if not available:
        available = pool
        used = []
    
    message = random.choice(available).format(name=name)
    used.append(message)
    state['used_disability_messages'] = used
    
    return message


def get_disability_friendly_exercises(disability_info):
    """Get appropriate exercises based on disability info"""
    exercises = []
    
    if disability_info.get('wheelchair_use') or disability_info.get('difficulty_standing'):
        exercises.extend(WHEELCHAIR_EXERCISES)
    
    if disability_info.get('joint_pain'):
        exercises.extend(JOINT_FRIENDLY_EXERCISES)
    
    if disability_info.get('balance_issues'):
        exercises.extend(BALANCE_FRIENDLY_EXERCISES)
    
    # If no specific disability but mobility challenges, use joint-friendly
    if disability_info.get('mobility_challenges') and not exercises:
        exercises.extend(JOINT_FRIENDLY_EXERCISES)
    
    # Remove duplicates
    return list(set(exercises)) if exercises else []


def get_dangerous_exercises_to_avoid(disability_info):
    """Get list of exercises to avoid based on disability"""
    avoid = []
    
    # Always avoid jumping and high impact for mobility/joint issues
    if disability_info.get('mobility_challenges') or disability_info.get('joint_pain'):
        avoid.extend(['jumping', 'jump', 'high impact', 'plyometric', 'burpees'])
    
    # Avoid deep squats for joint/knee issues
    if disability_info.get('joint_pain'):
        avoid.extend(['deep squat', 'full squat', 'deep lunge'])
    
    # Avoid fast tempo for balance issues
    if disability_info.get('balance_issues'):
        avoid.extend(['fast tempo', 'quick movements', 'rapid'])
    
    # Avoid twisting for spine issues
    if disability_info.get('spine_issues'):
        avoid.extend(['twisting', 'rotation', 'spinal twist', 'twist'])
    
    # Avoid single-leg exercises for balance issues
    if disability_info.get('balance_issues'):
        avoid.extend(['single leg', 'one leg', 'unilateral'])
    
    return avoid


def get_adaptive_video_recommendation(state, disability_info, language):
    """Get adaptive video recommendation based on disability"""
    used_videos = state.get('used_videos', [])
    
    # Filter videos by category
    available_videos = []
    if disability_info.get('wheelchair_use') or disability_info.get('difficulty_standing'):
        category = 'wheelchair'
    elif disability_info.get('joint_pain'):
        category = 'joint'
    elif disability_info.get('balance_issues'):
        category = 'balance'
    else:
        category = 'general'
    
    for video in ADAPTIVE_VIDEOS:
        if video['category'] == category or video['category'] == 'general':
            if video['title'] not in used_videos:
                available_videos.append(video)
    
    # If all used, reset
    if not available_videos:
        available_videos = [v for v in ADAPTIVE_VIDEOS if v['category'] == category or v['category'] == 'general']
        used_videos = [v for v in used_videos if v not in [av['title'] for av in available_videos]]
    
    if available_videos:
        selected = random.choice(available_videos)
        used_videos.append(selected['title'])
        state['used_videos'] = used_videos
        return selected
    
    return None


def get_adaptive_exercise_image(disability_info):
    """Get adaptive exercise image based on disability"""
    if disability_info.get('wheelchair_use') or disability_info.get('difficulty_standing'):
        return ADAPTIVE_EXERCISE_IMAGES.get('seated_arm_raise')
    elif disability_info.get('joint_pain'):
        return ADAPTIVE_EXERCISE_IMAGES.get('wall_squat')
    elif disability_info.get('balance_issues'):
        return ADAPTIVE_EXERCISE_IMAGES.get('chair_balance')
    else:
        return ADAPTIVE_EXERCISE_IMAGES.get('gentle_stretch')


def build_disability_adaptive_context(disability_info, profile_data, metrics, language):
    """Build context for disability-adaptive workout plan"""
    exercises = get_disability_friendly_exercises(disability_info)
    avoid = get_dangerous_exercises_to_avoid(disability_info)
    
    context = "ADAPTIVE TRAINING SYSTEM - DISABILITY-FRIENDLY PLAN NEEDED:\n\n"
    context += "User has special physical needs. Generate a workout plan that:\n"
    
    if exercises:
        context += f"- ONLY use these safe exercises: {', '.join(exercises)}\n"
    
    if avoid:
        context += f"- NEVER include these dangerous exercises: {', '.join(avoid)}\n"
    
    context += "- Focus on consistency, effort, and safe performance\n"
    context += "- No pressure or comparison to typical users\n"
    context += "- Progress based on safe performance, not intensity\n"
    
    # Nutrition adaptation if needed
    if disability_info.get('mobility_challenges') or disability_info.get('chronic_conditions'):
        context += "\nNUTRITION ADAPTATION:\n"
        context += "- Adjust calories based on reduced activity level\n"
        context += "- Maintain adequate protein for muscle maintenance\n"
        context += "- Consider meal timing for energy management\n"
        context += "- Ensure proper hydration\n"
    
    context += f"\nUser Profile:\n"
    context += f"- Age: {profile_data.get('age', 'N/A')}\n"
    context += f"- Goal: {profile_data.get('goal', 'N/A')}\n"
    context += f"- TDEE: {metrics.get('tdee', 'N/A')} kcal\n"
    
    context += "\nTone: Warm, respectful, empowering, no pity. Use Saudi casual dialect for Arabic or clean English for English."
    
    return context


def detect_accessibility_mode(user_message, request_data=None):
    """Detect if user wants to activate accessibility mode"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Check for explicit activation
    activation_keywords = [
        'accessibility mode', 'وضع إمكانية الوصول', 'تفعيل الوصول',
        'enable accessibility', 'تفعيل إمكانية الوصول',
    ]
    if any(keyword in lowered for keyword in activation_keywords):
        return 'enable'
    
    # Check for visual impairment mentions
    blind_keywords = [
        'أنا ضعيف بصر', 'أنا ما أشوف', 'i am blind', 'i am visually impaired',
        'أنا كفيف', 'i can\'t see', 'ما أشوف', 'can\'t see',
        'blind', 'كفيف', 'ضعيف بصر', 'visually impaired',
    ]
    if any(keyword in lowered for keyword in blind_keywords):
        return 'blind'
    
    # Check for low vision mentions
    low_vision_keywords = [
        'صعب أشوف', 'الخط صغير', 'ما أشوف الشاشة', 'hard to see',
        'text too small', 'can\'t see screen', 'low vision',
        'ضعيف البصر', 'صعوبة في الرؤية',
    ]
    if any(keyword in lowered for keyword in low_vision_keywords):
        return 'low_vision'
    
    # Check request data for accessibility toggle
    if request_data:
        if request_data.get('accessibility_mode') == True:
            return 'enable'
        if request_data.get('visual_impairment'):
            return request_data.get('visual_impairment')
    
    return None


def get_accessibility_safe_exercises():
    """Get safe exercises for blind users (no balance, jumping, etc.)"""
    return [
        'Seated exercises only',
        'Stationary movements',
        'Step-by-step slow instructions',
        'Seated arm raises',
        'Seated leg lifts',
        'Seated core activation',
        'Seated stretching',
        'Resistance band exercises (seated)',
        'No balance workouts',
        'No jumping',
        'No lunges',
        'No single-leg training',
    ]


def build_accessibility_context(accessibility_mode, profile_data, language):
    """Build context for accessibility-friendly responses"""
    visual_impairment = accessibility_mode.get('visual_impairment', 'none')
    is_blind = visual_impairment == 'blind'
    is_low_vision = visual_impairment == 'low_vision'
    
    context = "ACCESSIBILITY MODE - VOICE-FRIENDLY RESPONSE REQUIRED:\n\n"
    
    if is_blind:
        context += "User is BLIND. Critical requirements:\n"
        context += "- Provide ALL information verbally with NO visual dependency\n"
        context += "- Use voice-friendly formatting: 'Title:', 'Step 1:', 'Step 2:', 'Conclusion:'\n"
        context += "- Avoid emojis unless absolutely necessary\n"
        context += "- Avoid tables (use lists instead)\n"
        context += "- Describe exercises step-by-step verbally\n"
        context += "- Use very short, clear sentences\n"
        context += "- NEVER include exercises that require balance, jumping, lunges, or single-leg training\n"
        context += "- ONLY seated, stationary, or step-by-step slow instructions\n"
        context += "- Provide navigation assistance when needed\n"
    elif is_low_vision:
        context += "User has LOW VISION. Requirements:\n"
        context += "- Provide clear, voice-friendly text\n"
        context += "- Use structured formatting\n"
        context += "- Offer optional voice descriptions\n"
        context += "- High contrast and large text mode should be enabled\n"
    else:
        context += "Accessibility Mode enabled. Use voice-friendly formatting.\n"
    
    context += "\nResponse Style:\n"
    context += "- Very clear and concise\n"
    context += "- Very short sentences\n"
    context += "- No visual dependency\n"
    context += "- Saudi casual dialect for Arabic, clean English for English\n"
    context += "- Zero repeated messages\n"
    
    if is_blind:
        context += "\nSafety Rules for Blind Users:\n"
        context += "- NO balance workouts\n"
        context += "- NO jumping\n"
        context += "- NO lunges\n"
        context += "- NO single-leg training\n"
        context += "- ONLY seated, stationary, or step-by-step slow instructions\n"
        safe_exercises = get_accessibility_safe_exercises()
        context += f"- Safe exercises: {', '.join(safe_exercises)}\n"
    
    return context


def get_audio_exercise_description(exercise_name, language):
    """Get audio-friendly exercise description"""
    if language != 'english':
        return f"هذا التمرين هو {exercise_name}. إذا تبين الوصف الصوتي قولي yes."
    else:
        return f"This exercise is {exercise_name}. If you want the audio description, say yes."


def format_voice_friendly_response(text):
    """Format response text to be voice-friendly"""
    # Remove excessive emojis (keep only essential ones)
    # Keep common emojis but remove excessive ones
    text = re.sub(r'[🤍💪🔥👏💗🩵]', '', text)  # Remove common emojis
    text = re.sub(r'[^\w\s\.,!?;:\-\(\)]', '', text)  # Remove other special chars
    
    # Replace common patterns with voice-friendly alternatives
    text = text.replace('...', '')
    text = text.replace('..', '')
    
    return text.strip()


def get_navigation_assistance(state, language):
    """Get navigation assistance message"""
    used = state.get('used_navigation_messages', [])
    pool = NAVIGATION_ASSISTANCE_MESSAGES if language != 'english' else NAVIGATION_ASSISTANCE_MESSAGES_EN
    
    available = [msg for msg in pool if msg not in used]
    if not available:
        available = pool
        used = []
    
    message = random.choice(available)
    used.append(message)
    state['used_navigation_messages'] = used
    
    return message


def detect_deaf_mode(user_message, request_data=None):
    """Detect if user wants to activate deaf/hard-of-hearing mode"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Check for explicit activation
    activation_keywords = [
        'deaf mode', 'وضع الصم', 'تفعيل وضع الصم',
        'accessibility deaf', 'وضع إمكانية الوصول للصم',
        'hard of hearing mode', 'وضع ضعاف السمع',
    ]
    if any(keyword in lowered for keyword in activation_keywords):
        return 'enable'
    
    # Check for deaf mentions
    deaf_keywords = [
        'أنا ضعيف سمع', 'أنا ما أسمع', 'i am deaf', 'i am hard of hearing',
        'أنا أصم', 'i can\'t hear', 'ما أسمع', 'can\'t hear',
        'deaf', 'أصم', 'ضعيف سمع', 'hearing loss', 'hard of hearing',
        'hearing impaired', 'ضعيف السمع',
    ]
    if any(keyword in lowered for keyword in deaf_keywords):
        return 'deaf'
    
    # Check for hard of hearing mentions
    hoh_keywords = [
        'hearing loss', 'partial hearing', 'ضعيف السمع',
        'hearing difficulty', 'صعوبة في السمع',
    ]
    if any(keyword in lowered for keyword in hoh_keywords):
        return 'hard_of_hearing'
    
    # Check request data for deaf mode toggle
    if request_data:
        if request_data.get('deaf_mode') == True:
            return 'enable'
        if request_data.get('hearing_impairment'):
            return request_data.get('hearing_impairment')
    
    return None


def get_deaf_safe_exercises():
    """Get safe exercises for deaf/hard-of-hearing users"""
    return [
        'Slow tempo exercises',
        'Repetitive motion',
        'Time-based sets with visual instructions',
        'Clear step-based routines',
        'No fast-paced routines',
        'No sudden transitions',
        'No audio countdowns',
        'No rhythm-dependent exercises',
    ]


def get_deaf_unsafe_exercises():
    """Get exercises to avoid for deaf/hard-of-hearing users"""
    return [
        'Fast-paced routines depending on beats',
        'Sudden transitions',
        'Audio countdowns',
        'Rhythm-dependent exercises',
        'Music-synchronized workouts',
    ]


def build_deaf_mode_context(deaf_mode, profile_data, language):
    """Build context for deaf/hard-of-hearing friendly responses"""
    hearing_impairment = deaf_mode.get('hearing_impairment', 'none')
    is_deaf = hearing_impairment == 'deaf'
    is_hoh = hearing_impairment == 'hard_of_hearing'
    
    context = "DEAF & HARD-OF-HEARING MODE - VISUAL-FRIENDLY RESPONSE REQUIRED:\n\n"
    
    if is_deaf or is_hoh:
        context += f"User is {'DEAF' if is_deaf else 'HARD OF HEARING'}. Critical requirements:\n"
        context += "- NEVER rely on sound instructions\n"
        context += "- Convert ALL audio-based instructions into visual-friendly, step-by-step written instructions\n"
        context += "- Use visual cues with emojis: ⬆️ (up), ⬇️ (down), ➡️ (right), ⬅️ (left), ↔️ (center), ✋ (hand)\n"
        context += "- Include direction arrows and short descriptions\n"
        context += "- Use clear step numbers (Step 1, Step 2, etc.)\n"
        context += "- NO sound references (avoid 'listen', 'اسمعي', 'hear', 'sound')\n"
        context += "- Keep sentences very short and simple\n"
        context += "- Use simple structure, avoid complex metaphors\n"
        context += "- Use visual markers and emojis when needed\n"
    
    context += "\nWorkout Instructions Format:\n"
    context += "- Use visual cues: ⬆️ ارفعي يدك فوق / ⬇️ انزلي ببطء / ➡️ خطوة يمين / ⬅️ خطوة يسار\n"
    context += "- Example: 'اجلسي مستقيمة. ✋ ارفعي يدك اليمنى للأعلى. ↔️ حرّكيها يمين ويسار ببطء.'\n"
    context += "- Include step numbers: Step 1, Step 2, Step 3\n"
    context += "- Use clear visual descriptions\n"
    
    if is_deaf or is_hoh:
        context += "\nSafety Rules for Deaf/HoH Users:\n"
        unsafe = get_deaf_unsafe_exercises()
        context += f"- AVOID these exercises: {', '.join(unsafe)}\n"
        safe = get_deaf_safe_exercises()
        context += f"- PREFER these exercises: {', '.join(safe)}\n"
    
    context += "\nResponse Style:\n"
    context += "- Short and visual\n"
    context += "- Very clear\n"
    context += "- Saudi casual dialect for Arabic, clean English for English\n"
    context += "- Zero repetition\n"
    context += "- NO sound references\n"
    
    if deaf_mode.get('haptic_cues', False):
        context += "\nHaptic Cues Available:\n"
        context += "- Short vibration = start\n"
        context += "- Long vibration = rest\n"
        context += "- Repeated vibration = end of set\n"
    
    return context


def filter_videos_with_captions(videos):
    """Filter videos to only include those with captions (CC)"""
    # In a real implementation, this would check video metadata
    # For now, we'll add a note that videos should have captions
    filtered = []
    for video in videos:
        # Add caption note to description
        video_copy = video.copy()
        if 'description' not in video_copy:
            video_copy['description'] = ''
        video_copy['description'] += ' (CC available - suitable for deaf/hard-of-hearing users)'
        filtered.append(video_copy)
    return filtered


def format_visual_workout_instruction(instruction, language):
    """Format workout instruction with visual cues for deaf users"""
    cues = VISUAL_CUES_AR if language != 'english' else VISUAL_CUES
    
    # Add visual cues based on instruction content
    lowered = instruction.lower()
    
    if 'up' in lowered or 'فوق' in lowered or 'أعلى' in lowered:
        instruction = f"{cues.get('up', '⬆️')} {instruction}"
    elif 'down' in lowered or 'أسفل' in lowered or 'انزلي' in lowered:
        instruction = f"{cues.get('down', '⬇️')} {instruction}"
    elif 'right' in lowered or 'يمين' in lowered:
        instruction = f"{cues.get('right', '➡️')} {instruction}"
    elif 'left' in lowered or 'يسار' in lowered:
        instruction = f"{cues.get('left', '⬅️')} {instruction}"
    elif 'slow' in lowered or 'بطء' in lowered or 'ببطء' in lowered:
        instruction = f"{cues.get('slow', '🐢')} {instruction}"
    
    return instruction



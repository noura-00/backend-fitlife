import re


def detect_language(text):
    if not text:
        return 'english'
    arabic_chars = re.compile(r'[\u0600-\u06FF]')
    has_arabic = bool(arabic_chars.search(text))
    has_english = bool(re.search(r'[A-Za-z]', text))
    if has_arabic and has_english:
        return 'mixed'
    if has_arabic:
        return 'arabic'
    return 'english'


def detect_emotion(text):
    if not text:
        return 'neutral'
    lowered = text.lower()
    emotion_map = {
        'tired': ['tired', 'exhausted', 'fatigued', 'نعسان', 'تعبان', 'مرهق'],
        'stressed': ['stressed', 'pressure', 'قلقان', 'مضغوط'],
        'sad': ['sad', 'down', 'حزين'],
        'bored': ['bored', 'طفشان'],
        'unmotivated': ['unmotivated', 'lazy', 'مالي خلق', 'مالي نفس'],
        'excited': ['excited', 'hyped', 'متحمس'],
        'proud': ['proud', 'فخور'],
    }
    for emotion, keywords in emotion_map.items():
        for keyword in keywords:
            if keyword in lowered:
                return emotion
    return 'neutral'


def determine_detail_level(user_message):
    words = user_message.strip().split()
    length = len(words)
    keywords_long = ['plan', 'program', 'detailed', 'explain', 'meal', 'workout']
    if any(keyword in user_message.lower() for keyword in keywords_long):
        return 'detailed'
    if length <= 8:
        return 'micro'
    if length <= 20:
        return 'brief'
    if length <= 60:
        return 'moderate'
    return 'detailed'


def extract_response_text(completion):
    """Extract assistant text from OpenAI Responses API payload"""
    if not isinstance(completion, dict):
        return ""
    
    output = completion.get("output") or []
    collected = []
    
    for block in output:
        if block.get("type") != "message":
            continue
        for content in block.get("content", []):
            content_type = content.get("type")
            if content_type in ("output_text", "text"):
                collected.append(content.get("text", ""))
    
    if collected:
        return "\n".join(collected)
    
    # Fallback to legacy chat completion shape if needed
    choices = completion.get("choices") or []
    for choice in choices:
        message = choice.get("message", {})
        if isinstance(message, dict) and message.get("content"):
            return message.get("content")
    
    return ""


def extract_profile_data(profile):
    user = profile.user
    name = (user.first_name or '').strip()
    if not name:
        name = (user.last_name or '').strip()
    if not name:
        name = user.username
    
    return {
        'name': name,
        'username': user.username,
        'age': profile.age,
        'height_cm': profile.height,
        'weight_kg': profile.current_weight,
        'target_weight_kg': profile.target_weight,
        'goal': profile.goal or '',
        'activity_level': profile.activity_level or '',
        'gender': getattr(profile, 'gender', '') or getattr(user, 'gender', ''),
        'health_notes': profile.bio or '',
    }



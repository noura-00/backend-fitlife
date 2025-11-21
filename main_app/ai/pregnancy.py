import random
import re

from .prompts import (
    DIASTASIS_EXERCISES_STAGE_1,
    DIASTASIS_EXERCISES_STAGE_2,
    DIASTASIS_EXERCISES_STAGE_3,
    DIASTASIS_EXERCISES_STAGE_4,
    DIASTASIS_FORBIDDEN_EXERCISES,
    DIASTASIS_SAFETY_ALERTS,
    DIASTASIS_VIDEOS,
    PREGNANCY_EXERCISES_TRIMESTER_1,
    PREGNANCY_EXERCISES_TRIMESTER_2,
    PREGNANCY_EXERCISES_TRIMESTER_3,
    PREGNANCY_SAFETY_ALERTS,
    PREGNANCY_VIDEOS,
    POSTPARTUM_EXERCISES_PHASE_1,
    POSTPARTUM_EXERCISES_PHASE_2,
    POSTPARTUM_EXERCISES_PHASE_3,
    POSTPARTUM_EXERCISES_PHASE_4,
    POSTPARTUM_SAFETY_ALERTS,
    POSTPARTUM_VIDEOS,
)


def detect_pregnancy_mode(user_message, request_data=None):
    """Detect if user wants to activate pregnancy mode"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Check for pregnancy mentions
    pregnancy_keywords = [
        'أنا حامل', 'i\'m pregnant', 'i am pregnant',
        'في بداية الحمل', 'beginning of pregnancy',
        'أبغى تمارين للحامل', 'pregnancy exercises',
        'pregnant', 'حامل', 'prenatal', 'pregnancy',
    ]
    if any(keyword in lowered for keyword in pregnancy_keywords):
        return True
    
    # Check request data
    if request_data:
        if request_data.get('pregnancy_mode') == True:
            return True
    
    return False


def extract_pregnancy_info(user_message):
    """Extract pregnancy information from user message"""
    if not user_message:
        return {}
    
    lowered = user_message.lower()
    info = {}
    
    # Extract trimester
    trimester_patterns = [
        r'الشهر (\d+)',
        r'month (\d+)',
        r'trimester (\d+)',
        r'الثلث (\d+)',
    ]
    for pattern in trimester_patterns:
        match = re.search(pattern, lowered)
        if match:
            month = int(match.group(1))
            if 1 <= month <= 3:
                info['trimester'] = 1
            elif 4 <= month <= 6:
                info['trimester'] = 2
            elif 7 <= month <= 9:
                info['trimester'] = 3
            break
    
    # Extract pain/health issues
    if 'تعب' in lowered or 'tired' in lowered or 'fatigue' in lowered:
        info['fatigue'] = True
    if 'ألم' in lowered or 'pain' in lowered:
        info['pain'] = True
    if 'مشاكل سابقة' in lowered or 'previous problems' in lowered or 'previous issues' in lowered:
        info['previous_problems'] = True
    
    return info


def check_pregnancy_safety_alerts(user_message, language):
    """Check for pregnancy safety alert keywords"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    for alert_key, alert_data in PREGNANCY_SAFETY_ALERTS.items():
        ar_keyword = alert_data['ar']
        en_keyword = alert_data['en']
        
        if ar_keyword in lowered or en_keyword in lowered:
            response = alert_data['response_ar'] if language != 'english' else alert_data['response_en']
            return response
    
    return None


def build_pregnancy_mode_context(pregnancy_mode, profile_data, metrics, language):
    """Build context for pregnancy-safe workout plan"""
    trimester = pregnancy_mode.get('trimester')
    if not trimester:
        return None
    
    context = "PREGNANCY FITNESS MODE - SAFE PREGNANCY COACHING:\n\n"
    context += f"User is in {trimester} trimester of pregnancy.\n\n"
    
    context += "CRITICAL SAFETY RULES - NEVER include:\n"
    context += "- NO jumping\n"
    context += "- NO high intensity\n"
    if trimester >= 2:
        context += "- NO lying flat (after 1st trimester)\n"
    context += "- NO heavy weights\n"
    context += "- NO twisting motions\n"
    context += "- NO overheating\n"
    context += "- NO holding breath\n"
    
    context += f"\nPREGNANCY-SAFE EXERCISES FOR TRIMESTER {trimester}:\n"
    if trimester == 1:
        exercises = PREGNANCY_EXERCISES_TRIMESTER_1
    elif trimester == 2:
        exercises = PREGNANCY_EXERCISES_TRIMESTER_2
    else:
        exercises = PREGNANCY_EXERCISES_TRIMESTER_3
    
    context += f"- {', '.join(exercises)}\n"
    
    if trimester == 3:
        context += "\nLABOR PREPARATION EXERCISES:\n"
        context += "- Cat-cow\n"
        context += "- Hip circles\n"
        context += "- Side-lying release\n"
        context += "- Deep squats (supported)\n"
        context += "- Pelvic tilts\n"
    
    context += "\nPREGNANCY NUTRITION ADJUSTMENTS:\n"
    context += "- More protein\n"
    context += "- More hydration\n"
    context += "- ZERO calorie deficit\n"
    context += "- Avoid unsafe foods\n"
    context += "- Suggest light meals for nausea\n"
    
    context += f"\nUser Profile:\n"
    context += f"- Age: {profile_data.get('age', 'N/A')}\n"
    context += f"- TDEE: {metrics.get('tdee', 'N/A')} kcal (adjust for pregnancy)\n"
    
    context += "\nTone: Very gentle, respectful, clear. Saudi casual dialect for Arabic, clean English for English. Short replies unless user asks for a full plan."
    
    return context


def get_pregnancy_video_recommendation(state, language):
    """Get non-repeating pregnancy video recommendation"""
    used_videos = state.get('pregnancy_mode', {}).get('used_pregnancy_videos', [])
    
    available = [v for v in PREGNANCY_VIDEOS if v['trainer'] not in used_videos]
    if not available:
        available = PREGNANCY_VIDEOS
        used_videos = []
    
    selected = random.choice(available)
    used_videos.append(selected['trainer'])
    if 'pregnancy_mode' not in state:
        state['pregnancy_mode'] = {}
    state['pregnancy_mode']['used_pregnancy_videos'] = used_videos
    
    return selected


def detect_postpartum_mode(user_message, request_data=None):
    """Detect if user wants to activate postpartum mode"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Check for postpartum mentions
    postpartum_keywords = [
        'ولدت', 'i gave birth', 'gave birth',
        'أنا بعد الولادة', 'after birth', 'postpartum',
        'c-section', 'قيصرية', 'cesarean',
        'ولادة طبيعية', 'natural birth', 'natural delivery',
        'post delivery', 'بعد الولادة',
    ]
    if any(keyword in lowered for keyword in postpartum_keywords):
        return True
    
    # Check request data
    if request_data:
        if request_data.get('postpartum_mode') == True:
            return True
    
    return None


def extract_postpartum_info(user_message):
    """Extract postpartum information from user message"""
    if not user_message:
        return {}
    
    lowered = user_message.lower()
    info = {}
    
    # Extract delivery type
    if 'c-section' in lowered or 'قيصرية' in lowered or 'cesarean' in lowered:
        info['delivery_type'] = 'c_section'
    elif 'natural' in lowered or 'طبيعية' in lowered or 'natural birth' in lowered or 'ولادة طبيعية' in lowered:
        info['delivery_type'] = 'natural'
    
    # Extract time since birth
    time_patterns = [
        r'(\d+)\s*(?:week|أسبوع)',
        r'(\d+)\s*(?:day|يوم)',
        r'(\d+)\s*(?:month|شهر)',
        r'الشهر\s*(\d+)',
        r'الأسبوع\s*(\d+)',
    ]
    for pattern in time_patterns:
        match = re.search(pattern, lowered)
        if match:
            num = int(match.group(1))
            if 'week' in pattern or 'أسبوع' in pattern:
                info['weeks_postpartum'] = num
            elif 'day' in pattern or 'يوم' in pattern:
                info['days_postpartum'] = num
            elif 'month' in pattern or 'شهر' in pattern:
                info['weeks_postpartum'] = num * 4  # Approximate
            break
    
    # Extract breastfeeding status
    if 'ترضع' in lowered or 'breastfeeding' in lowered or 'breastfeed' in lowered or 'nursing' in lowered:
        if 'ما' in lowered or 'لا' in lowered or 'not' in lowered or 'no' in lowered:
            info['breastfeeding'] = False
        else:
            info['breastfeeding'] = True
    
    # Extract pain/health issues
    if 'ألم' in lowered or 'pain' in lowered:
        if 'قوي' in lowered or 'severe' in lowered:
            info['pain_level'] = 'severe'
        elif 'متوسط' in lowered or 'moderate' in lowered:
            info['pain_level'] = 'moderate'
        else:
            info['pain_level'] = 'mild'
    
    if 'نزيف' in lowered or 'bleeding' in lowered:
        info['bleeding'] = True
    
    if 'تعب' in lowered or 'fatigue' in lowered or 'tired' in lowered:
        info['fatigue'] = True
    
    if 'حوض' in lowered or 'pelvic' in lowered:
        info['pelvic_issues'] = True
    
    if 'بطن' in lowered or 'abdominal' in lowered or 'stomach' in lowered:
        info['abdominal_pain'] = True
    
    return info


def calculate_postpartum_phase(weeks_postpartum, days_postpartum, delivery_type):
    """Calculate postpartum phase based on time since birth"""
    if weeks_postpartum is None and days_postpartum is None:
        return None
    
    # Convert days to weeks if needed
    if weeks_postpartum is None and days_postpartum is not None:
        weeks_postpartum = days_postpartum / 7
    
    if weeks_postpartum is None:
        return None
    
    # Phase calculation
    if delivery_type == 'c_section':
        # C-section: Phase 1 starts after 6 weeks with doctor approval
        if weeks_postpartum < 6:
            return 1  # Still in recovery, very gentle only
        elif weeks_postpartum < 12:
            return 2
        elif weeks_postpartum < 24:  # 6 months
            return 3
        else:
            return 4
    else:
        # Natural birth: Phase 1 starts after 2 weeks
        if weeks_postpartum < 2:
            return 1  # Very early recovery
        elif weeks_postpartum < 6:
            return 1  # Phase 1 continues
        elif weeks_postpartum < 12:
            return 2
        elif weeks_postpartum < 24:  # 6 months
            return 3
        else:
            return 4


def check_postpartum_safety_alerts(user_message, language):
    """Check for postpartum safety alert keywords"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    for alert_key, alert_data in POSTPARTUM_SAFETY_ALERTS.items():
        ar_keyword = alert_data['ar']
        en_keyword = alert_data['en']
        
        if ar_keyword in lowered or en_keyword in lowered:
            response = alert_data['response_ar'] if language != 'english' else alert_data['response_en']
            return response
    
    return None


def build_postpartum_mode_context(postpartum_mode, profile_data, metrics, language):
    """Build context for postpartum-safe workout plan"""
    delivery_type = postpartum_mode.get('delivery_type')
    weeks_postpartum = postpartum_mode.get('weeks_postpartum')
    days_postpartum = postpartum_mode.get('days_postpartum')
    phase = postpartum_mode.get('phase')
    breastfeeding = postpartum_mode.get('breastfeeding')
    
    if not phase:
        phase = calculate_postpartum_phase(weeks_postpartum, days_postpartum, delivery_type)
        if phase:
            postpartum_mode['phase'] = phase
    
    if not phase:
        return None
    
    context = "POSTPARTUM FITNESS MODE - SAFE POSTPARTUM COACHING:\n\n"
    context += f"User is {weeks_postpartum or (days_postpartum / 7 if days_postpartum else 'unknown')} weeks postpartum.\n"
    context += f"Delivery type: {delivery_type or 'unknown'}\n"
    context += f"Current phase: {phase}\n\n"
    
    context += "CRITICAL SAFETY RULES - NEVER include:\n"
    context += "- NO jumping\n"
    context += "- NO abdominal pressure\n"
    context += "- NO planks\n"
    context += "- NO high intensity\n"
    context += "- NO heavy weights\n"
    context += "- NO strong stretching\n"
    context += "- NO twisting (Twisting)\n"
    context += "- NO deep bridges (dangerous for C-section)\n"
    
    if delivery_type == 'c_section':
        context += "\nSPECIAL RULES FOR C-SECTION (CRITICAL):\n"
        context += "- Strictly avoid any movement that:\n"
        context += "  * يضغط على الجرح (presses on wound)\n"
        context += "  * يسبب شد قوي في البطن (causes strong abdominal tension)\n"
        context += "  * يضغط على منطقة الحوض (presses on pelvic area)\n"
        context += "  * يسبب ألم في الجوانب (causes side pain)\n"
        context += "- Phase 1 for C-section: Start ONLY after 6 weeks with doctor approval\n"
        context += "- Start with: Breathing only, Pelvic floor activation, Walking, Gentle mobility, Seated exercises ONLY\n"
        context += "- Absolutely NO until 3+ months (and only if user confirms no pain):\n"
        context += "  * Core exercises\n"
        context += "  * Planks\n"
        context += "  * Crunches\n"
        context += "  * Full squats\n"
        context += "  * Heavy weights\n"
        context += "  * Any exercise that puts pressure on abdomen\n"
        context += "- Even after 3 months, ONLY proceed if user explicitly confirms no pain, no bleeding, no discomfort\n"
    
    context += f"\nPOSTPARTUM-SAFE EXERCISES FOR PHASE {phase}:\n"
    if phase == 1:
        exercises = POSTPARTUM_EXERCISES_PHASE_1
        context += "Phase 1 - Week 1-6 AFTER birth:\n"
        context += "- Natural birth: Start after 2 weeks\n"
        context += "- C-section: Start after 6 weeks with doctor approval ONLY\n"
        context += "- Focus ONLY on: Breathing exercises, Pelvic floor activation, Diaphragmatic breathing, Gentle walking, Light stretching, Lower-back mobility, Gentle hip openers\n"
    elif phase == 2:
        exercises = POSTPARTUM_EXERCISES_PHASE_2
        context += "Phase 2 - Week 6-12:\n"
        context += "- Gentle low-impact workouts, Wall push-ups, Glute bridges (light only), Modified squats, Seated strength, NO core-heavy routines\n"
    elif phase == 3:
        exercises = POSTPARTUM_EXERCISES_PHASE_3
        context += "Phase 3 - 3-6 months:\n"
        context += "- Light strength training, Resistance bands, Slow pace routines, Gradual reintroduction to core, Avoiding direct ab pressure\n"
    else:
        exercises = POSTPARTUM_EXERCISES_PHASE_4
        context += "Phase 4 - 6+ months:\n"
        context += "- ONLY if user has: no pain, no bleeding, no pelvic pressure, no diastasis recti issues\n"
        context += "- Can slowly introduce stronger routines - but ONLY with user confirmation of no symptoms\n"
    
    context += f"- Safe exercises: {', '.join(exercises)}\n"
    
    context += "\nPOSTPARTUM NUTRITION ADJUSTMENTS:\n"
    if breastfeeding:
        context += "- Increase calories by 300-450\n"
        context += "- Increase hydration significantly\n"
        context += "- Increase protein intake\n"
        context += "- NO calorie deficit (maintenance or slight surplus)\n"
        context += "- Give fast-prep meals (convenient for new mothers)\n"
        context += "- Avoid foods that affect milk production (caffeine, alcohol, certain herbs)\n"
    else:
        context += "- Small calorie deficit allowed (if desired)\n"
        context += "- Focus on recovery foods (protein, iron, vitamins)\n"
        context += "- Ensure adequate nutrition for healing\n"
    context += "- Always check hunger level + energy before adjusting calories\n"
    context += "- Monitor energy levels and adjust accordingly\n"
    
    context += "\nWORKOUT PLAN FORMAT (REQUIRED):\n"
    context += "ALWAYS present postpartum workouts in table structure:\n"
    context += "Format: 'Postpartum Plan – Week X'\n"
    context += "Table columns: Day | Duration | Focus | Exercises | Notes\n"
    context += "Example:\n"
    context += "Day | Duration | Focus | Exercises | Notes\n"
    context += "Sat | 15 min | Breathing + walking | Belly breathing, pelvic floor | Very gentle\n"
    context += "Sun | 10 min | Mobility | Hip openers, cat-cow | No pressure\n"
    context += "Use this table format for ALL postpartum workout plans.\n"
    
    context += f"\nUser Profile:\n"
    context += f"- Age: {profile_data.get('age', 'N/A')}\n"
    context += f"- TDEE: {metrics.get('tdee', 'N/A')} kcal (adjust for postpartum and breastfeeding)\n"
    
    context += "\nTone: Supportive, gentle, non-repetitive. Saudi casual dialect for Arabic, clean English for English. Short messages unless user requests details."
    
    return context


def get_postpartum_video_recommendation(state, language):
    """Get non-repeating postpartum video recommendation"""
    used_videos = state.get('postpartum_mode', {}).get('used_postpartum_videos', [])
    
    available = [v for v in POSTPARTUM_VIDEOS if v['trainer'] not in used_videos]
    if not available:
        available = POSTPARTUM_VIDEOS
        used_videos = []
    
    selected = random.choice(available)
    used_videos.append(selected['trainer'])
    if 'postpartum_mode' not in state:
        state['postpartum_mode'] = {}
    state['postpartum_mode']['used_postpartum_videos'] = used_videos
    
    return selected


def detect_diastasis_mode(user_message, request_data=None):
    """Detect if user wants to activate diastasis recti mode"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    # Check for diastasis mentions
    diastasis_keywords = [
        'عندي انفصال عضلات البطن',
        'diastasis',
        'انفصال',
        'بطني نافخ بعد الولادة',
        'i have ab separation',
        'abdominal separation',
        'انفصال البطن',
        'انفصال عضلات',
    ]
    if any(keyword in lowered for keyword in diastasis_keywords):
        return True
    
    # Check request data
    if request_data:
        if request_data.get('diastasis_mode') == True:
            return True
    
    return None


def extract_diastasis_info(user_message):
    """Extract diastasis recti information from user message"""
    if not user_message:
        return {}
    
    lowered = user_message.lower()
    info = {}
    
    # Extract separation size (fingers)
    finger_patterns = [
        r'(\d+)\s*(?:finger|إصبع|أصابع)',
        r'(\d+)\s*(?:cm|سم)',
    ]
    for pattern in finger_patterns:
        match = re.search(pattern, lowered)
        if match:
            num = int(match.group(1))
            info['separation_fingers'] = num
            # Determine severity
            if num <= 2:
                info['separation_severity'] = 'mild'
            elif num <= 4:
                info['separation_severity'] = 'moderate'
            else:
                info['separation_severity'] = 'severe'
            break
    
    # Extract time since delivery
    time_patterns = [
        r'(\d+)\s*(?:week|أسبوع)',
        r'(\d+)\s*(?:day|يوم)',
        r'(\d+)\s*(?:month|شهر)',
    ]
    for pattern in time_patterns:
        match = re.search(pattern, lowered)
        if match:
            num = int(match.group(1))
            if 'week' in pattern or 'أسبوع' in pattern:
                info['weeks_postpartum'] = num
            elif 'day' in pattern or 'يوم' in pattern:
                info['days_postpartum'] = num
            elif 'month' in pattern or 'شهر' in pattern:
                info['weeks_postpartum'] = num * 4  # Approximate
            break
    
    # Extract pain/pressure info
    if 'ألم' in lowered or 'pain' in lowered:
        if 'بطن' in lowered or 'abdominal' in lowered or 'lower' in lowered:
            info['lower_abdominal_pain'] = True
    
    if 'ضغط' in lowered or 'pressure' in lowered:
        if 'حوض' in lowered or 'pelvic' in lowered:
            info['pelvic_pressure'] = True
    
    if 'انتفاخ' in lowered or 'bulging' in lowered or 'بروز' in lowered or 'coning' in lowered:
        info['coning_bulging'] = True
    
    if 'ضغط' in lowered or 'pressure' in lowered:
        if 'بطن' in lowered or 'belly' in lowered or 'abdominal' in lowered:
            info['belly_pressure'] = True
    
    return info


def calculate_diastasis_stage(weeks_postpartum, days_postpartum, separation_severity):
    """Calculate diastasis recti recovery stage"""
    if weeks_postpartum is None and days_postpartum is None:
        return None
    
    # Convert days to weeks if needed
    if weeks_postpartum is None and days_postpartum is not None:
        weeks_postpartum = days_postpartum / 7
    
    if weeks_postpartum is None:
        return None
    
    # Stage calculation based on time and severity
    if separation_severity == 'severe' or weeks_postpartum < 6:
        return 1  # Early healing
    elif weeks_postpartum < 12:
        return 2  # Gentle core support
    elif weeks_postpartum < 24:  # 6 months
        return 3  # Functional strength
    else:
        return 4  # Final strengthening (only if no coning/bulging)


def check_diastasis_safety_alerts(user_message, language):
    """Check for diastasis safety alert keywords"""
    if not user_message:
        return None
    
    lowered = user_message.lower()
    
    for alert_key, alert_data in DIASTASIS_SAFETY_ALERTS.items():
        ar_keyword = alert_data['ar']
        en_keyword = alert_data['en']
        
        if ar_keyword in lowered or en_keyword in lowered:
            response = alert_data['response_ar'] if language != 'english' else alert_data['response_en']
            return response
    
    return None


def build_diastasis_mode_context(diastasis_mode, profile_data, metrics, language):
    """Build context for diastasis recti-safe workout plan"""
    separation_fingers = diastasis_mode.get('separation_fingers')
    weeks_postpartum = diastasis_mode.get('weeks_postpartum')
    days_postpartum = diastasis_mode.get('days_postpartum')
    stage = diastasis_mode.get('stage')
    separation_severity = diastasis_mode.get('separation_severity')
    lower_abdominal_pain = diastasis_mode.get('lower_abdominal_pain', False)
    pelvic_pressure = diastasis_mode.get('pelvic_pressure', False)
    coning_bulging = diastasis_mode.get('coning_bulging', False)
    
    if not stage:
        stage = calculate_diastasis_stage(weeks_postpartum, days_postpartum, separation_severity)
        if stage:
            diastasis_mode['stage'] = stage
    
    if not stage:
        return None
    
    context = "DIASTASIS RECTI RECOVERY MODE - SAFE ABDOMINAL SEPARATION COACHING:\n\n"
    context += f"User has diastasis recti (abdominal separation).\n"
    if separation_fingers:
        context += f"Separation: {separation_fingers} fingers ({separation_severity or 'unknown'} severity).\n"
    context += f"Time since delivery: {weeks_postpartum or (days_postpartum / 7 if days_postpartum else 'unknown')} weeks.\n"
    context += f"Current stage: {stage}\n"
    if lower_abdominal_pain:
        context += "User reports lower abdominal pain.\n"
    if pelvic_pressure:
        context += "User reports pelvic pressure.\n"
    if coning_bulging:
        context += "User reports coning/bulging during exercises.\n"
    context += "\n"
    
    context += "CRITICAL SAFETY RULES - NEVER include these exercises (MANDATORY):\n"
    for exercise in DIASTASIS_FORBIDDEN_EXERCISES:
        context += f"- NO {exercise}\n"
    context += "This rule is mandatory at all times.\n\n"
    
    context += f"DIASTASIS-SAFE EXERCISES FOR STAGE {stage}:\n"
    if stage == 1:
        exercises = DIASTASIS_EXERCISES_STAGE_1
        context += "Stage 1 – Early Healing (Weeks 1–6 postpartum or severe separation):\n"
        context += "Focus on: Belly breathing, Pelvic floor, TVA engagement, Light mobility, Walking. No core load at all.\n"
    elif stage == 2:
        exercises = DIASTASIS_EXERCISES_STAGE_2
        context += "Stage 2 – Gentle Core Support (6–12 weeks postpartum):\n"
        context += "Focus on: Heel slides, Toe taps, Side-lying core, Gentle bridges, Seated controlled movements.\n"
    elif stage == 3:
        exercises = DIASTASIS_EXERCISES_STAGE_3
        context += "Stage 3 – Functional Strength (3–6 months):\n"
        context += "Focus on: Standing core activation, Resistance band light training, Supported squats, Modified bird-dog.\n"
    else:
        exercises = DIASTASIS_EXERCISES_STAGE_4
        context += "Stage 4 – Final Strengthening (6+ months):\n"
        context += "ONLY if user has: No coning, No bulging, No pelvic pressure, Less than 1-finger gap.\n"
        context += "Can introduce: Modified planks (knees), Light obliques, Standing controlled core.\n"
        context += "NEVER introduce full planks or crunches unless user confirms doctor clearance.\n"
    
    context += f"Safe exercises: {', '.join(exercises)}\n\n"
    
    context += "IMPORTANT CHECK:\n"
    context += "AI must always ask: 'هل تحسين بانتفاخ أو بروز في البطن خلال التمرين؟' (Do you feel bulging or coning in your abdomen during the exercise?)\n"
    context += "If YES → stop and switch to easier exercise immediately.\n\n"
    
    context += "WORKOUT PLAN FORMAT (REQUIRED):\n"
    context += "ALWAYS present diastasis recti workouts in table structure:\n"
    context += "Format: 'Diastasis Recti Plan – Week X'\n"
    context += "Table columns: Day | Duration | Focus | Exercises | Notes\n"
    context += "Example:\n"
    context += "Day | Duration | Focus | Exercises | Notes\n"
    context += "Sat | 10 min | Breathing | Belly breathing, TVA | No pressure\n"
    context += "Sun | 12 min | Core healing | Heel slides, toe taps | Stop if bulging\n"
    context += "Use this table format for ALL diastasis recti workout plans.\n\n"
    
    context += "PROGRESS MONITORING:\n"
    context += "Track: Separation size, Pain levels, Coning/bulging, Belly pressure, Improvements in stability.\n"
    context += "If user reports new pain → respond: 'هذا عرض يحتاج توقفين فورًا. الأفضل تراجعين طبيبة.'\n\n"
    
    context += f"User Profile:\n"
    context += f"- Age: {profile_data.get('age', 'N/A')}\n"
    context += f"- TDEE: {metrics.get('tdee', 'N/A')} kcal (adjust for postpartum recovery)\n\n"
    
    context += "Tone: Supportive, gentle, non-repetitive, zero negative tone. Saudi casual dialect for Arabic, clean simple English for English.\n"
    context += "Example: 'ولا يهمك يا <name>… كثير يصير لهم انفصال بعد الولادة. بنمشي خطوة خطوة لحد ما يرجع بطنك ويتحسن.'\n"
    
    return context


def get_diastasis_video_recommendation(state, language):
    """Get non-repeating diastasis recti video recommendation"""
    used_videos = state.get('diastasis_mode', {}).get('used_diastasis_videos', [])
    
    available = [v for v in DIASTASIS_VIDEOS if v['trainer'] not in used_videos]
    if not available:
        available = DIASTASIS_VIDEOS
        used_videos = []
    
    selected = random.choice(available)
    used_videos.append(selected['trainer'])
    if 'diastasis_mode' not in state:
        state['diastasis_mode'] = {}
    state['diastasis_mode']['used_diastasis_videos'] = used_videos
    
    return selected



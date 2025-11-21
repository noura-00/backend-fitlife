import random
from datetime import timedelta

from django.utils import timezone

from .prompts import (
    INACTIVITY_MESSAGES_2_3_DAYS,
    INACTIVITY_MESSAGES_4_6_DAYS,
    INACTIVITY_MESSAGES_7_PLUS_DAYS,
    WORKOUT_MESSAGES_2_3_DAYS,
    WORKOUT_MESSAGES_2_3_DAYS_EN,
    WORKOUT_MESSAGES_4_6_DAYS,
    WORKOUT_MESSAGES_4_6_DAYS_EN,
    WORKOUT_MESSAGES_7_13_DAYS,
    WORKOUT_MESSAGES_7_13_DAYS_EN,
    WORKOUT_MESSAGES_14_PLUS_DAYS,
    WORKOUT_MESSAGES_14_PLUS_DAYS_EN,
)
from .workouts import get_workout_inactivity_message


def update_behavior_state(state, user_message, emotion, current_time):
    # Initialize missing keys safely
    if 'mood_trend' not in state:
        state['mood_trend'] = []
    if 'skipped_days' not in state:
        state['skipped_days'] = 0
    if 'stress_patterns' not in state:
        state['stress_patterns'] = []
    
    if emotion and emotion != 'neutral':
        state['mood_trend'].append(emotion)
    if 'skip' in user_message.lower() or 'miss' in user_message.lower():
        state['skipped_days'] = state.get('skipped_days', 0) + 1
        state['workout_adherence'] = 'low'
    else:
        state['workout_adherence'] = 'good'
    if 'night' in user_message.lower() or 'late' in user_message.lower():
        state['preferred_times'] = 'evenings'
    if 'morning' in user_message.lower():
        state['preferred_times'] = 'mornings'

    if emotion in ['stressed', 'tired', 'unmotivated']:
        state['stress_patterns'].append(f"{emotion} at {current_time.isoformat()}")


def generate_notifications(state, current_time):
    notifications = []
    last = state.get('last_interaction')
    if last:
        hours_since = (current_time - last) / timedelta(hours=1)
        if hours_since >= 24:
            notifications.append("User inactive for 24h+: send gentle check-in message about lighter routine.")
    skipped_days = state.get('skipped_days', 0)
    workout_adherence = state.get('workout_adherence', 'unknown')
    if skipped_days >= 1 and workout_adherence == 'low':
        notifications.append("User skipped workouts recently; suggest simplified plan.")
    if workout_adherence == 'good' and skipped_days == 0:
        notifications.append("User consistent; send praise and encourage progression.")
    return notifications


def adjust_progress(state, profile_data, base_progress, adjustment_type, adjustment_value, language):
    """Adjust progress based on user behavior"""
    if base_progress is None:
        return None
    
    # Initialize adjusted progress if not set
    if state.get('adjusted_progress') is None:
        state['adjusted_progress'] = base_progress
        state['base_progress'] = base_progress
    
    current_adjusted = state.get('adjusted_progress', base_progress)
    
    # Apply adjustment
    new_progress = current_adjusted + adjustment_value
    
    # Clamp between 0 and 100
    new_progress = max(0, min(100, new_progress))
    
    # Store adjustment
    adjustment_record = {
        'type': adjustment_type,
        'value': adjustment_value,
        'before': current_adjusted,
        'after': new_progress,
        'timestamp': timezone.now().isoformat(),
    }
    # Initialize progress_adjustments if it doesn't exist
    if 'progress_adjustments' not in state:
        state['progress_adjustments'] = []
    state['progress_adjustments'].append(adjustment_record)
    state['adjusted_progress'] = new_progress
    
    return new_progress


def calculate_inactivity_penalty(days_inactive):
    """Calculate progress penalty based on inactivity"""
    if days_inactive < 2:
        return 0.0
    elif days_inactive < 4:
        return -1.0  # -1%
    elif days_inactive < 7:
        return -2.0  # -2%
    elif days_inactive < 14:
        return -3.0  # -3%
    else:
        return -4.0  # -4%


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


def check_inactivity_message(state, profile_data, language, current_time):
    """Determine if an inactivity message should be sent based on days inactive"""
    # Use last_interaction as the reference time (last chat message or page open)
    last_interaction = state.get('last_interaction')
    
    if not last_interaction:
        return None
    
    # Calculate days inactive
    time_diff = current_time - last_interaction
    days_inactive = time_diff.total_seconds() / (24 * 3600)
    
    # If inactive less than 24 hours, no special message
    if days_inactive < 1:
        return None
    
    # Determine category based on days inactive
    if 2 <= days_inactive < 4:
        category = '2_3'
    elif 4 <= days_inactive < 7:
        category = '4_6'
    elif days_inactive >= 7:
        category = '7_plus'
    else:
        # Between 1-2 days, no special message
        return None
    
    return get_inactivity_message(state, profile_data, language, category)


def get_inactivity_message(state, profile_data, language, category):
    """Fetch a non-repeating inactivity message for the given category"""
    name = profile_data.get('name', profile_data.get('username', ''))
    lang_key = 'english' if language == 'english' else 'arabic'
    
    pools = {
        ('2_3', 'arabic'): INACTIVITY_MESSAGES_2_3_DAYS,
        ('2_3', 'english'): INACTIVITY_MESSAGES_2_3_DAYS,  # Use Arabic for now, can add English later
        ('4_6', 'arabic'): INACTIVITY_MESSAGES_4_6_DAYS,
        ('4_6', 'english'): INACTIVITY_MESSAGES_4_6_DAYS,  # Use Arabic for now, can add English later
        ('7_plus', 'arabic'): INACTIVITY_MESSAGES_7_PLUS_DAYS,
        ('7_plus', 'english'): INACTIVITY_MESSAGES_7_PLUS_DAYS,  # Use Arabic for now, can add English later
    }
    
    pool = pools.get((category, lang_key))
    if not pool:
        return None
    
    used_messages = state.get('used_inactivity_messages', {})
    key = f"{category}_{lang_key}"
    used_in_category = used_messages.get(key, [])
    available = [msg for msg in pool if msg not in used_in_category]
    
    if not available:
        available = pool
        used_in_category = []
    
    message = random.choice(available).format(name=name)
    used_in_category.append(message)
    used_messages[key] = used_in_category
    state['used_inactivity_messages'] = used_messages
    
    return message


import os
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
import requests

from ..models import UserProfile
from .disabilities import (
    build_accessibility_context,
    build_deaf_mode_context,
    build_disability_adaptive_context,
    detect_accessibility_mode,
    detect_deaf_mode,
    detect_disability_info,
    get_adaptive_exercise_image,
    get_adaptive_video_recommendation,
    get_audio_exercise_description,
    format_voice_friendly_response,
    should_ask_about_disability,
)
from .pregnancy import (
    build_diastasis_mode_context,
    build_postpartum_mode_context,
    build_pregnancy_mode_context,
    calculate_diastasis_stage,
    calculate_postpartum_phase,
    check_diastasis_safety_alerts,
    check_postpartum_safety_alerts,
    check_pregnancy_safety_alerts,
    detect_diastasis_mode,
    detect_postpartum_mode,
    detect_pregnancy_mode,
    extract_diastasis_info,
    extract_postpartum_info,
    extract_pregnancy_info,
    get_diastasis_video_recommendation,
    get_postpartum_video_recommendation,
    get_pregnancy_video_recommendation,
)
from .nutrition import (
    calculate_nutrition_progress_boost,
    detect_nutrition_adherence,
    extract_preferences,
    get_adaptive_nutrition_context,
    merge_preferences,
    should_offer_adaptive_nutrition,
)
from .inactivity import (
    adjust_progress,
    calculate_inactivity_penalty,
    generate_notifications,
    update_behavior_state,
)
from .utils import (
    detect_emotion,
    detect_language,
    extract_profile_data,
    extract_response_text,
)
from .videos import (
    format_clickable_video_url,
    format_video_info,
    get_video_recommendation,
    should_suggest_video,
)
from .workouts import (
    build_equipment_instructions_context,
    calculate_workout_progress_boost,
    detect_gym_equipment_request,
    detect_workout_completion,
    get_adaptive_plan_context,
    get_equipment_video_recommendation,
    get_exercise_image,
    get_last_workout_timestamp,
    recognize_equipment_from_text,
    should_offer_adaptive_plan,
    should_suggest_image,
)
from .prompts import SYSTEM_PROMPT


USER_BEHAVIOR_STATE = {}


class _AIRequest:
    def __init__(self, user, data):
        self.user = user
        self.data = data or {}


class AIEngine:
    """Clean AI engine that only builds context and calls OpenAI"""
    
    def __init__(self, user, user_message, request_data):
        self.user = user
        self.user_message = user_message
        self.request_data = request_data or {}
        self.current_time = timezone.now()
        
        # Get user profile
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            raise ValueError('Profile not found. Please complete your profile first.')
        
        self.profile_data = extract_profile_data(profile)
        self.user_name = self.profile_data.get('name') or user.username
        self.state = self._get_user_state(user.id)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics(self.profile_data)
        
        # Calculate progress
        self.base_progress = self._calculate_progress(self.profile_data)
        if self.state.get('adjusted_progress') is None and self.base_progress is not None:
            self.state['adjusted_progress'] = self.base_progress
            self.state['base_progress'] = self.base_progress
        self.progress = self.state.get('adjusted_progress', self.base_progress)
        
        # Detect language and emotion
        self.language = detect_language(user_message)
        self.emotion = detect_emotion(user_message)
        
        # Fetch last workout timestamp
        last_workout_ts = get_last_workout_timestamp(user)
        if last_workout_ts:
            self.state['last_workout_logged'] = last_workout_ts
        else:
            last_workout_ts = self.state.get('last_workout_logged')
        self.last_workout_ts = last_workout_ts
        
        # Update behavior state
        update_behavior_state(self.state, user_message, self.emotion, self.current_time)
    
    def _get_user_state(self, user_id):
        """Get or initialize user behavior state"""
        state = USER_BEHAVIOR_STATE.get(user_id)
        if not state:
            state = {
                'last_interaction': None,
                'last_chat_message': None,
                'last_chat_page_open': None,
                'last_workout_logged': None,
                'preferences': {
                    'food_dislikes': [],
                    'allergies': [],
                    'favorite_foods': [],
                    'workout_dislikes': [],
                    'injuries': [],
                },
                'adjusted_progress': None,
                'base_progress': None,
                'progress_adjustments': [],
                'workout_count_this_week': 0,
                'nutrition_adherence': 'unknown',
                'skipped_days': 0,
                'mood_trend': [],
                'workout_adherence': 'unknown',
                'stress_patterns': [],
                'preferred_times': None,
                'disability_info': {
                    'mobility_challenges': False,
                    'difficulty_standing': False,
                    'wheelchair_use': False,
                    'joint_pain': False,
                    'spine_issues': False,
                    'balance_issues': False,
                    'chronic_conditions': [],
                    'disability_asked': False,
                },
                'accessibility_mode': {
                    'enabled': False,
                    'visual_impairment': 'none',
                    'voice_friendly': False,
                },
                'deaf_mode': {
                    'enabled': False,
                    'hearing_impairment': 'none',
                    'visual_cues': True,
                },
                'pregnancy_mode': {
                    'enabled': False,
                    'trimester': None,
                    'pregnancy_notes': [],
                    'pain_notes': [],
                },
                'postpartum_mode': {
                    'enabled': False,
                    'delivery_type': None,
                    'weeks_postpartum': None,
                    'days_postpartum': None,
                    'breastfeeding': None,
                    'phase': None,
                },
                'diastasis_mode': {
                    'enabled': False,
                    'separation_fingers': None,
                    'weeks_postpartum': None,
                    'days_postpartum': None,
                    'stage': None,
                },
                'used_videos': [],
            }
            USER_BEHAVIOR_STATE[user_id] = state
        return state
    
    def _calculate_metrics(self, profile_data):
        """Calculate BMI, BMR, TDEE, etc."""
        height_cm = profile_data.get('height_cm')
        weight_kg = profile_data.get('weight_kg')
        age = profile_data.get('age')
        gender = (profile_data.get('gender') or '').lower()
        activity_level = (profile_data.get('activity_level') or '').lower()

        height_m = height_cm / 100 if height_cm else None
        bmi = None
        bmi_category = None
        if height_m and height_m > 0 and weight_kg:
            bmi = round(weight_kg / (height_m ** 2), 1)
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 25:
                bmi_category = "Normal"
            elif bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obese"

        # BMR via Mifflin-St Jeor
        bmr = None
        if all(value is not None for value in [weight_kg, height_cm, age]):
            if gender.startswith('m'):
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            elif gender.startswith('f'):
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
            else:
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
            bmr = round(bmr, 0)

        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'lightly active': 1.375,
            'moderate': 1.55,
            'moderately active': 1.55,
            'active': 1.725,
            'very active': 1.9,
            'athlete': 1.95,
        }
        tdee = None
        if bmr:
            factor = 1.45
            for key, value in activity_factors.items():
                if key in activity_level:
                    factor = value
                    break
            tdee = round(bmr * factor, 0)

        safe_weekly_rate = None
        if weight_kg:
            safe_weekly_rate = round(weight_kg * 0.0075, 1)

        return {
            'bmi': bmi,
            'bmi_category': bmi_category,
            'bmr': bmr,
            'tdee': tdee,
            'safe_weekly_rate': safe_weekly_rate,
        }
    
    def _calculate_progress(self, profile_data):
        """Calculate progress percentage from current weight to target weight"""
        current = profile_data.get('weight_kg')
        target = profile_data.get('target_weight_kg')
        goal = profile_data.get('goal', '').lower()
        
        if not current or not target:
            return None
        
        try:
            current_num = float(current)
            target_num = float(target)
        except (ValueError, TypeError):
            return None
        
        if current_num == 0 and target_num == 0:
            return None
        
        diff = abs(current_num - target_num)
        max_weight = max(current_num, target_num)
        
        if max_weight == 0:
            return None
        
        progress = max(0, min(100, round((1 - (diff / max_weight)) * 100)))
        
        if 'weight loss' in goal or 'cut' in goal or 'lose' in goal:
            if current_num <= target_num:
                return 100
        
        if 'muscle building' in goal or 'bulk' in goal or 'gain' in goal:
            if current_num >= target_num:
                return 100
        
        return progress
    
    def build_context(self):
        """Build comprehensive context string from all detected features - ALWAYS returns a clean string"""
        
        def safe_str(value):
            """Convert any value to a safe string representation"""
            if value is None:
                return ""
            if isinstance(value, str):
                return value
            if isinstance(value, (dict, list)):
                # Never return dict/list representation - return empty string instead
                return ""
            return str(value)
        
        def safe_append(parts, text):
            """Safely append text to parts list, ensuring it's a string"""
            if text:
                safe_text = safe_str(text).strip()
                if safe_text:
                    parts.append(safe_text)
        
        # Initialize all context sections as empty strings
        profile_text = ""
        detected_factors_text = ""
        workout_text = ""
        nutrition_text = ""
        pregnancy_text = ""
        disability_text = ""
        inactivity_text = ""
        video_text = ""
        image_text = ""
        notifications_text = ""
        
        # Build profile text
        profile_lines = []
        profile_lines.append(f"User name: {safe_str(self.user_name)}")
        profile_lines.append(f"Age: {safe_str(self.profile_data.get('age', 'Unknown'))}")
        profile_lines.append(f"Gender: {safe_str(self.profile_data.get('gender', 'Unknown'))}")
        profile_lines.append(f"Current weight: {safe_str(self.profile_data.get('weight_kg', 'Unknown'))} kg")
        profile_lines.append(f"Target weight: {safe_str(self.profile_data.get('target_weight_kg', 'Unknown'))} kg")
        profile_lines.append(f"Goal: {safe_str(self.profile_data.get('goal', 'Unknown'))}")
        profile_lines.append(f"Activity level: {safe_str(self.profile_data.get('activity_level', 'Unknown'))}")
        
        if self.progress is not None:
            profile_lines.append(f"Progress: {self.progress:.1f}%")
        
        if self.profile_data.get('health_notes'):
            profile_lines.append(f"Health notes: {safe_str(self.profile_data.get('health_notes'))}")
        
        # Metrics
        if self.metrics.get('bmi'):
            profile_lines.append(f"BMI: {safe_str(self.metrics.get('bmi'))} ({safe_str(self.metrics.get('bmi_category', ''))})")
        if self.metrics.get('tdee'):
            profile_lines.append(f"TDEE: {safe_str(self.metrics.get('tdee'))} kcal/day")
        
        # Preferences
        prefs = self.state.get('preferences', {})
        if prefs.get('food_dislikes'):
            profile_lines.append(f"Food dislikes: {', '.join([safe_str(x) for x in prefs['food_dislikes']])}")
        if prefs.get('allergies'):
            profile_lines.append(f"Allergies: {', '.join([safe_str(x) for x in prefs['allergies']])}")
        if prefs.get('workout_dislikes'):
            profile_lines.append(f"Workout dislikes: {', '.join([safe_str(x) for x in prefs['workout_dislikes']])}")
        
        profile_text = "\n".join(profile_lines)
        
        # Build detected factors text
        detected_lines = []
        if self.emotion and self.emotion != 'neutral':
            detected_lines.append(f"User seems {safe_str(self.emotion)}")
        detected_lines.append(f"User language: {safe_str(self.language)}")
        detected_factors_text = "\n".join(detected_lines)
        
        # Progress adjustments
        progress_adjustment_lines = []
        if detect_workout_completion(self.user_message):
            self.state['workout_count_this_week'] = self.state.get('workout_count_this_week', 0) + 1
            boost = calculate_workout_progress_boost(self.state, self.current_time)
            if boost > 0 and self.base_progress is not None:
                current_adjusted = self.state.get('adjusted_progress', self.base_progress)
                new_progress = adjust_progress(self.state, self.profile_data, self.base_progress, 'workout', boost, self.language)
                if new_progress is not None:
                    progress_change = new_progress - current_adjusted
                    if progress_change > 0:
                        progress_adjustment_lines.append(f"Progress increased by {boost:.1f}% due to workout completion.")
        
        nutrition_adherence = detect_nutrition_adherence(self.user_message)
        if nutrition_adherence:
            self.state['nutrition_adherence'] = nutrition_adherence
            boost = calculate_nutrition_progress_boost(nutrition_adherence)
            if boost > 0 and self.base_progress is not None:
                current_adjusted = self.state.get('adjusted_progress', self.base_progress)
                new_progress = adjust_progress(self.state, self.profile_data, self.base_progress, 'nutrition', boost, self.language)
                if new_progress is not None:
                    progress_change = new_progress - current_adjusted
                    if progress_change > 0:
                        progress_adjustment_lines.append(f"Progress increased by {boost:.1f}% due to nutrition adherence.")
        
        if self.last_workout_ts:
            days_inactive = (self.current_time - self.last_workout_ts).total_seconds() / (24 * 3600)
            if days_inactive >= 2:
                penalty = calculate_inactivity_penalty(days_inactive)
                if penalty < 0 and self.base_progress is not None:
                    current_adjusted = self.state.get('adjusted_progress', self.base_progress)
                    new_progress = adjust_progress(self.state, self.profile_data, self.base_progress, 'inactivity', penalty, self.language)
                    if new_progress is not None:
                        progress_change = new_progress - current_adjusted
                        if progress_change < 0:
                            progress_adjustment_lines.append(f"Progress decreased by {abs(penalty):.1f}% due to inactivity.")
        
        if progress_adjustment_lines:
            detected_factors_text += "\n" + "\n".join(progress_adjustment_lines)
        
        # Extract preferences
        preferences_found = extract_preferences(self.user_message)
        if preferences_found:
            merge_preferences(self.state['preferences'], preferences_found)
        
        # Inactivity info
        inactivity_lines = []
        if self.last_workout_ts:
            workout_inactivity_days = (self.current_time - self.last_workout_ts).total_seconds() / (24 * 3600)
            if workout_inactivity_days > 2:
                inactivity_lines.append(f"User hasn't logged a workout in {int(workout_inactivity_days)} days")
        
        is_first_message = self.state.get('last_interaction') is None
        if not is_first_message and self.state.get('last_interaction'):
            chat_inactivity_hours = (self.current_time - self.state['last_interaction']).total_seconds() / 3600
            if chat_inactivity_hours > 24:
                inactivity_lines.append(f"User hasn't chatted in {int(chat_inactivity_hours)} hours")
        
        inactivity_text = "\n".join(inactivity_lines)
        
        # Disability detection and context
        disability_info = self.state.get('disability_info', {})
        detected_disability = detect_disability_info(self.user_message)
        if detected_disability:
            disability_info.update(detected_disability)
            self.state['disability_info'] = disability_info
        
        has_special_needs = any([
            disability_info.get('mobility_challenges'),
            disability_info.get('difficulty_standing'),
            disability_info.get('wheelchair_use'),
            disability_info.get('joint_pain'),
            disability_info.get('spine_issues'),
            disability_info.get('balance_issues'),
        ])
        
        if has_special_needs:
            disability_context = build_disability_adaptive_context(
                disability_info, self.profile_data, self.metrics, self.language
            )
            if disability_context:
                disability_text = safe_str(disability_context)
        
        # Accessibility mode
        accessibility_mode = self.state.get('accessibility_mode', {})
        detected_accessibility = detect_accessibility_mode(self.user_message, self.request_data)
        if detected_accessibility:
            accessibility_mode['enabled'] = True
            accessibility_mode['voice_friendly'] = True
            if detected_accessibility == 'blind':
                accessibility_mode['visual_impairment'] = 'blind'
            elif detected_accessibility == 'low_vision':
                accessibility_mode['visual_impairment'] = 'low_vision'
            elif detected_accessibility == 'enable':
                if 'blind' in self.user_message.lower() or 'كفيف' in self.user_message.lower():
                    accessibility_mode['visual_impairment'] = 'blind'
                else:
                    accessibility_mode['visual_impairment'] = 'low_vision'
            self.state['accessibility_mode'] = accessibility_mode
        
        if accessibility_mode.get('enabled', False):
            accessibility_context = build_accessibility_context(accessibility_mode, self.profile_data, self.language)
            if accessibility_context:
                if not disability_text:
                    disability_text = safe_str(accessibility_context)
                else:
                    disability_text += "\n" + safe_str(accessibility_context)
        
        # Deaf mode
        deaf_mode = self.state.get('deaf_mode', {})
        detected_deaf = detect_deaf_mode(self.user_message, self.request_data)
        if detected_deaf:
            deaf_mode['enabled'] = True
            if detected_deaf == 'deaf':
                deaf_mode['hearing_impairment'] = 'deaf'
            elif detected_deaf == 'hard_of_hearing':
                deaf_mode['hearing_impairment'] = 'hard_of_hearing'
            elif detected_deaf == 'enable':
                if 'deaf' in self.user_message.lower() or 'أصم' in self.user_message.lower():
                    deaf_mode['hearing_impairment'] = 'deaf'
                else:
                    deaf_mode['hearing_impairment'] = 'hard_of_hearing'
            self.state['deaf_mode'] = deaf_mode
        
        if deaf_mode.get('enabled', False):
            deaf_context = build_deaf_mode_context(deaf_mode, self.profile_data, self.language)
            if deaf_context:
                if not disability_text:
                    disability_text = safe_str(deaf_context)
                else:
                    disability_text += "\n" + safe_str(deaf_context)
        
        # Pregnancy mode
        pregnancy_mode = self.state.get('pregnancy_mode', {})
        detected_pregnancy = detect_pregnancy_mode(self.user_message, self.request_data)
        
        pregnancy_safety_alert = check_pregnancy_safety_alerts(self.user_message, self.language)
        if pregnancy_safety_alert:
            pregnancy_text = f"CRITICAL SAFETY ALERT: {safe_str(pregnancy_safety_alert)}"
        
        if detected_pregnancy and not pregnancy_mode.get('enabled', False):
            pregnancy_info = extract_pregnancy_info(self.user_message)
            if pregnancy_info.get('trimester'):
                pregnancy_mode['enabled'] = True
                pregnancy_mode['trimester'] = pregnancy_info.get('trimester')
                if 'pregnancy_notes' not in pregnancy_mode:
                    pregnancy_mode['pregnancy_notes'] = []
                if 'pain_notes' not in pregnancy_mode:
                    pregnancy_mode['pain_notes'] = []
                if pregnancy_info.get('fatigue'):
                    pregnancy_mode['pregnancy_notes'].append('fatigue')
                if pregnancy_info.get('pain'):
                    pregnancy_mode['pain_notes'].append('general pain')
                self.state['pregnancy_mode'] = pregnancy_mode
        
        if pregnancy_mode.get('enabled', False):
            pregnancy_info = extract_pregnancy_info(self.user_message)
            if pregnancy_info.get('trimester'):
                pregnancy_mode['trimester'] = pregnancy_info.get('trimester')
            if 'pregnancy_notes' not in pregnancy_mode:
                pregnancy_mode['pregnancy_notes'] = []
            if 'pain_notes' not in pregnancy_mode:
                pregnancy_mode['pain_notes'] = []
            if pregnancy_info.get('fatigue'):
                pregnancy_mode['pregnancy_notes'].append('fatigue')
            if pregnancy_info.get('pain'):
                pregnancy_mode['pain_notes'].append('general pain')
            self.state['pregnancy_mode'] = pregnancy_mode
        
        if pregnancy_mode.get('enabled', False) and pregnancy_mode.get('trimester'):
            pregnancy_context = build_pregnancy_mode_context(pregnancy_mode, self.profile_data, self.metrics, self.language)
            if pregnancy_context:
                if pregnancy_text:
                    pregnancy_text += "\n" + safe_str(pregnancy_context)
                else:
                    pregnancy_text = safe_str(pregnancy_context)
        
        # Postpartum mode
        postpartum_mode = self.state.get('postpartum_mode', {})
        detected_postpartum = detect_postpartum_mode(self.user_message, self.request_data)
        
        postpartum_safety_alert = check_postpartum_safety_alerts(self.user_message, self.language)
        if postpartum_safety_alert:
            if pregnancy_text:
                pregnancy_text += f"\nCRITICAL SAFETY ALERT: {safe_str(postpartum_safety_alert)}"
            else:
                pregnancy_text = f"CRITICAL SAFETY ALERT: {safe_str(postpartum_safety_alert)}"
        
        if detected_postpartum and not postpartum_mode.get('enabled', False):
            postpartum_info = extract_postpartum_info(self.user_message)
            if postpartum_info.get('delivery_type') and (postpartum_info.get('weeks_postpartum') or postpartum_info.get('days_postpartum')):
                postpartum_mode['enabled'] = True
                postpartum_mode['delivery_type'] = postpartum_info.get('delivery_type')
                postpartum_mode['weeks_postpartum'] = postpartum_info.get('weeks_postpartum')
                postpartum_mode['days_postpartum'] = postpartum_info.get('days_postpartum')
                postpartum_mode['breastfeeding'] = postpartum_info.get('breastfeeding')
                phase = calculate_postpartum_phase(
                    postpartum_mode['weeks_postpartum'],
                    postpartum_mode['days_postpartum'],
                    postpartum_mode['delivery_type']
                )
                if phase:
                    postpartum_mode['phase'] = phase
                self.state['postpartum_mode'] = postpartum_mode
        
        if postpartum_mode.get('enabled', False):
            postpartum_info = extract_postpartum_info(self.user_message)
            if postpartum_info.get('delivery_type'):
                postpartum_mode['delivery_type'] = postpartum_info.get('delivery_type')
            if postpartum_info.get('weeks_postpartum'):
                postpartum_mode['weeks_postpartum'] = postpartum_info.get('weeks_postpartum')
            if postpartum_info.get('days_postpartum'):
                postpartum_mode['days_postpartum'] = postpartum_info.get('days_postpartum')
            if postpartum_info.get('breastfeeding') is not None:
                postpartum_mode['breastfeeding'] = postpartum_info.get('breastfeeding')
            if postpartum_info.get('weeks_postpartum') or postpartum_info.get('days_postpartum'):
                phase = calculate_postpartum_phase(
                    postpartum_mode.get('weeks_postpartum'),
                    postpartum_mode.get('days_postpartum'),
                    postpartum_mode.get('delivery_type')
                )
                if phase:
                    postpartum_mode['phase'] = phase
            self.state['postpartum_mode'] = postpartum_mode
        
        if postpartum_mode.get('enabled', False) and postpartum_mode.get('phase'):
            postpartum_context = build_postpartum_mode_context(postpartum_mode, self.profile_data, self.metrics, self.language)
            if postpartum_context:
                if pregnancy_text:
                    pregnancy_text += "\n" + safe_str(postpartum_context)
                else:
                    pregnancy_text = safe_str(postpartum_context)
        
        # Diastasis mode
        diastasis_mode = self.state.get('diastasis_mode', {})
        detected_diastasis = detect_diastasis_mode(self.user_message, self.request_data)
        
        diastasis_safety_alert = check_diastasis_safety_alerts(self.user_message, self.language)
        if diastasis_safety_alert:
            if pregnancy_text:
                pregnancy_text += f"\nCRITICAL SAFETY ALERT: {safe_str(diastasis_safety_alert)}"
            else:
                pregnancy_text = f"CRITICAL SAFETY ALERT: {safe_str(diastasis_safety_alert)}"
        
        if detected_diastasis and not diastasis_mode.get('enabled', False):
            diastasis_info = extract_diastasis_info(self.user_message)
            if diastasis_info.get('separation_fingers') and (diastasis_info.get('weeks_postpartum') or diastasis_info.get('days_postpartum')):
                diastasis_mode['enabled'] = True
                diastasis_mode['separation_fingers'] = diastasis_info.get('separation_fingers')
                diastasis_mode['weeks_postpartum'] = diastasis_info.get('weeks_postpartum')
                diastasis_mode['days_postpartum'] = diastasis_info.get('days_postpartum')
                stage = calculate_diastasis_stage(
                    diastasis_mode['weeks_postpartum'],
                    diastasis_mode['days_postpartum'],
                    diastasis_info.get('separation_severity')
                )
                if stage:
                    diastasis_mode['stage'] = stage
                self.state['diastasis_mode'] = diastasis_mode
        
        if diastasis_mode.get('enabled', False):
            diastasis_info = extract_diastasis_info(self.user_message)
            if diastasis_info.get('separation_fingers'):
                diastasis_mode['separation_fingers'] = diastasis_info.get('separation_fingers')
            if diastasis_info.get('weeks_postpartum'):
                diastasis_mode['weeks_postpartum'] = diastasis_info.get('weeks_postpartum')
            if diastasis_info.get('days_postpartum'):
                diastasis_mode['days_postpartum'] = diastasis_info.get('days_postpartum')
            if diastasis_info.get('weeks_postpartum') or diastasis_info.get('days_postpartum'):
                stage = calculate_diastasis_stage(
                    diastasis_mode.get('weeks_postpartum'),
                    diastasis_mode.get('days_postpartum'),
                    diastasis_info.get('separation_severity')
                )
                if stage:
                    diastasis_mode['stage'] = stage
            self.state['diastasis_mode'] = diastasis_mode
        
        if diastasis_mode.get('enabled', False) and diastasis_mode.get('stage'):
            diastasis_context = build_diastasis_mode_context(diastasis_mode, self.profile_data, self.metrics, self.language)
            if diastasis_context:
                if pregnancy_text:
                    pregnancy_text += "\n" + safe_str(diastasis_context)
                else:
                    pregnancy_text = safe_str(diastasis_context)
        
        # Equipment context
        if detect_gym_equipment_request(self.user_message, self.request_data):
            equipment_key = recognize_equipment_from_text(self.user_message)
            if equipment_key:
                equipment_context = build_equipment_instructions_context(equipment_key, self.language)
                if equipment_context:
                    workout_text = safe_str(equipment_context)
        
        # Adaptive plan context
        if should_offer_adaptive_plan(self.user_message, self.emotion, self.last_workout_ts, self.current_time, self.state):
            adaptive_context = get_adaptive_plan_context(
                self.profile_data, self.metrics, self.state, self.last_workout_ts, self.current_time, self.language, self._calculate_progress
            )
            if adaptive_context:
                if workout_text:
                    workout_text += "\n" + safe_str(adaptive_context)
                else:
                    workout_text = safe_str(adaptive_context)
        
        # Adaptive nutrition context
        if should_offer_adaptive_nutrition(self.user_message, self.emotion, self.last_workout_ts, self.current_time, self.state):
            nutrition_context = get_adaptive_nutrition_context(
                self.profile_data, self.metrics, self.state, self.last_workout_ts, self.current_time, self.language, self.user_message, self.emotion, self._calculate_progress
            )
            if nutrition_context:
                nutrition_text = safe_str(nutrition_context)
        
        # Video recommendations
        if should_suggest_video(self.user_message, self.state, self.emotion):
            current_pregnancy_mode = self.state.get('pregnancy_mode', {})
            current_postpartum_mode = self.state.get('postpartum_mode', {})
            current_diastasis_mode = self.state.get('diastasis_mode', {})
            current_accessibility_mode = self.state.get('accessibility_mode', {})
            current_disability_info = self.state.get('disability_info', {})
            current_has_special_needs = any([
                current_disability_info.get('mobility_challenges'),
                current_disability_info.get('difficulty_standing'),
                current_disability_info.get('wheelchair_use'),
                current_disability_info.get('joint_pain'),
                current_disability_info.get('spine_issues'),
                current_disability_info.get('balance_issues'),
            ])
            
            video = None
            if current_pregnancy_mode.get('enabled', False):
                video = get_pregnancy_video_recommendation(self.state, self.language)
            elif current_postpartum_mode.get('enabled', False):
                video = get_postpartum_video_recommendation(self.state, self.language)
            elif current_diastasis_mode.get('enabled', False):
                video = get_diastasis_video_recommendation(self.state, self.language)
            elif current_has_special_needs:
                video = get_adaptive_video_recommendation(self.state, current_disability_info, self.language)
            elif detect_gym_equipment_request(self.user_message, self.request_data):
                video = get_equipment_video_recommendation(self.state, self.language)
            else:
                video = get_video_recommendation(self.state, self.profile_data, self.language)
            
            if video:
                video_info = format_video_info(video, self.language)
                if video_info:
                    video_text = f"Video recommendation: {safe_str(video_info)}"
        
        # Image recommendations
        if should_suggest_image(self.user_message):
            current_accessibility_mode = self.state.get('accessibility_mode', {})
            current_disability_info = self.state.get('disability_info', {})
            current_has_special_needs = any([
                current_disability_info.get('mobility_challenges'),
                current_disability_info.get('difficulty_standing'),
                current_disability_info.get('wheelchair_use'),
                current_disability_info.get('joint_pain'),
                current_disability_info.get('spine_issues'),
                current_disability_info.get('balance_issues'),
            ])
            is_blind = current_accessibility_mode.get('visual_impairment') == 'blind'
            if is_blind:
                exercise_name = "exercise"
                audio_desc = get_audio_exercise_description(exercise_name, self.language)
                image_text = f"User is BLIND. Provide audio description: {safe_str(audio_desc)}"
            else:
                if current_has_special_needs:
                    image = get_adaptive_exercise_image(current_disability_info)
                else:
                    image = get_exercise_image(self.user_message, self.state)
                if image:
                    image_name = safe_str(image.get('name', ''))
                    image_url = safe_str(image.get('url', ''))
                    image_desc = safe_str(image.get('description', ''))
                    image_text = f"Exercise image: {image_name} - {image_url} - {image_desc}"
        
        # Notifications
        notifications = generate_notifications(self.state, self.current_time)
        if notifications:
            notifications_text = f"System reminders: {', '.join([safe_str(n) for n in notifications])}"
        
        # Build final context string - ALWAYS return a string
        final_parts = []
        if profile_text:
            final_parts.append(f"User profile:\n{profile_text}")
        if detected_factors_text:
            final_parts.append(f"Detected factors:\n{detected_factors_text}")
        if workout_text:
            final_parts.append(f"Workout context:\n{workout_text}")
        if nutrition_text:
            final_parts.append(f"Nutrition context:\n{nutrition_text}")
        if pregnancy_text:
            final_parts.append(f"Pregnancy context:\n{pregnancy_text}")
        if disability_text:
            final_parts.append(f"Disability context:\n{disability_text}")
        if inactivity_text:
            final_parts.append(f"Inactivity context:\n{inactivity_text}")
        if video_text:
            final_parts.append(f"Video context:\n{video_text}")
        if image_text:
            final_parts.append(f"Image context:\n{image_text}")
        if notifications_text:
            final_parts.append(f"Notifications:\n{notifications_text}")
        
        final_parts.append(f"User message: {safe_str(self.user_message)}")
        
        # Join all parts and return as single string
        return "\n\n".join(final_parts)
    
    def generate(self):
        """Generate AI response by calling OpenAI API"""
        # Build context
        context = self.build_context()
        
        # Get API key
        api_key = os.environ.get('OPENAI_API_KEY', '').strip().strip('"').strip("'")
        if not api_key or api_key == 'your-openai-api-key-here' or api_key == 'your-openai-api-key':
            raise ValueError('OpenAI API key is not configured')
        
        # Replace user name placeholder in system prompt
        system_prompt_filled = SYSTEM_PROMPT.replace("{{user_name}}", self.user_name)
        
        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt_filled},
            {"role": "user", "content": context},
        ]
        
        # Call OpenAI API
        payload = {
            "model": "gpt-4.1",
            "input": messages,
            "temperature": 0.7,
            "max_output_tokens": 400,
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
                timeout=30,
            )
        except requests.RequestException as exc:
            raise Exception(f'OpenAI API request failed: {exc}')
        
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', response.text) if isinstance(error_data, dict) else response.text
            except:
                error_message = response.text
            
            raise Exception(f'OpenAI API error (Status {response.status_code}): {error_message[:500]}')
        
        try:
            completion = response.json()
        except ValueError:
            raise Exception('Invalid response from OpenAI')
        
        content = extract_response_text(completion).strip()
        if not content:
            raise Exception('Empty response from OpenAI')
        
        # Format for accessibility if needed
        accessibility_mode = self.state.get('accessibility_mode', {})
        if accessibility_mode.get('enabled', False) and accessibility_mode.get('voice_friendly', False):
            content = format_voice_friendly_response(content)
        
        # Update state
        self.state['last_interaction'] = self.current_time
        self.state['last_chat_message'] = self.current_time
        self.state['last_chat_page_open'] = self.current_time
        USER_BEHAVIOR_STATE[self.user.id] = self.state
        
        return content


class _OpenAIHandler:
    """Django view handler that uses AIEngine"""
    
    def post(self, request):
        data = request.data or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            engine = AIEngine(request.user, user_message, data)
            content = engine.generate()
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        
        # Build response data
        response_data = {'message': content}
        
        # Add mode flags if active
        state = engine.state
        if state.get('accessibility_mode', {}).get('enabled', False):
            response_data['accessibility_mode'] = True
            response_data['visual_impairment'] = state['accessibility_mode'].get('visual_impairment', 'none')
        
        if state.get('deaf_mode', {}).get('enabled', False):
            response_data['deaf_mode'] = True
            response_data['hearing_impairment'] = state['deaf_mode'].get('hearing_impairment', 'none')
        
        if state.get('postpartum_mode', {}).get('enabled', False):
            response_data['postpartum_mode'] = True
            response_data['phase'] = state['postpartum_mode'].get('phase')
        
        if state.get('diastasis_mode', {}).get('enabled', False):
            response_data['diastasis_mode'] = True
            response_data['stage'] = state['diastasis_mode'].get('stage')
        
        return Response(response_data, status=status.HTTP_200_OK)


def generate_ai_response(user, message, request_data):
    """Legacy function for backward compatibility"""
    handler = _OpenAIHandler()
    payload = dict(request_data or {})
    if message is not None:
        payload['message'] = message
    fake_request = _AIRequest(user=user, data=payload)
    return handler.post(fake_request)

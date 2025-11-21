import random

from .prompts import EXERCISE_VIDEOS


def format_clickable_video_url(url: str) -> str:
    """Format a video URL as a clickable HTML link"""
    return f"<a href='{url}' target='_blank'>{url}</a>"


def should_suggest_video(user_message, state, emotion):
    """Determine if AI should suggest a video"""
    if not user_message:
        return False
    
    lowered = user_message.lower()
    
    # User explicitly asks for video
    video_keywords = [
        'فيديو', 'video', 'يوتيوب', 'youtube', 'تمرين فيديو', 'workout video',
        'أعطني فيديو', 'give me video', 'فيديو تمرين', 'exercise video',
    ]
    if any(keyword in lowered for keyword in video_keywords):
        return True
    
    # User seems stuck or unmotivated
    stuck_keywords = [
        'ما أعرف', 'don\'t know', 'محتارة', 'confused', 'ما أعرف كيف',
        'help me', 'ساعدني', 'lost', 'ضايعة', 'stuck',
    ]
    if any(keyword in lowered for keyword in stuck_keywords) and emotion in ['unmotivated', 'tired', 'stressed']:
        return True
    
    return False


def get_video_recommendation(state, profile_data, language):
    """Get a non-repeating video recommendation"""
    preferences = state.get('preferences', {})
    injuries = preferences.get('injuries', [])
    workout_dislikes = preferences.get('workout_dislikes', [])
    used_videos = state.get('used_videos', [])
    
    # Filter videos based on injuries and dislikes
    available_videos = []
    for video in EXERCISE_VIDEOS:
        # Skip if video title contains disliked exercise
        skip = False
        for dislike in workout_dislikes:
            if dislike.lower() in video['title'].lower():
                skip = True
                break
        if skip:
            continue
        
        # Skip if already used
        if video['title'] in used_videos:
            continue
        
        available_videos.append(video)
    
    # If all videos used, reset and start over
    if not available_videos:
        available_videos = EXERCISE_VIDEOS
        used_videos = []
    
    # Select random video
    selected = random.choice(available_videos)
    used_videos.append(selected['title'])
    state['used_videos'] = used_videos
    
    return selected


def format_video_info(video, language=None):
    """Format video information with clickable URL"""
    if not video or not isinstance(video, dict):
        return None
    
    # Format the link as clickable URL
    clickable_link = format_clickable_video_url(video.get('link', ''))
    
    video_info = (
        f"Title: {video.get('title', 'N/A')}\n"
        f"Duration: {video.get('duration', 'N/A')}\n"
        f"Difficulty: {video.get('difficulty', 'N/A')}\n"
        f"Link: {clickable_link}\n"
        f"Description: {video.get('description', 'N/A')}"
    )
    
    return video_info



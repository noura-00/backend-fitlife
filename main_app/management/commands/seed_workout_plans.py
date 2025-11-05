from django.core.management.base import BaseCommand
from main_app.models import WorkoutPlan

class Command(BaseCommand):
    help = 'Create predefined workout plans for each goal'

    def handle(self, *args, **options):
        # Delete existing general plans (plans without user) to avoid duplicates
        deleted_count = WorkoutPlan.objects.filter(user=None).delete()[0]
        self.stdout.write(
            self.style.WARNING(f'Deleted {deleted_count} existing general plans')
        )

        workout_plans = [
            {
                'title': 'Weight Loss Plan - Beginners',
                'goal_type': 'cut',
                'duration': 8,
                'description': 'Comprehensive workout plan for weight loss and fat burning for beginners. Focuses on cardio exercises and light strength training.',
                'equipment_needed': 'Light weights (2-5 kg), exercise mat, jump rope',
                'notes': '''📋 Weekly Plan:
• Days 1, 3, 5: Strength Training (30 minutes)
  - Squats: 3 sets × 10-12 reps
  - Push-ups: 3 sets × 8-10 reps
  - Lunges: 3 sets × 10 reps per leg
  - Plank: 3 sets × 30 seconds
  
• Days 2, 4: Cardio (20-30 minutes)
  - Brisk walking or light jogging: 20-30 minutes
  - Jump rope: 3 sets × 1 minute
  
• Rest days: 6, 7

💡 Important Tips:
• Start slowly and gradually increase intensity
• Make sure to drink water before, during, and after exercise
• Eat a light protein-rich meal after exercise
• Adequate sleep (7-8 hours) is very important for fat burning
• Monitor calories along with exercise'''
            },
            {
                'title': 'Weight Loss Plan - Advanced',
                'goal_type': 'cut',
                'duration': 12,
                'description': 'Intensive plan for advanced level to lose weight quickly while maintaining muscle mass.',
                'equipment_needed': 'Medium to heavy weights (5-15 kg), treadmill or bike, exercise mat',
                'notes': '''📋 Weekly Plan:
• Days 1, 3, 5: Intensive Strength Training (45-60 minutes)
  - Heavy squats: 4 sets × 6-8 reps
  - Incline push-ups: 4 sets × 10-12 reps
  - Deadlift: 4 sets × 6-8 reps
  - Pull-ups: 4 sets × 8-10 reps
  - Intensive lunges: 4 sets × 12 reps
  
• Days 2, 4, 6: HIIT Training (20-30 minutes)
  - Warm-up: 5 minutes light jogging
  - Interval training: 30 seconds intense exercise + 30 seconds rest
  - Exercises: Burpees, Jump Squats, Mountain Climbers, High Knees
  - Cool-down: 5 minutes light walking
  
• Rest day: 7

💡 Important Tips:
• Ensure adequate nutrition to maintain muscles
• Consume 2-2.5 grams of protein per kg of body weight
• Reduce carbohydrates in the evening
• HIIT exercises burn more calories even after the workout
• Weigh yourself every week at the same time and same conditions'''
            },
            {
                'title': 'Muscle Building Plan - Beginners',
                'goal_type': 'bulk',
                'duration': 12,
                'description': 'Comprehensive plan for building muscle and strength for beginners. Focuses on compound basic exercises.',
                'equipment_needed': 'Barbell, free weights, bench, pull-up bar',
                'notes': '''📋 Weekly Plan (3-4 days):
• Day 1: Chest and Triceps (45 minutes)
  - Barbell bench press: 4 sets × 8-10 reps
  - Incline press: 3 sets × 10-12 reps
  - Dumbbell press: 3 sets × 10-12 reps
  - Triceps exercises: 3 sets × 10-12 reps
  
• Day 2: Back and Biceps (45 minutes)
  - Deadlift: 4 sets × 6-8 reps
  - Pull-ups: 4 sets × 8-10 reps
  - Rows: 3 sets × 10-12 reps
  - Biceps exercises: 3 sets × 10-12 reps
  
• Day 3: Legs and Shoulders (45 minutes)
  - Squats: 4 sets × 8-10 reps
  - Lunges: 3 sets × 12 reps
  - Shoulder exercises: 3 sets × 10-12 reps
  - Leg raises: 3 sets × 12-15 reps

💡 Important Tips:
• Focus on basic exercises (Squat, Bench Press, Deadlift)
• Gradually increase weight every week
• Rest 60-90 seconds between sets
• Eat a protein-rich meal (30-40g) after exercise
• Get 7-9 hours of sleep daily for muscle growth'''
            },
            {
                'title': 'Muscle Building Plan - Advanced',
                'goal_type': 'bulk',
                'duration': 16,
                'description': 'Advanced training program to increase muscle mass and maximize workout benefits.',
                'equipment_needed': 'Barbell, free weights of all sizes, multi-function bench',
                'notes': '''📋 Weekly Plan (5-6 days):
• Day 1: Chest and Triceps
• Day 2: Back and Biceps
• Day 3: Legs (including heavy squats)
• Day 4: Shoulders and Traps
• Day 5: Arms (intensive triceps and biceps)
• Day 6: Light cardio or active rest
• Day 7: Complete rest

💪 Basic exercises for each muscle group:
• Chest: Bench Press, Incline Press, Dumbbell Flyes
• Back: Deadlift, Pull-ups, Barbell Rows, T-Bar Rows
• Legs: Squats, Leg Press, Lunges, Leg Curls, Calf Raises
• Shoulders: Overhead Press, Lateral Raises, Rear Delt Flyes
• Arms: Barbell Curls, Tricep Dips, Hammer Curls

💡 Important Tips:
• Use Progressive Overload principle (gradually increase load)
• Nutrition division: 6-8 meals daily, 2.5-3g protein/kg
• Muscle rest: 48-72 hours between training the same group
• Useful supplements: protein, creatine, vitamin D
• Track your progress: write down weights and reps for each exercise'''
            },
            {
                'title': 'Weight Maintenance Plan',
                'goal_type': 'maintain',
                'duration': 4,
                'description': 'Balanced plan to maintain your current weight and improve overall fitness.',
                'equipment_needed': 'Light to medium weights, exercise mat',
                'notes': '''📋 Weekly Plan (4-5 days):
• Days 1, 3, 5: Strength Training (30-40 minutes)
  - Full body exercises: Squats, Push-ups, Rows, Shoulder Press
  - 3 sets × 10-15 reps per exercise
  - 45-60 seconds rest between sets
  
• Days 2, 4: Cardio (30-45 minutes)
  - Brisk walking, jogging, cycling, or swimming
  - Choose an activity you enjoy
  
• Rest days: 6, 7 (or at least one day)

💡 Important Tips:
• Maintain daily activity: use stairs, walk more
• Eat balanced meals with protein, carbs, and healthy fats
• Monitor your weight weekly to ensure stability
• Adjust exercise intensity according to your needs
• Enjoy physical activity - this is the secret to consistency'''
            },
            {
                'title': 'Home Workouts Without Equipment - Beginners',
                'goal_type': 'home',
                'duration': 6,
                'description': 'Complete workout plan that can be performed at home without any equipment. Perfect for beginners.',
                'equipment_needed': 'None - bodyweight exercises',
                'notes': '''📋 Weekly Plan (4-5 days):
• Warm-up: 5 minutes marching in place + stretching exercises

• Days 1, 3, 5: Strength Training (20-30 minutes)
  1. Push-ups: 3 sets × 5-10 reps
  2. Squats: 3 sets × 10-15 reps
  3. Plank: 3 sets × 20-30 seconds
  4. Lunges: 3 sets × 10 reps per leg
  5. Leg raises: 3 sets × 10-15 reps
  6. Bridge: 3 sets × 10-15 reps

• Days 2, 4: Cardio (15-20 minutes)
  - Jumping in place: 30 seconds × 5 times
  - Running in place: 30 seconds × 5 times
  - Jumping Jacks: 30 seconds × 5 times
  - High Knees: 30 seconds × 5 times

• Rest days: 6, 7

💡 Important Tips:
• Start with easy exercises then gradually increase difficulty
• Use motivating music to boost enthusiasm
• Designate a comfortable space at home for exercise
• You can increase difficulty by adding reps or extending exercise duration
• Drink water continuously during exercise'''
            },
            {
                'title': 'Home Workouts Without Equipment - Advanced',
                'goal_type': 'home',
                'duration': 8,
                'description': 'Advanced exercises without equipment to build strength and endurance at home.',
                'equipment_needed': 'None - bodyweight exercises',
                'notes': '''📋 Weekly Plan (5-6 days):

• Days 1, 3, 5: Advanced Strength Training (30-45 minutes)
  1. Advanced Push-ups: Diamond Push-ups, Decline Push-ups (4 sets × 10-15)
  2. Advanced Squats: Jump Squats, Pistol Squats (4 sets × 15-20)
  3. Advanced Plank: Side Plank, Plank Up-Down (4 sets × 45-60 seconds)
  4. Burpees: 4 sets × 10-15 reps
  5. Mountain Climbers: 4 sets × 30-45 seconds
  6. Pull-ups (if you have a bar): 4 sets × 8-12 reps
  
• Days 2, 4, 6: HIIT Training (20-30 minutes)
  - Warm-up: 5 minutes
  - 8 exercises × 45 seconds exercise + 15 seconds rest
  - Exercises: Burpees, Jump Squats, Push-ups, High Knees, 
              Mountain Climbers, Plank Jacks, Jumping Lunges, Side Planks
  - Cool-down: 5 minutes stretching exercises

💡 Important Tips:
• Plyometric exercises improve power, jumping, and speed
• Monitor exercise intensity - should be difficult but manageable
• Use a Timer to organize time precisely
• Gradually increase difficulty by adding reps or reducing rest times
• Bodyweight exercises are very effective for building functional strength'''
            },
        ]

        created_count = 0
        for plan_data in workout_plans:
            plan, created = WorkoutPlan.objects.get_or_create(
                title=plan_data['title'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new workout plans')
        )


"""Static prompts, templates, and message pools for FitLife AI."""

SYSTEM_PROMPT = """
You are FitLife AI Coach — a smart, natural, friendly Saudi fitness & nutrition coach who adapts your tone based on the user's message. 

You reply like a real person, not a bot.



===========================

NAME USAGE RULES

===========================

- DO NOT mention the user's name in every reply.

- ONLY use the user's name when:

    • greeting them directly

    • comforting them (fear, pain, pregnancy, stress)

    • beginning a sensitive explanation

    • situations where using the name feels natural and NOT repetitive

- Never use the name at the end of a message.

- Use the name exactly as provided by the authenticated user.



===========================

GREETING RULES

===========================

Recognize all greeting words automatically:

"hii", "hi", "hey", "hello", "هلا", "أهلين", "اهلين", "مرحبا", 

"السلام", "السلام عليكم", "صباح الخير", "مساء الخير"



Reply naturally:

Arabic: "هلا، كيف أقدر أساعدك؟" 

English: "Hey! How can I help you?"



Keep it human, friendly, short, and not repetitive.



===========================

TONE RULES (ADAPTIVE)

===========================

- Pregnancy or health concerns → gentle, respectful, medically safe.

- Motivation → warm, supportive, not exaggerated.

- Workouts → clear, practical, professional.

- Pain/Stress/Tired → soft, understanding.

- Casual chat → friendly Saudi dialect.



===========================

LANGUAGE RULES

===========================

- User writes Arabic → reply in Saudi Arabic.

- User writes English → reply in simple English.

- Mixed message → reply mainly Arabic unless user prefers English.

- Do NOT mix languages unless the user does.



===========================

LENGTH RULES

===========================

- Normal reply: 1–2 sentences max.

- Plans/workouts: 3–6 short lines.

- No long paragraphs unless user explicitly asks.



===========================

BEHAVIOR RULES

===========================

- Never sound robotic or formal.

- Never repeat the same phrase twice.

- Never use generic AI lines ("as an AI", "by analyzing", etc).

- Respond based on context and user's feelings.



===========================

CLICKABLE LINK RULES

===========================

- ALL video links MUST be in clean clickable HTML format:

  <a href="URL" target="_blank">اضغطي هنا</a>



- NEVER send plain raw URLs.



===========================

SAFETY

===========================

If user mentions: pregnancy, pain, dizziness, bleeding → give SAFE advice only.

No medical diagnosis. 

No dangerous exercise suggestions.



===========================

EXAMPLES OF GOOD RESPONSES

===========================

Greeting:

"هلا! كيف أقدر أفيدك اليوم؟"



Pregnancy:

"تمام، خليني أعطيك شي آمن يناسب أسبوعك."



Workout:

"أقترح تمارين خفيفة، دقيقة دقيقة، بدون ضغط."



Motivation:

"ولا يهمك، نضبطها خطوة بخطوة."

"""

NEW_USER_GREETINGS = [
    'هلا {name}! 🤍 جاهزين نبدأ رحلتك على راحتك؟',
    'مرحباً {name}! حماس إنك معنا… يلا نبدأ ونبني خطة تناسبك 100%.',
    'يا أهلاً {name}! سعيدة أكون مدربتك وداعمتك، يلا ننطلق بخطوات بسيطة.',
    'هلا فيك {name}! اليوم أول خطوة لبداية أفضل، مستعدة؟',
    '{name}! 🤍 جاهزة نبدأ شيء يغير يومك؟ أنا هنا معك طول الطريق.',
]

RETURNING_USER_GREETINGS = [
    'ياهلا {name}! أشوفك ثابتة 👏 استمري، تقدّمك واضح.',
    'رجعتي يا {name}! دائماً مبسوطة بشوفتك هنا 🤍',
    '{name}! حضورك هنا يعني إنك مصممة، فخورة فيك.',
    'هلا {name}! كل مرة ترجعين فيها، تقربين خطوة من هدفك.',
    '{name}! 🔥 اشتقنا لطلتك… جاهزة نكمل الخطة؟',
    'رجعتي يا {name}، وهذا أهم شيء… الاستمرار!',
    'ياهلا وألف مرحبا {name}! تقدّمك الفترة الأخيرة يُفرح!',
]

MOTIVATION_PHRASES = [
    'خطوات بسيطة، نتائج كبيرة… استمري 🩵',
    'كل يوم تحسين فيه عافية… انتِ قدّها.',
    'شوي شوي، أهم شيء ما توقفين.',
    'أفتخر فيك والله… جهدك يبان.',
    'شغلك ممتاز، بس الاستمرار هو السر.',
    'ترى ما تحتاجين تكونين مثالية… بس مستمرة.',
    'قربتي كثير! لا تستهينين بنفسك.',
]

PROGRESS_MESSAGES_0_25 = [
    'بداية ممتازة يا {name}! أهم شيء إنك بدأتي.',
    'استمري على هالوتيرة يا {name}، الطريق قدامك بس انتي قادرة.',
]

PROGRESS_MESSAGES_26_60 = [
    'شغلك واضح يا {name}! قاعدة تتقدمين بشكل جميل.',
    'أشوف تقدّم قوي… استمري ونوصل لهدفك سوا.',
]

PROGRESS_MESSAGES_61_85 = [
    'قربتي كثير يا {name}! باقي شوي وتحققين الهدف.',
    'اللي تسوينه رهيب… قربتي تخلصين المشوار.',
]

PROGRESS_MESSAGES_86_99 = [
    'يا {name}! والله ما بقي إلا شوي! استمري مثل ما انتي.',
    'قربتي توصلين، لا توقفين الحين!',
]

PROGRESS_MESSAGES_100 = [
    'مبرووووك يا {name}! وصلتي لهدفك! فخورة فيك مرة 🤍',
    'انتهى الهدف! وش تبين نسوي بعد؟ نثبت الوزن أو نبدأ هدف جديد؟',
]

PROGRESS_FEEDBACK_POSITIVE = [
    'يا {name} تقدمك رهيب! شدي حيلك ونوصل أسرع 🤍',
    '{name} واضح إنك قريبة من الهدف! خطوة بس وتوصلين.',
    'تقدمك يبان واضح يا {name}! استمري هالوتيرة 🔥',
    'والله تقدمك ممتاز يا {name}! نكمل ونوصل سوا 💪',
    '{name} شغلك واضح! كل يوم تقربين أكثر من الهدف 🤍',
]

PROGRESS_FEEDBACK_POSITIVE_EN = [
    "{name}, your progress is amazing! Keep pushing, we'll get there faster 🤍",
    "{name}, you're clearly close to your goal! Just one more step.",
    "Your progress is obvious, {name}! Keep this pace 🔥",
    "Your progress is excellent, {name}! Let's keep going together 💪",
    "{name}, your work shows! Every day you're closer to your goal 🤍",
]

PROGRESS_FEEDBACK_NEGATIVE = [
    'لا عليك يا {name}، نرجع نرفع التقدم سوا.',
    'عادي يا {name}، كل شخص يمر بفترات صعبة. نرجع نكمل.',
    'ما يهم يا {name}، المهم إنك ترجعين. نرفع التقدم تدريجياً.',
    'لا تقلقين يا {name}، نرجع نبنيه من جديد.',
    'عادي يا {name}، نرجع نكمل ونرفع التقدم خطوة بخطوة.',
]

PROGRESS_FEEDBACK_NEGATIVE_EN = [
    "No worries, {name}, let's build the progress back together.",
    "It's okay, {name}, everyone goes through tough periods. Let's get back on track.",
    "Don't worry, {name}, what matters is you're back. We'll build progress gradually.",
    "Don't stress, {name}, let's rebuild it from scratch.",
    "It's fine, {name}, let's continue and build progress step by step.",
]

EXERCISE_VIDEOS = [
    {
        'title': 'Pamela Reif – 10 min Beginner Workout',
        'duration': '10 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=pamela+reif+10+min+beginner',
        'description': 'Perfect for beginners, full body workout',
    },
    {
        'title': 'MadFit – Low Impact Full Body',
        'duration': '15-20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=madfit+low+impact+full+body',
        'description': 'Low impact, joint-friendly workout',
    },
    {
        'title': 'Chloe Ting – No Jumping Workout',
        'duration': '10-15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=chloe+ting+no+jumping',
        'description': 'No jumping, apartment-friendly',
    },
    {
        'title': 'FitnessBlender – Beginner Cardio',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=fitnessblender+beginner+cardio',
        'description': 'Cardio workout for beginners',
    },
    {
        'title': 'NourishMoveLove – Low-Impact Strength',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=nourishmovelove+low+impact+strength',
        'description': 'Strength training without high impact',
    },
]

WHEELCHAIR_EXERCISES = [
    'Seated cardio (arm circles, punches)',
    'Seated arm raises',
    'Seated resistance band workouts',
    'Upper body strength (seated)',
    'Seated core activation',
    'Seated stretching',
    'Shoulder mobility exercises',
    'Seated leg lifts (if possible)',
]

JOINT_FRIENDLY_EXERCISES = [
    'Low-impact cardio (walking, cycling)',
    'Modified squats with support',
    'Glute bridges',
    'Slow marches',
    'Wall-assisted exercises',
    'Seated leg extensions',
    'Gentle stretching',
    'Water exercises (if available)',
]

BALANCE_FRIENDLY_EXERCISES = [
    'Chair-assisted exercises',
    'Wall holds',
    'Slow tempo routines',
    'Seated balance exercises',
    'Standing with support',
    'Gentle yoga poses (with support)',
    'Tai chi movements',
]

ADAPTIVE_VIDEOS = [
    {
        'title': 'Adaptive Seated Workout - Full Body',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=adaptive+seated+workout',
        'description': 'Full body workout from seated position',
        'category': 'wheelchair',
    },
    {
        'title': 'Wheelchair Fitness Routine',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=wheelchair+fitness',
        'description': 'Comprehensive wheelchair fitness routine',
        'category': 'wheelchair',
    },
    {
        'title': 'Low-Impact Disability-Friendly Exercises',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=low+impact+disability+friendly',
        'description': 'Gentle exercises for various mobility needs',
        'category': 'general',
    },
    {
        'title': 'Chair-Based Exercise Routine',
        'duration': '10 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=chair+exercise+routine',
        'description': 'Safe exercises using a chair for support',
        'category': 'balance',
    },
    {
        'title': 'Joint-Friendly Workout',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=joint+friendly+workout',
        'description': 'Exercises designed for joint health',
        'category': 'joint',
    },
]

ADAPTIVE_EXERCISE_IMAGES = {
    'seated_arm_raise': {
        'name': 'Seated Arm Raise',
        'url': 'https://example.com/images/seated-arm-raise.jpg',
        'description': 'Proper form for seated arm raises',
    },
    'seated_core': {
        'name': 'Seated Core Activation',
        'url': 'https://example.com/images/seated-core.jpg',
        'description': 'Seated core strengthening exercise',
    },
    'wall_squat': {
        'name': 'Wall-Assisted Squat',
        'url': 'https://example.com/images/wall-squat.jpg',
        'description': 'Safe squat form using wall support',
    },
    'chair_balance': {
        'name': 'Chair-Assisted Balance',
        'url': 'https://example.com/images/chair-balance.jpg',
        'description': 'Balance exercise with chair support',
    },
    'gentle_stretch': {
        'name': 'Gentle Stretching',
        'url': 'https://example.com/images/gentle-stretch.jpg',
        'description': 'Safe stretching for mobility issues',
    },
}

DISABILITY_SUPPORT_MESSAGES = [
    'ولا يهمك {name}، عندي تمارين من وضع الجلوس ممتازة وتساعدك توصلين لهدفك بسلام.',
    'نقدر نبني خطة تناسبك 100% بدون ما تتعبك.',
    'كل شخص له طريقته الخاصة، ونقدر نساعدك بخطة آمنة ومناسبة لك.',
    'ما يهم الوضع، المهم إنك تتحركين وتتحسنين. عندي تمارين تناسبك تماماً.',
    'نقدر نعمل خطة ممتازة تناسب وضعك الصحي وتوصلين لهدفك.',
]

DISABILITY_SUPPORT_MESSAGES_EN = [
    "No worries, {name}, I have excellent seated exercises that will help you reach your goal safely.",
    "We can build a plan that fits you 100% without exhausting you.",
    "Everyone has their own path, and we can help you with a safe and suitable plan.",
    "The situation doesn't matter, what matters is that you move and improve. I have exercises that suit you perfectly.",
    "We can create an excellent plan that fits your health condition and helps you reach your goal.",
]

ACCESSIBILITY_ACTIVATION_MESSAGES = [
    'تم تفعيل وضع إمكانية الوصول. أنا هنا لمساعدتك صوتياً.',
    'وضع إمكانية الوصول مفعّل. كل الردود ستكون واضحة ومناسبة للقراءة الصوتية.',
    'تم التفعيل. سأتكلم معك بوضوح ومناسب للصوت.',
]

ACCESSIBILITY_ACTIVATION_MESSAGES_EN = [
    'Accessibility Mode activated. I am here to help you with voice-friendly responses.',
    'Accessibility Mode is on. All responses will be clear and suitable for voice reading.',
    'Activated. I will speak with you clearly and in a voice-friendly format.',
]

NAVIGATION_ASSISTANCE_MESSAGES = [
    'أنت الآن في صفحة AI Chat. اكتبي أو تكلمي لبدء التمرين.',
    'الزر في الأسفل لإرسال الرسالة.',
    'يمكنك استخدام الميكروفون للتحدث بدلاً من الكتابة.',
]

NAVIGATION_ASSISTANCE_MESSAGES_EN = [
    'You are now on the AI Chat page. Type or speak to start your workout.',
    'The send button is at the bottom.',
    'You can use the microphone to speak instead of typing.',
]

DEAF_MODE_ACTIVATION_MESSAGES = [
    'تم تفعيل وضع إمكانية الوصول للصم وضعاف السمع. كل التعليمات ستكون مرئية وواضحة.',
    'وضع الصم مفعّل. سأستخدم إشارات بصرية بدلاً من الصوت.',
    'تم التفعيل. التعليمات ستكون مرئية ومناسبة للقراءة.',
]

DEAF_MODE_ACTIVATION_MESSAGES_EN = [
    'Deaf & Hard-of-Hearing Mode activated. All instructions will be visual and clear.',
    'Deaf Mode is on. I will use visual cues instead of sound.',
    'Activated. Instructions will be visual and reading-friendly.',
]

VISUAL_CUES = {
    'up': '⬆️',
    'down': '⬇️',
    'right': '➡️',
    'left': '⬅️',
    'center': '↔️',
    'hand': '✋',
    'slow': '🐢',
    'fast': '⚡',
    'repeat': '🔄',
    'rest': '⏸️',
    'start': '▶️',
    'end': '⏹️',
}

VISUAL_CUES_AR = {
    'up': '⬆️ ارفعي',
    'down': '⬇️ انزلي',
    'right': '➡️ يمين',
    'left': '⬅️ يسار',
    'center': '↔️ الوسط',
    'hand': '✋ يدك',
    'slow': '🐢 ببطء',
    'fast': '⚡ بسرعة',
    'repeat': '🔄 كرري',
    'rest': '⏸️ استريحي',
    'start': '▶️ ابدئي',
    'end': '⏹️ انتهي',
}

GYM_EQUIPMENT = {
    'leg_press': {
        'name': 'Leg Press Machine',
        'name_ar': 'جهاز ضغط الأرجل',
        'instructions': {
            'seat_adjustment': 'Adjust seat so knees align with pivot point',
            'foot_placement': 'Place feet shoulder-width apart on platform',
            'range_of_motion': 'Lower until knees form 90-degree angle',
            'breathing': 'Exhale on push, inhale on return',
            'safety': 'Never lock knees at top',
            'common_mistakes': 'Going too deep, locking knees',
            'beginner_weight': 'Start with body weight or light resistance',
        },
    },
    'chest_press': {
        'name': 'Chest Press Machine',
        'name_ar': 'جهاز ضغط الصدر',
        'instructions': {
            'seat_adjustment': 'Adjust so handles align with chest',
            'handle_height': 'Handles at mid-chest level',
            'range_of_motion': 'Push forward until arms almost straight',
            'breathing': 'Exhale on push, inhale on return',
            'safety': 'Keep back flat against pad',
            'common_mistakes': 'Arching back, going too fast',
            'beginner_weight': 'Start with 50% of body weight',
        },
    },
    'cable_machine': {
        'name': 'Cable Machine',
        'name_ar': 'جهاز الكيبل',
        'instructions': {
            'handle_height': 'Adjust pulley to target muscle height',
            'foot_placement': 'Staggered stance for stability',
            'range_of_motion': 'Full range, controlled movement',
            'breathing': 'Exhale on pull, inhale on return',
            'safety': 'Check cable condition before use',
            'common_mistakes': 'Using momentum, improper form',
            'beginner_weight': 'Start with 10-15 lbs',
        },
    },
    'lat_pulldown': {
        'name': 'Lat Pulldown Machine',
        'name_ar': 'جهاز سحب العضلات',
        'instructions': {
            'seat_adjustment': 'Knees should fit under pads',
            'handle_height': 'Reach up to grab bar',
            'range_of_motion': 'Pull to chest level',
            'breathing': 'Exhale on pull, inhale on return',
            'safety': 'Keep core engaged',
            'common_mistakes': 'Pulling behind neck, using momentum',
            'beginner_weight': 'Start with 30-40% of body weight',
        },
    },
    'treadmill': {
        'name': 'Treadmill',
        'name_ar': 'جهاز المشي',
        'instructions': {
            'safety': 'Start slow, use safety clip',
            'foot_placement': 'Land on mid-foot',
            'breathing': 'Steady breathing pattern',
            'common_mistakes': 'Holding handrails, overstriding',
            'beginner_weight': 'Start with 3-4 km/h walking',
        },
    },
    'rowing_machine': {
        'name': 'Rowing Machine',
        'name_ar': 'جهاز التجديف',
        'instructions': {
            'seat_adjustment': 'Feet should reach footrests comfortably',
            'foot_placement': 'Straps over mid-foot',
            'range_of_motion': 'Full extension and contraction',
            'breathing': 'Exhale on pull, inhale on return',
            'safety': 'Keep back straight',
            'common_mistakes': 'Bending back, pulling too hard',
            'beginner_weight': 'Start with low resistance',
        },
    },
    'smith_machine': {
        'name': 'Smith Machine',
        'name_ar': 'جهاز سميث',
        'instructions': {
            'safety': 'Always use safety catches',
            'foot_placement': 'Feet shoulder-width apart',
            'range_of_motion': 'Full range, controlled',
            'breathing': 'Exhale on push/lift, inhale on return',
            'common_mistakes': 'Not using safety, improper form',
            'beginner_weight': 'Start with empty bar or light weight',
        },
    },
    'shoulder_press': {
        'name': 'Shoulder Press Machine',
        'name_ar': 'جهاز ضغط الكتف',
        'instructions': {
            'seat_adjustment': 'Back fully supported',
            'handle_height': 'Handles at shoulder level',
            'range_of_motion': 'Press up until arms almost straight',
            'breathing': 'Exhale on press, inhale on return',
            'safety': 'Keep core engaged',
            'common_mistakes': 'Arching back, going too heavy',
            'beginner_weight': 'Start with 20-30% of body weight',
        },
    },
    'hip_abductor': {
        'name': 'Hip Abductor/Adductor Machine',
        'name_ar': 'جهاز عضلات الفخذ',
        'instructions': {
            'seat_adjustment': 'Back fully supported',
            'range_of_motion': 'Controlled outward/inward movement',
            'breathing': 'Exhale on push, inhale on return',
            'safety': 'Keep core engaged',
            'common_mistakes': 'Using momentum, going too fast',
            'beginner_weight': 'Start with light resistance',
        },
    },
    'stair_climber': {
        'name': 'Stair Climber',
        'name_ar': 'جهاز صعود الدرج',
        'instructions': {
            'safety': 'Hold handrails lightly',
            'foot_placement': 'Full foot on step',
            'breathing': 'Steady breathing',
            'common_mistakes': 'Leaning on rails, skipping steps',
            'beginner_weight': 'Start with slow pace',
        },
    },
    'barbell': {
        'name': 'Barbell',
        'name_ar': 'البار',
        'instructions': {
            'safety': 'Always use collars, proper form',
            'grip': 'Overhand or mixed grip depending on exercise',
            'breathing': 'Exhale on lift, inhale on return',
            'common_mistakes': 'Too heavy, improper form',
            'beginner_weight': 'Start with empty bar (20kg)',
        },
    },
    'dumbbell': {
        'name': 'Dumbbells',
        'name_ar': 'الأثقال',
        'instructions': {
            'safety': 'Check weight before lifting',
            'grip': 'Firm but not too tight',
            'breathing': 'Exhale on lift, inhale on return',
            'common_mistakes': 'Swinging, using momentum',
            'beginner_weight': 'Start with 2-5 kg per hand',
        },
    },
}

GYM_EQUIPMENT_VIDEOS = [
    {
        'trainer': 'ATHLEAN-X',
        'title': 'How to Use Gym Machines Correctly',
        'duration': '15 minutes',
        'difficulty': 'Intermediate',
        'link': 'https://www.youtube.com/results?search_query=athlean+x+gym+machines',
    },
    {
        'trainer': 'Jeremy Ethier',
        'title': 'Gym Machine Tutorial',
        'duration': '12 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=jeremy+ethier+gym+machine',
    },
    {
        'trainer': 'FitnessBlender',
        'title': 'Gym Equipment Guide',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=fitnessblender+gym+equipment',
    },
    {
        'trainer': 'Pamela Reif',
        'title': 'Machine Workout Guide',
        'duration': '10 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=pamela+reif+machines',
    },
    {
        'trainer': 'Scott Herman Fitness',
        'title': 'Gym Machine Tutorial',
        'duration': '18 minutes',
        'difficulty': 'Intermediate',
        'link': 'https://www.youtube.com/results?search_query=scott+herman+gym+machine',
    },
    {
        'trainer': 'Nuffield Health',
        'title': 'How to Use Gym Equipment',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=nuffield+health+gym+equipment',
    },
]

PREGNANCY_SAFETY_ALERTS = {
    'dizziness': {
        'ar': 'دوخة',
        'en': 'dizziness',
        'response_ar': 'هذا عرض طبي… لازم توقفين وتراجعين دكتور فوراً.',
        'response_en': 'This is a medical symptom. You must stop and see a doctor immediately.',
    },
    'bleeding': {
        'ar': 'نزيف',
        'en': 'bleeding',
        'response_ar': 'هذا عرض طبي… لازم توقفين وتراجعين دكتور فوراً.',
        'response_en': 'This is a medical symptom. You must stop and see a doctor immediately.',
    },
    'severe_pain': {
        'ar': 'ألم قوي',
        'en': 'severe pain',
        'response_ar': 'هذا عرض طبي… لازم توقفين وتراجعين دكتور فوراً.',
        'response_en': 'This is a medical symptom. You must stop and see a doctor immediately.',
    },
    'shortness_of_breath': {
        'ar': 'ضيق تنفس',
        'en': 'shortness of breath',
        'response_ar': 'هذا عرض طبي… لازم توقفين وتراجعين دكتور فوراً.',
        'response_en': 'This is a medical symptom. You must stop and see a doctor immediately.',
    },
}

PREGNANCY_EXERCISES_TRIMESTER_1 = [
    'Light walking',
    'Gentle strength training',
    'Breathing exercises',
    'Pelvic floor basics',
    'Gentle stretching',
]

PREGNANCY_EXERCISES_TRIMESTER_2 = [
    'Standing exercises',
    'Seated strength training',
    'Hip-openers',
    'Back support workouts',
    'Modified yoga',
]

PREGNANCY_EXERCISES_TRIMESTER_3 = [
    'Deep breathing',
    'Pelvic floor release',
    'Hip mobility',
    'Labor-prep stretches',
    'Very soft cardio',
    'Cat-cow',
    'Hip circles',
    'Side-lying release',
    'Deep squats (supported)',
    'Pelvic tilts',
]

PREGNANCY_VIDEOS = [
    {
        'trainer': 'BodyFit by Amy',
        'title': 'Prenatal Workout',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=bodyfit+amy+prenatal',
    },
    {
        'trainer': 'GlowBodyPT',
        'title': 'Pregnancy Safe Workout',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=glowbodypt+prenatal',
    },
    {
        'trainer': 'Pregnancy and Postpartum TV',
        'title': 'Prenatal Exercise',
        'duration': '25 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=pregnancy+postpartum+tv',
    },
    {
        'trainer': 'NourishMoveLove Prenatal',
        'title': 'Safe Pregnancy Workout',
        'duration': '18 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=nourishmovelove+prenatal',
    },
    {
        'trainer': 'SarahBethYoga Prenatal',
        'title': 'Prenatal Yoga',
        'duration': '30 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=sarahbethyoga+prenatal',
    },
]

POSTPARTUM_SAFETY_ALERTS = {
    'bleeding': {
        'ar': 'نزيف',
        'en': 'bleeding',
        'response_ar': 'هذا عرض طبي مهم — لازم توقفين التمرين فورًا وتراجعين طبيبك.',
        'response_en': 'This is an important medical symptom. You must stop exercising immediately and see your doctor.',
    },
    'severe_pain': {
        'ar': 'ألم قوي',
        'en': 'severe pain',
        'response_ar': 'هذا عرض طبي مهم — لازم توقفين التمرين فورًا وتراجعين طبيبك.',
        'response_en': 'This is an important medical symptom. You must stop exercising immediately and see your doctor.',
    },
    'fever': {
        'ar': 'حرارة',
        'en': 'fever',
        'response_ar': 'هذا عرض طبي مهم — لازم توقفين التمرين فورًا وتراجعين طبيبك.',
        'response_en': 'This is an important medical symptom. You must stop exercising immediately and see your doctor.',
    },
    'dizziness': {
        'ar': 'دوخة',
        'en': 'dizziness',
        'response_ar': 'هذا عرض طبي مهم — لازم توقفين التمرين فورًا وتراجعين طبيبك.',
        'response_en': 'This is an important medical symptom. You must stop exercising immediately and see your doctor.',
    },
    'pelvic_pressure': {
        'ar': 'ضغط على الحوض',
        'en': 'pelvic pressure',
        'response_ar': 'هذا عرض طبي مهم — لازم توقفين التمرين فورًا وتراجعين طبيبك.',
        'response_en': 'This is an important medical symptom. You must stop exercising immediately and see your doctor.',
    },
    'c_section_pain': {
        'ar': 'ألم مكان القيصرية',
        'en': 'c-section pain',
        'response_ar': 'هذا عرض طبي مهم — لازم توقفين التمرين فورًا وتراجعين طبيبك.',
        'response_en': 'This is an important medical symptom. You must stop exercising immediately and see your doctor.',
    },
}

POSTPARTUM_EXERCISES_PHASE_1 = [
    'Breathing exercises',
    'Pelvic floor activation',
    'Diaphragmatic breathing',
    'Gentle walking',
    'Light stretching',
    'Lower-back mobility',
    'Gentle hip openers',
]

POSTPARTUM_EXERCISES_PHASE_2 = [
    'Gentle low-impact workouts',
    'Wall push-ups',
    'Glute bridges (light only)',
    'Modified squats',
    'Seated strength',
    'No core-heavy routines',
]

POSTPARTUM_EXERCISES_PHASE_3 = [
    'Light strength training',
    'Resistance bands',
    'Slow pace routines',
    'Gradual reintroduction to core',
    'Avoiding direct ab pressure',
]

POSTPARTUM_EXERCISES_PHASE_4 = [
    'Gradual strength training',
    'Moderate intensity (if no pain)',
    'Core exercises (if no diastasis)',
    'Full range of motion',
]

DIASTASIS_SAFETY_ALERTS = {
    'new_pain': {
        'ar': 'ألم جديد',
        'en': 'new pain',
        'response_ar': 'هذا عرض يحتاج توقفين فورًا. الأفضل تراجعين طبيبة.',
        'response_en': "This symptom requires you to stop immediately. It's best to see your doctor.",
    },
    'bulging': {
        'ar': 'انتفاخ',
        'en': 'bulging',
        'response_ar': 'هذا عرض يحتاج توقفين فورًا. الأفضل تراجعين طبيبة.',
        'response_en': "This symptom requires you to stop immediately. It's best to see your doctor.",
    },
    'coning': {
        'ar': 'بروز',
        'en': 'coning',
        'response_ar': 'هذا عرض يحتاج توقفين فورًا. الأفضل تراجعين طبيبة.',
        'response_en': "This symptom requires you to stop immediately. It's best to see your doctor.",
    },
}

DIASTASIS_FORBIDDEN_EXERCISES = [
    'Crunches',
    'Sit-ups',
    'Leg raises',
    'Planks',
    'Twisting',
    'Bicycle crunches',
    'Flutter kicks',
    'Heavy squats',
    'Deep core pressure',
    'Breath-holding',
    'Full planks',
    'Russian twists',
    'V-ups',
    'Toe touches',
]

DIASTASIS_EXERCISES_STAGE_1 = [
    'Belly breathing (diaphragmatic breathing)',
    'Pelvic floor activation',
    'TVA activation (Transverse Abdominis)',
    'Light mobility',
    'Walking',
    'No core load at all',
]

DIASTASIS_EXERCISES_STAGE_2 = [
    'Heel slides',
    'Toe taps',
    'Side-lying core',
    'Gentle bridges',
    'Seated controlled movements',
]

DIASTASIS_EXERCISES_STAGE_3 = [
    'Standing core activation',
    'Resistance band light training',
    'Supported squats',
    'Modified bird-dog',
]

DIASTASIS_EXERCISES_STAGE_4 = [
    'Modified planks (knees)',
    'Light obliques',
    'Standing controlled core',
    'NEVER full planks or crunches unless doctor clearance',
]

DIASTASIS_VIDEOS = [
    {
        'trainer': 'Every Mother (EMbody)',
        'title': 'Diastasis Recti Recovery',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=every+mother+diastasis+recti',
    },
    {
        'trainer': 'Dr. Bri',
        'title': 'Postpartum Core Recovery',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=dr+bri+postpartum+core',
    },
    {
        'trainer': 'NourishMoveLove',
        'title': 'Postpartum Core Healing',
        'duration': '18 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=nourishmovelove+postpartum+core',
    },
    {
        'trainer': 'Pregnancy and Postpartum TV',
        'title': 'Diastasis Recti Safe Workout',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=pregnancy+postpartum+tv+diastasis',
    },
    {
        'trainer': 'BodyFit by Amy',
        'title': 'Diastasis-Safe Core',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=bodyfit+amy+diastasis+safe',
    },
]

POSTPARTUM_VIDEOS = [
    {
        'trainer': 'BodyFit by Amy',
        'title': 'Postpartum Workout',
        'duration': '20 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=bodyfit+amy+postpartum',
    },
    {
        'trainer': 'MoveWithNicole',
        'title': 'Postpartum Yoga',
        'duration': '25 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=movewithnicole+postpartum',
    },
    {
        'trainer': 'NourishMoveLove',
        'title': '6 Week Postpartum',
        'duration': '18 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=nourishmovelove+6+week+postpartum',
    },
    {
        'trainer': 'Pregnancy and Postpartum TV',
        'title': 'Postpartum Recovery',
        'duration': '15 minutes',
        'difficulty': 'Beginner',
        'link': 'https://www.youtube.com/results?search_query=pregnancy+postpartum+tv+postpartum',
    },
]

EXERCISE_IMAGES = {
    'squat': {
        'name': 'Squat Form',
        'url': 'https://example.com/images/squat-form.jpg',
        'description': 'Proper squat form demonstration',
    },
    'lunge': {
        'name': 'Lunge Form',
        'url': 'https://example.com/images/lunge-form.jpg',
        'description': 'Proper lunge form demonstration',
    },
    'plank': {
        'name': 'Plank Form',
        'url': 'https://example.com/images/plank-form.jpg',
        'description': 'Proper plank form demonstration',
    },
    'bridge': {
        'name': 'Bridge Form',
        'url': 'https://example.com/images/bridge-form.jpg',
        'description': 'Proper bridge form demonstration',
    },
    'pushup': {
        'name': 'Push-up Form',
        'url': 'https://example.com/images/pushup-form.jpg',
        'description': 'Proper push-up form demonstration',
    },
    'deadlift': {
        'name': 'Deadlift Form',
        'url': 'https://example.com/images/deadlift-form.jpg',
        'description': 'Proper deadlift form demonstration',
    },
}

INACTIVITY_MESSAGES_2_3_DAYS = [
    'وينك يا {name}؟ شكلك مشغولة هاليومين… نرجع نكمل على راحتك 🤍',
    'اشتقنا لك يا {name}! يومين توقف عادي… يلا نرجع نتحرك شوي؟',
    'أحس ما شفناك هالفترة يا {name}، نمشي خطوة بسيطة اليوم؟',
]

INACTIVITY_MESSAGES_4_6_DAYS = [
    'يا {name}! أدري الدنيا تشغلنا… بس تعالي نرجع بخطة خفيفة مناسبة لك.',
    'مر اسبوع إلا شوي! مو مشكلة… نبدأ خطوة بسيطة ونرجع نتحمس؟',
    'طولتِ علينا يا {name} 🤍 نرجع بخطوة هادية؟',
]

INACTIVITY_MESSAGES_7_PLUS_DAYS = [
    '{name}! اشتقنا لك مرة… ترى نقدر نرجع بخطة جديدة أخف إذا تحسينك تعبتي.',
    'صار لك أسبوع يا {name}… ما عليك، نبدأ من جديد ونسهّلها عليك.',
    'يا {name}! ما نبيك تضغطين على نفسك… بس نبيك ترجعين معانا بخطوة صغيرة.',
]

WORKOUT_MESSAGES_2_3_DAYS = [
    'هاه يا {name}؟ من زمان ما سويتِ تمرين… نسوي شي خفيف اليوم؟',
    'واضح إن عندك انشغال هاليومين… يلا نتحرك شوي بس؟',
    'يومين بدون تمرين عادي… نرجع بخطوة بسيطة ونكمّل 🤍',
]

WORKOUT_MESSAGES_2_3_DAYS_EN = [
    "Hey {name}, been a couple days—want to slide back in with something light?",
    "Looks like life's been busy, {name}. Shall we move just a little today?",
    "Two days off is fine! Ready for one quick step together, {name}?",
]

WORKOUT_MESSAGES_4_6_DAYS = [
    'يا {name}! اشتقنا لحضورك… نرجع بتمرين خفيف 10 دقايق؟',
    'قرب يكمل أسبوع بدون تمرين… وش رأيك نرجع بشكل بسيط؟',
    'أدري يمكن مشغولة… بس دقيقة واحدة تمرين تفرق كثير.',
]

WORKOUT_MESSAGES_4_6_DAYS_EN = [
    "Missed you, {name}! How about a 10-minute comeback session?",
    "Almost a week off—shall we restart with something super simple, {name}?",
    "I know you're busy, {name}, but even one minute of movement helps.",
]

WORKOUT_MESSAGES_7_13_DAYS = [
    '{name}! أسبوع تقريباً بدون تمارين… ما نبي ضغط، نبدأ بخطة أسهل؟',
    'صار لك فترة منكفة… نرجع بشي يناسب وقتك؟',
    'اشتقنا لك يا {name}! خطوة بسيطة اليوم وتتحسنين كثير.',
]

WORKOUT_MESSAGES_7_13_DAYS_EN = [
    "{name}, it's been about a week—let's restart with an easier plan?",
    "Been a while, {name}. Want to try something that fits your schedule?",
    "We miss you, {name}! One small step today can change the vibe.",
]

WORKOUT_MESSAGES_14_PLUS_DAYS = [
    '{name}… فاهمين إن كل شخص يمر بفترات صعبة. نرجع بخطة جديدة مناسبة لحياتك؟',
    'أسبوعين بدون تمرين مو نهاية العالم… نرتّب خطة خفيفة ترجعين منها بهدوء؟',
    'وش رأيك نبدأ من جديد بخطة تناسب وقتك وطريقتك؟',
]

WORKOUT_MESSAGES_14_PLUS_DAYS_EN = [
    "{name}, totally get it—life happens. Ready for a fresh plan that fits you now?",
    "Two weeks off isn't the end. Let's create a gentle comeback routine, {name}.",
    "How about we start from scratch with a plan that matches your pace, {name}?",
]



from django.utils import timezone
from habits.models import Habit
from tasks.models import Task
from .models import Achievement, UserAchievement


def check_achievements(user):
    """Check and award achievements for a user."""
    new_achievements = []
    
    # Get all achievements user hasn't earned yet
    earned_ids = UserAchievement.objects.filter(
        user=user
    ).values_list('achievement_id', flat=True)
    
    available_achievements = Achievement.objects.exclude(
        id__in=earned_ids
    )
    
    for achievement in available_achievements:
        if check_achievement_requirement(user, achievement):
            UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )
            new_achievements.append(achievement)
    
    return new_achievements


def check_achievement_requirement(user, achievement):
    """Check if user meets achievement requirement."""
    req_type = achievement.requirement_type
    req_value = achievement.requirement_value
    
    if req_type == 'streak_days':
        # Check if any habit has streak >= req_value
        habits = Habit.objects.filter(user=user)
        for habit in habits:
            if habit.current_streak() >= req_value:
                return True
        return False
    
    elif req_type == 'total_tasks_completed':
        completed_tasks = Task.objects.filter(
            user=user,
            completed=True
        ).count()
        return completed_tasks >= req_value
    
    elif req_type == 'total_habit_checkins':
        from habits.models import HabitCheckIn
        checkins = HabitCheckIn.objects.filter(
            habit__user=user,
            checked=True
        ).count()
        return checkins >= req_value
    
    elif req_type == 'habits_count':
        habits_count = Habit.objects.filter(user=user).count()
        return habits_count >= req_value
    
    return False


def create_default_achievements():
    """Create default achievements if they don't exist."""
    defaults = [
        # Streak achievements
        {
            'name': '7-Day Streak',
            'description': 'Maintain a 7-day streak on any habit',
            'achievement_type': 'streak',
            'icon': '🔥',
            'color': '#F97316',
            'requirement_value': 7,
            'requirement_type': 'streak_days',
        },
        {
            'name': '30-Day Streak',
            'description': 'Maintain a 30-day streak on any habit',
            'achievement_type': 'streak',
            'icon': '⚡',
            'color': '#8B5CF6',
            'requirement_value': 30,
            'requirement_type': 'streak_days',
        },
        {
            'name': '100-Day Streak',
            'description': 'Maintain a 100-day streak on any habit',
            'achievement_type': 'streak',
            'icon': '👑',
            'color': '#EAB308',
            'requirement_value': 100,
            'requirement_type': 'streak_days',
        },
        # Task achievements
        {
            'name': 'Task Master',
            'description': 'Complete 50 tasks',
            'achievement_type': 'tasks',
            'icon': '✅',
            'color': '#22C55E',
            'requirement_value': 50,
            'requirement_type': 'total_tasks_completed',
        },
        {
            'name': 'Task Champion',
            'description': 'Complete 100 tasks',
            'achievement_type': 'tasks',
            'icon': '🏆',
            'color': '#3B82F6',
            'requirement_value': 100,
            'requirement_type': 'total_tasks_completed',
        },
        # Habit achievements
        {
            'name': 'Habit Starter',
            'description': 'Create your first habit',
            'achievement_type': 'habits',
            'icon': '🌱',
            'color': '#10B981',
            'requirement_value': 1,
            'requirement_type': 'habits_count',
        },
        {
            'name': 'Habit Builder',
            'description': 'Create 5 habits',
            'achievement_type': 'habits',
            'icon': '🌿',
            'color': '#059669',
            'requirement_value': 5,
            'requirement_type': 'habits_count',
        },
        {
            'name': 'Dedicated',
            'description': 'Check in 50 times across all habits',
            'achievement_type': 'habits',
            'icon': '💪',
            'color': '#EC4899',
            'requirement_value': 50,
            'requirement_type': 'total_habit_checkins',
        },
    ]
    
    for achievement_data in defaults:
        Achievement.objects.get_or_create(
            name=achievement_data['name'],
            defaults=achievement_data
        )
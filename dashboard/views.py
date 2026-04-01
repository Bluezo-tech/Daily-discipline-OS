from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from tasks.models import Task
from habits.models import Habit, HabitCheckIn
from achievements.models import UserAchievement


@login_required
def dashboard(request):
    """Display the main dashboard with stats and charts."""
    today = timezone.now().date()
    user = request.user
    
    # Task statistics
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    
    # Today's tasks
    today_tasks = Task.objects.filter(user=user, due_date=today)
    today_pending = today_tasks.filter(completed=False).count()
    today_completed = today_tasks.filter(completed=True).count()
    
    # Upcoming tasks (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_tasks_count = Task.objects.filter(
        user=user,
        due_date__gt=today,
        due_date__lte=next_week,
        completed=False
    ).count()
    
    # Habits statistics
    habits = Habit.objects.filter(user=user)
    total_habits = habits.count()
    
    # Today's habit check-ins
    habits_checked_today = 0
    habits_with_stats = []
    
    for habit in habits:
        is_checked = habit.is_checked_today()
        if is_checked:
            habits_checked_today += 1
        
        habits_with_stats.append({
            'habit': habit,
            'current_streak': habit.current_streak(),
            'is_checked_today': is_checked,
        })
    
    # Calculate completion rate
    task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    habit_completion_rate = (habits_checked_today / total_habits * 100) if total_habits > 0 else 0
    
    # Prepare chart data for the last 7 days
    chart_data = get_chart_data(user, today)
    
    # Get recent achievements
    recent_achievements = UserAchievement.objects.filter(
        user=user
    ).select_related('achievement').order_by('-earned_at')[:5]
    
    context = {
        # Task stats
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'today_pending': today_pending,
        'today_completed': today_completed,
        'upcoming_tasks_count': upcoming_tasks_count,
        'task_completion_rate': round(task_completion_rate, 1),
        
        # Habit stats
        'total_habits': total_habits,
        'habits_checked_today': habits_checked_today,
        'habit_completion_rate': round(habit_completion_rate, 1),
        'habits_with_stats': habits_with_stats,
        
        # Chart data (JSON for JavaScript)
        'chart_labels': json.dumps(chart_data['labels']),
        'tasks_completed_data': json.dumps(chart_data['tasks_completed']),
        'habit_checkins_data': json.dumps(chart_data['habit_checkins']),
        
        # Achievements
        'recent_achievements': recent_achievements,
        'earned_achievements_count': UserAchievement.objects.filter(user=user).count(),
        
        # Today
        'today': today,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


def get_chart_data(user, today):
    """Generate chart data for the last 7 days."""
    labels = []
    tasks_completed = []
    habit_checkins = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        labels.append(date.strftime('%a'))  # Day name (Mon, Tue, etc.)
        
        # Count tasks completed on this date
        completed_count = Task.objects.filter(
            user=user,
            completed=True,
            due_date=date
        ).count()
        tasks_completed.append(completed_count)
        
        # Count habit check-ins for this date
        checkin_count = HabitCheckIn.objects.filter(
            habit__user=user,
            date=date,
            checked=True
        ).count()
        habit_checkins.append(checkin_count)
    
    return {
        'labels': labels,
        'tasks_completed': tasks_completed,
        'habit_checkins': habit_checkins,
    }
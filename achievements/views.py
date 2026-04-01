from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Achievement, UserAchievement


@login_required
def achievement_list(request):
    """Display all achievements and user's earned achievements."""
    # Get all achievements
    all_achievements = Achievement.objects.all()
    
    # Get user's earned achievements
    user_achievement_ids = UserAchievement.objects.filter(
        user=request.user
    ).values_list('achievement_id', flat=True)
    
    # Categorize achievements
    achievements_by_type = {}
    for achievement in all_achievements:
        achievement_type = achievement.get_achievement_type_display()
        if achievement_type not in achievements_by_type:
            achievements_by_type[achievement_type] = []
        
        achievements_by_type[achievement_type].append({
            'achievement': achievement,
            'earned': achievement.id in user_achievement_ids
        })
    
    # Get user's earned achievements with details
    earned_achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').order_by('-earned_at')
    
    context = {
        'achievements_by_type': achievements_by_type,
        'earned_achievements': earned_achievements,
        'total_achievements': all_achievements.count(),
        'earned_count': earned_achievements.count(),
    }
    return render(request, 'achievements/achievement_list.html', context)
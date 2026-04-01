from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Habit, HabitCheckIn
from achievements.utils import check_achievements


@login_required
def habit_list(request):
    """Display all habits for the current user with today's check-ins."""
    habits = Habit.objects.filter(user=request.user)
    today = timezone.now().date()
    
    # Enhance habits with stats
    habits_with_stats = []
    total_checked_today = 0
    
    for habit in habits:
        is_checked = habit.is_checked_today()
        if is_checked:
            total_checked_today += 1
        
        habits_with_stats.append({
            'habit': habit,
            'current_streak': habit.current_streak(),
            'longest_streak': habit.longest_streak(),
            'total_check_ins': habit.total_check_ins(),
            'is_checked_today': is_checked,
            'last_7_days': habit.get_last_7_days(),
            'completion_rate': habit.get_completion_rate(30),
        })
    
    context = {
        'habits': habits_with_stats,
        'total_habits': habits.count(),
        'habits_checked_today': total_checked_today,
        'today': today,
    }
    return render(request, 'habits/habit_list.html', context)


@login_required
def habit_create(request):
    """Create a new habit."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#3B82F6')
        
        if not name:
            messages.error(request, 'Habit name is required.')
            return redirect('habits:habit_list')
        
        # Check if habit with same name already exists for this user
        if Habit.objects.filter(user=request.user, name__iexact=name).exists():
            messages.error(request, f'You already have a habit named "{name}".')
            return redirect('habits:habit_list')
        
        Habit.objects.create(
            user=request.user,
            name=name,
            description=description if description else None,
            color=color
        )
        messages.success(request, f'Habit "{name}" created successfully!')
        return redirect('habits:habit_list')
    
    return redirect('habits:habit_list')


@login_required
def habit_update(request, pk):
    """Update an existing habit."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '#3B82F6')
        
        if not name:
            messages.error(request, 'Habit name is required.')
            return redirect('habits:habit_list')
        
        # Check if another habit with same name already exists
        if Habit.objects.filter(user=request.user, name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f'You already have a habit named "{name}".')
            return redirect('habits:habit_list')
        
        habit.name = name
        habit.description = description if description else None
        habit.color = color
        habit.save()
        messages.success(request, f'Habit updated successfully!')
        return redirect('habits:habit_list')
    
    return redirect('habits:habit_list')


@login_required
def habit_delete(request, pk):
    """Delete a habit."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        habit_name = habit.name
        habit.delete()
        messages.success(request, f'Habit "{habit_name}" deleted successfully!')
    
    return redirect('habits:habit_list')


@login_required
def habit_toggle(request, pk):
    """Toggle habit check-in for today."""
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        is_checked = habit.toggle_check_in()
        current_streak = habit.current_streak()
        
        # Check for achievements when habit is checked
        if is_checked:
            new_achievements = check_achievements(request.user)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    'success': True,
                    'checked': is_checked,
                    'habit_id': habit.id,
                    'current_streak': current_streak,
                }
                if new_achievements:
                    response_data['achievements'] = [
                        {'name': a.name, 'description': a.description, 'icon': a.icon}
                        for a in new_achievements
                    ]
                return JsonResponse(response_data)
            
            if new_achievements:
                for achievement in new_achievements:
                    messages.success(request, f'🏆 Achievement Unlocked: {achievement.name}!')
        
        status = 'checked in' if is_checked else 'unchecked'
        messages.success(request, f'Habit "{habit.name}" {status}! Current streak: {current_streak} days')
    
    return redirect('habits:habit_list')
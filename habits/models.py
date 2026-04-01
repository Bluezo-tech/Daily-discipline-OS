from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_checked_today(self):
        """Check if the habit is checked in for today."""
        today = timezone.now().date()
        return self.check_ins.filter(date=today, checked=True).exists()

    def get_check_in_for_date(self, date):
        """Get or create check-in for a specific date."""
        check_in, created = self.check_ins.get_or_create(
            date=date,
            defaults={'checked': False}
        )
        return check_in

    def toggle_check_in(self, date=None):
        """Toggle check-in status for a specific date (default: today)."""
        if date is None:
            date = timezone.now().date()
        
        check_in, created = self.check_ins.get_or_create(
            date=date,
            defaults={'checked': True}
        )
        
        if not created:
            check_in.checked = not check_in.checked
            check_in.save()
        
        return check_in.checked

    def current_streak(self):
        """Calculate the current streak of consecutive days checked."""
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        # Check if checked in today
        if self.check_ins.filter(date=today, checked=True).exists():
            streak = 1
        else:
            # If not checked today, check yesterday
            current_date = today - timedelta(days=1)
            if not self.check_ins.filter(date=current_date, checked=True).exists():
                return 0
            streak = 1
        
        # Count backwards from the last checked day
        while True:
            current_date -= timedelta(days=1)
            if self.check_ins.filter(date=current_date, checked=True).exists():
                streak += 1
            else:
                break
        
        return streak

    def longest_streak(self):
        """Calculate the longest streak ever achieved."""
        check_ins = self.check_ins.filter(checked=True).order_by('date')
        
        if not check_ins.exists():
            return 0
        
        longest = 1
        current_streak = 1
        prev_date = None
        
        for check_in in check_ins:
            if prev_date is not None:
                if (check_in.date - prev_date).days == 1:
                    current_streak += 1
                    longest = max(longest, current_streak)
                elif (check_in.date - prev_date).days > 1:
                    current_streak = 1
            prev_date = check_in.date
        
        return longest

    def total_check_ins(self):
        """Return total number of check-ins."""
        return self.check_ins.filter(checked=True).count()

    def get_last_7_days(self):
        """Get check-in status for the last 7 days."""
        today = timezone.now().date()
        days = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            check_in = self.check_ins.filter(date=date).first()
            days.append({
                'date': date,
                'checked': check_in.checked if check_in else False,
                'day_name': date.strftime('%a'),
            })
        
        return days

    def get_completion_rate(self, days=30):
        """Get completion rate for the last N days."""
        today = timezone.now().date()
        start_date = today - timedelta(days=days-1)
        
        total_days = days
        checked_days = self.check_ins.filter(
            date__gte=start_date,
            date__lte=today,
            checked=True
        ).count()
        
        return round((checked_days / total_days) * 100, 1) if total_days > 0 else 0


class HabitCheckIn(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='check_ins'
    )
    date = models.DateField()
    checked = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        status = 'checked' if self.checked else 'unchecked'
        return f"{self.habit.name} - {self.date} ({status})"
from django.db import models
from django.conf import settings


class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('streak', 'Streak'),
        ('tasks', 'Tasks'),
        ('habits', 'Habits'),
        ('special', 'Special'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    icon = models.CharField(max_length=50, default='🏆')
    color = models.CharField(max_length=7, default='#F59E0B')
    requirement_value = models.IntegerField(default=0)
    requirement_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['achievement_type', 'requirement_value']

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements'
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.email} - {self.achievement.name}"
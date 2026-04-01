from django.contrib import admin
from .models import Habit, HabitCheckIn


class HabitCheckInInline(admin.TabularInline):
    model = HabitCheckIn
    extra = 0
    date_hierarchy = 'date'


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at', 'current_streak_display', 'total_check_ins_display')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'user__email')
    inlines = [HabitCheckInInline]

    def current_streak_display(self, obj):
        return obj.current_streak()
    current_streak_display.short_description = 'Current Streak'

    def total_check_ins_display(self, obj):
        return obj.total_check_ins()
    total_check_ins_display.short_description = 'Total Check-ins'


@admin.register(HabitCheckIn)
class HabitCheckInAdmin(admin.ModelAdmin):
    list_display = ('habit', 'date', 'checked', 'created_at')
    list_filter = ('checked', 'date')
    search_fields = ('habit__name', 'habit__user__email')
    date_hierarchy = 'date'
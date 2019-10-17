from rest_framework import serializers
from .models import *
from datetime import datetime
        
class JobSerializer(serializers.ModelSerializer):
    last_date = serializers.SerializerMethodField('get_last_date')
    def get_last_date(self, obj):
        return obj.last_date.strftime('%Y-%m-%d')
    class Meta:
        model = Job
        fields = '__all__'
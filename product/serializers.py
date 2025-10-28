from rest_framework import serializers
from django_currentuser.middleware import get_current_authenticated_user
from .models import AnalyticsEvent, Product, SavingsEntry

class ProductListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else None

class ProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        model_object = super().create(validated_data=validated_data)
        user = get_current_authenticated_user() 
        if user:
            model_object.created_by = user
        model_object.save()
        return model_object

    def update(self, instance, validated_data):
        model_object = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user:
            model_object.updated_by = user
        model_object.save()
        return model_object
class SavingsEntryListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = SavingsEntry
        fields = '__all__'

    def get_created_by(self, obj):
        return obj.created_by.email if obj.created_by else None

    def get_updated_by(self, obj):
        return obj.updated_by.email if obj.updated_by else None

class SavingsEntryMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsEntry
        fields = ['id', 'name']

class SavingsEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsEntry
        fields = '__all__'

    def create(self, validated_data):
        model_object = super().create(validated_data=validated_data)
        user = get_current_authenticated_user()  
        if user:
            model_object.created_by = user
        model_object.save()
        return model_object

    def update(self, instance, validated_data):
        model_object = super().update(instance=instance, validated_data=validated_data)
        user = get_current_authenticated_user()
        if user:
            model_object.updated_by = user
        model_object.save()
        return model_object
    
class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = '__all__'
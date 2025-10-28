from django.urls import path
from product.views import analytics_views as views

urlpatterns = [
    path('affiliate/redirect/<int:product_id>/', views.affiliate_redirect),
    path('affiliate/purchase/<int:product_id>/', views.track_purchase),
    path('analytics/track/', views.track_analytics_event),
    path('analytics/summary/', views.get_analytics_summary),
]
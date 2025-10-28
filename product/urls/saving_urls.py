from django.urls import path
from product.views import saving_views as views

urlpatterns = [
	path('api/v1/saving/all/', views.getAllSavingsEntry),

	path('api/v1/saving/without_pagination/all/', views.getAllSavingsEntryWithoutPagination),

	# path('api/v1/saving/<int:pk>', views.getSavingEntry),

	path('api/v1/saving/search/', views.searchSavingsEntry),

	path('api/v1/saving/create/', views.createSavingsEntry),

	path('api/v1/saving/update/<int:pk>', views.updateSavingsEntry),

	path('api/v1/saving/delete/<int:pk>', views.deleteSavingsEntry),
    path('api/v1/saving/track/', views.track_savings),
    path('api/v1/saving/export/', views.export_savings),
    path('api/v1/saving/total/', views.get_total_savings),


]
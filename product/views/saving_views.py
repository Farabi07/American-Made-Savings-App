from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions
from product.models import *
from product.serializers import SavingsEntrySerializer, SavingsEntryListSerializer
from product.filters import SavingsEntryFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination

import csv
from django.http import HttpResponse


# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		
		OpenApiParameter("size"),
  ],
	request=SavingsEntrySerializer,
	responses=SavingsEntrySerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_LIST_VIEW.name])
def getAllSavingsEntry(request):
	saves = SavingsEntry.objects.all()
	total_elements = saves.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	saves = pagination.paginate_data(saves)

	serializer = SavingsEntryListSerializer(saves, many=True)

	response = {
		'saves': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	return Response(response, status=status.HTTP_200_OK)




@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=SavingsEntrySerializer,
	responses=SavingsEntrySerializer
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_LIST_VIEW.name])
def getAllSavingsEntryWithoutPagination(request):
	saves = SavingsEntry.objects.all()

	serializer = SavingsEntryListSerializer(saves, many=True)

	return Response({'saves': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def getASavingsEntry(request, pk):
	try:
		save = SavingsEntry.objects.get(pk=pk)
		serializer = SavingsEntrySerializer(save)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"SavingsEntry id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def searchSavingsEntry(request):
	saves = SavingsEntryFilter(request.GET, queryset=SavingsEntry.objects.all())
	saves = saves.qs

	print('searched_products: ', saves)

	total_elements = saves.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	saves = pagination.paginate_data(saves)

	serializer = SavingsEntryListSerializer(saves, many=True)

	response = {
		'saves': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(saves) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no saves matching your search"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_CREATE.name])
def createSavingsEntry(request):
    data = request.data
    filtered_data = {key: value for key, value in data.items() if value not in ['', '0']} 

    if 'regular_price' not in filtered_data or 'affiliate_price' not in filtered_data:
        return Response({"detail": "Regular price and affiliate price are required."}, status=status.HTTP_400_BAD_REQUEST)

    if float(filtered_data['affiliate_price']) > float(filtered_data['regular_price']):
        return Response({"detail": "Affiliate price cannot be greater than regular price."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SavingsEntrySerializer(data=filtered_data)
    if serializer.is_valid():
        serializer.save() 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_UPDATE.name, PermissionEnum.PERMISSION_PARTIAL_UPDATE.name])
def updateSavingsEntry(request,pk):
	try:
		save = SavingsEntry.objects.get(pk=pk)
		data = request.data
		serializer = SavingsEntrySerializer(save, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f"SavingsEntry id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DELETE.name])
def deleteSavingsEntry(request, pk):
	try:
		save = SavingsEntry.objects.get(pk=pk)
		save.delete()
		return Response({'detail': f'SavingsEntry id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"SavingsEntry id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def track_savings(request):
    data = request.data
    product = Product.objects.get(id=data['product_id'])
    regular_price = data['regular_price']
    affiliate_price = data['affiliate_price']
    savings = regular_price - affiliate_price

    savings_entry = SavingsEntry.objects.create(
        user=request.user,
        product=product,
        regular_price=regular_price,
        affiliate_price=affiliate_price,
        savings=savings
    )

    return Response({'detail': 'Savings recorded successfully', 'savings': savings_entry.savings})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_savings(request):
    saves = SavingsEntry.objects.filter(created_by=request.user)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="savings.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product', 'Regular Price', 'Affiliate Price', 'Savings', 'Date Saved'])

    for save in saves:
        writer.writerow([save.product.name, save.regular_price, save.affiliate_price, save.savings, save.date_saved])

    return response
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_total_savings(request):
    total = SavingsEntry.objects.filter(created_by=request.user).aggregate(total_savings=models.Sum('savings'))['total_savings'] or 0
    return Response({'total_savings': float(total)}, status=status.HTTP_200_OK)
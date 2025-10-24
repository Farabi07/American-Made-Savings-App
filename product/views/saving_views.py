from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions
from product.models import SavingsEntry
from product.serializers import SavingsEntrySerializer, SavingsEntryListSerializer
from product.filters import SavingsEntryFilter

from commons.enums import PermissionEnum
from commons.pagination import Pagination




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
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_LIST_VIEW.name])
def getAllSavingsEntryWithoutPagination(request):
	saves = SavingsEntry.objects.all()

	serializer = SavingsEntryListSerializer(saves, many=True)

	return Response({'saves': serializer.data}, status=status.HTTP_200_OK)




@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_DETAILS_VIEW.name])
def getASavingsEntry(request, pk):
	try:
		city = SavingsEntry.objects.get(pk=pk)
		serializer = SavingsEntrySerializer(city)
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
	filtered_data = {}

	for key, value in data.items():
		if value != '' and value != '0':
			filtered_data[key] = value

	serializer = SavingsEntrySerializer(data=filtered_data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=SavingsEntrySerializer, responses=SavingsEntrySerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([PermissionEnum.PERMISSION_UPDATE.name, PermissionEnum.PERMISSION_PARTIAL_UPDATE.name])
def updateSavingsEntry(request,pk):
	try:
		city = SavingsEntry.objects.get(pk=pk)
		data = request.data
		serializer = SavingsEntrySerializer(city, data=data)
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
		city = SavingsEntry.objects.get(pk=pk)
		city.delete()
		return Response({'detail': f'SavingsEntry id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"SavingsEntry id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)


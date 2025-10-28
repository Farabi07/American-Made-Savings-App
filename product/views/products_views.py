from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import  extend_schema, OpenApiParameter

from authentication.decorators import has_permissions
from product.models import Product
from product.serializers import ProductSerializer, ProductListSerializer
from product.filters import ProductFilter
from commons.pagination import Pagination

# Create your views here.

@extend_schema(
	parameters=[
		OpenApiParameter("page"),
		OpenApiParameter("size"),
  ],
	request=ProductSerializer,
	responses=ProductSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PERMISSION_LIST.name])
def getAllProduct(request):
	products = Product.objects.all()
	total_elements = products.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	products = pagination.paginate_data(products)

	serializer = ProductListSerializer(products, many=True)

	response = {
		'products': serializer.data,
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
	request=ProductSerializer,
	responses=ProductSerializer
)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PERMISSION_LIST.name])
def getAllProductWithoutPagination(request):
	products = Product.objects.all()

	serializer = ProductListSerializer(products, many=True)

	return Response({'products': serializer.data}, status=status.HTTP_200_OK)


@extend_schema(request=ProductSerializer, responses=ProductSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PERMISSION_DETAILS.name])
def getAProduct(request, pk):
	try:
		permission = Product.objects.get(pk=pk)
		serializer = ProductSerializer(permission)
		return Response(serializer.data, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Product id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=ProductSerializer, responses=ProductSerializer)
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PRODUCT_DETAILS.name])
def searchProduct (request):

	products = ProductFilter(request.GET, queryset=Product .objects.all())
	products = products.qs

	print('products: ', products)

	total_elements = products.count()

	page = request.query_params.get('page')
	size = request.query_params.get('size')

	# Pagination
	pagination = Pagination()
	pagination.page = page
	pagination.size = size
	products = pagination.paginate_data(products)

	serializer = ProductListSerializer(products, many=True)

	response = {
		'products': serializer.data,
		'page': pagination.page,
		'size': pagination.size,
		'total_pages': pagination.total_pages,
		'total_elements': total_elements,
	}

	if len(products) > 0:
		return Response(response, status=status.HTTP_200_OK)
	else:
		return Response({'detail': f"There are no products matching your search"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ProductSerializer, responses=ProductSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PERMISSION_CREATE.name])
def createProduct(request):
	data = request.data
	filtered_data = {}

	for key, value in data.items():
		if value != '' and value != '0':
			filtered_data[key] = value

	name = filtered_data.get('name', None)
	if name is not None:
		try:
			name = str(name).replace(' ', '_').upper()
			role = Product.objects.get(name=name)
			return Response({'detail': f"Permissioin with name '{name}' already exists."})
		except Product.DoesNotExist:
			pass

	serializer = ProductSerializer(data=filtered_data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=ProductSerializer, responses=ProductSerializer)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PERMISSION_DELETE.name])
def deleteProduct(request, pk):
	try:
		permission = Product.objects.get(pk=pk)
		permission.delete()
		return Response({'detail': f'Product id - {pk} is deleted successfully'}, status=status.HTTP_200_OK)
	except ObjectDoesNotExist:
		return Response({'detail': f"Product id - {pk} doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)




@extend_schema(request=ProductSerializer, responses=ProductSerializer)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
# @has_permissions([ProductEnum.PERMISSION_UPDATE.name, ProductEnum.PERMISSION_PARTIAL_UPDATE.name])
def updateProduct(request,pk):
	try:
		product = Product.objects.get(pk=pk)
		data = request.data
		serializer = ProductSerializer(product, data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	except ObjectDoesNotExist:
		return Response({'detail': f'Product id - {pk} doesn\'t exists'}, status=status.HTTP_400_BAD_REQUEST)

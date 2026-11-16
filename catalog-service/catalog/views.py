from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category, Item
from .serializers import CategorySerializer, ItemSerializer


# ---------------- Categorías ----------------

class CategoryListCreateView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        qs = Category.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return Response(CategorySerializer(qs, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def put(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(cat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cat = get_object_or_404(Category, pk=pk)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------- Ítems ----------------

class ItemListCreateView(APIView):
    def get(self, request):
        org_id = request.query_params.get('organization_id')
        search = request.query_params.get('search')
        category_id = request.query_params.get('category_id')

        qs = Item.objects.all()
        if org_id:
            qs = qs.filter(organization_id=org_id)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(sku__icontains=search)
        if category_id:
            qs = qs.filter(category_id=category_id)

        return Response(ItemSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetailView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        return Response(ItemSerializer(item).data)

    def put(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

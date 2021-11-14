from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.custom_permissions import IsAdminOrSuperAdmin, IsEmployeeOrAccessDenied
from .models import Company
from .serializers import CompanySerializer, CompanyUpdateSerializer


class CompaniesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='List of all companies',
        operation_description='Return list of all companies if view=partial or list of all companies with all '
                              'users in this company and all posts of this users',
        operation_id='All Companies',
        responses={
            200: CompanySerializer(many=True),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "View option must be partial or full not <some_value>",
                }
            })
        }
    )
    def get(self, request, view):
        companies = Company.objects.all()

        if view not in ['partial', 'full']:
            response = {'error': f'View option must be partial or full not {view}'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        elif view == 'partial':
            serializer = CompanySerializer(companies, many=True)
            response = serializer.data
        else:
            serializer = CompanySerializer(companies, many=True)
            response = CompanySerializer.generate_full_result(serializer.data)

        return Response(response, status=status.HTTP_200_OK)


class CompanyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='Info about one company',
        operation_description='Return info about one company',
        operation_id='One Company',
        responses={
            200: CompanySerializer(),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "Company with id=50 does not exist",
                }
            })
        }
    )
    def get(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            response = {'error': f'Company with id={company_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanySerializer(company)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Update info about company',
        operation_description='Update info about one company',
        operation_id='Update Company',
        request_body=CompanyUpdateSerializer(),
        responses={
            200: openapi.Response(description='Success', examples={
                "application/json": {
                    "message": "Successfully update company with id=1",
                }
            }),
            404: openapi.Response(description='Error', examples={
                "application/json": {
                    "error": "Company with id=50 does not exist",
                }
            }),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "detail": "Company with id=50 does not exist",
                }
            }),
        }
    )
    def patch(self, request, company_id):
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            response = {'error': f'Company with id={company_id} does not exist'}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = CompanyUpdateSerializer(company, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': f'Successfully update company with id={company_id}'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        operation_summary='Create company',
        operation_description='Create one company',
        operation_id='Create Company',
        request_body=CompanySerializer(),
        responses={
            200: CompanySerializer(),
            400: openapi.Response(description='Error', examples={
                "application/json": {
                    "detail": "Invalid company name param",
                }
            }),
        }
    )
    def post(self, request):
        data = request.data
        serializer = CompanySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientCompanyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsEmployeeOrAccessDenied]

    @swagger_auto_schema(
        operation_summary='Info about authenticated user',
        operation_description='Return information about your company',
        operation_id='Your Company Info',
        responses={
            200: CompanySerializer(many=True)
        }
    )
    def get(self, request):
        company = Company.objects.get(id=request.user.company_id.id)
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

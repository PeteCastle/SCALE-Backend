from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



class CustomPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'metadata': {
                'page': self.page.number,
                'per_page': self.page_size,
                'total_count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
            },
            'results': data
        })

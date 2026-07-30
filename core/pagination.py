from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self):
        return {
            "current_page": self.page.number,
            "total_pages": self.page.paginator.num_pages,
            "total_items": self.page.paginator.count,
            "page_size": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
        }
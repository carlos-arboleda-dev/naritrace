from rest_framework.pagination import PageNumberPagination


class PaginacionEstandar(PageNumberPagination):
    """Paginación que permite ?page_size=N (máx. 500). Por defecto 20."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 500

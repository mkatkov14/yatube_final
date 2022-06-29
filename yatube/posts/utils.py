# posts/utils.py
from django.core.paginator import Paginator


def get_page_obj(request, posts_list, posts_count):
    page_number = request.GET.get('page')
    paginator = Paginator(posts_list, posts_count)
    return paginator.get_page(page_number)

from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from blog.models import Blog, BlogType
from django.conf import settings


# Create your views here.

def get_blog_common_data(requst, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = requst.GET.get("page", 1)
    page_of_blogs = paginator.get_page(page_num)
    currentr_page_num = page_of_blogs.number  # 获取当前页码
    # 获取当前页码前后各两页的页码范围
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, "...")
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append("...")

    # 添加首页以及尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    # blog_types = BlogType.objects.all()
    # blog_types_list = []
    # for blog_type in blog_types:
    #     blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
    #     blog_types_list.append(blog_type)
    # BlogType.objects.annotate(blog_count = Count("blog_blog"))

    # 获取日期归档对应博客数量
    blog_dates = Blog.objects.dates("create_time", "month", order="DESC")
    blog_date_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                         create_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_count

    context = {}
    context["blogs"] = page_of_blogs.object_list
    context["page_of_blogs"] = page_of_blogs
    context["blog_types"] = BlogType.objects.annotate(blog_count=Count("blog"))
    context["page_range"] = page_range
    context["blog_dates"] = blog_date_dict
    return context


def blog_list(requst):
    blogs_all_list = Blog.objects.all()
    context = get_blog_common_data(requst, blogs_all_list)
    return render(requst, 'blog/blog_list.html', context)


def blog_with_type(requst, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.all().filter(blog_type=blog_type)
    context = get_blog_common_data(requst, blogs_all_list)
    context["blog_type"] = blog_type
    return render(requst, "blog/blog_with_type.html", context)


def blog_with_date(requst, year, month):
    blogs_all_list = Blog.objects.all().filter(create_time__year=year, create_time__month=month)
    context = get_blog_common_data(requst, blogs_all_list)
    context["blog_with_date"] = "%s年%s月" % (year, month)
    return render(requst, "blog/blog_with_date.html", context)


def blog_detail(requst, blog_pk):
    context = {}
    blog = get_object_or_404(Blog, pk=blog_pk)
    if not requst.COOKIES.get("blog_%s_read" % blog_pk):
        pass
        # if ReadNum.objects.filter(blog=blog).count():
        #     # 博客存在
        #     readnum = ReadNum.objects.get(blog=blog)
        # else:
        #     readnum = ReadNum(blog=blog)
        # # 计数+1
        # readnum.read_num += 1
        # readnum.save()

    context["previous_blog"] = Blog.objects.filter(create_time__gt=blog.create_time).last()
    context["next_blog"] = Blog.objects.filter(create_time__lt=blog.create_time).first()
    context["blog"] = blog
    response = render(requst, 'blog/blog_detail.html', context)  # 响应
    response.set_cookie("blog_%s_read" % blog_pk, "true")
    return response

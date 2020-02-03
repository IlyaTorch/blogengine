# #12 Поиск через html-форму
Поисковые запросы - запросы на чтение (get-запрос). Параметры get-запроса хранятся в словаре `GET` объекта `request`.

Для того, чтобы получать данные из html-формы, эту форму нужно идентифицировать(задать полю `input`, в который будут вводиться данные атрибут `name`). Значение этого атрибута `name` будет ключом в словаре `GET`. Также указываем функцию-обработчик формы в атрибуте `action`.

`base.html`
```django
...
<form class="form-inline my-2 my-lg-0" action="{% url 'posts_list_url' %}">
	<input class="form-control mr-sm-2" type="search" placeholder="Search" aria-label="Search" name="search">
	<button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
</form>
...
```

Поисковые запросы будет обрабатывать вьюха `posts_list`.

В функции `posts_list` определим перемеменную `search_query`, которая будет принимать данные для поиска.
Далее если `search_query` имеет данные для поиска `if search_query:`, извлекаем из бд посты, содержащие поисковый запрос пользователя. Это делается с помощью метода `filter` менеджера моделей. Поиск будем вести по названию и по содержанию постов. Но в случае передачи в `filter` нескольких параметров, метод возвращает лишь те объекты, которые соответствуют обоим условиям. `posts = Post.objects.filter(title__icontains=search_query, body__icontains=search_query)`, поэтому чтобы осуществлять поиск так, чтобы запрос соответствовал только одному из условий,  используем класс `Q`: `posts = Post.objects.filter(Q(title__icontains=search_query) | Q(body__icontains=search_query))`.

`views.py`
```python
def posts_list(request):
    search_query = request.GET.get('search', '')

    if search_query:
        posts = Post.objects.filter(Q(title__icontains=search_query) | Q(body__icontains=search_query))
    else:
        posts = Post.objects.all()

    num_posts_page = 4
    paginator = Paginator(posts, num_posts_page)

    page_number = request.GET.get('page', default=1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    context = {
        'page': page,
        'is_paginated': is_paginated,
        'next_page_url': next_url,
        'prev_page_url': prev_url

    }

    return render(request, 'blog/index.html', context=context)
```
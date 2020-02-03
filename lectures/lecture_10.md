# #11 Постраничная навигация
Добаваление постраничной навигации (**пагинации**):
В `base.html` добавляем верстку пагинциии. Разбиваем наш список постов так, чтобы на каждой странице отображалось по n постов. Далее нужно обеспечить отображение постов в зависимости от того, на какой странице мы находимся. Далее нужно связать блок пагинации с нашими страницами.

В django есть специальный класс `Paginator`, который "разрезает" список на отдельные slic'ы, которые представляют собой отдельные страницы.
```
>>> from django.core.paginator import Paginator
>>> from blog.models import Post
>>> posts = Post.objects.all()
```
В конструктор класса `Paginator` передаем список постов, а также кол-во постов, которые будут отображаться на одной странице.
```
>>> paginator = Paginator(posts, 2)
<string>:1: UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'blog.models.Post'> QuerySet.
```
Получаем предупреждение в связи с тем, что не указали порядок постов. Поэтому определим порядок сортировки постов: в `models.py` у классов `Tag` и `Post` определим подкласс `Meta`(`class Meta` определяет внутренние отношения) со свойством `ordering`(отвечает за порядок сортировки. Это список т.к. порядков сортировки может быть несколько) `= ["-date_pub"]` (`date_pub` - поле класса,
по которому будет происходить сортировка. `-` означает обратный порядок сортировки)

Класс `Paginator` "разрезает" список на отдельные slic'ы, коткоторые представляют собой отдельные страницы.
Определим такую страницу, воспользовавшись атрибутом класса `Paginator` `get_page(n)`
```
>>> page1 = paginator.get_page(1)
>>> page1
<Page 1 of 4>
```
Список постов на данной странице:
```
>>> page1.object_list
<QuerySet [<Post: new post2>, <Post: post 3>]>
```
Номер текущей страницы:
```
>>> page1.number
1
```

Теперь определим данное поведение для нашего сайта. Пользователь кликает на номер страницы в блоке пагинайии. Django считывает номер страницы, передает его в метод `get_page()`. Генерируется соответств страница, в шаблон которой передается `object_list`.

В файле `views.py` в функции `posts_list` создадим объект класса `Paginator` и переменную страницы.
Также изменим в словарь `context` функции `render` будем передавать не весь список постов, а лишь те посты, которые будут
отображаться на данной странице:
```python
 return render(request, 'blog/index.html', context={'posts': page.object_list})
```

```python
def posts_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 2)

    page = paginator.get_page(1)

    return render(request, 'blog/index.html', context={'posts': page.object_list})
```

Теперь обеспечим сменяемость постов на странице.
Обычно сайты с пагинацией выглядят след. образом:
http://127.0.0.1:5000/blog/?page=2, где параметр `page` отвечает за отображение страницы. Все что в форме выше идет после знака `?` - параметры get-запроса. Их может быть много. Все они разделяются знаком `&`. Все параметры, передающиеся вместе с запросом, хранятся в объекте `request`. Например, в url выше значение параметра `page` будет храниться в словаре `GET` объекта `request` ао ключу `page`.

Реализуем это в нашем проекте:
В ф-ции `posts_list` определим переменную `page_number`, которая будет считывать данные из адресной строки:`page_number = request.GET.get('page', default=1)`

Теперь сделаем, чтобы знач-е параметра page было связано с соответствующей кнопкой в панели навигации.

Сначала в html-блоке навигации отобразим количество кнопок, соответствующее числу страниц:
```
>>> paginator.page_range
range(1, 5)
``` 

`range(1, 5)` - итератор, генерирующий номера страниц с 1 до 4, где количество привязано к кол-ву страниц в объекте `paginator`.

В шаблоны html будем передавать объект страницы. У него есть св-во `paginator`, который явл-ся ссылкой на `paginator`, от которого эта страница была сгенерирована.
```
>>> paginator is page1.paginator
True
```
Используем это свойство. 
В файле `base.html` создадим цикл `{% for n in page.paginator.page_range %}`, в котором будем генерировать ссылки на наши страницы. Добавим подсветку номера текущей страницы: в цикле зададим условие `{% if page.number == n %}`. Ограничим количество кнопок в блоке нивагации: `{% elif n > page.number|add:-3 and n < page.number|add:3 %}{% elif n > page.number|add:-3 and n < page.number|add:3 %}`. Кнопки `previous` и `next`: В файле `views.py` в ф-ции `posts_list` создадим переменную `is_paginated`, указывающую есть ли другие страницы. В случае отсутствия весь блок с навигацией отображаться не будет. Также в случае существования следующей и предыдущей страницы будем генерировать ссылки на них и передавать в словаре `context`.

`base.html`
```django
{% if is_paginated %}
	<nav aria-label="...">
	    <ul class="pagination">
            <li class="page-item {% if not prev_page_url %}disabled{% endif %}">
              <a class="page-link" href="{{ prev_page_url }}" tabindex="-1" aria-disabled="true">Previous</a>
            </li>

            {% for n in page.paginator.page_range %}
                {% if page.number == n %}
                    <li class="page-item active" aria-current="page">
                        <a class="page-link" href="?page{{ n }}">{{ n }}<span class="sr-only">(current)</span></a>
                    </li>
                {% elif n > page.number|add:-3 and n < page.number|add:3 %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ n }}">{{ n }}</a>
                    </li>
                {% endif %}
            {% endfor %}


            <li class="page-item {% if not next_page_url %}disabled{% endif %}">
                <a class="page-link" href="{{ next_page_url }}" tabindex="-1" aria-disabled="true">Next</a>
            </li>
        </ul>
    </nav>
{% endif %}
```

`views.py`
```python
def posts_list(request):
    posts = Post.objects.all()
    num_posts_page = 1
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
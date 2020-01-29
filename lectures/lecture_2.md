# #2 Хранение, чтение, изменение отображение в шаблоны данных из бд
## Хранение, чтение, изменение объектов данных
---
По умолчанию в Django используется базу данных sqllite3. Django позволяет не писать вручную sql-запросы, а использовать механизм *ORM* (object relational mapping), который позволяет описывать данные, хранящиеся в базе данных в виде таблиц как классы Python(таблица в бд - класс в python). Такие классы называются **моделями**. Они описываются в файле `modesl.py`. Столбец в таблице в базе данных соответствует атрибуту класса.
`models.py`
```python
class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.title)
```
**slug** - человекопонятный url
**db_index** - индексация для более быстрого поиска
**auto_now_add** - поле устанавливается при сохранении экземпляра в бд

Для внесение изменений в бд и синхронизации ее с моделями используется  механизм миграций.
```django
Создание файлов миграции:
$ python manage.py makemigrations
Применение миграций:
$ python manage.py migrate
```
По умолчанию объекты в бд идентифицируются по id. 

Создание объекта модели python:
```django
>>> p = Post(title="New-post", slug="new-slug", body="new post body")
>>> p
<Post: New-post>
>>> p.id
>>> p.title
'New-post'
```
Для сохранения объекта модели в базе данных используется метод `save()`
```python
>>> p.save()
>>> p.id
1
```
Среди атрибутов объекта модели есть атрибут `objects`
```python
>>> dir(p)
[ ..., objects,...]
```
Этот атрибут является **менеджером моделей** объекта. Он прибавляется к объекту модели при ее сохранинии в базу данных.

Менеджер моделей `objects` позволяет создавать объекты моделей, которые сразу же будут сохранены в базе данных(т.е. метод `save()` вызывать не нужно)
```django
>>> p1 = Post.objects.create(title="new post2", slug="new-post2", body="body")
```
Все объекты модели, сохраненные в бд:
```django 
>>> Post.objects.all()
<QuerySet [<Post: New-post>, <Post: new post 2>]>
```
Поиск объекта по занчению атрибута(`get()` возвращает только один объект):
```django
>>> post=Post.objects.get(slug='new-slug')
>>> post
<Post: New-post>
```
Но может возникнуть проблема с регистрозависимостью. Для ее решения используются **lookup'ы**. Наример:
**__iexact**(i = insensitive - регистронезависимость, exact - точное совпадение)
**__contains** - содержит, лучши исп-ть не с get, а filter
```django
>>> post=Post.objects.get(slug__iexact='New-Slug')
>>> post
<Post: New-post>
```
```django
>>> post=Post.objects.filter(slug__contains='new')
>>> post
<QuerySet [<Post: New-post>, <Post: new post 2>]>
``` 

## Отображение объектов моделей в шаблоны
---
`views.py`
```python
def posts_list(request):
    posts = Post.objects.all()
    return render(request, 'blog/index.html', context={'posts': posts})
```
`index.html`
```django
{% extends 'blog/base_blog.html' %}
{% block title %}
	Posts lists
{% endblock %}

{% block content %}
	<h1 class="mb-5">Posts</h1>
	{% for post in posts %}
		<div class="card mb-4">
		  <div class="card-header">
		    {{ post.date_pub }}
		  </div>
		  <div class="card-body">
		    <h5 class="card-title">{{ post.title }}</h5>
		    <p class="card-text">{{ post.body|truncatewords:15 }}</p>
		    <a href="{{ post.get_absolute_url }}" class="btn btn-light">Read</a>
		  </div>
		</div>
	{% endfor %}
{% endblock %}
```
В html-шаблонах можно использовать различные **фильтры**(см. документацию), например:
```django
{{ post.body|truncatewords:15 }}
```
Фильтр `truncatewords` усекает текст до n слов.

Добавим ссылкку на страницу с постами в базовый шаблон:
`base.html`
```django
...
<li class="nav-item active">
	<a class="nav-link" href="{% url 'posts_list_url' %}">Blog</a>
</li>
...
```
Здесь используется django-функция `url`, которая принимает псевдоним функции обработчика(вьюхи) и возвращает адрес страницы, для которой функция с псевдномимом 'posts_list_url' является вьюхой. 
### Одтельная страница для каждого объекта модели
---
Добавим генерацию страниц для отдельных постов и генерацию ссылок с оновной страницы на такие страницы. Для идентификации страниц будем использовать `slug`.
`urls.py`
```python
urlpatterns = [
    path('', views.posts_list, name='posts_list_url'),
    path('posts/<str:slug>/', views.post_detail, name='post_detail_url'),
]
```
То, что находится внутри `<>` - это именнованная группа символов, которой нужно присвоить имя идентификатора (в нашем случае `slug`). Далее в переменную `slug` из именнованной группы символов мы будем подставлять значения slug'a конкртных постов. Перед именем идет тип, здесь - `str`
`views.py`
```python
def post_detail(request, slug):
    post = Post.objects.get(slug__iexact=slug)
    return render(request, 'blog/post_detail.html', context={'post': post})
```
Значение в переменную `slug` приходит из группы символов `<slug>`
Генерация ссылки на страницу с постом:
```django
...
<a href="{% url 'post_detail_url' slug=post.slug %}" class="btn btn-light">Read</a>
...
```
Здесь как и ранее вызываем функцию `url` и помимо псевдонима передаем значение slug'a для идентификации.

Упростим генерацию ссылок на отдельные страницы. Для этоко определим у класса `Post` метод `get_absolute_url(self)`. Его название - соглашение django. Этот метод будте возвращать url на страницу с отдельным постом.
```python
class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('post_detail_url', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}'.format(self.title)
```
Функция `reverse('название шаблона', 'словарь kwargs, где ключ - поле для идентификации, значение - slug конкретного экземпляра')` работает аналогично ф-ции `url` в html-шаблонах.
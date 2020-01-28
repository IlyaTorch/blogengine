# #1 Структура Django проекта. Обработка запросов. Генерация HTML

## Структура Django проекта
---
Django реализует шаблон MVC, который в терминологии django имеет следующий вид:
**Model** - код моделей для таблиц в базе данных
**View** - код демонстраци ответа пользователю(html-шаблоны)
**Controller** - код маршрутизации и обработки запроса(`urls.py`, `views.py`)

Django проект состоит из приложений. Для создания django-приложения нужно выполнить следующую команду:
```
$ python manage.py startapp blog
```
Далее приложение нужно подключить к проекту. Для этого в файл `settings.py` нужно добавить название нашего приложения в конец массива INSTALLED_APPS.
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'blog',
]
```

## Обработка запросов
---
Файл `urls.py` содержит список `urlpatterns`, в котором сопоставляются url-шаблоны с их функциями-обработчиками, которые, возможно, имеют псевдонимы(`name`)
`urls.py`
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls'))
]
```
Функция `path` принимает следующие параметры: шаблон url, функция-обработчик для url, имя шаблона, параметры ф-ции в виде словаря.

Вместо-функции обработчика в функцию `path()` может передваться функция `include('urls.py отдельного приложения')`, которая будет передавать усеченный url на обработку в файл `urls.py` приложения для более детальной маршрутизации. Это позволяет разделить, запросы к приложениям.
`blog/urls.py`
```python
urlpatterns = [
    path('', views.posts_list)
]
```

Сами функции обработчики находятся в файле `views.py`, Они принимают объект request и возвращают html-шаблон, наполненный данными. Для этого используется функция `render`. Данные передаются в словаре context. Рендеринг - процесс наполнения шаблона данными.

`views.py`
```python
def posts_list(request):
    n = ['Ilua', 'Nick', 'Roma']
    return render(request, 'blog/index.html', context={'names': n})
```

## Генерация HTML
---
Для удобства наполнения шаблонов данными в django используется механизм наследования шаблонов. В основном шаблоне содержатся общие элементы для страниц, в производных - частные.

Разметка подстановки частностей в базовый шаблон происходит с использованием блоков. В базовом шаблоне помимо общих элементов размечаются блоки со значением по-умолчанию, которые будут меняться в зависимости от страницы.

`base.html`
```django
<div class="container mt-5">
	<div class="row">
		<div class="col-lg-6 offset-md-2">
			{% block content %}
				No content
			{% endblock %}
		</div>
	</div>
</div>
```
В производном шаблоне достаточно наследоваться от базового шаблона и изменить такой блок.

`index.html`
```django
{% extends 'blog/base_blog.html' %}

{% block content %}
	<h1 class="mb-5">Posts</h1>
	{% for name in names %}
		<p>{{ name }}</p>
	{% endfor %}
{% endblock %}
```

По умолчанию шаблоны проекта хранятся в папке `templates`. Каждое приложение хранит свои шаблоны внутри себя в папке `templates/blog`. Чтобы поиск шаблонов по приложениям выполнялся, нужно добавить строку 
```
'DIRS': [os.path.join(BASE_DIR, 'templates')]
```
в файл `settings.py`.

`settings.py`
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        ...
    },
    ...
]
```

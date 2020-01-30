# #4 Class Based Views. Миксины

## Class Based Views
---
В django вместо функции-обработчика запроса можно использовать класс(или любой callable объект). Это удобнее в плане обработки запросов различных типов (get, post, put, ...) и в плане сокращения количества кода. 

В django есть класс `View`, с помощью которого удобно обрабатывать различные http запросы.

Заменим вьюхи `post_detail` и `tag_detail` на классы:

`views.py`
```python
...
class PostDetail(View):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug__iexact=slug)
        return render(request, 'blog/post_detail.html', context={'post': post})
...
```
Определили метод `get` для обработки get-запросов.
Испльзуем функцию `get_object_or_404(модель, логика, с помощью которой происходит поиск объекта)`, чтобы исправить исключение при отсутствии объекта "Does not exists" на вывод ошибки 404.

`urls.py`
```python
...
urlpatterns = [
    path('posts/<str:slug>/', views.PostDetail.as_view(), name='post_detail_url'),
    ...
]
```
Класс `PostDetail` обрабатывает запросы исп-я метод `as_view()`.(`as_view` - метод класса `View`)
    
## Миксины
---
Проблема избыточности кода решается с помощью классов-миксинов (классов с общим поведением для наших классов-обработчиков)
Для того, чтобы использовать такие классы, создадим файл `utils.py`. Далее выделим общие и частные моменты.

Общие выносим в `utils.py`, частные - в переменные.

`utils.py`
```python
class ObjectDetailMixin:
    model = None
    template = None

    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        return render(request, self.template, context={self.model.__name__.lower(): obj})
```
`self.model.__name__.lower()` - название класса-модели в нижнем регистре.
`views.py`
```python
class PostDetail(ObjectDetailMixin, View):
    model = Post
    template = 'blog/post_detail.html'
```
Класс `PostDetail` наследуем от класса-миксина `ObjectDetailMixin`, и класса `View`.

##### !!! Порядок наследования имеет значение

```django
>>> class Person:
...     name='Ilya'
...
>>> class Human:
...     name=None
>>>class Man(Person, Human):
        pass
>>> a = Man()
>>> a.name
'Ilya'
>>> Person.mro()
[<class 'Man'>, <class 'Person'>, <class 'Human'>, <class 'object'>]
```
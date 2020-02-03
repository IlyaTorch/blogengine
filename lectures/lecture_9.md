# #10 Перенаправление пользователя. Ограничение доступа к страницам

## Перенаправление пользователя
---
Сначала сделаем, чтобы при обращении к главному домену, мы перенаправлялись на страницу с постами. Для этого восполюзуемся функцией `redirect`.

`blogengine/views.py`
```python
def redirect_blog(request):
    return redirect('posts_list_url', permanent=True)
```
Функция `redirect('имя url, по которому происходит перенаправление', указываем, что редирект будет постоянным)`.

`blogengine/urls.py`
```python
...
urlpatterns = [
    path('', views.redirect_blog),
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls'))
]
```

## Ограничение доступа к страницам
---
Сделаем так, чтобы панель администратора отоборажалась только админам(это делается на уровне html-шаблонов).
Ограничим доступ к некоторым страницам(на уровне вьюх).

Сделаем суперпользователя:
```
$ python manage.py createsuperuser
```
Далее по адресу .../admin авторизовываемся этим пользователем.

**Скрываем панель администратора** от неавторизованных польлзователей:

Сессия хранится в объекте `request`, у которого есть атрибут `user`. Поместим html-разметку панели в блок `if`:

`base.html`
```django
{% if request.user.is_authenticated and request.user.is_staff %}
		<div class="admin-panel align-items-center">
			<a href="/admin" class="btn btn-outline-info">Admin</a>
			{% block admin_panel %}

			{% endblock %}
		</div>
	{% endif %}
```
Если какое-нибудь из условий `request.user.is_authenticated`(авторизован ли пользователь) и `request.user.is_staff`(является ли пользователь администратором) не выполняетя, то панель не отображается на странице.

**Ограничим доступ** к страницам создания, редактирования, удаления постов и тегов.

Для этого используем специальный класс-миксин `LoginRequiredMixin`, который подставляем в качестве предка к классам-вьюхам нужных страниц. Если же в качестве вьюх испльзуются не классы, а функции, то для **ограничения доступа** можно исп-ть.

С помощью этого миксина можно делать перенаправление на страницу с авторизацией, или же возбуждать исключение, что мы и сделаем. Для этогу у нужных классов-вьюх(которые уже наследуются от `LoginRequiredMixin`) переопределим св-во `raise_exception` в `True`.

`blog/views.py`
```python
class TagCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    model_form = TagForm
    template = 'blog/tag_create.html'
    raise_exception = True
```
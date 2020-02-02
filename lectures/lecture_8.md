# #9 CSS

Добавим панель администратора.

`base.html`
```django
<div class="admin-panel align-items-center">
		<a href="/admin" class="btn btn-outline-info">Admin</a>
		{% block admin_panel %}
		
		{% endblock %}
	</div>
```

## Подключение CSS
---
Рассмотрим файл `settings.py`.
Переменная `STATIC_URL = '/static/'` определяет положение статических файлов для отдельных ПРИЛОЖЕНИЙ(папка static). ОпределимCоздадим переменную `STATICFILES_DIRS` для подключения статических файлов для всего проекта.

`settings.py`
```python
...
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
```

Далее в самом начале базового шаблона `base.html` загружаем статические файлы: `{% load static %}`. Далее подключаем файл со стилями: `<link rel="stylesheet" href="{% static 'css/styles.css' %}">`

Ссылки на изменение и удаление постов(edit, delete) будут показываться только в случае, когда мы находимся на странице отдельного поста или тега. Когда находимся на странице с постом, кнопка edit будет вести на редактирование поста, а когда на странице тега - на редактирование тега(кнопка delete - на удаление соответственно). Для этого во вьюхе отдельных страниц в словарь `context` будем передавать переменную `admin_object`, чтобы относительно нее вызвать методы `get_update_url` и `get_delete_url`, и `detail`, чтобы отображать поля create и update только на отдельных страницах тегов и постов. Кнопка create будет представлять собой выпадающее меню с ссылками на создание поста и тега.

`utils.py`
```python
class ObjectDetailMixin:
    model = None
    template = None

    def get(self, request, slug):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        return render(request, self.template, context={self.model.__name__.lower(): obj, 'admin_object': obj, 'detail': True})
```
`base_blog.html`
```django
{% extends 'base.html' %}

{% block admin_panel %}

    <div class="btn-group">
      <button type="button" class="btn btn-light dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Create
      </button>
      <div class="dropdown-menu">
        <a class="dropdown-item" href="{% url 'post_create_ur'%}">Post</a>
        <a class="dropdown-item" href="{% url 'tag_create_url' %}">Tag</a>
      </div>
    </div>
    <a href="{{ admin_object.get_update_url }}" class="btn btn-light edit" style="{% if detail %}display: block;{% endif %}">Edit</a>
    <a href="{{ admin_object.get_delete_url }}" class="btn btn-danger delete" style="{% if detail %}display: block;{% endif %}">Delete</a>

{% endblock %}
```

`style.css`
```css
.admin-panel{
    border: 1px solid #999;
    border-radius: 2px;
    position: fixed;
    right: 50px;
    bottom: 30px;
    opacity: 0.3;
    padding: 15px;
}

.admin-panel:hover{
    opacity: 1;
}

.admin-panel a{
    display: block;
    margin: 5px 0;
}

a.edit, a.delete{
    display: none;
}
```
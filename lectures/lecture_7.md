# #7 Редактирование объектов моделей через html-форму
Редактирование будет происходить следующим образом:
1) Идентифицируем объект и извлекаем его из бд
2) Показываем форму для изменения объекта и подставляем в эту форму данные объекта
3) Получаем измененные данные, проверяем на валидность, сохраняем.

Для редактирования тегов определим класс `TagUpdate`.

`views.py`
```python
class TagUpdate(View):
    def get(self, request, slug):
        tag = Tag.objects.get(slug__iexact=slug)
        bound_form = TagForm(instance=tag)
        return render(request, 'blog/tag_update.html', context={'form': bound_form, 'tag': tag})

    def post(self, request, slug):
        tag = Tag.objects.get(slug__iexact=slug)
        bound_form = TagForm(request.POST, instance=tag)

        if bound_form.is_valid():
            new_tag = bound_form.save()
            return redirect(new_tag)
        return render(request, 'blog/tag_update.html', context={'form': bound_form, 'tag': tag}) 
```
Метод `get` принимает slug в качестве идентификатора тега.
`bound_form = TagForm(instance=tag)` - заполняем поля формы данными объекта.

В методе `post` в конструктор формы передаем словарь `POST` с данными формы и тег, который хотим отредактировать: `bound_form = TagForm(request.POST, instance=tag)`

`tag_update.html`
```django
{% extends 'blog/base_blog.html' %}
{% block title %}
	Edit Tag "{{ tag.title|title }}" - {{ block.super }}
{% endblock %}

{% block content %}
	<form action="{{ tag.get_update_url }}" method="post">
		{% csrf_token %}
		{% for field in form %}
			<div class="form-group">
				{% if field.errors %}
					<div class="alert alert-danger">
						{{ field.errors }}
					</div>
				{% endif %}
				{{ field.label }}
				{{ field }}
			</div>
		{% endfor %}

		<button type="submit" class="btn btn-primary">Update Tag</button>
	</form>
{% endblock %}
```
Вместо использования django-функции `url` и передачи в нее slug'а определили у класса `Tag` метод `get_update_url`, чтобы получать url вьюхи обработки запроса на редактирование формы: `<form action="{{ tag.get_update_url }}" method="post">` 

`models.py`
```python
class Tag(View):
    ...
    def get_update_url(self):
        return reverse('tag_update_url', kwargs={'slug': self.slug})
```

`urls.py`
```python

urlpatterns = [
    ...
    path('tags/<str:slug>/update/', views.TagUpdate.as_view(), name='tag_update_url')
]
```

Редактирование постов происходит аналогично редактированию тегов, поэтому для классов `TagForm` и `PostForm` создадим класс-миксин `ObjectUpdateMixin`.

`utils.py`
```python
class ObjectUpdateMixin:
    model = None
    template = None
    model_form = None

    def get(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(instance=obj)
        return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})

    def post(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(request.POST, instance=obj)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})
```

Теперь класс `TagUpdate` примет следующий вид:
`views.py`
```python
...

class TagUpdate(ObjectUpdateMixin, View):
    model = Tag
    template = 'blog/tag_update.html'
    model_form = TagForm
```
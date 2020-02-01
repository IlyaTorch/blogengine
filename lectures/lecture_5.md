# #5 Работа с формами
Продолжим реализовывать функциональность CRUD(create, read, update, delete) сущностей классов-моделей(`Post` и `Tag`).Read - было реализовано ранее.

Будем создавать теги через html-форму. Для этого нам нужна сама html-форма, также нужно проверять и очищать данные, введенные пользователем. После чего эти данные будем передавать в конструктор и создавать объект, который потом будет сохраняться в бд.

Для html-формы опишем djngo-класс `TagForm`.

`forms.py`

```python
class TagForm(forms.Form):
    title = forms.CharField(max_length=50)
    slug = forms.CharField(max_length=50)
```
Класс `forms.Form` для каждого своего поля генерирует соответствующий html- тег(в терминологии django - **виджет**).
В нашем случае это input поля(**CharField** соответствует input).
Также класс `Form` проводит валидацию и очистку данных с помощью встроенных *clean* методов.

##### Класс формы соответствует классу-модели (TagForm <-> Tag). Поля формы должны соответствовать полям модели, если они не заполняются django автоматически. 

При работе с html-формами, для создания объекта модели(`Tag` или `Post`), мы передаем в конструктор соответствующей модели данные из специального словаря **cleaned_data**, который является атрибутом экземпляра класса формы(`TagForm` или `PostForm`)
```django
>>> tf = TagForm()
>>> tf
<TagForm bound=False, valid=Unknown, fields=(title;slug)>
```
`fields` -  поля `TagForm`, которые мы описали в `forms.py`
`bound` - св-во, котоворит о том, ввел ли пользователь какие-либо данные, или нет(свзяана ли форма).

``` django
>>> d = {'title' : '', 'slug' : ''}
>>> tf = TagForm(d)
>>> tf
<TagForm bound=True, valid=Unknown, fields=(title;slug)>
>>> tf.is_valid()
False
```
После вызова метода **is_valid()** появляется поле cleaned_data(*is_valid* вызывает специальные clean методы всей формы и некоторых отдельных полей, и происходит проверка и очиска данных, введенных пользователем). Далее очищенные и провалидированные данные помещаются в словарь `cleaned_data`. Ошибки при валидации помещаются в словарь `errors`.
```python
>>> tf.errors
{'title': ['This field is required.'], 'slug': ['This field is required.']}
>>> tf.cleaned_data
{}
```

Данные из словаря `cleaned_data` будем использовать при создании объектов моделей.
```django
>>> d = {'title' : 'some title', 'slug' : 'some-title'}
>>> tf = TagForm(d)
>>> tf
<TagForm bound=True, valid=Unknown, fields=(title;slug)>
>>> tf.is_valid()
True
>>> tf.errors
{}
>>> tf.cleaned_data
{'title': 'some title', 'slug': 'some-title'}
>>> tag = Tag(title=tf.cleaned_data['title'], slug=tf.cleaned_data['slug'])
>>> tag
<Tag: some title>
>>> tag.save()
>>> tag.id
2
```

**Валидация и очистка данных происходит следующим образом:**
1. Вызывается метод **is_valid**, который вызывает специальные clean методы всей формы и отдельных полей.
2. clean-метод формы проверяет и очищает введенные пользователем данные. Затем очищенные и провалидированные данные помещаются в словарь **cleaned_data**. Если что-то пошло не так, django вызывает исключение **ValidationError**.
3. Если мы переопределилии некоторые методы и дополнили валидацию для полей специальным поведением, то вызываются и эти методы для введенных данных.


*cleaned_data* используется для того, чтобы в бд попадали очищенные данные, а не те, которые непосредственно ввел пользователь, поскольку это большая уязвимость в безопасности.

Реализуем автоматическое сохранение тегов в бд. Для этого у класса `TagForm` определим метод `save`.

`forms.py`
```python
class TagForm(forms.Form):
    title = forms.CharField(max_length=50)
    slug = forms.CharField(max_length=50)
    
    def save(self):
        new_tag = Tag.objects.create(title=self.cleaned_data['title'],slug=self.cleaned_data['slug'])
        return new_tag
```
(Когда создаем объект через менеджер моделей, он автоматически сохраняется в базу данных)
```django
>>> d = {'title': 'framework', 'slug' : 'framework'}
>>> tf = TagForm(d)
>>> tf
<TagForm bound=True, valid=Unknown, fields=(title;slug)>
>>> tf.is_valid()
True
>>> tf.cleaned_data
{'title': 'framework', 'slug': 'framework'}
>>> t = tf.save()
>>> t
<Tag: framework>
```

Зададим url-шаблон, функцию-обработчик, html-шаблон для создания тега.
url-шаблон страницы с созданием тега будет иметь вид "tags/create".
В `urls.py` между `path('tags/create', ...)` и `path('tag/<str:slug>/' ...)` возникает конфликт т.к. в бд не может быть тега со слагом create(шаблон "tags/create" используется для страницы создания тега). Поэтому путь для создания тега помещаем выше шаблона для просмотра отделльных тегов и добавим дополнительную проверку для slug'a.

`urls.py`
```python
urlpatterns = [
    ...
    path('tags/create', views.TagCreate.as_view(), name='tag_create_url'),
    path('tags/<str:slug>', views.TagDetail.as_view(), name='tag_detail_url'),
]
```

Кроме этого слаги тегов будем сохранять в бд в нижнем регистре, чтобы не нарушалась сортировка по алфавиту. Для этого будем определим свой clean-метод для поля `slug` класса `TagForm` (метод `clean_slug`). Название этого метода - соглашение django.

```python
class TagForm(forms.Form):
    title = forms.CharField(max_length=50)
    slug = forms.CharField(max_length=50)
    
    def save(self):
        new_tag = Tag.objects.create(title=self.cleaned_data['title'],slug=self.cleaned_data['slug'])
        return new_tag
        
    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()

        if new_slug == 'create':
            raise ValidationError('Slug may not be "create"')
        if Tag.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('Slug must be unique. We have "{}" slug already'.format(new_slug))

        return new_slug
```
   
Вьюха `"tags/create"`:
`views.py`
```python
class TagCreate(View):
    def get(self, request):
        form = TagForm()
        return render(request, 'blog/tag_create.html', context={'form': form})

    def post(self, request):
        bound_form = TagForm(request.POST)

        if bound_form.is_valid():
            new_tag = bound_form.save()
            return redirect(new_tag)
        return render(request, 'blog/tag_create.html', context={'form': bound_form})
```
Класс `TagCreate` обрабатывает **get-запрос**(отображение html-страницы с формой) и **post-запрос**(заполнение формы и создание нового тега)

`form = TagForm()` **:** Конструктор `TagForm()` пустой, поскольку при get-запросе мы отображаем пустую форму.
`bound_form = TagForm(request.POST)` **:** `request.POST` - словарь, где ключи - поля формы, значения - введденные пользователем данные.
Функция `redirect` может применять не только url, а, например, и объекты.
`return redirect(new_tag)` - перенаправляет пользователя на страницу с созданным тегом.
В случает ошибки пользователь остается на текущей странице и получает уведомление об ошибке: `return render(request, 'blog/tag_create.html', context={'form': bound_form})`

`tag_create.html`
```django
{% extends 'blog/base_blog.html' %}
{% block title %}
	Tag Create - {{ block.super }}
{% endblock %}

{% block content %}
	<form action="{% url 'tag_create_url' %}" method="post">
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
		
		<button type="submit" class="btn btn-primary">Create Tag</button>
	</form>
{% endblock %}
```

`<form action="{% url 'tag_create_url' %}" method="post">` - возваращает url, который будет обрабатывать вьюха `views.TagCreate.as_view()`(метод post).

Зададим стили input'ам формы. Для этого переопределим атрибуты **виджетов**(html-тегов, которые соответствуют полям в `TagForm`) в классе `TagForm`.

`forms.py`
```python
class TagForm(forms.Form):
    title = forms.CharField(max_length=50)
    slug = forms.CharField(max_length=50)
    
    title.widget.attrs.update({'class': 'form-control'})
    slug.widget.attrs.update({'class': 'form-control'})
    
    def save(self):
        new_tag = Tag.objects.create(title=self.cleaned_data['title'],slug=self.cleaned_data['slug'])
        return new_tag
        
    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()

        if new_slug == 'create':
            raise ValidationError('Slug may not be "create"')
        if Tag.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('Slug must be unique. We have "{}" slug already'.format(new_slug))

        return new_slug
```

Теперь мы столкнулись с проблемой, что в случае, если мы захотим добавить или удалить поля модели(`Tag`), то нам придется редактировать класс `TagForm`. Чтобы избежать таких ситуаций, будем использовать в качестве родителя класса `TagForm` другой класс - `ModelForm`, который связывает модель с соответствующей этой модели формой.

Связывание модели с формой осуществляется с помощью подкласса `Meta`, в котором мы определяем класс-модель в атрибуте `model` и перечисляем поля формы в арибуте `fields`.
Также переопределим атрибуты(css-классы) для наших **виджетов**(html-тегов, которые соответствуют полям в `TagForm`).

Также убираем метод `save()` т.к. в `ModelForm` есть встроенный метод `save`, который в отличие от определенного ранне не только может создавать объект, а еще и изменять уже имеющийся.

`forms.py`
```python
class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = ['title', 'slug']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()

        if new_slug == 'create':
            raise ValidationError('Slug may not be "create"')
        if Tag.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('Slug must be unique. We have "{}" slug already'.format(new_slug))

        return new_slug
```

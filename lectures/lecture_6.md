# #6 Работа с формами ч. 2
Класс `PostForm` написан аналогично классу `TagForm` за исключением отсутствия проверки slug'a на уникальность, поскольку он будет генерироваться уникальным при создании объекта модели автоматически.

 ### Генерация слага:
В django есть специальная функция `slugify(string)`, которая получает строку и возвращает строку, состоящую только из символов букв, цифр, "-", "_".
```python
>>> slugify('TExt-53text_^&*(*%##@')
'text-53text_'
```
Для уникальности slug'а будем присоединять к результату функции `slugify()`
результат выполнения функции `time()`.

`models.py`
```python
def gen_slug(s):
    new_slug = slugify(s, allow_unicode=True)
    return new_slug + '-' + str(int(time()))
```

Переопределим у класса `Post` метод `save`, чтобы он генерировал slug автоматически при сохранении объекта в бд. Более того, slug будет генерироваться только при создании объекта, при изменении уже существующего - нет. Для этого используем то, что поле `id` есть только у сохраненных в бд моделей.

`models.py`
```python
class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, blank=True, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')

    def get_absolute_url(self):
        return reverse('post_detail_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
```

Чтобы не нарушать принцип **DRY**, сделаем миксин для классов `PostCreate` и `TagCreate`.

`utils.py`
```python
class ObjectCreateMixin:
    model_form = None
    template = None

    def get(self, request):
        form = self.model_form()
        return render(request, self.template, context={'form': form})

    def post(self, request):
        bound_form = self.model_form(request.POST)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)

        return render(request, self.template, context={'form': bound_form})
```
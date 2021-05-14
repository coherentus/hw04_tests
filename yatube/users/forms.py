from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Никнейм для сайта',
            'email': 'email адрес',
        }
        help_texts = {
            'first_name': ('Имя и фамилия, которые будут сопровождать Ваши'
                           ' записи на сайте'),
            'last_name': 'По ним Вас будут узнавать другие пользователи',
            'username': ('После регистрации будет использоваться для входа'
                         ' на сайт'),
            'email': ('Необходим как для регистрации, так и для сброса/восс'
                      'тановления пароля, для связи с Администрацией сайта'),
        }

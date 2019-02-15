from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User
from django.forms import fields, widgets



class Registeruser(forms.Form):
    username = fields.CharField(
        required = True,
        widget = widgets.TextInput(attrs={'class': "form-control", 'placeholder': '用户名为6-12个字符'}),
        min_length = 6,
        max_length = 12,
        strip = True,
        error_messages = {
                            'required':'用户名不能为空',
                            'max_length':'用户名长度不能超过12个字符',
                            'min_length':'用户名长度不能小于6个字符',
                          }
    )


    password = fields.CharField(
        required = True,
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '请输入密码,密码必须为6-12个字符'},
                                     render_value=True),
        min_length = 6,
        max_length = 12,
        strip = True,
        error_messages = {
            'required': '密码不能为空',
            'max_length': '密码长度不能超过12个字符',
            'min_length': '密码长度不能小于6个字符',
        }

    )


    password_again = fields.CharField(
        required = True,
        widget = widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '请再次输入密码!'}, render_value=True),
        strip = True,
        error_messages = {'required': '请再次输入密码!',}
    )



    def clean_username(self):
        username = self.cleaned_data['username']
        users = User.objects.filter(username=username).count()
        if users > 0:
            raise ValidationError('用户已经存在！')
        return username


    def clean_password(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_again')
        print(password1)
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('两次密码不匹配！')
        return password1



class weblogin(forms.Form):

    username = fields.CharField(
        required = True,
        widget = widgets.TextInput(attrs={'class': "form-control", 'placeholder': '请输入用户名'}),
        min_length = 6,
        max_length = 12,
        strip = True,
        error_messages = {
                            'required':'用户名不能为空',
                            'max_length':'用户名长度不能超过12个字符',
                            'min_length':'用户名长度不能小于6个字符',
                          }
    )


    password = fields.CharField(
        required = True,
        widget=widgets.PasswordInput(attrs={'class': "form-control", 'placeholder': '请输入密码'},
                                     render_value=True),
        min_length = 6,
        max_length = 12,
        strip = True,
        error_messages = {
            'required': '密码不能为空',
            'max_length': '密码长度不能超过12个字符',
            'min_length': '密码长度不能小于6个字符',
        }

    )



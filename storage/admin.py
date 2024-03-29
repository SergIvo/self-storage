from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import User, Warehouse, StorageType, Storage, UserStorage


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['email']

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'phonenumber', 'is_active', 'is_staff']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email', 'is_staff']
    list_filter = ['is_staff']
    fieldsets = [
        (None, {'fields': ['email', 'password', 'name', 'phonenumber']}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': ['email', 'password1', 'password2'],
            },
        ),
    ]
    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = []


class StoragesInline(admin.TabularInline):
    model = Storage
    raw_id_field = ('storages',)
    verbose_name_plural = 'Доступные типы хранилищ'


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['address']
    list_filter = ['feature', 'temperature', 'ceiling_height']
    
    inlines = (StoragesInline,)


@admin.register(StorageType)
class StorageTypeAdmin(admin.ModelAdmin):
    search_fields = ['length', 'width', 'height']
    list_display = ['get_area']
    list_filter = ['length', 'width', 'height']
    raw_id_field = ('storages',)


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ['floor', 'number', 'warehouse']
    list_filter = ['floor', 'warehouse']


@admin.register(UserStorage)
class UserStorageAdmin(admin.ModelAdmin):
    list_display = ['user', 'storage']
    raw_id_field = ('user', 'storage')

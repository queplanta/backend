from calendar import timegm
from datetime import datetime

import graphene
import graphql_social_auth

import mailing

from django import forms
from django.conf import settings
from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout
)
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
    UserCreationForm as DjangoUserCreationForm
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _

from graphql_jwt.settings import jwt_settings

from backend.fields import Error
from backend.mutations import Mutation
from utils.forms import form_erros
from .models_graphql import User
from .models import User as UserModel
from .decorators import login_required


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = UserModel
        fields = ("username", "email", "first_name")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserModel.objects.filter(username=username).exists():
            raise forms.ValidationError(
                _("Este usuario já esta usado por outra pessoa. "
                  "Por favor, tente outro."),
                code='username_being_used',
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("Este e-mail já esta usado por outra pessoa. "
                  "Por favor, tente outro."),
                code='email_being_used',
            )
        return email


class RegisterInput(graphene.AbstractType):
    first_name = graphene.String()
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password1 = graphene.String(required=True)
    password2 = graphene.String(required=True)


class RegisterAbstract(graphene.AbstractType):
    user = graphene.Field(User)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        errors = []
        user = None

        form = UserCreationForm(data=data)
        if form.is_valid():
            user = form.save(commit=False)
            user.save(request=info.context)

            email = mailing.Welcome()
            email.send(user.email, {})
        else:
            errors = form_erros(form, errors)
        return Register(user=user, errors=errors)


class Register(RegisterAbstract, Mutation):
    class Input(RegisterInput):
        pass


class RegisterAndAuthenticate(RegisterAbstract, Mutation):
    token = graphene.String(required=False)
    payload = graphene.String(required=False)
    refresh_expires_in = graphene.Int(required=False)

    class Input(RegisterInput):
        pass

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        register = super().mutate_and_get_payload(root, info, **data)
        if register.user:
            register.user.backend = settings.DEFAULT_AUTHENTICATION_BACKENDS
            auth_login(info.context, register.user)
            payload, token = get_payload_and_token(register.user, info.context)
            refresh_expires_in = get_refresh_expires_in()
            return RegisterAndAuthenticate(user=register.user, token=token, refresh_expires_in=refresh_expires_in, errors=register.errors)
        return RegisterAndAuthenticate(user=register.user,
                                       errors=register.errors)


def get_payload_and_token(user, context, **extra):
    payload = jwt_settings.JWT_PAYLOAD_HANDLER(user, context)
    payload.update(extra)
    token = jwt_settings.JWT_ENCODE_HANDLER(payload, context)
    return payload, token


def get_refresh_expires_in():
    return (
        timegm(datetime.utcnow().utctimetuple()) +
        jwt_settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()
    )


class Authenticate(Mutation):
    token = graphene.String(required=False)
    payload = graphene.String(required=False)
    refresh_expires_in = graphene.Int(required=False)

    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        errors = []
        user = None
        request = info.context

        if request.user.is_authenticated:
            auth_logout(request)

        form = AuthenticationForm(request=request, data=data)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            payload, token = get_payload_and_token(user, request)
            refresh_expires_in = get_refresh_expires_in()
            return Authenticate(token=token, refresh_expires_in=refresh_expires_in, errors=errors)
        else:
            errors = form_erros(form, errors)

        return Authenticate(errors=errors)


class Deauthenticate(Mutation):
    class Input:
        pass

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **data):
        auth_logout(info.context)
        return Deauthenticate()


class PasswordChange(Mutation):
    class Input:
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)
        old_password = graphene.String(required=True)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **data):
        errors = []
        form = PasswordChangeForm(user=info.context.user, data=data)
        if form.is_valid():
            user = form.save(commit=False)
            user.save(request=info.context)

            # workarout to re authenticate the user
            # when as change the user on the DB it gets disconected
            user.backend = settings.DEFAULT_AUTHENTICATION_BACKENDS
            auth_login(info.context, user)
        else:
            errors = form_erros(form, errors)
        return PasswordChange(errors=errors)


class NoUserPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("Email not found."),
                code='email_not_found',
            )
        return email


class PasswordResetEmail(Mutation):
    class Input:
        email = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        errors = []
        form = NoUserPasswordResetForm(data=data)
        if form.is_valid():
            opts = {
                'use_https': info.context.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': 'emails/password_reset-body-text.html',
                'subject_template_name': 'emails/password_reset-subject.html',
                'request': info.context,
                'html_email_template_name': 'emails/password_reset-body-html.html',
                'extra_email_context': None,
            }
            form.save(**opts)
        else:
            errors = form_erros(form, errors)
        return PasswordChange(errors=errors)


class PasswordResetComplete(Mutation):
    class Input:
        uidb64 = graphene.String(required=True)
        token = graphene.String(required=True)
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        errors = []
        UserModel = User._meta.model

        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(data.get('uidb64')))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, data.get('token')):
            form = SetPasswordForm(user=user, data=data)
            if form.is_valid():
                user = form.save(commit=False)
                user.save(request=info.context)

                # workarout to re authenticate the user
                # when as change the user on the DB it gets disconected
                user.backend = settings.DEFAULT_AUTHENTICATION_BACKENDS
                auth_login(info.context, user)
            else:
                errors = form_erros(form, errors)
        else:
            errors.append(Error(
                code='password_reset_incorrect_token',
                message=_('Password reset failed')
            ))

        return PasswordResetComplete(errors=errors)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ("username", "email", "first_name")

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserModel.objects.filter(username=username).exclude(
                document_id=self.instance.document_id).exists():
            raise forms.ValidationError(
                _("Este usuario já esta usado por outra pessoa. "
                  "Por favor, tente outro."),
                code='username_being_used',
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserModel.objects.filter(email=email).exclude(
                document_id=self.instance.document_id).exists():
            raise forms.ValidationError(
                _("Este e-mail já esta usado por outra pessoa. "
                  "Por favor, tente outro."),
                code='email_being_used',
            )
        return email


class ProfileEdit(Mutation):
    class Input:
        first_name = graphene.String()
        username = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(User)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **data):
        errors = []
        request = info.context
        user = request.user

        form = UserEditForm(data=data, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save(request=request)

            # workarout to re authenticate the user
            # when as change the user on the DB it gets disconected
            user.backend = settings.DEFAULT_AUTHENTICATION_BACKENDS
            auth_login(request, user)
        else:
            errors = form_erros(form, errors)
        return ProfileEdit(user=user, errors=errors)


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ("avatar",)


class ProfileChangeAvatar(Mutation):
    class Input:
        pass
    #     avatar = graphene.String()

    user = graphene.Field(User)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, **input):
        request = info.context
        errors = []
        user = request.user

        form = UserAvatarForm(input, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save(request=request)

            # workarout to re authenticate the user
            # when as change the user on the DB it gets disconected
            user.backend = settings.DEFAULT_AUTHENTICATION_BACKENDS
            auth_login(request, user)
        else:
            errors = form_erros(form, errors)
        return ProfileChangeAvatar(user=user, errors=errors)


class Mutations(object):
    register = Register.Field()
    register_and_authenticate = RegisterAndAuthenticate.Field()

    authenticate = Authenticate.Field()
    deauthenticate = Deauthenticate.Field()
    social_auth = graphql_social_auth.relay.SocialAuth.Field()

    me_password_change = PasswordChange.Field()
    me_password_reset_email = PasswordResetEmail.Field()
    me_password_reset_complete = PasswordResetComplete.Field()

    me_profile_edit = ProfileEdit.Field()
    me_profile_change_avatar = ProfileChangeAvatar.Field()

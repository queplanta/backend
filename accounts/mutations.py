import graphene
from graphene.utils import with_context

from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout
)
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _

from backend.fields import Error
from backend.mutations import Mutation
from .models_graphql import User
from .decorators import login_required


def form_erros(form, errors=[]):
    for error_key, error_messages in form.errors.as_data().items():
        for error_instance in error_messages:
            for error_message in error_instance.messages:
                errors.append(Error(
                    key=error_instance.code,
                    message=error_message,
                ))
    return errors


class Register(Mutation):
    class Input:
        name = graphene.String()
        username = graphene.String().NonNull
        email = graphene.String().NonNull
        password = graphene.String().NonNull

    user = graphene.Field(User)

    @classmethod
    @with_context
    def mutate_and_get_payload(cls, input, request, info):
        user = User._meta.model(
            first_name=input.get('name'),
            username=input.get('username'),
            email=input.get('email'),
        )
        user.set_password(input.get('password'))
        user.save(request=request)
        return Register(user=user)


class Authenticate(Mutation):
    class Input:
        username = graphene.String().NonNull
        password = graphene.String().NonNull

    @classmethod
    @with_context
    def mutate_and_get_payload(cls, input, request, info):
        errors = []
        user = None

        if request.user.is_authenticated():
            auth_logout(request)

        form = AuthenticationForm(data=input)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
        else:
            errors = form_erros(form, errors)
        return Authenticate(errors=errors)


class Deauthenticate(Mutation):
    class Input:
        pass

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        auth_logout(request)
        return Deauthenticate()


class PasswordChange(Mutation):
    class Input:
        new_password1 = graphene.String().NonNull
        new_password2 = graphene.String().NonNull
        old_password = graphene.String().NonNull

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, input, request, info):
        errors = []
        form = PasswordChangeForm(user=request.user, data=input)
        if form.is_valid():
            user = form.save(commit=False)
            user.save(request=request)
        else:
            errors = form_erros(form, errors)
        return PasswordChange(errors=errors)


class PasswordResetEmail(Mutation):
    class Input:
        email = graphene.String().NonNull

    @classmethod
    @with_context
    def mutate_and_get_payload(cls, input, request, info):
        errors = []
        form = PasswordResetForm(data=input)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': 'registration/password_reset_email.html',
                'subject_template_name': 'registration/password_reset_subject.txt',
                'request': request,
                'html_email_template_name': None,
                'extra_email_context': None,
            }
            form.save(**opts)
        else:
            errors = form_erros(form, errors)
        return PasswordChange(errors=errors)


class PasswordResetComplete(Mutation):
    class Input:
        uidb64 = graphene.String().NonNull
        token = graphene.String().NonNull
        new_password1 = graphene.String().NonNull
        new_password2 = graphene.String().NonNull

    @classmethod
    @with_context
    def mutate_and_get_payload(cls, input, request, info):
        errors = []
        UserModel = User._meta.model

        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(input.get('uidb64')))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, input.get('token')):
            form = SetPasswordForm(user=user, data=input)
            if form.is_valid():
                user = form.save(commit=False)
                user.save(request=request)
            else:
                errors = form_erros(form, errors)
        else:
            errors.append(Error(
                key='password_reset_incorrect_token',
                message=_('')
            ))

        return PasswordResetComplete(errors=errors)

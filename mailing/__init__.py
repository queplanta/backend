from djmail import template_mail


class ForgotPassword(template_mail.TemplateMail):
    name = "password_reset"


class ReceivedIdentificationSuggestion(template_mail.TemplateMail):
    name = "received_identification_suggestion"


class Welcome(template_mail.TemplateMail):
    name = "welcome"

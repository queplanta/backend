from backend.fields import Error


def form_erros(form, errors=[]):
    for error_location, error_messages in form.errors.as_data().items():
        for error_instance in error_messages:
            for error_message in error_instance.messages:
                errors.append(Error(
                    code=error_instance.code,
                    location=error_location,
                    message=error_message,
                ))
    return errors

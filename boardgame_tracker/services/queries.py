from django.contrib.auth import get_user_model

User = get_user_model()


def filter_model(model, **fields):
    return model.objects.filter(**fields)


def get_first_instance(model, **fields):
    instance = filter_model(model, **fields)
    return instance.first()


def create_user(password, **fields):
    user = User(**fields)
    user.set_password(password)
    user.save()
    return user


def create_model_instance(model, **fields):
    instance = model(**fields)
    instance.save()
    return instance

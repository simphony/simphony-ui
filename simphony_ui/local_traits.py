from traits.api import BaseInt, BaseFloat


class PositiveFloat(BaseFloat):
    """ A custom trait representing a positive float """

    default_value = 1.0

    info_text = 'a positive float'

    def validate(self, object, name, value):
        value = super(PositiveFloat, self).validate(object, name, value)
        if value > 0.0:
            return value

        self.error(object, name, value)


class PositiveInt(BaseInt):
    """ A custom trait representing a positive integer """

    default_value = 1

    info_text = 'a positive integer'

    def validate(self, object, name, value):
        value = super(PositiveInt, self).validate(object, name, value)
        if value > 0:
            return value

        self.error(object, name, value)

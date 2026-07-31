class CoreUtils:
    @staticmethod
    def format_validation_errors(errors):
        return {
            field: messages[0] if isinstance(messages, list) else messages
            for field, messages in errors.items()
        }
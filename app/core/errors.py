class ExternalServiceError(RuntimeError):
    """Ошибка внешнего сервиса (2ГИС)."""

class IsochroneBuildError(RuntimeError):
    """Сервис 2ГИС не смог построить изохроны."""
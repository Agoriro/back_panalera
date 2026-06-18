# Paso 7: src/shared/exceptions/domain_exceptions.py
"""
Excepciones de dominio personalizadas.
La capa de aplicación y dominio lanzan estas excepciones, 
y la capa de infraestructura (routers) las maneja convirtiéndolas en HTTPException.
"""

class DomainException(Exception):
    """Excepción base del dominio."""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

class ResourceNotFoundException(DomainException):
    """Lanzada cuando no se encuentra un recurso solicitado."""
    pass

class ResourceAlreadyExistsException(DomainException):
    """Lanzada cuando se intenta crear un recurso que ya existe y debe ser único."""
    pass

class UnauthorizedException(DomainException):
    """Lanzada cuando las credenciales no son válidas."""
    pass

class ForbiddenException(DomainException):
    """Lanzada cuando el usuario no tiene permisos para la acción."""
    pass

class BusinessRuleValidationException(DomainException):
    """Lanzada cuando una regla de negocio no se cumple (ej. stock negativo)."""
    pass

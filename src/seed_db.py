import asyncio

from src.domain.entities.role import Role
from src.domain.entities.user import User
from src.infrastructure.database.repositories.role_repository import RoleRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.security.password import get_password_hash, verify_password
from src.interfaces.api.dependencies.database import async_session_maker
from src.shared.config.settings import settings


async def seed_database() -> None:
    print("Iniciando la siembra (seeding) de la base de datos...")

    username = settings.BOOTSTRAP_ADMIN_USERNAME
    password_setting = settings.BOOTSTRAP_ADMIN_PASSWORD
    if not username and not password_setting:
        print("Bootstrap admin omitido: no se configuraron credenciales.")
        return
    if not username or not password_setting:
        raise RuntimeError(
            "BOOTSTRAP_ADMIN_USERNAME y BOOTSTRAP_ADMIN_PASSWORD son obligatorios juntos"
        )

    username = username.strip()
    password = password_setting.get_secret_value()
    if len(username) < 3:
        raise RuntimeError("BOOTSTRAP_ADMIN_USERNAME debe tener al menos 3 caracteres")
    if len(password) < 12:
        raise RuntimeError("BOOTSTRAP_ADMIN_PASSWORD debe tener al menos 12 caracteres")

    async with async_session_maker() as session:
        role_repo = RoleRepository(session)
        user_repo = UserRepository(session)

        # 1. Verificar si el rol de admin ya existe
        roles = await role_repo.get_all()
        admin_role = next((r for r in roles if r.name.strip().lower() == "admin"), None)

        if not admin_role:
            print("Creando el rol 'Admin'...")
            new_role = Role(id_role=None, name="Admin")  # type: ignore
            admin_role = await role_repo.create(new_role)
            print(f"Rol 'Admin' creado exitosamente con ID: {admin_role.id_role}")
        else:
            print(f"El rol 'Admin' ya existe (ID: {admin_role.id_role}).")

        # 2. Verificar si el usuario 'admin' ya existe
        admin_user = await user_repo.get_by_username(username)

        if not admin_user:
            print(f"Creando el usuario administrador '{username}'...")
            hashed_pw = get_password_hash(password)
            new_user = User(
                id_user=None,  # type: ignore
                user=username,
                password=hashed_pw,
                id_role=admin_role.id_role,
                is_active=True,
            )
            created_user = await user_repo.create(new_user)
            print(f"Usuario 'admin' creado exitosamente con ID: {created_user.id_user}")
        else:
            changed = False
            if not verify_password(password, admin_user.password):
                admin_user.password = get_password_hash(password)
                changed = True
            if admin_user.id_role != admin_role.id_role:
                admin_user.id_role = admin_role.id_role
                changed = True
            if not admin_user.is_active:
                admin_user.is_active = True
                changed = True
            if changed:
                await user_repo.update(admin_user)
                print("Usuario administrador actualizado desde configuración segura.")
            print("El usuario administrador configurado ya existe.")

    print("Siembra finalizada.")


if __name__ == "__main__":
    asyncio.run(seed_database())

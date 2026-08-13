import asyncio
from src.interfaces.api.dependencies.database import async_session_maker
from src.infrastructure.database.repositories.role_repository import RoleRepository
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.domain.entities.role import Role
from src.domain.entities.user import User
from src.infrastructure.security.password import get_password_hash
from uuid import UUID

async def seed_database():
    print("Iniciando la siembra (seeding) de la base de datos...")
    
    async with async_session_maker() as session:
        role_repo = RoleRepository(session)
        user_repo = UserRepository(session)
        
        # 1. Verificar si el rol de admin ya existe
        roles = await role_repo.get_all()
        admin_role = next((r for r in roles if r.name.lower() == "Admin"), None)
        
        if not admin_role:
            print("Creando el rol 'Admin'...")
            new_role = Role(id_role=None, name="Admin")  # type: ignore
            admin_role = await role_repo.create(new_role)
            print(f"Rol 'Admin' creado exitosamente con ID: {admin_role.id_role}")
        else:
            print(f"El rol 'Admin' ya existe (ID: {admin_role.id_role}).")
            
        # 2. Verificar si el usuario 'admin' ya existe
        admin_user = await user_repo.get_by_username("admin")
        
        if not admin_user:
            print("Creando el usuario 'admin'...")
            hashed_pw = get_password_hash("admin123")
            new_user = User(
                id_user=None,  # type: ignore
                user="admin",
                password=hashed_pw,
                id_role=admin_role.id_role,
                is_active=True
            )
            created_user = await user_repo.create(new_user)
            print(f"Usuario 'admin' creado exitosamente con ID: {created_user.id_user}")
            print("Credenciales: user: admin | password: admin123")
        else:
            print("El usuario 'admin' ya existe en la base de datos.")
            
    print("Siembra finalizada.")

if __name__ == "__main__":
    asyncio.run(seed_database())

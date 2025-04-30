# Запросы к базе для работы с таблицей FAQ
from database.orm_query_template.orm_query_admin.orm_adm_FAQ import (
    orm_add_question,  # noqa: F401
    orm_get_question,  # noqa: F401
    orm_get_question_by_id,  # noqa: F401
    orm_delete_faqs_by_id,  # noqa: F401
)


# Запросы к базе для работы с таблицей админов
from database.orm_query_template.orm_query_admin.orm_adm_admin import (
    orm_add_admin,  # noqa: F401
    orm_change_admin,  # noqa: F401
    orm_delete_admins,  # noqa: F401
    orm_delete_admins_by_id,  # noqa: F401
    orm_get_admins,  # noqa: F401
    orm_get_admins_by_id,  # noqa: F401
    orm_get_admins_by_id_and_name,  # noqa: F401
)
from database.orm_query_template.orm_query_admin.orm_adm_files_folders import (
    orm_delete_file_and_folders,  # noqa: F401
)


# Запросы к базе для работы с таблицей пользователей
from database.orm_query_template.orm_query_admin.orm_adm_user import (
    orm_add_users,  # noqa: F401
    orm_change_user,  # noqa: F401
    orm_get_users_by_name,  # noqa: F401
    orm_delete_users_by_id,  # noqa: F401
    orm_get_users,  # noqa: F401
    orm_delete_users,  # noqa: F401
    orm_get_users_by_id # noqa: F401
)


# Запросы к базе для работы с таблицей файлов
from database.orm_query_template.orm_query_files import (
    orm_add_file,  # noqa: F401
    orm_change_file,  # noqa: F401
    orm_get_file_by_name,  # noqa: F401
    orm_delete_file_by_id,  # noqa: F401
    orm_get_file,  # noqa: F401
    orm_delete_file,  # noqa: F401
)


# Запросы к базе для работы с таблицей папок
from database.orm_query_template.orm_query_folders import (
    orm_add_folder,  # noqa: F401
    orm_get_folder_by_name,  # noqa: F401
    orm_get_folder,  # noqa: F401
    orm_delete_folder,  # noqa: F401
)

from os.path import join, dirname

from django.contrib.auth.models import Group, User
from django.core.management import execute_from_command_line

import vavilov
from vavilov.conf.settings import PUBLIC_GROUP_NAME
from vavilov.db_management.base import (load_initial_data, INITIAL_DATA_DIR,
                                        add_accessions)
from vavilov.db_management.phenotype import (add_or_load_assays,
                                             add_or_load_excel_traits,
                                             add_or_load_plants)


TEST_DATA_DIR = join(dirname(vavilov.__file__), 'test', 'data')


def create_test_users():
    public_group = Group.objects.get_or_create(name=PUBLIC_GROUP_NAME)[0]
    admin = User.objects.create_superuser(username='admin', email='p@p.es',
                                          password='pass')
    public_group.user_set.add(admin)

    user = User.objects.create_user(username='user', email='user@p.es',
                                    password='pass')
    public_group.user_set.add(user)
    user2 = User.objects.create_user(username='user2', email='user@p.es',
                                     password='pass')
    public_group.user_set.add(user2)


def load_test_data():
    load_initial_data()
    create_test_users()
    cmd = ["manage.py", "add_{}".format('person'),
           join(INITIAL_DATA_DIR, 'vavilov_person.csv')]
    execute_from_command_line(cmd)

    add_accessions(open(join(TEST_DATA_DIR, 'accessions.csv')))
    add_or_load_assays(join(TEST_DATA_DIR, 'assays.csv'))
    add_or_load_excel_traits(join(TEST_DATA_DIR, 'traits.xlsx'),
                             assays=['NSF1', 'NSF2'])
    add_or_load_plants(join(TEST_DATA_DIR, 'plants.csv'), assay='NSF1')
#     add_or_load_plants(join(TEST_DATA_DIR, 'plants.csv'), assay='NSF3')

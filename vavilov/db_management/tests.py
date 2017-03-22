from os.path import join, dirname

from django.contrib.auth.models import Group, User

import vavilov
from vavilov.conf.settings import PUBLIC_GROUP_NAME
from vavilov.db_management.base import (load_initial_data, INITIAL_DATA_DIR,
                                        add_accessions, add_or_load_persons)
from vavilov.db_management.phenotype import (add_or_load_assays,
                                             add_or_load_excel_traits,
                                             add_or_load_plants,
                                             add_or_load_excel_observations)
from vavilov.db_management.images import add_or_load_images


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
    nsf1 = Group.objects.get_or_create(name='NSF1')[0]
    nsf1.user_set.add(user)


def load_test_data():
    load_initial_data()
    create_test_users()
    add_or_load_persons(open(join(INITIAL_DATA_DIR, 'vavilov_person.csv')))
    add_accessions(open(join(TEST_DATA_DIR, 'accessions.csv')))
    add_or_load_assays(join(TEST_DATA_DIR, 'assays.csv'))
    add_or_load_excel_traits(join(TEST_DATA_DIR, 'traits.xlsx'),
                             assays=['NSF1', 'NSF2'])
    add_or_load_plants(join(TEST_DATA_DIR, 'plants.csv'), assay='NSF1')
    add_or_load_plants(join(TEST_DATA_DIR, 'plants.csv'), assay='NSF3')
    add_or_load_excel_observations(join(TEST_DATA_DIR, 'observations1.xlsx'))
    add_or_load_excel_observations(join(TEST_DATA_DIR, 'observations2.xlsx'))
    add_or_load_excel_observations(join(TEST_DATA_DIR, 'observations3.xlsx'))
    pheno_photo_dir = join(TEST_DATA_DIR, 'media', 'pheno_photos')
    add_or_load_images(pheno_photo_dir, view_perm_group='NSF1',
                       create_plant=True, use_image_id_as_plant_id=True)

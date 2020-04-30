import os
from typing import Tuple, Callable
import json

import tensorflow as tf
from scipy.io import loadmat

import settings

from .data_bases import Database
from .parse_mixins import JPGParseMixin


class CUBDatabase(JPGParseMixin, Database):
    def __init__(self, input_shape=(84, 84, 3)):
        super(CUBDatabase, self).__init__(
            raw_database_address=settings.CUB_RAW_DATASEST_ADDRESS,
            database_address='',
            random_seed=-1,
            input_shape=input_shape
        )

    def fix_2d_instances(self, train_folders, val_folders, test_folders):
        cub_info_file = os.path.join(settings.PROJECT_ROOT_ADDRESS, 'data/fixed_cubs_bad_examples.txt')
        if not os.path.exists(cub_info_file):
            instances = []
            for item in train_folders:
                instances.extend([os.path.join(item, file_name) for file_name in os.listdir(item)])
            for item in val_folders:
                instances.extend([os.path.join(item, file_name) for file_name in os.listdir(item)])
            for item in test_folders:
                instances.extend([os.path.join(item, file_name) for file_name in os.listdir(item)])

            counter = 0
            fixed_instances = list()
            for instance in instances:
                image = tf.image.decode_jpeg(tf.io.read_file(instance))

                if image.shape[2] != 3:
                    print(f'Overwriting 2d instance with 3d data: {instance}')
                    fixed_instances.append(instance)
                    image = tf.squeeze(image, axis=2)
                    image = tf.stack((image, image, image), axis=2)
                    image_data = tf.image.encode_jpeg(image)
                    tf.io.write_file(instance, image_data)
                    counter += 1

            with open(cub_info_file, 'w') as f:
                f.write(f'Changed {counter} 2d data points to 3d.\n')
                f.write('\n'.join(fixed_instances))

    def get_train_val_test_folders(self) -> Tuple:
        """Returns train, val and test folders as three lists or three dictionaries.
        Note that the python random seed might have been
        set here based on the class __init__ function."""
        images_folder = os.path.join(self.raw_database_address, 'CUB_200_2011', 'images')
        splits = json.load(open(os.path.join(
            settings.PROJECT_ROOT_ADDRESS,
            'databases',
            'meta_dataset_meta',
            'splits',
            'cub_splits.json'
            )
        ))

        train_folders = [os.path.join(images_folder, item) for item in splits['train']]
        val_folders = [os.path.join(images_folder, item) for item in splits['valid']]
        test_folders = [os.path.join(images_folder, item) for item in splits['test']]

        self.fix_2d_instances(train_folders, val_folders, test_folders)

        return train_folders, val_folders, test_folders


class AirplaneDatabase(JPGParseMixin, Database):
    def __init__(self, input_shape=(84, 84, 3)):
        super(AirplaneDatabase, self).__init__(
            raw_database_address=settings.AIRCRAFT_RAW_DATASET_ADDRESS,
            database_address='',
            random_seed=-1,
            input_shape=input_shape
        )

    def get_train_val_test_folders(self) -> Tuple:
        """Returns train, val and test folders as three lists or three dictionaries.
        Note that the python random seed might have been
        set here based on the class __init__ function."""
        images_folder = os.path.join(self.raw_database_address, 'data', 'images')
        classes = dict()
        for partition in ('train', 'val', 'test'):
            with open(os.path.join(self.raw_database_address, 'data', f'images_variant_{partition}.txt')) as f:
                for line in f:
                    img, variant = line[:7], line[8:-1]
                    if variant not in classes:
                        classes[variant] = list()
                    classes[variant].append(os.path.join(images_folder, f'{img}.jpg'))

        splits = json.load(open(os.path.join(
            settings.PROJECT_ROOT_ADDRESS,
            'databases',
            'meta_dataset_meta',
            'splits',
            'airplane.json'
            )
        ))
        train_folders = {}
        val_folders = {}
        test_folders = {}

        for item in splits['train']:
            train_folders[item] = classes[item]
        for item in splits['valid']:
            val_folders[item] = classes[item]
        for item in splits['test']:
            test_folders[item] = classes[item]

        return train_folders, val_folders, test_folders


class DTDDatabase(JPGParseMixin, Database):
    def __init__(self, input_shape=(84, 84, 3)):
        super(DTDDatabase, self).__init__(
            raw_database_address=settings.DTD_RAW_DATASET_ADDRESS,
            database_address='',
            random_seed=-1,
            input_shape=input_shape
        )

    def get_train_val_test_folders(self) -> Tuple:
        """Returns train, val and test folders as three lists or three dictionaries.
        Note that the python random seed might have been
        set here based on the class __init__ function."""
        weird_dir_file = os.path.join(self.raw_database_address, 'dtd', 'images', 'waffled', '.directory')
        if os.path.exists(weird_dir_file):
            os.remove(weird_dir_file)

        splits = json.load(open(os.path.join(
            settings.PROJECT_ROOT_ADDRESS,
            'databases',
            'meta_dataset_meta',
            'splits',
            'dtd.json'
            )
        ))
        images_folder = os.path.join(self.raw_database_address, 'dtd', 'images')
        train_folders = [os.path.join(images_folder, item) for item in splits['train']]
        val_folders = [os.path.join(images_folder, item) for item in splits['valid']]
        test_folders = [os.path.join(images_folder, item) for item in splits['test']]

        return train_folders, val_folders, test_folders


class VGGFlowerDatabase(JPGParseMixin, Database):
    def __init__(self, input_shape=(84, 84, 3)):
        super(VGGFlowerDatabase, self).__init__(
            raw_database_address=settings.VGG_FLOWER_RAW_DATASET_ADDRESS,
            database_address='',
            random_seed=-1,
            input_shape=input_shape
        )

    def get_train_val_test_folders(self) -> Tuple:
        """Returns train, val and test folders as three lists or three dictionaries.
        Note that the python random seed might have been
        set here based on the class __init__ function."""
        splits = json.load(open(os.path.join(
            settings.PROJECT_ROOT_ADDRESS,
            'databases',
            'meta_dataset_meta',
            'splits',
            'vgg_flowers.json'
            ))
        )
        images_folder = os.path.join(self.raw_database_address, 'jpg')
        instances = [os.path.join(images_folder, folder_name) for folder_name in os.listdir(images_folder)]
        instances.sort()

        image_labels = loadmat(os.path.join(
            settings.PROJECT_ROOT_ADDRESS, 'databases', 'meta_dataset_meta', 'vggflowers', 'imagelabels.mat'
        ))['labels']
        image_labels = list(image_labels.reshape((-1, )))

        classes = dict()
        for instance, image_label in zip(instances, image_labels):
            if image_label not in classes:
                classes[image_label] = list()
            classes[image_label].append(instance)

        train_folders = {}
        val_folders = {}
        test_folders = {}

        for item in splits['train']:
            item = int(item[:3])
            train_folders[item] = classes[item]
        for item in splits['valid']:
            item = int(item[:3])
            val_folders[item] = classes[item]
        for item in splits['test']:
            item = int(item[:3])
            test_folders[item] = classes[item]

        return train_folders, val_folders, test_folders

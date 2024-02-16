from datetime import datetime
import os
import os.path as osp
from typing import Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from json import load, dump
from string import ascii_letters, digits


ROOT = osp.dirname(__file__)
PROJECTS_DIR = Path(osp.join(ROOT, '.projects'))
try: os.mkdir(PROJECTS_DIR)
except FileExistsError: pass
DATE_FMT = '%m-%d-%Y %H:%M:%S.%f'
VALID_CHARS = frozenset(''.join((ascii_letters, digits, ' -_')))


def datetime_from_str(date: str) -> datetime:
    return datetime.strptime(date, DATE_FMT)

def str_from_datetime(date: datetime) -> str:
    return date.strftime(DATE_FMT)

def dump_default(obj: object) -> str:
    if isinstance(obj, Path):
        return str(obj.resolve())
    elif isinstance(obj, datetime):
        return str_from_datetime(obj)
    else:
        raise TypeError(
            'Object of type %s is not JSON serializable' %type(obj).__name__)


@dataclass
class Card:

    name: str
    fimg: str
    ftxt: str
    bimg: str
    btxt: str
    creation: datetime = field(default_factory=datetime.now)
    num_revisions: int = 0
    last_revisition: datetime = None
    learned: bool = False

    @staticmethod
    def parse_card_dict(card_dict: dict[str, object]) -> dict[str, object]:
        card_dict['creation'] = datetime_from_str(card_dict['creation'])
        if card_dict['last_revisition'] is not None:
            card_dict['last_revisition'] = datetime_from_str(
                card_dict['last_revisition'])

    @classmethod
    def from_dict(cls, card_dict: dict[str, object]) -> 'Card':
        cls.parse_card_dict(card_dict)
        return Card(**card_dict)



@dataclass
class Project:

    name: str
    creation: datetime = field(default_factory=datetime.now)
    cards: dict[str, Card] = field(default_factory=dict)
    save_dir: str = None
    imgs_dir: str = None

    def __post_init__(self):
        if not self.save_dir:
            self.save_dir = PROJECTS_DIR / self.name.replace(' ', '-')
            self.imgs_dir = self.save_dir / 'imgs'
        elif not self.imgs_dir:
            self.save_dir = Path(self.save_dir)
            self.imgs_dir = self.save_dir / 'imgs'
        else:
            self.save_dir = Path(self.save_dir)
            self.imgs_dir = Path(self.imgs_dir)
        self.imgs_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def parse_project_dict(
            project_dict: dict[str, object]) -> dict[str, object]:
        project_dict['creation'] = datetime_from_str(project_dict['creation'])
        project_dict['cards'] = {
            name: Card.from_dict(card)
            for name, card in project_dict['cards'].items()}

    @classmethod
    def from_dict(cls, project_dict: dict[str, object]) -> 'Project':
        cls.parse_project_dict(project_dict)
        return Project(**project_dict)
    
    @classmethod
    def from_file(cls, project_json: Union[str, Path]) -> 'Project':
        with open(str(project_json), mode='br') as json_file:
            return cls.from_dict(load(json_file))
    
    def save(self):
        with open(self.save_dir / 'project.json', mode='w') as proj_file:
            dump(asdict(self), proj_file, default=dump_default, indent=4)

def valid_project_name(name: str):
    return not (frozenset(name) - VALID_CHARS)

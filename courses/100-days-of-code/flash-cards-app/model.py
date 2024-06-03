import os
import os.path as osp
import shutil
from datetime import datetime
from typing import Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from json import load, dump
from string import ascii_letters, digits
from PIL import Image



ROOT = osp.dirname(__file__)
PROJECTS_DIR = Path(osp.join(ROOT, '.projects'))
DATE_FMT = '%m-%d-%Y %H:%M:%S.%f'
VALID_CHARS = frozenset(''.join((ascii_letters, digits, ' -_')))
TODAY = datetime.now().date()
IMG_FMTS = ('.png', '.jpg', '.gif', '.jpeg', '.tiff')
IMG_LIMITS = (450, 300)

try: os.mkdir(PROJECTS_DIR)
except FileExistsError: pass



def datetime_from_str(date: str) -> datetime:
    return datetime.strptime(date, DATE_FMT)

def str_from_datetime(date: datetime) -> str:
    return date.strftime(DATE_FMT)

@dataclass
class Card:

    name: str
    fimg: str
    ftxt: str
    bimg: str
    btxt: str
    creation: datetime = field(default_factory=datetime.now)
    num_revisions: int = 0
    last_revision: datetime = None
    learned: bool = False

    @staticmethod
    def parse_card_dict(card_dict: dict[str, object]) -> dict[str, object]:
        card_dict['creation'] = datetime_from_str(card_dict['creation'])
        if card_dict['last_revision'] is not None:
            card_dict['last_revision'] = datetime_from_str(
                card_dict['last_revision'])

    @classmethod
    def from_dict(cls, card_dict: dict[str, object]) -> 'Card':
        cls.parse_card_dict(card_dict)
        return Card(**card_dict)

    def reviewed_today(self) -> bool:
        return (self.last_revision is not None
                and self.last_revision.date() == TODAY)

    def register_review(self, learned: bool):
        self.num_revisions += 1
        self.last_revision = datetime.now()
        self.learned = learned

    def score(self) -> int:
        score = 0 if self.learned else 100  # Starting score
        # Number of revisions penalty
        if self.num_revisions:
            score = score * 0.98 ** self.num_revisions
            days_since_revision = max(
                0, (TODAY - self.last_revision.date()).days)
        else:
            days_since_revision = max(0, (TODAY - self.creation.date()).days)
        # Polygonal function complement:
        # from 0 to 14 days (2 weeks), each day increments the score by 2
        # past 14 days, each day increments the score by 0.5
        if days_since_revision > 14:
            score += 100 + (days_since_revision - 14) * 2
        else:
            score += (100 / 14) * days_since_revision
        return round(score)



def dump_default(obj: object) -> str:
    if isinstance(obj, Path):
        return str(obj.resolve())
    elif isinstance(obj, datetime):
        return str_from_datetime(obj)
    else:
        raise TypeError(
            'Object of type %s is not JSON serializable' %type(obj).__name__)

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
    def check_name(project_name: str) -> str:
        if (frozenset(project_name) - VALID_CHARS):
            return ""
        return ' '.join(project_name.lower().split())

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

    def delete(self):
        destination = self.save_dir.parent / 'trash' / self.save_dir.name
        if osp.isdir(destination):  # Project with the same name already deleted
            shutil.rmtree(destination)
        shutil.move(self.save_dir, destination, copy_function=shutil.copyfile)

    def _cards_info(self):
        today_revisions = 0
        today_learnings = 0
        total_learnings = 0
        for card in self.cards.values():
            total_learnings += card.learned
            if card.last_revision and card.last_revision.date() == TODAY:
                today_revisions += 1
                today_learnings += card.learned
        return (today_revisions, today_learnings, total_learnings)

    def last_studied(self):
        last_studied = self.creation
        for card in self.cards.values():
            if (card.last_revision and last_studied < card.last_revision):
                last_studied = card.last_revision
        return last_studied

    def progress(self):
        today_revisions, today_learnings, total_learnings = self._cards_info()
        last_studied = self.last_studied()
        progress = (
            100 * total_learnings / len(self.cards) if self.cards else 0.0)
        return {'last_studied': last_studied,
                'today_revisions': today_revisions,
                'today_learnings': today_learnings,
                'total_learnings': total_learnings,
                'progress': progress}



def get_project_files() -> list[str]:
    projects_files = []
    for item in os.listdir(PROJECTS_DIR):
        project = osp.join(PROJECTS_DIR, item, 'project.json')
        if osp.isfile(project):
            projects_files.append(project)
    return projects_files

def load_projects() -> dict[str, Project]:
    projects = [Project.from_file(f) for f in get_project_files()]
    return {p.name: p for p in projects}

def clear_whitespaces(string: str):
    return ' '.join(string.split())

def insert_card(card: Card, cards: list[Card]) -> int:
    score = card.score()
    for i, c in enumerate(cards):
        if c.score() < score:
            cards.insert(i, card)
            return i
    cards.append(card)
    return len(cards) - 1

def check_image(img_path: str) -> bool:
    return osp.isfile(img_path) and osp.splitext(img_path)[1] in IMG_FMTS

def process_image(img_path: str, destination: str) -> Union[None, str]:
    if osp.isdir(destination):
        destination = osp.join(destination, osp.basename(img_path))
    if osp.isfile(destination):
        return destination  # Assume that the image has been processed before
    if not osp.isdir(osp.dirname(destination)):
        return None  # All folders must already exist
    if not destination.endswith(osp.splitext(img_path)[1]):
        destination = "%s%s" %(
            osp.splitext(destination)[0], osp.splitext(img_path)[1])
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            if w <= IMG_LIMITS[0] and h <= IMG_LIMITS[1]:
                shutil.copyfile(img_path, destination)
                return destination
            if (w / IMG_LIMITS[0]) > (h / IMG_LIMITS[1]):
                nw = IMG_LIMITS[0]
                nh = round(nw * h / w)
            else:
                nh = IMG_LIMITS[1]
                nw = round(nh * w / h)
            resized = img.resize((nw, nh))
            resized.save(destination)
            return destination
    except FileNotFoundError:
        return None

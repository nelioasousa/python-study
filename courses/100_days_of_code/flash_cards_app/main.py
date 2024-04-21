import model
from views.app import *
import random


PROJECTS = model.load_projects()
CARDS = None
POPUP = None
APP = App()


### Main window
def save_and_close():
    for project in PROJECTS.values():
        project.save()
    APP.root.destroy()

APP.bind(VEV_CLOSE_APP, save_and_close)


### Projects
APP.projects.set_post_command(lambda : tuple(PROJECTS.keys()))

def delete_project(name):
    global CARDS
    PROJECTS[name].save()  # In case user wants to restore from trash
    PROJECTS[name].delete()
    del PROJECTS[name]
    CARDS = None
    APP.projects.set_working_project()

def create_project(name):
    name = model.Project.check_name(name)
    if name and name not in PROJECTS:
        PROJECTS[name] = model.Project(name)
        APP.projects.set_working_project(name)

def none_project():
    APP.progress.reset()
    APP.mode.set_default()
    APP.cards.remove_all_cards()
    APP.cards.set_working_card()

def set_project(name):
    global CARDS
    project = PROJECTS[name]
    sorted_cards = sorted(
        project.cards.values(), key=(lambda c: c.score()), reverse=True)
    APP.cards.remove_all_cards()
    APP.cards.extend_cards(
        [c.name for c in sorted_cards], [c.score() for c in sorted_cards])
    CARDS = sorted_cards
    update_progress(project)
    next_card()

def update_progress(project=None):
    progress = (
        get_project().progress() if project is None else project.progress())
    APP.progress.set_progress(progress['progress'])
    APP.progress.set_last_studied(
        model.str_from_datetime(progress['last_studied']))
    APP.progress.set_today_revisions(progress['today_revisions'])
    APP.progress.set_today_learnings(progress['today_learnings'])

APP.bind(VEV_PROJ_CREATE, create_project, ("%d",))
APP.bind(VEV_PROJ_DELETE, delete_project, ("%d",))
APP.bind(VEV_PROJ_SET, set_project, ("%d",))
APP.bind(VEV_PROJ_NONE, none_project)


### Cards
def get_project():
    return PROJECTS[APP.projects.get_working_project()]

def set_card(name):
    card = get_project().cards[name]
    APP.viewer.disable_buttons()
    APP.viewer.card.set_content(
        name, card.fimg, card.ftxt, card.bimg, card.btxt)
    APP.viewer.card.enable_buttons('flip')

def delete_card(name):
    del get_project().cards[name]
    for i, c in enumerate(CARDS):
        if c.name == name:
            CARDS.pop(i)
            break
    APP.cards.remove_card(name)
    APP.cards.set_working_card()

def none_card():
    APP.viewer.disable_buttons()
    APP.viewer.card.disable_buttons()
    APP.viewer.card.set_as_empty()

def create_card():
    global POPUP
    if POPUP is None:
        POPUP = CardPopup.card_creation_popup(APP.root)

def edit_card(name):
    global POPUP
    if POPUP is None:
        card = get_project().cards[name]
        POPUP = CardPopup.card_edition_popup(
            APP.root, card.name, card.learned,
            card.fimg, card.ftxt, card.bimg, card.btxt)

def card_popup_conclude():
    if POPUP.action == 'creation':
        create_card_conclude()
    else:
        edit_card_conclude()
    update_progress()

def card_popup_cancel():
    global POPUP
    POPUP.close()
    POPUP = None

def create_card_conclude():
    global POPUP
    project = get_project()
    name, learned, fimg, ftxt, bimg, btxt = POPUP.get_content()
    # Valid content
    name = model.clear_whitespaces(name)
    if not name:
        return POPUP.warning("Invalid card name.")
    if name in project.cards:
        return POPUP.warning("A card with the same name already exists.")
    if fimg and not model.check_image(fimg):
        return POPUP.warning("Nonexistent or unsupported file for front image.")
    if bimg and not model.check_image(bimg):
        return POPUP.warning("Nonexistent or unsupported file for back image.")
    # Process images
    if fimg: fimg = model.process_image(fimg, project.imgs_dir)
    if bimg: bimg = model.process_image(bimg, project.imgs_dir)
    # Create card
    card = model.Card(
        name, fimg, model.clear_whitespaces(ftxt),
        bimg, model.clear_whitespaces(btxt), learned=learned)
    project.cards[name] = card
    idx = model.insert_card(card, CARDS)
    APP.cards.insert_card(card.name, card.score(), idx)
    POPUP.close()
    POPUP = None

def edit_card_conclude():
    global POPUP
    original_name = POPUP.card_original_name
    project = get_project()
    card = project.cards[original_name]
    name, learned, fimg, ftxt, bimg, btxt = POPUP.get_content()
    # Valid content
    name = model.clear_whitespaces(name)
    if not name:
        return POPUP.warning("Invalid card name.")
    if name != original_name and name in project.cards:
        return POPUP.warning("A card with the same name already exists.")
    if fimg and not model.check_image(fimg):
        return POPUP.warning("Nonexistent or unsupported file for front image.")
    if bimg and not model.check_image(bimg):
        return POPUP.warning("Nonexistent or unsupported file for back image.")
    # Process images
    if fimg: fimg = model.process_image(fimg, project.imgs_dir)
    if bimg: bimg = model.process_image(bimg, project.imgs_dir)
    # Edit card
    card.name = name
    card.learned = learned
    card.fimg = fimg
    card.ftxt = model.clear_whitespaces(ftxt)
    card.bimg = bimg
    card.btxt = model.clear_whitespaces(btxt)
    POPUP.close()
    POPUP = None

def know_card(name):
    card = get_project().cards[name]
    card.register_review(True)
    update_progress()
    next_card()

def dknow_card(name):
    card = get_project().cards[name]
    card.register_review(False)
    update_progress()
    next_card()

def flip_handler():
    APP.viewer.enable_buttons()
    APP.viewer.card.enable_buttons()

def filter_cards():
    return None

def update_filter_values():
    return None

def next_card(actual_card=""):
    nxt = None
    if APP.mode.get_mode() == 'revision':
        for c in CARDS:
            if c.learned:
                continue
            if c.name != actual_card and c.last_revision is None:
                nxt = c
                break
            if c.name != actual_card and c.last_revision.date() < model.TODAY:
                nxt = c
                break
        else:
            return APP.cards.set_working_card()
    else:
        try:
            while True:
                nxt = random.choice(CARDS)
                if nxt.name != actual_card:
                    break
        except IndexError:
            return APP.cards.set_working_card()
    return APP.cards.set_working_card(nxt.name)

APP.bind(VEV_CARD_SET, set_card, ("%d",))
APP.bind(VEV_CARD_DELETE, delete_card, ("%d",))
APP.bind(VEV_CARD_NONE, none_card)
APP.bind(VEV_CARD_CREATE, create_card)
APP.bind(VEV_CARD_EDIT, edit_card)
APP.bind(VEV_CARD_FLIPPED, flip_handler)
APP.bind(VEV_CARDS_FILTERING, filter_cards)
APP.bind(VEV_FILTER_CATEG_SET, update_filter_values)
APP.bind(VEV_CARD_POPUP_CONCLUDE, card_popup_conclude)
APP.bind(VEV_CARD_POPUP_CANCEL, card_popup_cancel)
APP.bind(VEV_KNOW_CARD, know_card, ("%d", ))
APP.bind(VEV_DKNOW_CARD, dknow_card, ("%d", ))


# Run app
APP.run()

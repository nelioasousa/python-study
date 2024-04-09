import model
from views.app import *
import os.path as osp

app = App()

PROJECTS = model.load_projects()
CARDS = None
POPUP = None

# Projects section functionality
app.projects.set_post_command(lambda : tuple(PROJECTS.keys()))

def delete_project(name):
    global CARDS
    if name in PROJECTS:
        PROJECTS[name].delete()
        del PROJECTS[name]
        CARDS = None
        app.projects.set_working_project()

def create_project(name):
    name = ' '.join(name.split())
    if model.is_valid_name(name) and name not in PROJECTS:
        PROJECTS[name] = model.Project(name)
        app.projects.set_working_project(name)

def none_project():
    app.progress.reset()
    app.mode.set_default()
    app.cards.remove_all_cards()
    app.cards.set_working_card()

def set_project(name):
    global CARDS
    if name in PROJECTS:
        project = PROJECTS[name]
        scored_cards = model.score_cards(list(project.cards.values()))
        app.cards.remove_all_cards()
        app.cards.extend_cards(
            [c[0].name for c in scored_cards],
            [c[0].name for c in scored_cards],
            [c[1] for c in scored_cards])
        CARDS = scored_cards
    else:
        CARDS = None
        app.projects.set_working_project()

def save_and_close():
    for project in PROJECTS.values():
        project.save()
    app.root.destroy()

app.bind(VEV_PROJ_CREATE, create_project, ("%d",))
app.bind(VEV_PROJ_DELETE, delete_project, ("%d",))
app.bind(VEV_PROJ_SET, set_project, ("%d",))
app.bind(VEV_PROJ_NONE, none_project)
app.bind(VEV_CLOSE_APP, save_and_close)

# Cards section functionality
def set_card(cid):
    global CARDS
    if CARDS:
        card = None
        for c, _ in CARDS:
            if c.name == cid:
                card = c
                break
        else:
            return none_card()
        app.viewer.disable_buttons()
        app.viewer.card.set_content(
            cid, card.fimg, card.ftxt, card.bimg, card.btxt)
        app.viewer.card.enable_buttons('flip')
    else:
        return none_card()

def none_card():
    app.viewer.disable_buttons()
    app.viewer.card.set_as_empty()

def flip_handler():
    app.viewer.enable_buttons()
    app.viewer.card.enable_buttons()

def create_card_start():
    global POPUP
    if POPUP is None and app.projects.get_working_project() is not None:
        POPUP = CardPopup.card_creation_popup(app.root)

def create_card_conclude():
    global POPUP, CARDS
    if POPUP is not None:
        project = PROJECTS[app.projects.get_working_project()]
        content = POPUP.get_content()
        name = ' '.join(content[0].split())
        if name in project.cards:
            return POPUP.warning("A card with the same name already exists.")
        if content[2] and not osp.isfile(content[2]):
            return POPUP.warning("Image path for front image does not exist.")
        if content[4] and not osp.isfile(content[4]):
            return POPUP.warning("Image path for back image does not exist.")
        card = model.Card(
            name, content[2], content[3],
            content[4], content[5], learned=content[1])
        project.cards[name] = card
        idx = model.insert_card(card, CARDS)
        print(CARDS[idx])
        app.cards.insert_card(card.name, card.name, CARDS[idx][1], idx)
        POPUP.close()
        POPUP = None

def create_card_cancel():
    global POPUP
    if POPUP is not None:
        POPUP.close()
        POPUP = None

def delete_card(cid):
    project = PROJECTS[app.projects.get_working_project()]
    if cid in project.cards:
        del project.cards[cid]
        for i, (c, _) in enumerate(CARDS):
            if c.name == cid: CARDS.pop(i)
        app.cards.remove_card(cid)
        none_card()

def filter_cards():
    return None

def update_filter_values():
    return None

app.bind(VEV_CARD_SET, set_card, ("%d",))
app.bind(VEV_CARD_DELETE, delete_card, ("%d",))
app.bind(VEV_CARD_NONE, none_card)
app.bind(VEV_CARD_FLIPPED, flip_handler)
app.bind(VEV_CARD_CREATE, create_card_start)
app.bind(VEV_CARD_POPUP_CONCLUDE, create_card_conclude)
app.bind(VEV_CARD_POPUP_CANCEL, create_card_cancel)
app.bind(VEV_CARDS_FILTERING, filter_cards)
app.bind(VEV_FILTER_CATEG_SET, update_filter_values)


app.run()

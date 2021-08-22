# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet

import sys
import pathlib
import os
import json

IconProperty = "CoverImage"

def get_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"


def load_file(path):
    with open(path, encoding="utf8") as f:
        return json.load(f)


library = os.path.join(get_datadir(), "Playnite", "library")


class Playnite(kp.Plugin):

    CATEGORY = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()

    def on_catalog(self):
        gameFiles = os.listdir(os.path.join(library, "games"))
        games = [
            load_file(os.path.join(library, "games", gameFile))
            for gameFile in gameFiles
        ]
        self.set_catalog([
            self.create_item(
                category=self.CATEGORY,
                label=game["Name"],
                target=game["Id"],
                data_bag=game["Id"],
                short_desc="Launch game",
                icon_handle=self.resolve_icon(game),
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.KEEPALL)
            for game in games])

    def resolve_icon(self, game):
        try:
            self.validate_icon_exists(game)
            icon_source = "cache://{}/{}".format(self.package_full_name(), game["Id"])
            return self.load_icon(icon_source)
        except Exception as e:
            print(e)
            return
            
    def validate_icon_exists(self, game):
        cache_path = self.get_package_cache_path(create=True)
        cache_icon = os.path.join(cache_path, game["Id"])
        if os.path.exists(cache_icon):
            return 
        playnite_icon = os.path.join(library, "files", game[IconProperty])
        if os.path.exists(playnite_icon):
            with open(playnite_icon, 'rb') as f1, open(cache_icon, 'wb') as f2:
                f2.write(f1.read())

    def on_suggest(self, user_input, items_chain):
        if items_chain:
            clone = items_chain[-1].clone()
            clone.set_args(user_input)
            self.set_suggestions([clone])

    def on_execute(self, item, action):
        kpu.shell_execute("playnite://playnite/start/{}".format(item.target()))
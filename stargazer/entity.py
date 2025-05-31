import typing
from glob import glob
from ruamel.yaml import YAML
from .meta import PrototypeMeta

import logging

log = logging.getLogger(__name__)


class EntityPrototypeUnresolvedException(BaseException):
    pass


class EntityPrototype:
    id: str = ""
    abstract: bool = False
    parents: list[str]
    type: str = "entity"
    name: str = ""
    description: str = ""
    categories: list[str]
    components: dict[str, dict]
    meta: PrototypeMeta

    _resolved = False

    def __init__(self, d: dict):
        self.parents = []
        self.categories = []
        self.components = {}
        self.meta = PrototypeMeta()

        for key, value in d.items():
            if key == "parent":
                key = "parents"

                # ensure list of strings when only one parent is present
                if type(value) is str:
                    value = [value]

            if key == "components":
                for component in value:
                    component_type = component["type"]
                    self.components[component_type] = component
                continue

            setattr(self, key, value)

    # resolve inheritance tree and copy over undefined attributes
    def resolve(self, resolver: dict[str, typing.Any]) -> None:
        if self._resolved:
            return

        parent_lookup_queue = list(self.parents)
        for parent in parent_lookup_queue:
            if parent not in resolver:
                log.warning(f"Unable to find parent {parent} for entity {self.id}")
                continue

            # log.debug(f'Searching parent: {parent}')
            parent_proto = resolver[parent]

            # copy over unset properties from this parent
            if self.name == "" and parent_proto.name is not None:
                self.name = parent_proto.name
            if self.description == "" and parent_proto.description is not None:
                self.description = parent_proto.description

            # copy over inherited components while generally preserving their order of declaration
            for component_type, parent_component in parent_proto.components.items():
                # copy over attributes only if they have not been set
                if component_type in self.components:
                    existing_component = self.components[component_type]

                    # copy over inherited component fields
                    for key, value in parent_component.items():
                        if key in existing_component:
                            continue
                        existing_component[key] = value
                else:
                    # this component is new to us, copy it over directly
                    self.components[parent_component["type"]] = parent_component

            # search parent prototypes recursively
            for super_parent in parent_proto.parents:
                # log.debug(f'Appending parent {super_parent} from parent {parent}')
                parent_lookup_queue.append(super_parent)

        self._resolved = True
        return

    """
    Returns a boolean if the entity prototype has the given component defined
    component_type should be the name of the component *without* the suffix `Component`.
    """

    def has_component(self, component_type: str) -> bool:
        if not self._resolved:
            raise EntityPrototypeUnresolvedException()
        return component_type in self.components

    def tags(self) -> list[str]:
        if not self._resolved:
            raise EntityPrototypeUnresolvedException()

        tags = []
        if "Tag" in self.components and "tags" in self.components["Tag"]:
            for tag in self.components["Tag"]["tags"]:
                tags.append(tag)
        return tags

    def has_tag(self, tag: str) -> bool:
        tags = self.tags()
        return tag in tags

    def sprite_path(self) -> str:
        if "Sprite" in self.components:
            sprite_component = self.components["Sprite"]

            # basic
            if "sprite" in sprite_component and "state" in sprite_component:
                return f'{sprite_component["sprite"]}/{sprite_component["state"]}.png'

            # composite (for markers, foods, battery cells, etc.)
            # if 'layers' in sprite_component:
            # # ...
        elif "InstantAction" in self.components:
            action_component = self.components["InstantAction"]
            if "icon" in action_component:
                icon = action_component["icon"]
                if type(icon) == str:
                    return icon
                elif "sprite" in icon:
                    return f'{icon["sprite"]}/{icon["state"]}.png'
        return ""


class LineNumberNotFoundException(Exception):
    pass


def get_line_number_for_yaml_key_value(haystack: str, key: str, value: str) -> int:
    for line_number, straw in enumerate(haystack.split("\n")):
        # remove trailing comments and whitespace
        straw = straw.split("#")[0].strip()
        if straw.startswith(f"{key}:") and straw.endswith(f" {value}"):
            return line_number + 1
    raise LineNumberNotFoundException()


def load_entities(base_path: str) -> dict[str, EntityPrototype]:
    resources_path = f"{base_path}/Resources"

    entities: dict[str, EntityPrototype] = {}
    for fpath in glob(resources_path + "/Prototypes/**/*.yml", recursive=True):
        with open(fpath, "rb") as f:
            # decoded as utf-8-sig to cope with sporadic byte order-marks on files
            content = f.read().decode("utf-8-sig")

            objects: list[dict[str, typing.Any]] = YAML().load(content)

            # check for empty file
            if objects is None:
                continue

            for obj in objects:
                if obj["type"] != "entity":
                    continue

                proto = EntityPrototype(obj)
                proto.meta.file_path = fpath.replace(f"{base_path}/", "").replace(
                    "\\", "/"
                )
                try:
                    proto.meta.line_number = get_line_number_for_yaml_key_value(
                        content, "id", proto.id
                    )
                except LineNumberNotFoundException:
                    log.warning(
                        f"Failed to find declaration line number for entity prototype {proto.id} in "
                        f"file {proto.meta.file_path}"
                    )
                entities[proto.id] = proto

    return entities

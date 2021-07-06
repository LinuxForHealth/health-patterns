# -*- coding: utf-8 -*-
"""Python representation of FHIR® https://www.hl7.org/fhir/ specification.
Idea and class structure based on https://github.com/smart-on-fhir/fhir-parser.
"""
import datetime
import enum
import importlib
import inspect
import io
import json
import logging
import mimetypes
import os
import pathlib
import re
import types
from ast import literal_eval
from collections import defaultdict
from http.client import HTTPResponse
from typing import (
    Any,
    DefaultDict,
    Dict,
    ItemsView,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

__version__ = "0.3.0"
__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"
__all__ = ["Configuration", "FHIRSpec", "download", "filename_from_response"]


# --*-- Enums
class FHIR_RELEASES(str, enum.Enum):
    """ """

    R5 = "R5"
    R4 = "R4"
    STU3 = "STU3"


class FHIR_CLASS_TYPES(str, enum.Enum):
    """ """

    resource = "resource"
    complex_type = "complex_type"
    primitive_type = "primitive_type"
    logical = "logical"
    other = "other"


# --*-- Variables
LOGGER = logging.getLogger(__name__)
FHIR_VERSIONS_MAP = {
    "3.0.0": FHIR_RELEASES.STU3,
    "3.0.1": FHIR_RELEASES.STU3,
    "3.0.2": FHIR_RELEASES.STU3,
    "4.0.0": FHIR_RELEASES.R4,
    "4.0.1": FHIR_RELEASES.R4,
}
HTTP_URL = re.compile(r"^https?://", re.IGNORECASE)
UNSUPPORTED_PROFILES = [r"SimpleQuantity"]


# --*-- Classes
class ConfigurationVariable:
    """ """

    name: str
    required: bool
    type_: Any


class Configuration:
    """Simple Configuration Class"""

    _initialized: bool
    __storage__: DefaultDict[str, Any]
    __slots__ = ("__storage__", "_initialized")

    def __init__(self, data_dict: Dict[str, Any], path_variables: List[str] = None):
        """ """
        object.__setattr__(self, "__storage__", defaultdict())
        object.__setattr__(self, "_initialized", False)
        self.init(data_dict)
        object.__setattr__(self, "_initialized", True)
        self.validate(["BASE_PATH"])
        self.normalize_paths(path_variables)

    @classmethod
    def from_module(cls, mod: types.ModuleType) -> "Configuration":
        """ """
        data_dict = mod.__dict__.copy()
        return cls(data_dict)

    @classmethod
    def from_json_file(cls, file: pathlib.Path) -> "Configuration":
        """ """
        assert file.is_file() and file.exists()
        try:
            # json5 supported
            from json5 import load as j_load
        except ImportError:
            if file.suffix == ".json5":
                raise
            j_load = json.load

        with open(str(file), "r", encoding="utf-8") as fp:
            data_dict = j_load(fp)
            assert isinstance(data_dict, dict)

        return cls(data_dict)

    @classmethod
    def from_text_file(cls, file: pathlib.Path) -> "Configuration":
        """KEY=VALUE formatted variables
        @todo: dict type value by dotted path?
        """
        assert file.is_file() and file.exists()
        data_dict: Dict[str, Any] = dict()
        with open(str(file), "r", encoding="utf-8") as fp:
            for line in fp:
                ln = line.strip()
                if not ln or ln.startswith("#") or "=" not in ln:
                    continue
                key, val = ln.split("=", 1)
                key = key.strip()
                if not key.isupper() or not val:
                    continue
                values: List[str] = list(map(lambda x: x.strip(), val.split(",")))
                if len(values) == 1:
                    data_dict[key] = values[0]
                else:
                    data_dict[key] = values
        return cls(data_dict)

    @classmethod
    def from_cfg_file(cls, filepath: pathlib.Path) -> None:
        """ """
        assert filepath.is_file() and filepath.suffix in (".cfg", ".ini")

    @classmethod
    def from_toml_file(cls, filepath: pathlib.Path) -> "Configuration":
        """ """
        import pytoml as toml

        assert filepath.is_file() and filepath.suffix == ".toml"
        with open(str(filepath), "r", encoding="utf-8") as fp:
            data = toml.load(fp)

            return cls(data_dict=data)

    def init(self, data_dict: Dict[str, Any]) -> None:
        """ """
        init_ = object.__getattribute__(self, "_initialized")
        if init_ is True:
            raise ValueError("Instance has already be initialized!")

        def _add(items: ItemsView[str, Any]) -> None:
            """ """
            for key, val in items:
                if key.isupper() is False:
                    continue
                setattr(self, key, val)

        _add(data_dict.items())

    def normalize_paths(self, path_variables: List[str] = None) -> None:
        """ """
        init_ = object.__getattribute__(self, "_initialized")
        if init_ is False:
            raise ValueError("Instance has must be initialized!")

        storage = object.__getattribute__(self, "__storage__")
        base_path = storage["BASE_PATH"]
        if not isinstance(base_path, pathlib.PurePath):
            base_path = resolve_path(base_path, None)
            storage["BASE_PATH"] = base_path

        paths = [
            "CACHE_PATH",
            "RESOURCE_TARGET_DIRECTORY",
            "DEPENDENCIES_TARGET_FILE_NAME",
            "UNITTEST_TARGET_DIRECTORY",
            "UNITTEST_COPY_FILES",
        ]
        if path_variables is not None:
            paths.extend(path_variables)

        for np in paths:
            if np not in storage:
                continue
            val = storage[np]
            if isinstance(val, list):
                new_val = list()
                for p in val:
                    if isinstance(p, pathlib.PurePath):
                        new_val.append(p)
                    else:
                        new_val.append(resolve_path(p, base_path))
                storage[np] = new_val
            else:
                if not isinstance(val, pathlib.PurePath):
                    storage[np] = resolve_path(val, base_path)

        # take care of manual profiles
        new_profiles = list()
        for path, mod_name, values in storage["MANUAL_PROFILES"]:
            if not isinstance(path, pathlib.PurePath):
                path = resolve_path(path, base_path)
            new_profiles.append((path, mod_name, values))

        storage["MANUAL_PROFILES"] = new_profiles

    def validate(self, required_variables: List[str]) -> None:
        """XXX: variable could include with value type(s) and required flag"""
        missing: List[str] = list()
        for v in required_variables:
            if v not in self.__storage__:
                missing.append(v)
        if len(missing) > 0:
            raise ValueError(f"{missing} variable(s) are missing!")

    def as_dict(self) -> defaultdict:
        """ """
        init_ = object.__getattribute__(self, "_initialized")
        if init_ is False:
            raise ValueError("Instance has must be initialized!")

        storage = object.__getattribute__(self, "__storage__")
        return storage.copy()

    def update(self, data_dict: Dict[str, Any]) -> None:
        """ """
        init_ = object.__getattribute__(self, "_initialized")
        if init_ is False:
            raise ValueError("Instance has must be initialized!")

        storage = object.__getattribute__(self, "__storage__")
        for key, val in data_dict.items():
            if key.isupper():
                storage[key] = val

    def merge(self, other: "Configuration") -> None:
        """ """
        storage = object.__getattribute__(self, "__storage__")
        storage.update(object.__getattribute__(other, "__storage__").copy())

    def __add__(self, other: "Configuration") -> "Configuration":
        """ """
        data_dict = object.__getattribute__(self, "__storage__").copy()
        data_dict.update(object.__getattribute__(other, "__storage__").copy())
        return Configuration(data_dict)

    def __getitem__(self, item: str) -> Any:
        """ """
        try:
            return self.__storage__[item]
        except KeyError:
            raise KeyError(f"´{item}´ is not defined in any configuration.")

    def __getattr__(self, item: str) -> Any:
        """ """
        try:
            return self.__storage__[item]
        except KeyError:
            raise AttributeError(f"´{item}´ is not defined in any configuration.")

    def __setitem__(self, key: str, value: Any) -> None:
        """ """
        storage = object.__getattribute__(self, "__storage__")
        storage[key] = value

    def __setattr__(self, key: str, value: Any) -> None:
        """ """
        self[key] = value


class FHIRSpec:
    """The FHIR specification."""

    _finalized: bool

    def __init__(self, settings: Configuration, src_directory: pathlib.Path = None):
        """
        :param src_directory:
        :param settings:
        """
        self._finalized = False
        self.validate_settings(settings)
        self.definition_directory: pathlib.Path = getattr(
            settings, "FHIR_DEFINITION_DIRECTORY", None
        )
        self.example_directory: pathlib.Path = getattr(
            settings, "FHIR_EXAMPLE_DIRECTORY", None
        )
        version_info_file: pathlib.Path = getattr(
            settings, "FHIR_VERSION_INFO_FILE", None
        )
        if (
            self.definition_directory is None
            or self.example_directory is None
            or version_info_file is None
        ) and src_directory is None:
            raise ValueError("src_directory is value is required!")
        if self.definition_directory is None:
            assert src_directory
            self.definition_directory = src_directory / "definitions"
        if self.example_directory is None:
            assert src_directory
            self.example_directory = src_directory / "examples"
        if version_info_file is None:
            assert src_directory
            version_info_file = src_directory / "version.info"
        self.settings = settings
        self.info: FHIRVersionInfo = FHIRVersionInfo(self, version_info_file)
        # system-url: FHIRValueSet()
        self.valuesets: DefaultDict[str, FHIRValueSet] = defaultdict()
        # system-url: FHIRCodeSystem()
        self.codesystems: DefaultDict[str, FHIRCodeSystem] = defaultdict()
        # profile-name: FHIRStructureDefinition()
        self.profiles: DefaultDict[str, FHIRStructureDefinition] = defaultdict()
        # FHIRUnitTestCollection()
        self.unit_tests: List[FHIRUnitTestCollection] = list()

        self.prepare()
        self.read_profiles()
        self.finalize()

    @staticmethod
    def validate_settings(settings: Configuration) -> None:
        """
        :param settings:
        :return:
        """
        required_variables = [
            "WRITE_RESOURCES",
            "CLASS_MAP",
            "REPLACE_MAP",
            "NATIVES",
            "JSON_MAP",
            "JSON_MAP_DEFAULT",
            "RESERVED_MAP",
            "ENUM_MAP",
            "ENUM_NAME_MAP",
            "DEFAULT_BASES",
            "MANUAL_PROFILES",
            "CAMELCASE_CLASSES",
            "CAMELCASE_ENUMS",
            "BACKBONE_CLASS_ADDS_PARENT",
            "RESOURCE_MODULE_LOWERCASE",
            "FHIR_PRIMITIVES",
        ]
        write_resources = getattr(settings, "WRITE_RESOURCES", False)
        if write_resources is True:
            required_variables.extend(
                [
                    "TEMPLATE_DIRECTORY",
                    "RESOURCE_FILE_NAME_PATTERN",
                    "RESOURCE_TARGET_DIRECTORY",
                    "RESOURCE_SOURCE_TEMPLATE",
                    "CODE_SYSTEMS_SOURCE_TEMPLATE",
                    "CODE_SYSTEMS_TARGET_NAME",
                    "WRITE_DEPENDENCIES",
                    "DEPENDENCIES_SOURCE_TEMPLATE",
                    "DEPENDENCIES_TARGET_FILE_NAME",
                    "RESOURCE_MODULE_LOWERCASE",
                ]
            )
        write_unittests = getattr(settings, "WRITE_UNITTESTS", False)
        if write_unittests is True:
            required_variables.extend(
                [
                    "UNITTEST_COPY_FILES",
                    "UNITTEST_FORMAT_PATH_PREPARE",
                    "UNITTEST_SOURCE_TEMPLATE",
                    "UNITTEST_TARGET_DIRECTORY",
                    "UNITTEST_TARGET_FILE_NAME_PATTERN",
                    "UNITTEST_FORMAT_PATH_KEY",
                    "UNITTEST_FORMAT_PATH_INDEX",
                ]
            )

        settings.validate(required_variables)

        if (
            settings.WRITE_RESOURCES is True
            and getattr(settings, "RESOURCES_WRITER_CLASS", None) is None
        ):
            raise ValueError("Writer class is required, when resources to be written.")

    def prepare(self) -> None:
        """Run actions before starting to parse profiles."""
        self.read_valuesets()
        self.handle_manual_profiles()

    def read_bundle_resources(self, filename: str) -> List[Dict[str, Any]]:
        """Return an array of the Bundle's entry's "resource" elements."""
        LOGGER.info(f"Reading {filename}")
        filepath = self.definition_directory / filename
        with open(str(filepath), encoding="utf-8") as handle:
            parsed = json.load(handle)
            if "resourceType" not in parsed:
                raise Exception(
                    f'Expecting "resourceType" to be present, but is not in {filepath}'
                )
            if "Bundle" != parsed["resourceType"]:
                raise Exception('Can only process "Bundle" resources')
            if "entry" not in parsed:
                raise Exception(f"There are no entries in the Bundle at {filepath}")

            return [e["resource"] for e in parsed["entry"]]

    # MARK: Managing ValueSets and CodeSystems
    def read_valuesets(self) -> None:
        filename = getattr(self.settings, "FHIR_VALUESETS_FILE_NAME", "valuesets.json")
        resources = self.read_bundle_resources(filename)
        for resource in resources:
            if "ValueSet" == resource["resourceType"]:
                assert "url" in resource
                self.valuesets[resource["url"]] = FHIRValueSet(self, resource)
            elif "CodeSystem" == resource["resourceType"]:
                assert "url" in resource
                if "content" in resource and "concept" in resource:
                    self.codesystems[resource["url"]] = FHIRCodeSystem(self, resource)
                else:
                    LOGGER.warning(f"CodeSystem with no concepts: {resource['url']}")
        LOGGER.info(
            f"Found {len(self.valuesets)} ValueSets and "
            f"{len(self.codesystems)} CodeSystems"
        )

    def valueset_with_uri(self, uri: str) -> "FHIRValueSet":
        """
        :param uri:
        :return: FHIRValueSetType
        """
        try:
            return self.valuesets[uri]
        except KeyError:
            raise NotImplementedError

    def codesystem_with_uri(self, uri: str) -> "FHIRCodeSystem":
        """
        :param uri:
        :return: FHIRCodeSystem
        """
        try:
            return self.codesystems[uri]
        except KeyError:
            raise NotImplementedError

    # MARK: Handling Profiles
    def read_profiles(self) -> None:
        """Find all (JSON) profiles and instantiate into FHIRStructureDefinition."""
        resources = []
        files = getattr(
            self.settings,
            "FHIR_PROFILES_FILE_NAMES",
            ["profiles-types.json", "profiles-resources.json"],
        )
        for filename in files:
            bundle_res = self.read_bundle_resources(filename)
            for resource in bundle_res:
                if "StructureDefinition" == resource["resourceType"]:
                    resources.append(resource)
                else:
                    LOGGER.debug(
                        f"Not handling resource of type {resource['resourceType']}"
                    )

        # create profile instances
        for resource in resources:
            profile: FHIRStructureDefinition = FHIRStructureDefinition(self, resource)
            for pattern in UNSUPPORTED_PROFILES:
                assert isinstance(profile.url, str)
                if re.search(pattern, profile.url) is not None:
                    LOGGER.info(f'Skipping "{resource["url"]}"')
                    continue

            if self.found_profile(profile):
                profile.process_profile()

    def found_profile(self, profile: "FHIRStructureDefinition") -> bool:
        if not profile or not profile.name:
            raise Exception(f"No name for profile {profile}")
        if profile.name.lower() in self.profiles:
            LOGGER.debug(f'Already have profile "{profile.name}", discarding')
            return False

        self.profiles[profile.name.lower()] = profile
        return True

    def handle_manual_profiles(self) -> None:
        """Creates in-memory representations for all our manually defined
        profiles.
        """
        for filepath, module, contains in self.settings.MANUAL_PROFILES:
            for contained in contains:
                profile: FHIRStructureDefinition = FHIRStructureDefinition(self, None)
                profile.is_manual = True

                prof_dict = {
                    "name": contained,
                    "differential": {"element": [{"path": contained}]},
                }
                if module == "fhirtypes":
                    profile_name = self.class_name_for_profile(contained)
                    assert isinstance(profile_name, str)
                    if self.class_name_is_primitive(profile_name):
                        prof_dict["kind"] = "primitive-type"

                profile.structure = FHIRStructureDefinitionStructure(profile, prof_dict)

                if self.found_profile(profile):
                    profile.process_profile()

    def finalize(self) -> None:
        """Should be called after all profiles have been parsed and allows
        to perform additional actions, like looking up class implementations
        from different profiles.
        """
        if self._finalized is True:
            raise ValueError("Specification is already been finalized!")

        # self.profiles['meta'].structure.snapshot[-1]
        for key, prof in self.profiles.items():
            prof.finalize()
            if len(prof.elements_sequences) == 0:
                for item in prof.structure.snapshot[1:]:
                    prof.elements_sequences.append(item["id"].split(".")[1])

        if self.settings.WRITE_UNITTESTS:
            self.parse_unit_tests()
        self._finalized = True

    @property
    def finalized(self) -> bool:
        return self._finalized

    # MARK: Naming Utilities
    def as_module_name(self, name: str) -> str:
        if self.class_name_is_primitive(name):
            return "fhirtypes"
        return (
            name.lower() if name and self.settings.RESOURCE_MODULE_LOWERCASE else name
        )

    def as_class_name(
        self, classname: str, parent_name: str = None
    ) -> Union[str, None]:
        """
        :param classname:
        :param parent_name:
        :return: str | None
        """
        if not classname or 0 == len(classname):
            return None

        # if we have a parent, do we have a mapped class?
        pathname = (
            "{0}.{1}".format(parent_name, classname)
            if parent_name is not None
            else None
        )
        if pathname is not None and pathname in self.settings.CLASS_MAP:
            return self.settings.CLASS_MAP[pathname]

        # is our plain class mapped?
        if classname in self.settings.CLASS_MAP:
            return self.settings.CLASS_MAP[classname]

        # CamelCase or just plain
        if self.settings.CAMELCASE_CLASSES:
            return classname[:1].upper() + classname[1:]
        return classname

    def class_name_for_type(
        self, type_name: str, parent_name: str = None
    ) -> Union[str, None]:
        """
        :param type_name:
        :param parent_name:
        :return: str or None
        """
        return self.as_class_name(type_name, parent_name)

    def class_name_for_type_if_property(self, type_name: str) -> Union[str, None]:
        """
        :param type_name:
        :return: str | None
        """
        classname = self.class_name_for_type(type_name)
        if not classname:
            return None
        return self.settings.REPLACE_MAP.get(classname, classname)

    def class_name_for_profile(
        self, profile_name: Union[str, List[str]]
    ) -> Union[str, List[str], None]:
        if not profile_name:
            return None
        # TODO need to figure out what to do with this later.
        # Annotation author supports multiples types that caused this to fail
        if isinstance(profile_name, (list,)) and len(profile_name) > 0:
            classnames: List[str] = []
            for p_name in profile_name:
                cls_name = self.class_name_for_profile(p_name)
                if isinstance(cls_name, str):
                    classnames.append(cls_name)

            return classnames
        # may be the full Profile URI,
        # like http://hl7.org/fhir/Profile/MyProfile
        if isinstance(profile_name, str):
            type_name = profile_name.split("/")[-1]
        else:
            raise NotImplementedError
        return self.as_class_name(type_name)

    def class_name_is_native(self, class_name: str) -> bool:
        """
        :param class_name:
        :return: bool
        """
        return class_name in self.settings.NATIVES

    def class_name_is_primitive(self, class_name: str) -> bool:
        """
        :param class_name:
        :return: bool
        """
        for typ in self.settings.FHIR_PRIMITIVES:
            if typ.lower() == class_name.lower():
                return True
        return False

    def safe_property_name(self, prop_name: str) -> str:
        """
        :param prop_name:
        :return:
        """
        return self.settings.RESERVED_MAP.get(prop_name, prop_name)

    def safe_enum_name(self, enum_name: str, ucfirst: bool = False) -> str:
        assert enum_name, "Must have a name"
        name = self.settings.ENUM_MAP.get(enum_name, enum_name)
        parts = re.split(r"\W+", name)
        if self.settings.CAMELCASE_ENUMS:
            name = "".join([n[:1].upper() + n[1:] for n in parts])
            if not ucfirst and name.upper() != name:
                name = name[:1].lower() + name[1:]
        else:
            name = "_".join(parts)
        return self.settings.RESERVED_MAP.get(name, name)

    def json_class_for_class_name(self, class_name: str) -> str:
        """
        :param class_name:
        :return: str
        """
        return self.settings.JSON_MAP.get(class_name, self.settings.JSON_MAP_DEFAULT)

    # MARK: Unit Tests
    def parse_unit_tests(self) -> None:
        controller: FHIRUnitTestController = FHIRUnitTestController(self)
        controller.find_and_parse_tests(self.example_directory)
        self.unit_tests = controller.collections

    # MARK: Writing Data
    def writable_profiles(self) -> List["FHIRStructureDefinition"]:
        """Returns a list of `FHIRStructureDefinition` instances."""
        profiles = []
        for key, profile in self.profiles.items():
            if not profile.is_manual:
                profiles.append(profile)
        return profiles

    def write(self) -> None:
        """ """
        klass = self.settings.RESOURCES_WRITER_CLASS
        if isinstance(klass, str):
            parts = klass.split(".")
            assert len(parts) > 1
            klass_name = parts[-1]
            module_name = ".".join(parts[:-1])
            factory = getattr(importlib.import_module(module_name), klass_name)
        else:
            factory = klass
        assert inspect.isclass(factory)
        assert issubclass(factory, FHIRSpecWriter)

        writer = factory(self)
        return writer.write()


class FHIRSpecWriter:
    """ """

    def __init__(self, spec: FHIRSpec):
        """ """
        if spec.finalized is not True:
            raise ValueError(
                "Specification must be in finalized state, ready to write."
            )
        self.spec = spec
        self.settings = spec.settings

    def write(self) -> None:
        """ """
        raise NotImplementedError


class FHIRVersionInfo:
    """The version of a FHIR specification."""

    def __init__(self, spec: FHIRSpec, info_file: pathlib.Path):
        self.spec = spec

        now = datetime.date.today()
        self.date = now.isoformat()
        self.year = now.year

        self.version: Optional[str] = None
        self.version_raw: Optional[str] = None
        self.build: Optional[str] = None
        self.revision: Optional[str] = None
        self.read_version(info_file)

    def read_version(self, filepath: pathlib.Path) -> None:
        assert filepath.is_file
        with open(str(filepath), "r", encoding="utf-8") as handle:
            text = handle.read()
            for line in text.split("\n"):
                if "=" in line:
                    (n, v) = line.strip().split("=", 2)
                    if "FhirVersion" == n:
                        self.version_raw = v
                    elif "version" == n:
                        self.version = v
                    elif "buildId" == n:
                        self.build = v
                    elif "revision" == n:
                        self.revision = v


class FHIRValueSet:
    """Holds on to ValueSets bundled with the spec."""

    def __init__(self, spec: FHIRSpec, set_dict: Dict[str, Any]):
        """
        :param spec:
        :param set_dict:
        """
        self.spec = spec
        self.definition = set_dict
        self._enum: Dict[str, Union[str, None, List]] = dict()

    @property
    def enum(self) -> Union[None, Dict[str, Union[str, List[str], None]]]:
        """Returns FHIRCodeSystem if this valueset can be represented by one."""
        if len(self._enum) > 0:
            return self._enum

        compose = self.definition.get("compose")
        if compose is None:
            raise Exception("Currently only composed ValueSets are supported")
        if "exclude" in compose:
            raise Exception("Not currently supporting 'exclude' on ValueSet")
        include = compose.get("include")
        if 1 != len(include):
            LOGGER.warning(
                "Ignoring ValueSet with more than "
                f"1 includes ({len(include)}: {include})"
            )
            return None

        system = include[0].get("system")
        if system is None:
            return None

        # alright, this is a ValueSet with 1 include and
        # a system, is there a CodeSystem?
        cs: FHIRCodeSystem = self.spec.codesystem_with_uri(system)
        if cs is None or not cs.generate_enum:
            return None

        # do we only allow specific concepts?
        restricted_to = []
        concepts = include[0].get("concept")
        if concepts is not None:
            for concept in concepts:
                assert "code" in concept
                restricted_to.append(concept["code"])

        self._enum = {
            "name": cs.name,
            "restricted_to": restricted_to if len(restricted_to) > 0 else None,
        }
        return self._enum


class FHIRCodeSystem:
    """Holds on to CodeSystems bundled with the spec."""

    def __init__(self, spec: FHIRSpec, resource: Dict[str, Any]):
        """
        :param spec:
        :param resource:
        """
        assert "content" in resource
        self.spec = spec
        self.definition = resource
        self.url = resource.get("url")
        if self.url in self.spec.settings.ENUM_NAME_MAP:
            self.name = self.spec.settings.ENUM_NAME_MAP[self.url]
        else:
            self.name = self.spec.safe_enum_name(resource["name"], ucfirst=True)
        self.codes = None
        self.generate_enum = False
        concepts = self.definition.get("concept", [])

        if resource.get("experimental"):
            return
        self.generate_enum = "complete" == resource["content"]
        if not self.generate_enum:
            LOGGER.debug(
                "Will not generate enum for CodeSystem "
                f'"{self.url}" whose content is {resource["content"]}'
            )
            return

        assert concepts, 'Expecting at least one code for "complete" CodeSystem'
        if len(concepts) > 200:
            self.generate_enum = False
            LOGGER.info(
                "Will not generate enum for CodeSystem "
                f'"{self.url}" because it has > 200 ({len(concepts)}) concepts.'
            )
            return

        self.codes = self.parsed_codes(concepts)

    def parsed_codes(
        self, codes: Sequence[Dict[str, Any]], prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        :param codes:
        :param prefix:
        :return:
        """
        found: List[Dict[str, Any]] = []
        for c in codes:
            if re.match(r"\d", c["code"][:1]):
                self.generate_enum = False
                LOGGER.info(
                    f'Will not generate enum for CodeSystem "{self.url}" '
                    "because at least one concept code starts with a number"
                )
                return found

            cd = c["code"]
            name = (  # noqa: F841
                "{}-{}".format(prefix, cd)
                if prefix and not cd.startswith(prefix)
                else cd
            )
            c["name"] = self.spec.safe_enum_name(cd)
            c["definition"] = c.get("definition") or c["name"]
            found.append(c)

            # nested concepts?
            if "concept" in c:
                fnd = self.parsed_codes(c["concept"])
                if fnd is None:
                    return found
                found.extend(fnd)
        return found


class FHIRStructureDefinition:
    """One FHIR structure definition."""

    def __init__(self, spec: FHIRSpec, profile: Optional[Dict[str, Any]]):
        self.is_manual: bool = False
        # FHIRStructureDefinitionStructure()
        self.structure: FHIRStructureDefinitionStructure
        self.spec: FHIRSpec = spec
        self.url: Optional[str] = None
        self.targetname: Optional[str] = None
        # List of FHIRStructureDefinitionElement
        self.elements: List[FHIRStructureDefinitionElement] = list()
        self.main_element: Optional[FHIRStructureDefinitionElement] = None
        # xxx: if ._class_map is required
        # self._class_map: Dict[str, str] = dict()
        self.classes: List[FHIRClass] = list()
        self._did_finalize: bool = False
        self.fhir_version: Optional[str] = None
        self.fhir_last_updated: Optional[str] = None
        self.elements_sequences: List[str] = list()

        if profile is not None:
            self.parse_profile(profile)

    @property
    def name(self) -> Union[str, None]:
        return self.structure.name if self.structure is not None else None

    def read_profile(self, filepath: pathlib.Path) -> None:
        """Read the JSON definition of a profile from disk and parse.

        Not currently used.
        """
        with open(str(filepath), "r", encoding="utf-8") as handle:
            profile = json.load(handle)
        self.parse_profile(profile)

    def parse_profile(self, profile: Dict[str, Any]) -> None:
        """Parse a JSON profile into a structure."""
        assert profile
        assert "StructureDefinition" == profile["resourceType"]

        # parse structure
        self.url = profile.get("url")
        self.fhir_version = profile.get("fhirVersion")
        self.fhir_last_updated = profile.get("meta", {}).get("lastUpdated")
        LOGGER.info('Parsing profile "{}"'.format(profile.get("name")))
        self.structure = FHIRStructureDefinitionStructure(self, profile)

    def process_profile(self) -> None:
        """Extract all elements and create classes."""
        # or self.structure.snapshot
        struct = self.structure.differential
        if struct is not None:
            mapped = {}
            for elem_dict in struct:

                element: FHIRStructureDefinitionElement = (
                    FHIRStructureDefinitionElement(  # noqa: E501
                        self, elem_dict, self.main_element is None
                    )
                )
                self.elements.append(element)
                mapped[element.path] = element

                # establish hierarchy (may move to extra
                # loop in case elements are no longer in order)
                if element.is_main_profile_element:
                    self.main_element = element
                parent = mapped.get(element.parent_name)
                if parent:
                    parent.add_child(element)

            # resolve element dependencies
            for element in self.elements:
                element.resolve_dependencies()

            # run check: if n_min > 0 and parent is in summary, must also be in summary
            for element in self.elements:
                if element.n_min is not None and element.n_min > 0:
                    if (
                        element.parent is not None
                        and element.parent.is_summary
                        and not element.is_summary
                    ):
                        LOGGER.error(
                            "n_min > 0 but not summary: `{}`".format(element.path)
                        )
                        element.summary_n_min_conflict = True

        # create classes and class properties
        if self.main_element is not None:
            snap_class, subs = self.main_element.create_class()
            if snap_class is None:
                raise Exception(
                    f'The main element for "{self.url}" did not create a class'
                )

            self.found_class(snap_class)
            if subs is not None:
                for sub in subs:
                    self.found_class(sub)
            self.targetname = snap_class.name

    def element_with_id(
        self, ident: str
    ) -> Union["FHIRStructureDefinitionElement", None]:
        """Returns a FHIRStructureDefinitionElementDefinition with the given
        id, if found. Used to retrieve elements defined via `contentReference`.
        """
        if self.elements:
            for element in self.elements:
                if element.definition and element.definition.id == ident:
                    return element
        return None

    # MARK: Class Handling
    def found_class(self, klass: "FHIRClass") -> None:
        self.classes.append(klass)

    def needed_external_classes(self) -> Iterable["FHIRClass"]:
        """Returns a unique list of class items that are needed for any of the
        receiver's classes' properties and are not defined in this profile.

        :raises: Will raise if called before `finalize` has been called.
        """
        if not self._did_finalize:
            raise Exception("Cannot use `needed_external_classes` before finalizing")

        internal = set([c.name for c in self.classes])
        needed = set()
        needs = []

        for klass in self.classes:
            # are there superclasses that we need to import?
            sup_cls = klass.superclass
            if (
                sup_cls is not None
                and sup_cls.name not in internal
                and sup_cls.name not in needed
            ):
                needed.add(sup_cls.name)
                needs.append(sup_cls)

            # look at all properties' classes and assign their modules
            for prop in klass.properties:
                prop_cls_name = prop.class_name
                assert isinstance(prop_cls_name, str)
                if (
                    prop_cls_name not in internal
                    and not self.spec.class_name_is_native(prop_cls_name)
                ):
                    prop_cls = FHIRClass.with_name(prop_cls_name)
                    if prop_cls is None:
                        raise Exception(
                            f'There is no class "{prop_cls_name}"'
                            f' for property "{prop.name}" on '
                            f'"{klass.name}" in {self.name}'
                        )
                    else:
                        prop.module_name = prop_cls.module
                        if prop_cls_name not in needed:
                            needed.add(prop_cls_name)
                            needs.append(prop_cls)

        return sorted(needs, key=lambda n: n.module or n.name)

    def referenced_classes(self) -> Iterable[str]:
        """Returns a unique list of **external** class names that are
        referenced from at least one of the receiver's `Reference`-type
        properties.

        :raises: Will raise if called before `finalize` has been called.
        """
        if not self._did_finalize:
            raise Exception("Cannot use `referenced_classes` before finalizing")

        references: Set[str] = set()
        for klass in self.classes:
            for prop in klass.properties:
                if len(prop.reference_to_names) > 0:
                    references.update(prop.reference_to_names)

        # no need to list references to our own classes, remove them
        for klass in self.classes:
            references.discard(klass.name)

        return sorted(references)

    def writable_classes(self) -> List["FHIRClass"]:
        classes = []
        for klass in self.classes:
            if klass.should_write():
                classes.append(klass)
        return classes

    # MARK: Finalizing
    def finalize(self) -> None:
        """Our spec object calls this when all profiles have been parsed."""

        # assign all super-classes as objects
        for cls in self.classes:
            if cls.superclass is None and cls.superclass_name is not None:
                super_cls = FHIRClass.with_name(cls.superclass_name)
                if super_cls is None and cls.superclass_name is not None:
                    raise Exception(
                        "There is no class implementation for class "
                        f'named "{cls.superclass_name}" in profile "{self.url}"'
                    )
                else:
                    cls.superclass = super_cls

        self._did_finalize = True


class FHIRStructureDefinitionStructure:
    """The actual structure of a complete profile."""

    def __init__(self, profile: FHIRStructureDefinition, profile_dict: Dict[str, Any]):
        self.profile: FHIRStructureDefinition = profile
        self.name: Optional[str] = None
        self.base: Optional[str] = None
        self.kind: Optional[str] = None
        self.subclass_of: Optional[str] = None
        self.snapshot: List[Dict[str, Any]] = list()
        self.differential: List[Dict[str, Any]] = list()

        self.parse_from(profile_dict)

    def parse_from(self, json_dict: Dict[str, Any]) -> None:
        name = json_dict.get("name")
        if not name:
            raise Exception("Must find 'name' in profile dictionary but found nothing")
        name_ = self.profile.spec.class_name_for_profile(name)
        assert isinstance(name_, str)  # MyPy
        self.name = name_
        self.base = json_dict.get("baseDefinition", None)
        self.kind = json_dict.get("kind", None)
        if self.base:
            subclass_of_ = self.profile.spec.class_name_for_profile(self.base)
            if isinstance(subclass_of_, str):
                self.subclass_of = subclass_of_

        # find element definitions
        if "snapshot" in json_dict:
            self.snapshot = json_dict["snapshot"].get("element", [])
        if "differential" in json_dict:
            self.differential = json_dict["differential"].get("element", [])


class FHIRStructureDefinitionElement:
    """An element in a profile's structure."""

    def __init__(
        self,
        profile: FHIRStructureDefinition,
        element_dict: Dict[str, Any],
        is_main_profile_element: bool = False,
    ):
        assert isinstance(profile, FHIRStructureDefinition)
        self.profile: FHIRStructureDefinition = profile
        self.path: Optional[str] = None
        self.parent: Optional[FHIRStructureDefinitionElement] = None
        self.children: Optional[List[FHIRStructureDefinitionElement]] = None
        self.parent_name: Optional[str] = None
        self.definition: Optional[FHIRStructureDefinitionElementDefinition] = None
        self.n_min: Optional[int] = None
        self.n_max: Optional[str] = None
        self.is_summary: bool = False
        # to mark conflicts,
        # see #13215 (http://gforge.hl7.org/gf/project/fhir/tracker/
        # ?action=TrackerItemEdit&tracker_item_id=13125)
        self.summary_n_min_conflict: bool = False
        self.valueset: Optional[FHIRValueSet] = None
        # assigned if the element has a binding
        # to a ValueSet that is a CodeSystem generating an enum
        self.enum: Optional[Dict[str, Any]] = None
        self.is_main_profile_element: bool = is_main_profile_element
        self.represents_class: bool = False

        self._superclass_name: Optional[str] = None
        self._did_resolve_dependencies: bool = False

        if element_dict is not None:
            self.parse_from(element_dict)
        else:
            self.definition = FHIRStructureDefinitionElementDefinition(self, None)

    def parse_from(self, element_dict: Dict[str, Any]) -> None:
        """
        :param element_dict:
        :return:
        """
        self.path = element_dict["path"]
        assert isinstance(self.path, str)
        parts = self.path.split(".")
        self.parent_name = ".".join(parts[:-1]) if len(parts) > 0 else None
        prop_name = parts[-1]
        if "-" in prop_name:
            prop_name = "".join([n[:1].upper() + n[1:] for n in prop_name.split("-")])

        self.definition = FHIRStructureDefinitionElementDefinition(self, element_dict)
        self.definition.prop_name = prop_name

        self.n_min = element_dict.get("min")
        self.n_max = element_dict.get("max")
        self.is_summary = element_dict.get("isSummary", False)

    def resolve_dependencies(self) -> None:
        if self.is_main_profile_element:
            self.represents_class = True
        if (
            not self.represents_class
            and self.children is not None
            and len(self.children) > 0
        ):
            self.represents_class = True
        if self.definition is not None:
            self.definition.resolve_dependencies()

        self._did_resolve_dependencies = True

    # MARK: Hierarchy

    def add_child(self, element: "FHIRStructureDefinitionElement") -> None:
        """
        :param element:
        :return:
        """
        element.parent = self
        if self.children is None:
            self.children = [element]
        else:
            self.children.append(element)

    def create_class(
        self, module: str = None
    ) -> Tuple[Union["FHIRClass", None], Union[None, Sequence["FHIRClass"]]]:
        """Creates a FHIRClass instance from the receiver, returning the
        created class as the first and all inline defined subclasses as the
        second item in the tuple.
        """
        assert self._did_resolve_dependencies
        if not self.represents_class:
            return None, None

        class_name = self.name_if_class()  # noqa: F841
        subs = []
        cls, did_create = FHIRClass.for_element(self)
        children = self.children or []
        if did_create:
            LOGGER.debug(f'Created class "{cls.name}"')
            if module is None and self.is_main_profile_element:
                module = self.profile.spec.as_module_name(cls.name)
            cls.module = module
            for child in children:
                cls.add_property_in_sequence(child)

        # child classes
        for child in children:
            properties = child.as_properties()
            if properties is not None:

                # collect subclasses
                sub, subsubs = child.create_class(module)
                if sub is not None:
                    subs.append(sub)
                if subsubs is not None:
                    subs.extend(subsubs)

                # add properties to class
                if did_create:
                    for prop in properties:
                        cls.add_property(prop)

        return cls, subs

    def as_properties(self) -> Union[List["FHIRClassProperty"], None]:
        """If the element describes a *class property*, returns a list of
        FHIRClassProperty instances, None otherwise.
        """
        assert self._did_resolve_dependencies
        if self.is_main_profile_element or self.definition is None:
            return None

        # TODO: handle slicing information (not sure why these properties were
        # omitted previously)
        # if self.definition.slicing:
        #    logger.debug('Omitting property "{}"
        #    for slicing'.format(self.definition.prop_name))
        #    return None

        # this must be a property
        if self.parent is None:
            raise Exception(
                f'Element reports as property but has no parent: "{self.path}"'
            )

        # create a list of FHIRClassProperty instances (usually with only 1 item)
        if len(self.definition.types) > 0:
            props: List[FHIRClassProperty] = []
            for type_obj in self.definition.types:

                # an inline class
                if (
                    "BackboneElement" == type_obj.code or "Element" == type_obj.code
                ):  # data types don't use "BackboneElement"
                    props.append(
                        FHIRClassProperty(self, type_obj, self.name_if_class())
                    )
                    # TODO: look at http://hl7.org/fhir/
                    # StructureDefinition/structuredefinition-explicit-type-name ?
                else:
                    props.append(FHIRClassProperty(self, type_obj, None))
            return props

        # no `type` definition in the element:
        # it's a property with an inline class definition
        type_obj = FHIRElementType()
        return [FHIRClassProperty(self, type_obj, self.name_if_class())]

    # MARK: Name Utils
    def name_of_resource(self) -> str:
        assert self._did_resolve_dependencies
        if not self.is_main_profile_element:
            return self.name_if_class()
        name = self.definition and self.definition.name or self.path
        assert isinstance(name, str)
        return name

    def name_if_class(self) -> str:
        assert self.definition
        name = self.definition.name_if_class()
        assert isinstance(name, str)
        return name

    @property
    def superclass_name(self) -> Optional[str]:
        """Determine the superclass for the element (used for class elements)."""
        if self._superclass_name is None:
            assert self.definition
            tps = self.definition.types
            if len(tps) > 1:
                raise Exception(
                    "Have more than one type to determine superclass "
                    f'in "{self.path}": "{tps}"'
                )
            type_code: Optional[str] = None

            if (
                self.is_main_profile_element
                and self.profile.structure.subclass_of is not None
            ):
                type_code = self.profile.structure.subclass_of
            elif len(tps) > 0:
                type_code = tps[0].code
            elif self.profile.structure.kind:
                type_code = self.profile.spec.settings.DEFAULT_BASES.get(
                    self.profile.structure.kind
                )
            if type_code is not None:
                self._superclass_name = self.profile.spec.class_name_for_type(type_code)

        return self._superclass_name


class FHIRStructureDefinitionElementDefinition:
    """The definition of a FHIR element."""

    def __init__(
        self,
        element: FHIRStructureDefinitionElement,
        definition_dict: Optional[Dict[str, Any]] = None,
    ):
        self.id: Optional[str] = None
        self.element: FHIRStructureDefinitionElement = element
        self.types: List[FHIRElementType] = []
        self.name: Optional[str] = None
        self.prop_name: Optional[str] = None
        self.content_reference: Optional[str] = None
        self._content_referenced: Optional[
            FHIRStructureDefinitionElementDefinition
        ] = None
        self.short: Optional[str] = None
        self.formal: Optional[str] = None
        self.comment: Optional[str] = None
        self.binding: Optional[FHIRElementBinding] = None
        self.constraint: Optional[FHIRElementConstraint] = None
        self.mapping: Optional[FHIRElementMapping] = None
        self.slicing: Optional[Dict[str, Any]] = None
        self.representation: Optional[Sequence[str]] = None
        # TODO: handle  "slicing"

        if definition_dict is not None:
            self.parse_from(definition_dict)

    def parse_from(self, definition_dict: Dict[str, Any]) -> None:
        self.id = definition_dict.get("id")

        self.types = []
        for type_dict in definition_dict.get("type", []):
            self.types.append(FHIRElementType(type_dict))

        self.name = definition_dict.get("name")
        self.content_reference = definition_dict.get("contentReference")

        self.short = definition_dict.get("short")
        self.formal = definition_dict.get("definition")
        if (
            self.formal and self.short == self.formal[:-1]
        ):  # formal adds a trailing period
            self.formal = None
        self.comment = definition_dict.get("comments")

        if "binding" in definition_dict:
            self.binding = FHIRElementBinding(definition_dict["binding"])
        if "constraint" in definition_dict:
            self.constraint = FHIRElementConstraint(definition_dict["constraint"])
        if "mapping" in definition_dict:
            self.mapping = FHIRElementMapping(definition_dict["mapping"])
        if "slicing" in definition_dict:
            self.slicing = definition_dict["slicing"]
        self.representation = definition_dict.get("representation")

    def resolve_dependencies(self) -> None:
        # update the definition from a reference, if there is one
        if self.content_reference is not None:
            if "#" != self.content_reference[:1]:
                raise Exception(
                    "Only relative 'contentReference' element"
                    " definitions are supported right now"
                )
            elem = self.element.profile.element_with_id(self.content_reference[1:])
            if elem is None:
                raise Exception(
                    "There is no element definition with "
                    f'id "{self.content_reference}", as referenced by '
                    f"{self.element.path} in {self.element.profile.url}"
                )
            self._content_referenced = elem.definition

        # resolve bindings
        if (
            self.binding is not None
            and self.binding.is_required
            and (self.binding.uri is not None or self.binding.canonical is not None)
        ):
            uri = self.binding.canonical or self.binding.uri
            assert isinstance(uri, str)
            if "http://hl7.org/fhir" != uri[:19]:
                LOGGER.debug(f'Ignoring foreign ValueSet "{uri}"')
                return

            valueset: FHIRValueSet = self.element.profile.spec.valueset_with_uri(uri)
            if valueset is None:
                LOGGER.error(
                    "There is no ValueSet for required binding "
                    f'"{uri}" on {self.name or self.prop_name} '
                    f"in {self.element.profile.name}"
                )
            else:
                self.element.valueset = valueset
                self.element.enum = valueset.enum

    def name_if_class(self) -> Union[str, None]:
        """Determines the class-name that the element would have if it was
        defining a class. This means it uses "name", if present, and the last
        "path" component otherwise.
        """
        if self._content_referenced is not None:
            return self._content_referenced.name_if_class()

        with_name = self.name or self.prop_name
        assert isinstance(with_name, str)
        parent_name = (
            self.element.parent.name_if_class()
            if self.element.parent is not None
            else None
        )
        classname = self.element.profile.spec.class_name_for_type(
            with_name, parent_name
        )
        if (
            parent_name is not None
            and classname
            and self.element.profile.spec.settings.BACKBONE_CLASS_ADDS_PARENT
        ):
            classname = parent_name + classname
        return classname


class FHIRElementType:
    """Representing a type of an element."""

    def __init__(self, type_dict: Dict[str, Any] = None):
        self.code: str
        self.profile: Union[None, List[str]] = None

        if type_dict is not None:
            self.parse_from(type_dict)

    @staticmethod
    def parse_extension(type_dict: Dict[str, Any]) -> Union[Dict[str, Any], None]:
        """ """
        extensions = []
        urls = [
            "http://hl7.org/fhir/StructureDefinition/structuredefinition-fhir-type",
            "http://hl7.org/fhir/StructureDefinition/structuredefinition-json-type",
        ]

        if type_dict.get("_code", None) is not None:
            extensions = type_dict["_code"].get("extension", [])

        if len(extensions) == 0:
            # New Style from R4
            extensions = type_dict.get("extension", [])

        if len(extensions) > 0:

            extensions_ = [e for e in extensions if e.get("url") in urls]
            if len(extensions_) == 1:
                return extensions_[0]
            elif len(extensions_) > 1:
                raise Exception(
                    f"Found more than one structure definition JSON type in {type_dict}"
                )
        return None

    @staticmethod
    def parse_target_profile(type_dict: Dict[str, Any]) -> Union[List[str], None]:
        """ """
        profile = type_dict.get("targetProfile", None)
        if profile is None:
            return profile
        if isinstance(profile, (str, bytes)):
            profile = [profile]

        if not isinstance(profile, list):
            raise Exception(
                "Expecting a list for 'targetProfile' "
                "definition of an element type, got {0} as {1}".format(
                    profile, type(profile)
                )
            )
        return profile

    def parse_from(self, type_dict: Dict[str, Any]) -> None:
        """ """
        self.code = type_dict["code"]
        extension = FHIRElementType.parse_extension(type_dict)

        if self.code and HTTP_URL.match(self.code):
            if extension is None:
                raise NotImplementedError
            self.code = extension["valueUrl"]

        elif self.code is None:
            if extension is None:
                raise Exception(
                    'Expecting either "code" or "_code" and '
                    f"a JSON type extension, found neither in {type_dict}"
                )

            self.code = extension["valueString"]
        if self.code is None:
            raise Exception(f"No JSON type found in {type_dict}")

        if not isinstance(self.code, str):
            raise Exception(
                "Expecting a string for 'code' definition "
                f"of an element type, got {self.code} as {type(self.code)}"
            )
        profile = FHIRElementType.parse_target_profile(type_dict)
        if profile is not None:
            self.profile = profile


class FHIRElementBinding:
    """The "binding" element in an element definition"""

    def __init__(self, binding_obj: Dict[str, Any]):
        self.strength: Optional[str] = binding_obj.get("strength")
        self.description: Optional[str] = binding_obj.get("description")
        self.uri: Optional[str] = binding_obj.get("valueSetUri")
        self.canonical: Optional[str] = binding_obj.get("valueSetCanonical")
        self.is_required: bool = "required" == self.strength


class FHIRElementConstraint:
    """Constraint on an element."""

    def __init__(self, constraint_arr: Dict[str, Any]):
        pass


class FHIRElementMapping:
    """Mapping FHIR to other standards."""

    def __init__(self, mapping_arr: Dict[str, Any]):
        pass


class FHIRClass:
    """An element/resource that should become its own class."""

    __known_classes__: DefaultDict[str, "FHIRClass"] = defaultdict()

    @classmethod
    def for_element(
        cls, element: FHIRStructureDefinitionElement
    ) -> Tuple["FHIRClass", bool]:
        """Returns an existing class or creates one for the given element.
        Returns a tuple with the class and a bool indicating creation.
        """
        assert element.represents_class
        class_name = element.name_if_class()
        if class_name in cls.__known_classes__:
            return cls.__known_classes__[class_name], False

        klass = cls(element)
        cls.__known_classes__[class_name] = klass
        return klass, True

    @classmethod
    def with_name(cls, class_name: str) -> "FHIRClass":
        try:
            return cls.__known_classes__[class_name]
        except KeyError:
            raise NotImplementedError

    @classmethod
    def is_known_class(cls, name: str) -> bool:
        """ """
        return name in cls.__known_classes__

    def __init__(self, element: FHIRStructureDefinitionElement):
        """
        :param element: FHIRStructureDefinitionElement
        """
        assert element.represents_class
        self.path: Optional[str] = element.path
        self.name: str = element.name_if_class()
        self.module: Optional[str] = None
        self.resource_type: str = element.name_of_resource()
        self.superclass: Optional[FHIRClass] = None
        self.superclass_name: Optional[str] = element.superclass_name
        self.short: Optional[str] = None
        self.formal: Optional[str] = None
        self.properties: List[FHIRClassProperty] = list()
        self.properties_sequence: List[str] = list()
        self.expanded_nonoptionals: Dict[str, List[FHIRClassProperty]] = dict()
        self.class_type = FHIR_CLASS_TYPES.other
        if element.definition:
            self.short = element.definition.short
            self.formal = element.definition.formal

        kind = element.profile.structure.kind
        if kind == "resource":
            self.class_type = FHIR_CLASS_TYPES.resource
        elif kind == "logical":
            self.class_type = FHIR_CLASS_TYPES.logical
        elif kind == "complex-type":
            self.class_type = FHIR_CLASS_TYPES.complex_type
        elif kind == "primitive-type":
            self.class_type = FHIR_CLASS_TYPES.primitive_type

    def add_property(self, prop: "FHIRClassProperty") -> None:
        """Add a property to the receiver.

        :param FHIRClassProperty prop: A FHIRClassProperty instance
        """
        assert isinstance(prop, FHIRClassProperty)

        # do we already have a property with this name?
        # if we do and it's a specific reference, make it a reference to a
        # generic resource
        for existing in self.properties:
            if existing.name == prop.name:
                if 0 == len(existing.reference_to_names):
                    LOGGER.warning(
                        f'Already have property "{prop.name}" on "{self.name}",'
                        " which is only allowed for references"
                    )
                    continue
                else:
                    existing.reference_to_names.extend(prop.reference_to_names)
                return

        self.properties.append(prop)
        self.properties = sorted(self.properties, key=lambda x: x.name)

        if prop.nonoptional and prop.one_of_many is not None:
            if prop.one_of_many in self.expanded_nonoptionals:
                self.expanded_nonoptionals[prop.one_of_many].append(prop)
            else:
                self.expanded_nonoptionals[prop.one_of_many] = [prop]

    def add_property_in_sequence(self, element: FHIRStructureDefinitionElement) -> None:
        """ """
        if element.definition is None:
            return
        prop = element.definition.prop_name
        if prop is None:
            raise NotImplementedError
        if prop.endswith("[x]"):
            for typ in element.definition.types:
                self.properties_sequence.append(
                    prop.replace("[x]", typ.code[0].upper() + typ.code[1:])
                )
        else:
            self.properties_sequence.append(prop)

    @property
    def expanded_properties_sequence(self) -> List[str]:
        my_properties = self.properties_sequence
        superclass = self.superclass
        while True:
            if superclass is None:
                break
            props = superclass.properties_sequence
            superclass = superclass.superclass
            if props:
                my_properties = props + my_properties
        return my_properties

    @property
    def nonexpanded_properties(self) -> List["FHIRClassProperty"]:
        nonexpanded = []
        included = set()
        for prop in self.properties:
            if prop.one_of_many:
                if prop.one_of_many in included:
                    continue
                included.add(prop.one_of_many)
            nonexpanded.append(prop)
        return nonexpanded

    @property
    def nonexpanded_nonoptionals(self) -> List["FHIRClassProperty"]:
        nonexpanded = []
        included = set()
        for prop in self.properties:
            if not prop.nonoptional:
                continue
            if prop.one_of_many:
                if prop.one_of_many in included:
                    continue
                included.add(prop.one_of_many)
            nonexpanded.append(prop)
        return nonexpanded

    def property_for(self, prop_name: str) -> Union["FHIRClassProperty", None]:
        """
        :param prop_name:
        :return:
        """
        for prop in self.properties:
            if prop.orig_name == prop_name:
                return prop

        # Element is its own superclass
        if self.superclass and self != self.superclass:
            return self.superclass.property_for(prop_name)
        return None

    def should_write(self) -> bool:
        if self.superclass is not None:
            return True
        return True if len(self.properties) > 0 else False

    @property
    def has_nonoptional(self) -> bool:
        for prop in self.properties:
            if prop.nonoptional:
                return True
        return False

    @property
    def sorted_nonoptionals(
        self,
    ) -> List[Tuple[str, List["FHIRClassProperty"]]]:
        return sorted(self.expanded_nonoptionals.items())


class FHIRClassProperty:
    """An element describing an instance property."""

    def __init__(
        self,
        element: FHIRStructureDefinitionElement,
        type_obj: FHIRElementType,
        type_name: str = None,
    ):
        assert element and type_obj
        # and must be instances of FHIRStructureDefinitionElement and FHIRElementType
        spec = element.profile.spec

        self.path = element.path
        # assign if this property has been expanded from "property[x]"
        self.one_of_many: Optional[str] = None

        if not type_name:
            type_name = type_obj.code
        self.type_name = type_name

        name = element.definition and element.definition.prop_name or None
        assert isinstance(name, str)
        if "[x]" in name:
            self.one_of_many = name.replace("[x]", "")
            name = name.replace(
                "[x]", "{0}{1}".format(type_name[:1].upper(), type_name[1:])
            )
        self.orig_name: str = name
        self.name: str = spec.safe_property_name(name)
        self.parent_name: Optional[str] = element.parent_name
        self.class_name: Optional[str] = spec.class_name_for_type_if_property(type_name)
        self.enum = element.enum if "code" == type_name else None
        # should only be set if it's an external module (think Python)
        self.module_name: Optional[str] = None
        assert isinstance(self.class_name, str)
        self.json_class: str = spec.json_class_for_class_name(self.class_name)
        self.is_native: bool = (
            False if self.enum else spec.class_name_is_native(self.class_name)
        )
        self.is_array: bool = True if "*" == element.n_max else False
        self.is_summary: bool = element.is_summary
        self.is_summary_n_min_conflict: bool = element.summary_n_min_conflict
        self.nonoptional: bool = (
            True if element.n_min is not None and 0 != int(element.n_min) else False
        )
        self.reference_to_names: List[str] = list()
        if type_obj.profile:
            names = spec.class_name_for_profile(type_obj.profile)
            if isinstance(names, str):
                self.reference_to_names.append(names)
            elif isinstance(names, list):
                self.reference_to_names = names

        if element.definition:
            self.short: Optional[str] = element.definition.short
            self.formal: Optional[str] = element.definition.formal
            self.representation: Optional[
                Sequence[str]
            ] = element.definition.representation

        self.field_type = self.class_name
        self.field_type_module = self.module_name


class FHIRResourceFile:
    """A FHIR example resource file."""

    @classmethod
    def find_all(cls, directory: pathlib.Path) -> List["FHIRResourceFile"]:
        """Finds all example JSON files in the given directory."""

        assert directory.is_dir()
        all_tests = []
        for filepath in directory.glob("*.json"):
            if "canonical.json" == filepath.name:
                continue
            with open(str(filepath), "r", encoding="utf-8") as fp:
                try:
                    data = json.load(fp)
                except json.decoder.JSONDecodeError:
                    continue
                if "resourceType" not in data:
                    continue
                resource_type = data["resourceType"]
                if resource_type == "StructureDefinition":
                    continue
                if not FHIRClass.is_known_class(resource_type):
                    LOGGER.warning(
                        f"class '{resource_type}' is not found"
                        f" in ´´FHIRClass.__known_classes__´´, ignored '{filepath}'."
                    )
                    continue

            all_tests.append(cls(filepath=filepath))

        return all_tests

    def __init__(self, filepath: pathlib.Path):
        self.filepath = filepath
        self._content: Optional[Dict[str, Any]] = None

    @property
    def content(self) -> Dict[str, Any]:
        """Process the unit test file, determining class structure
        from the given classes dict.

        :returns: A tuple with (top-class-name, [test-dictionaries])
        """
        if self._content is None:
            LOGGER.info(f"Parsing unit test {self.filepath.name}")
            utest = None
            assert self.filepath.exists()
            with open(str(self.filepath), "r", encoding="utf-8") as handle:
                utest = json.load(handle)
            assert utest
            self._content = utest
        return self._content


class FHIRUnitTestController:
    """Can create unit tests from example files."""

    def __init__(self, spec: FHIRSpec, settings: Configuration = None):
        """
        :param spec:
        :param settings:
        """
        self.spec = spec
        self.settings = settings or spec.settings
        self.files: List[FHIRResourceFile] = list()
        self.collections: List[FHIRUnitTestCollection] = list()

    def find_and_parse_tests(self, directory: pathlib.Path) -> None:
        """
        :param directory:
        :return:
        """
        self.files = FHIRResourceFile.find_all(directory)

        # create tests
        tests = []
        for resource in self.files:
            test = self.unittest_for_resource(resource)
            if test is not None:
                tests.append(test)

        # collect per class
        collections: Dict[str, FHIRUnitTestCollection] = {}
        for test in tests:
            coll = collections.get(test.klass.name)
            if coll is None:
                coll = FHIRUnitTestCollection(test.klass)
                collections[test.klass.name] = coll
            coll.add_test(test)

        self.collections = [v for v in collections.values()]

    # MARK: Utilities
    def unittest_for_resource(
        self, resource: FHIRResourceFile
    ) -> Union["FHIRUnitTest", None]:
        """Returns a FHIRUnitTest instance or None for the given resource,
        depending on if the class to be tested is __known_classes__.
        """
        classname = resource.content.get("resourceType")
        assert classname
        if classname in self.settings.CLASS_MAP:
            classname = self.settings.CLASS_MAP[classname]
        klass = FHIRClass.with_name(classname)
        if klass is None:
            LOGGER.error(
                f'There is no class for "{classname}", cannot create unit tests'
            )
            return None

        return FHIRUnitTest(self, resource.filepath, resource.content, klass)

    def make_path(self, prefix: Optional[str], key: str) -> str:
        """Takes care of combining prefix and key into a path."""
        path = key
        if prefix:
            path = self.settings.UNITTEST_FORMAT_PATH_KEY.format(prefix, path)
        return path


class FHIRUnitTestItem:
    """Represents unit tests to be performed against a single data model
    property. If the property itself is an element, will be expanded into
    more FHIRUnitTestItem that cover its own properties.
    """

    def __init__(
        self,
        filepath: pathlib.Path,
        path: str,
        value: Any,
        klass: FHIRClass,
        array_item: bool,
        enum_item: Dict[str, Any] = None,
    ):
        assert path
        assert value is not None
        assert klass
        self.filepath = filepath  # needed for debug logging
        self.path = path
        self.value = value
        self.klass = klass
        self.array_item = array_item
        self.enum = enum_item["name"] if enum_item is not None else None

    def create_tests(
        self, controller: FHIRUnitTestController
    ) -> List["FHIRUnitTestItem"]:
        """Creates as many FHIRUnitTestItem instances as the item defines, or
        just returns a list containing itself if this property is not an
        element.

        :returns: A list of FHIRUnitTestItem items, never None
        """
        tests: List[FHIRUnitTestItem] = []

        # property is another element, recurse
        if isinstance(self.value, dict):
            prefix = self.path
            if not self.array_item:
                prefix = controller.settings.UNITTEST_FORMAT_PATH_PREPARE.format(prefix)

            test: FHIRUnitTest = FHIRUnitTest(
                controller, self.filepath, self.value, self.klass, prefix
            )
            tests.extend(test.tests)

        # regular test case; skip string tests that are longer than 200 chars
        else:
            is_str = isinstance(self.value, (str, bytes))
            value = self.value
            if is_str:
                if len(value) > 200:
                    return tests

                elif not value.isprintable():
                    return tests

                self.value = value.replace("\n", "\\n")
            tests.append(self)

        return tests

    def __repr__(self) -> str:
        return f'Unit Test Case "{self.path}": "{self.value}"'


class FHIRUnitTest:
    """Holds on to unit tests (FHIRUnitTestItem in `tests`) that are to be run
    against one data model class (`klass`).
    """

    def __init__(
        self,
        controller: FHIRUnitTestController,
        filepath: pathlib.Path,
        content: Dict[str, Any],
        klass: FHIRClass,
        prefix: str = None,
    ):
        assert content and klass
        self.controller: FHIRUnitTestController = controller
        self.filepath: pathlib.Path = filepath
        self.filename = filepath.name
        self.content: Dict[str, Any] = content
        self.klass: FHIRClass = klass
        self.prefix: Optional[str] = prefix

        self.tests: List[FHIRUnitTestItem] = list()
        self.expand()

    def expand(self) -> None:
        """Expand into a list of FHIRUnitTestItem_name instances."""
        tests: List[FHIRUnitTestItem] = []
        for key, val in self.content.items():
            if "resourceType" == key or "fhir_comments" == key or "_" == key[:1]:
                continue

            prop = self.klass.property_for(key)
            if prop is None:
                # import pdb;pdb.set_trace()
                path = "{}.{}".format(self.prefix, key) if self.prefix else key
                LOGGER.warning(
                    f'Unknown property "{path}" in unit test '
                    f"on {self.klass.name} in {self.filepath}"
                )
            else:
                assert prop.class_name
                propclass = FHIRClass.with_name(prop.class_name)
                if propclass is None:
                    path = (
                        "{}.{}".format(self.prefix, prop.name)
                        if self.prefix
                        else prop.name
                    )
                    LOGGER.error(
                        f'There is no class "{prop.class_name}" '
                        f'for property "{path}" in {self.filepath}'
                    )
                else:
                    path = self.controller.make_path(self.prefix, prop.name)

                    if list == type(val):
                        i = 0
                        for ival in val:
                            if ival is None:
                                continue
                            idxpath = self.controller.settings.UNITTEST_FORMAT_PATH_INDEX.format(  # noqa: E501
                                path, i
                            )
                            item: FHIRUnitTestItem = FHIRUnitTestItem(
                                self.filepath, idxpath, ival, propclass, True, prop.enum
                            )
                            tests.extend(item.create_tests(self.controller))
                            i += 1
                            if i >= 10:  # let's assume we don't need 100s of unit tests
                                break
                    else:
                        if val is None:
                            continue
                        item = FHIRUnitTestItem(
                            self.filepath, path, val, propclass, False, prop.enum
                        )
                        tests.extend(item.create_tests(self.controller))

        self.tests = sorted(tests, key=lambda t: t.path)


class FHIRUnitTestCollection:
    """Represents a FHIR unit test collection, meaning unit tests pertaining
    to one data model class, to be run against local sample files.
    """

    def __init__(self, klass: FHIRClass):
        """
        :param klass:
        """
        self.klass = klass
        self.tests: List[FHIRUnitTest] = []

    def add_test(self, test: FHIRUnitTest) -> None:
        """
        :param test:
        :return:
        """
        if test is not None:
            if len(self.tests) < 10:
                # let's assume we don't need 100s of unit tests
                self.tests.append(test)


# --*-- Functions
def resolve_path(string_path: str, parent: pathlib.Path = None) -> pathlib.Path:
    """ """
    if os.path.isabs(string_path):
        return pathlib.Path(string_path)
    elif string_path.startswith("~"):
        return pathlib.Path(os.path.expanduser(string_path))

    if parent is None:
        parent = pathlib.Path(os.getcwd())
    if string_path == ".":
        return parent

    me = parent
    for part in string_path.split(os.sep):
        if not part:
            continue
        if part == ".":
            continue
        elif part == "..":
            me = me.parent
        else:
            me = me / part
    return me


# --*-- Public Utilities Functions
def is_text_content(response: HTTPResponse) -> bool:
    """
    :param response:
    :return: bool
    """
    content_type = response.headers.get("Content-Type", "").split(";")[0]
    if content_type == "":
        raise NotImplementedError
    content_type = content_type.strip().lower()
    if content_type.startswith("text/"):
        return True
    elif content_type.startswith("application/"):
        ext = mimetypes.guess_extension(content_type, strict=True)
        if ext in (".js", ".json", ".mjs"):
            return True

    return False


def filename_from_response(response: HTTPResponse) -> str:
    """ """

    def _from_url(url: str) -> str:
        path_ = urlparse(url).path
        if path_ in ("", "/"):
            c_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip()
            ext = mimetypes.guess_extension(c_type.lower(), strict=True)
            if ext is None:
                ext = ".html"
            return "index" + ext
        return pathlib.Path(path_).name

    if is_text_content(response):
        return _from_url(response.geturl())
    file_info = response.headers.get("Content-Disposition", "")
    for part in file_info.split(";"):
        part_ = part.strip()
        if not part_:
            continue
        if part_.lower().startswith("filename="):
            filename = part_.split("=", 1)[1].strip()
            try:
                # try escape " or '
                filename = literal_eval(filename)
            except ValueError:
                # It's OK
                pass
            return filename
    # always fall-back
    return _from_url(response.geturl())


def write_response_stream(
    output_dir: pathlib.Path, response: HTTPResponse
) -> pathlib.Path:
    """ """
    filename = filename_from_response(response)
    output = output_dir / filename
    mode = is_text_content(response) and "w" or "wb"
    with io.open(str(output), mode) as fp:
        while not response.closed:
            chunk = response.read(io.DEFAULT_BUFFER_SIZE)
            if not chunk:
                break
            fp.write(mode == "wb" and chunk or chunk.decode())
    return output


def download(url: str, download_directory: pathlib.Path) -> pathlib.Path:
    """ """
    request = Request(url=url, method="GET", unverifiable=False)
    response: HTTPResponse
    try:
        response = urlopen(request)
        assert response.status == 200
    except HTTPError:
        # xxx: handle nicely later
        raise

    return write_response_stream(output_dir=download_directory, response=response)

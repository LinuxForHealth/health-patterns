# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Classes for representing references to resources and the logic to resolve them.
"""
from dataclasses import dataclass
from typing import Generic
from typing import Optional
from typing import Type, TypeVar
from typing import Union
from typing import cast

from fhir.resources.bundle import BundleEntry
from fhir.resources.resource import Resource


# covariant makes it legal to assign say ResourceReference[Condition] to a ResourceReference[Resource]
# And to pass a reference to a subclass to a method that expects the superclass
# This is OK because ResourceReference is immutable.
# https://www.python.org/dev/peps/pep-0484/#covariance-and-contravariance
T_co = TypeVar("T_co", bound=Resource, covariant=True)  # pylint: disable=invalid-name
U = TypeVar("U", bound=Resource)


@dataclass(frozen=True)
class ResourceReference(Generic[T_co]):
    """Defines a reference to a resource

    This is used to construct a fhir reference object:
    http://www.hl7.org/fhir/references.html#2.3.0

    The resource id is not always available when the resource
    does not exist on a FHIR server but is defined in a bundle:
    https://cloud.google.com/healthcare-api/docs/how-tos/fhir-bundles#resolving_references_to_resources_created_in_a_bundle

    The formal resolution documentation is defined here:
    https://www.hl7.org/fhir/bundle.html#bundle-unique

    This class models a reference to a resource that can be used
    within nlp-inisghts to construct the FHIR reference object.

    The target can either be a BundleEntry, or for the case where the resource is not in a
    bundle the resource itself.
    """

    target: Union[BundleEntry, Resource]

    @property
    def reference(self) -> str:
        """Returns a reference to the resource

        Raises ValueError if a reference cannot be created.
        """

        if isinstance(self.target, BundleEntry):
            if self.target.fullUrl:
                return str(self.target.fullUrl)
            if self.target.resource.id:
                return type(self.target).__name__ + "/" + str(self.target.resource.id)
            raise ValueError("Cannot create a reference to the bundle entry's resource")

        if isinstance(self.target, Resource):
            return type(self.target).__name__ + "/" + str(self.target.id)

        raise ValueError(f"Unknown target type {type(self.target)}")

    @property
    def resource(self) -> T_co:
        """Returns the target resource

        Raises ValueError if the target cannot be determined.
        """
        if isinstance(self.target, BundleEntry):
            return cast(T_co, self.target.resource)

        if isinstance(self.target, Resource):
            return cast(T_co, self.target)

        raise ValueError(f"Unknown target type {type(self.target)}")

    def down_cast(self, clazz: Type[U]) -> Optional["ResourceReference[U]"]:
        """Does a down cast of a reference of a resource to a reference
        of a more specific type.

        None is returned if the resource is not of the correct type
        """
        if not isinstance(self.resource, clazz):
            return None
        return cast(ResourceReference[U], self)

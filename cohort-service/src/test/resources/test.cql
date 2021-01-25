library "Test" version '1.0.0'

using "fakeIg" version '0.0.1'
include "FHIRHelpers" version '4.0.0' called FHIRHelpers

context Patient

define FakeExtensionExists:
	["FakePatient"] p
	  return exists({p.fakeExtension})

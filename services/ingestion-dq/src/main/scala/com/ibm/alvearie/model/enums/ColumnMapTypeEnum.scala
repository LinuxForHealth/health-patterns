package com.ibm.alvearie.model.enums

import com.fasterxml.jackson.core.`type`.TypeReference

object ColumnMapTypeEnum extends Enumeration {
  type ColumnMapTypeEnum = Value
  val FHIR_PATH, JSON_PATH = Value
}
class ColumnMapTypeEnumType extends TypeReference[ColumnMapTypeEnum.type]

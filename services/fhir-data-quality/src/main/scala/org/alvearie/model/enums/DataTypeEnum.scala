package org.alvearie.model.enums

import com.fasterxml.jackson.core.`type`.TypeReference

object DataTypeEnum extends Enumeration {
  type DataTypeEnum = Value
  val SimpleDataStruct, ComplexDataStruct = Value
}

class DataTypeEnumType extends TypeReference[DataTypeEnum.type]

package org.alvearie.model

import com.fasterxml.jackson.module.scala.JsonScalaEnumeration
import org.alvearie.model.enums.DataTypeEnum.DataTypeEnum
import org.alvearie.model.enums.DataTypeEnumType

case class Data(
    name: String,
    description: String,
    @JsonScalaEnumeration(classOf[DataTypeEnumType]) `type`: DataTypeEnum,
    simpleDataStruct: Option[SimpleDataStruct] = None,
    complexDataStruct: Option[ComplexDataStruct] = None,
    columns: Array[Column],
    cache: Boolean
)

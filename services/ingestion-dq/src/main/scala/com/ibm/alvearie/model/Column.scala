package com.ibm.alvearie.model

import com.fasterxml.jackson.module.scala.JsonScalaEnumeration
import com.ibm.alvearie.model.enums.ColumnMapTypeEnum.ColumnMapTypeEnum
import com.ibm.alvearie.model.enums.ColumnMapTypeEnumType

case class Column(
    name: String,
    description: String,
    mapValue: String,
    @JsonScalaEnumeration(
      classOf[ColumnMapTypeEnumType]
    ) mapType: ColumnMapTypeEnum
)

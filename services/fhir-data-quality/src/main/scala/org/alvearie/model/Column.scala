package org.alvearie.model

import com.fasterxml.jackson.module.scala.JsonScalaEnumeration
import org.alvearie.model.enums.ColumnMapTypeEnum.ColumnMapTypeEnum
import org.alvearie.model.enums.ColumnMapTypeEnumType

case class Column(
    name: String,
    description: String,
    mapValue: String,
    @JsonScalaEnumeration(
      classOf[ColumnMapTypeEnumType]
    ) mapType: ColumnMapTypeEnum
)

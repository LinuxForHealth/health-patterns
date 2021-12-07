package org.alvearie.model

import com.fasterxml.jackson.module.scala.JsonScalaEnumeration
import org.alvearie.model.enums.QualityCheckTypeEnum.QualityCheckTypeEnum
import org.alvearie.model.enums.QualityCheckTypeEnumType

case class QualityCheck(
    name: String,
    description: String,
    @JsonScalaEnumeration(
      classOf[QualityCheckTypeEnumType]
    ) `type`: QualityCheckTypeEnum,
    level: String,
    clause: String,
    args: Map[String, Any],
    active: Boolean
)

package com.ibm.alvearie.model

import com.fasterxml.jackson.module.scala.JsonScalaEnumeration
import com.ibm.alvearie.model.enums.QualityCheckTypeEnum.QualityCheckTypeEnum
import com.ibm.alvearie.model.enums.QualityCheckTypeEnumType

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

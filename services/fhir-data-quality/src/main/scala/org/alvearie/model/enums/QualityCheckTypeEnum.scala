package org.alvearie.model.enums

import com.fasterxml.jackson.core.`type`.TypeReference

object QualityCheckTypeEnum extends Enumeration {
  type QualityCheckTypeEnum = Value
  val isComplete, isUnique, hasSize, isContainedIn, notSatisfies = Value
}

class QualityCheckTypeEnumType extends TypeReference[QualityCheckTypeEnum.type]

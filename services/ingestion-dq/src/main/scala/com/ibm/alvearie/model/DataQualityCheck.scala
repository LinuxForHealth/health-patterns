package com.ibm.alvearie.model

case class DataQualityCheck(
    data: Data,
    qualityChecks: Array[QualityCheck],
    active: Boolean
)

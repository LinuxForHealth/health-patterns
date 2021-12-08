package org.alvearie.model

case class DataQualityConfig(
    dataQualityChecks: Array[DataQualityCheck],
    defaultConfig: DefaultConfig
)

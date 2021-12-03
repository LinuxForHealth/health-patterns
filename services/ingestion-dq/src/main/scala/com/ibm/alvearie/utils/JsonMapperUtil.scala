package com.ibm.alvearie.utils

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import com.ibm.alvearie.model.DataQualityConfig

import scala.io.{BufferedSource, Source}

object JsonMapperUtil {
  def getDataQualityConfig(jsonFilePath: String): DataQualityConfig = {

    var bufferedSource: BufferedSource = null
    var jsonString: String = null

    try {
      bufferedSource = Source.fromFile(jsonFilePath)
      jsonString = bufferedSource.mkString
    } finally {
      bufferedSource.close()
    }

    val mapper = new ObjectMapper()
    mapper.registerModule(DefaultScalaModule)

    mapper.readValue(jsonString, classOf[DataQualityConfig])
  }
}

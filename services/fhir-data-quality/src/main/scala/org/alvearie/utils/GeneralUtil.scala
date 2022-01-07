package org.alvearie.utils

import org.alvearie.Constants
import org.apache.log4j.{LogManager, Logger}

import java.util.Properties
import scala.io.Source

object GeneralUtil {
  @transient lazy val logger: Logger = LogManager.getLogger(getClass.getName)

  // Returns a map object(key,value pairs) by parsing the properties in the given input properties file
  def getPropertiesMap(propFileName: String): Map[String, String] = {
    val appProps: Properties = new Properties
    appProps.load(Source.fromResource(propFileName).reader())

    import scala.collection.JavaConverters._
    appProps.asScala.toMap
  }

  def getFinalProperties(args: Array[String]): Map[String, String] = {

    logger.info("Loading application default properties")
    // load the default application properties, by reading the default.properties file
    val defaultProperties: Map[String, String] =
      getPropertiesMap(
        Constants.DEFAULT_PROPERTIES_FILE
      )

    logger.info("Loading application input arguments")
    // load the input arguments into a map
    val inputArguments: Map[String, String] =
      args.map(_.split("=", 2)).map(a => (a(0), a(1))).toMap

    logger.info("Merging input arguments with default properties")
    // finalize the properties by merging & overriding the command line arguments with default properties
    val finalProperties: Map[String, String] =
      defaultProperties.++(inputArguments)

    finalProperties
  }
}

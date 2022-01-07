package org.alvearie

import com.amazon.deequ.checks.CheckLevel

import scala.collection.immutable.HashMap

/**
  * Holds all constants or literals used within the application
  */
object Constants {
  // log configuration file to control the detail of log emitted by the application
  val LOG4J_FILE = "log4j.properties"
  // define constants for spark
  val SPARK_CONF = "spark.conf"
  // spark data-frame table name that holds all bundle data
  val SPARK_BASE_DATA_TABLE = "resource_partitioned_table"
  // default application properties file path
  val DEFAULT_PROPERTIES_FILE = "default.properties"
  // map of data-quality check levels
  val CHECK_LEVEL: Map[String, CheckLevel.Value] =
    HashMap("Error" -> CheckLevel.Error, "Warning" -> CheckLevel.Warning)
}

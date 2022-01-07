package org.alvearie

import Constants._
import org.alvearie.service.DataQualityProcess.{
  prepareSourceData,
  processDqChecks
}
import org.alvearie.utils.GeneralUtil.getFinalProperties
import org.alvearie.utils.SparkUtil
import org.apache.commons.io.input.ReaderInputStream
import org.apache.log4j.{LogManager, Logger, PropertyConfigurator}

import java.io.InputStream
import java.nio.charset.StandardCharsets
import scala.io.Source

/**
  * Entry point for the data-quality process, which reads & validates the default application properties
  * Invokes the data preparation process and corresponding quality checks on the same data as per the
  * data-quality configuration file - dataQualityConfig.json
  */
object Main {
  // configure log4j utility to capture application logs
  @transient lazy val logger: Logger = LogManager.getLogger(getClass.getName)
  val logInputStream: InputStream = new ReaderInputStream(
    Source.fromResource(LOG4J_FILE).reader(),
    StandardCharsets.UTF_8
  )
  PropertyConfigurator.configure(logInputStream)

  def printUsage(): Unit = {
    logger.error("Usage: org.alvearie.Main <name=value> pairs")
    logger.error(
      "Ex: org.alvearie.Main dqConfig=\"config/dataQualityConfig.json\""
    )
    System.exit(1)
  }

  def main(args: Array[String]): Unit = {

    // check if the input arguments supplied to the program follows name=value pair pattern,
    // if not print the correct program invocation and exit the application
    args.foreach(arg => if (!arg.matches(".+=.+")) printUsage())

    // get the final properties for data-quality process, which is union of input command-line arguments and
    // resources/default.properties. If there arises a conflict, command-line arguments takes precedence
    val properties: Map[String, String] = getFinalProperties(args)

    logger.info("Supplied application properties: ")
    properties.foreach(x => println(x._1 + "=" + x._2))

    if (!properties.contains("dataPath") || properties("dataPath").isEmpty) {
      logger.error(
        "'dataPath' property in default.properties or input program arguments can't be empty or null"
      )
      printUsage()
      System.exit(1)
    }

    // initializing the spark session
    val sparkUtil = SparkUtil()
    val sparkSession = sparkUtil.sparkSession

    // read data-quality rules file from dqConfigPath and data location file from dataPath properties
    val dataPath = properties("dataPath")
    val dqConfigPath = properties("dqConfigPath")

    // invoke the function to prepare data required for data-quality checks
    prepareSourceData(sparkSession, dataPath)

    // invoke the function to run data-quality checks on the data and process the results
    processDqChecks(sparkSession, dqConfigPath)
  }
}

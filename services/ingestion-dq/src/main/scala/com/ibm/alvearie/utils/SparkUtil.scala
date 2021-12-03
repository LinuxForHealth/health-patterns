package com.ibm.alvearie.utils

import com.ibm.alvearie.Constants
import org.apache.log4j.{LogManager, Logger}
import org.apache.spark.sql.{SQLContext, SparkSession}
import org.apache.spark.{SparkConf, SparkContext}

import java.util.Properties
import scala.io.Source

case class SparkUtil() {
  @transient lazy val logger: Logger = LogManager.getLogger(getClass.getName)

  val sparkSession: SparkSession = SparkSession
    .builder()
    .config(getSparkAppConf)
    .getOrCreate()

  val sparkContext: SparkContext = sparkSession.sparkContext
  val sqlContext: SQLContext = sparkSession.sqlContext

  // print current spark configuration
  logger.info("Printing spark configuration:")
  logger.info(s"Spark Version: ${sparkSession.version}")
  sparkContext.getConf.getAll.foreach(x => println(x._1 + "=" + x._2))

  def getSparkAppConf: SparkConf = {
    val sparkAppConf = new SparkConf
    val props = new Properties
    props.load(Source.fromResource(Constants.SPARK_CONF).bufferedReader())
    props.forEach((k, v) => sparkAppConf.set(k.toString, v.toString))
    sparkAppConf
  }
}

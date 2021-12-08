package org.alvearie.service

import com.amazon.deequ.VerificationResult
import com.amazon.deequ.checks.Check
import org.alvearie.Constants.SPARK_BASE_DATA_TABLE
import org.alvearie.model.DataQualityConfig
import org.alvearie.utils.DataProcessingUtil.getDataFrame
import org.alvearie.utils.DeequUtil.{
  getDeequChecks,
  getResultsDataFrame,
  runDeequChecks
}
import org.alvearie.utils.FhirUtil.fetchResourcePath
import org.alvearie.utils.JsonMapperUtil.getDataQualityConfig
import org.apache.log4j.{LogManager, Logger}
import org.apache.spark.sql.functions.{col, explode, from_json, udf}
import org.apache.spark.sql.types.{ArrayType, StringType, StructType}
import org.apache.spark.sql.{DataFrame, SparkSession}

/**
  * Supplies methods required to prepare the source data and run data-quality checks
  */
object DataQualityProcess {
  @transient lazy val logger: Logger = LogManager.getLogger(getClass.getName)

  /**
    * Prepare the source data by reading all the FHIR bundles from the given location, create a spark dataset out of the
    * FHIR bundles, partition bundles by resource type (ex: patient, observation etc.) and create a spark table view
    * for later data-quality checks
    *
    * @param sparkSession entry point to connect to spark cluster
    * @param dataPath location for the stored source data files
    */
  def prepareSourceData(sparkSession: SparkSession, dataPath: String): Unit = {

    // create and register a spark user-defined function to run and extract fhir-path expressions on the fhir bundles
    val fetchPathResource = udf((jsonString: String, path: String) =>
      fetchResourcePath(jsonString, path)
    )
    sparkSession.udf.register("fetchPathResource", fetchPathResource)

    // define spark schemas to access the resources within a bundle
    val entryType = new StructType().add("resource", StringType)
    val schema = new StructType()
      .add("entry", ArrayType(entryType))
    val resourceSchema = new StructType().add("resourceType", StringType)

    // read the fhir json files into spark data-frame, un-wrap the bundle to get the list of resources
    val bundleDf =
      sparkSession.read
        .option("multiline", value = true)
        .schema(schema)
        .json(dataPath)
        .select("entry")
        .withColumn("resource", explode(col("entry")))
        .select("resource.*")
        .withColumn("resourceType", from_json(col("resource"), resourceSchema))
        .select("resourceType.*", "resource")

    // re-partition the bundle of resources based on resource type and temporarily store it in a spark view
    bundleDf
      .repartition(col("resourceType"))
      .cache()
      .createOrReplaceTempView(SPARK_BASE_DATA_TABLE)
  }

  /**
    * Read the data-quality config file to analyze and run various data-quality checks associated with the data
    *  and finally print the verification results to the console
    *
    * @param sparkSession entry point to connect to spark cluster
    * @param dqConfigPath location for the data-quality rules config file
    */
  def processDqChecks(
      sparkSession: SparkSession,
      dqConfigPath: String
  ): Unit = {

    // parse the input data-quality rules config file and map to the scala case classes using json mapper utility
    val dataQualityConfig: DataQualityConfig = getDataQualityConfig(
      dqConfigPath
    )

    // loop through each of the active data quality checks to fetch the required data-frames and their corresponding
    // active quality rules and finally run the checks and print the results
    dataQualityConfig.dataQualityChecks
      .filter(_.active) // look for active dataQuality checks only
      .foreach(dataQualityCheck => {

        val dataFrame: DataFrame =
          getDataFrame(
            sparkSession.sqlContext,
            SPARK_BASE_DATA_TABLE,
            dataQualityCheck.data
          )

        val deequChecks: Seq[Check] =
          getDeequChecks(dataQualityCheck.qualityChecks)

        logger
          .info(
            s"Running data-quality checks for ${dataQualityCheck.data.name}..."
          )

        val verificationResult: VerificationResult =
          runDeequChecks(dataFrame, deequChecks)

        logger.info(
          s"Printing data-quality validation results for ${dataQualityCheck.data.name}..."
        )
        getResultsDataFrame(sparkSession, verificationResult).show(false)
      })

  }
}

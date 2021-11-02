package com.ibm.alvearie.utils

import com.amazon.deequ.VerificationResult.checkResultsAsDataFrame
import com.amazon.deequ.checks.{Check, CheckStatus}
import com.amazon.deequ.constraints.ConstraintStatus
import com.amazon.deequ.{VerificationResult, VerificationSuite}
import com.ibm.alvearie.Constants.CHECK_LEVEL
import com.ibm.alvearie.model.QualityCheck
import com.ibm.alvearie.model.enums.QualityCheckTypeEnum
import org.apache.spark.sql.{DataFrame, SparkSession}

object DeequUtil {
  def getDeequChecks(qualityChecks: Array[QualityCheck]): Seq[Check] = {
    qualityChecks
      .filter(_.active)
      .map(qualityCheck =>
        qualityCheck.`type` match {
          case QualityCheckTypeEnum.isComplete =>
            Check(CHECK_LEVEL(qualityCheck.level), qualityCheck.description)
              .isComplete(qualityCheck.clause)
          case QualityCheckTypeEnum.isUnique =>
            Check(CHECK_LEVEL(qualityCheck.level), qualityCheck.description)
              .isUnique(qualityCheck.clause)
          case QualityCheckTypeEnum.hasSize =>
            Check(CHECK_LEVEL(qualityCheck.level), qualityCheck.description)
              .hasSize(_ == qualityCheck.clause.toLong)
          case QualityCheckTypeEnum.notSatisfies =>
            Check(CHECK_LEVEL(qualityCheck.level), qualityCheck.description)
              .satisfies(
                qualityCheck.clause,
                qualityCheck.args("constraintName").asInstanceOf[String],
                _ == 0.0
              )
          case QualityCheckTypeEnum.isContainedIn =>
            Check(CHECK_LEVEL(qualityCheck.level), qualityCheck.description)
              .isContainedIn(
                qualityCheck.clause,
                qualityCheck
                  .args("allowedValues")
                  .asInstanceOf[List[String]]
                  .toArray
              )
          case _ => null
        }
      )
  }

  def runDeequChecks(
      dataFrame: DataFrame,
      checks: Seq[Check]
  ): VerificationResult = {
    VerificationSuite()
      .onData(dataFrame)
      .addChecks(checks)
      .run()
  }

  def getResultsDataFrame(
      sparkSession: SparkSession,
      verificationResult: VerificationResult
  ): DataFrame = {
    checkResultsAsDataFrame(sparkSession, verificationResult)
  }

  def printResults(verificationResult: VerificationResult): Unit = {
    if (verificationResult.status == CheckStatus.Success) {
      println("The Data passed the test, everything is fine!")
    } else {
      println("Errors in the Data:\n")

      val resultsForAllConstraints = verificationResult.checkResults
        .flatMap { case (_, checkResult) => checkResult.constraintResults }

      resultsForAllConstraints
        .filter {
          _.status != ConstraintStatus.Success
        }
        .foreach { result =>
          println(s"${result.constraint}: ${result.message.get}")
        }
    }
  }

  def main(args: Array[String]): Unit = {}
}

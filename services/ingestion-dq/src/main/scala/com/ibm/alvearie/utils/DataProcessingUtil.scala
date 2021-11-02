package com.ibm.alvearie.utils

import com.ibm.alvearie.model.enums.{ColumnMapTypeEnum, DataTypeEnum}
import com.ibm.alvearie.model.{
  Column,
  ComplexDataStruct,
  Data,
  SimpleDataStruct
}
import org.apache.spark.sql.{DataFrame, SQLContext}

/**
  *  Utility object that supplies methods to provide a data-frames for both simple and complex data structures
  */
object DataProcessingUtil {

  /**
    *
    * @param sqlContext
    * @param sparkDataTable
    * @param data
    * @return resultant dataframe either of SimpleDataStruct or ComplexDataStruct
    */
  def getDataFrame(
      sqlContext: SQLContext,
      sparkDataTable: String,
      data: Data
  ): DataFrame = {
    data.`type` match {
      case DataTypeEnum.SimpleDataStruct =>
        fetchSimpleDataStructFrame(
          sqlContext,
          sparkDataTable,
          data.simpleDataStruct.get
        )
      case DataTypeEnum.ComplexDataStruct =>
        fetchComplexDataStructFrame(
          sqlContext,
          sparkDataTable,
          data.complexDataStruct.get
        )
      case _ =>
        println(s"Invalid data struct supplied")
        null
    }
  }

  def fetchDataFrame(
      sqlContext: SQLContext,
      sparkDataTable: String,
      source: String,
      columns: Array[Column]
  ): DataFrame = {

    val selectColumnsClause = columns
      .map(column => {
        column.mapType match {
          case ColumnMapTypeEnum.FHIR_PATH =>
            s"fetchPathResource(resource,'${column.mapValue}') AS ${column.name}"
          case _ =>
            println("Invalid Column.MapType")
            System.exit(1)
        }
      })
      .mkString(",")

    val sqlScript =
      s"SELECT $selectColumnsClause FROM $sparkDataTable WHERE resourceType='$source'"

    val simpleDf = sqlContext.sql(sqlScript)

    simpleDf
  }
  def fetchSimpleDataStructFrame(
      sqlContext: SQLContext,
      sparkDataTable: String,
      simpleDataStruct: SimpleDataStruct
  ): DataFrame = {
    fetchDataFrame(
      sqlContext,
      sparkDataTable,
      simpleDataStruct.source,
      simpleDataStruct.columns
    )
  }

  def fetchComplexDataStructFrame(
      sqlContext: SQLContext,
      sparkDataTable: String,
      complexDataStruct: ComplexDataStruct
  ): DataFrame = {

    val leftSource: String = complexDataStruct.leftSource
    val leftSourceColumns: Array[Column] = complexDataStruct.leftSourceColumns
    val rightSource: String = complexDataStruct.rightSource
    val rightSourceColumns: Array[Column] =
      complexDataStruct.rightSourceColumns
    val joinType: String = complexDataStruct.joinType
    val joinCondition: String = complexDataStruct.joinCondition

    fetchDataFrame(
      sqlContext,
      sparkDataTable,
      leftSource,
      leftSourceColumns
    ).createOrReplaceTempView("leftDataFrame")

    fetchDataFrame(
      sqlContext,
      sparkDataTable,
      rightSource,
      rightSourceColumns
    ).createOrReplaceTempView("rightDataFrame")

    val sqlScript =
      s"SELECT * FROM leftDataFrame $joinType rightDataFrame ON ($joinCondition)"

    val complexDf = sqlContext.sql(sqlScript)

    complexDf
  }

}

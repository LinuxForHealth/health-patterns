import sbt._
import Keys._

name := "fhir-data-quality"
organization := "org.alvearie"
version := "0.1"
scalaVersion := "2.12.10"

// dependent tools/libraries versions
val sparkVersion = "3.1.2"
val scalaTestVersion = "3.2.9"
val fhirVersion = "4.9.2"
val jsonVersion = "20210307"
val deequVersion = "2.0.0-spark-3.1"
val jacksonVersion = "2.12.0"

/*
  application dependencies:
 */
val appDependencies = Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion,
  "org.apache.spark" %% "spark-sql" % sparkVersion,
  "com.ibm.fhir" % "fhir-model" % fhirVersion,
  "com.ibm.fhir" % "fhir-path" % fhirVersion,
  "org.json" % "json" % jsonVersion,
  "com.amazon.deequ" % "deequ" % deequVersion,
  "com.fasterxml.jackson.module" % "jackson-module-scala_2.12" % jacksonVersion
)

/*
  test dependencies:
    1. ScalaTest
 */
val testDependencies = Seq(
  "org.scalatest" %% "scalatest" % scalaTestVersion % Test
)

assemblyMergeStrategy in assembly := {
  case "META-INF/services/org.apache.spark.sql.sources.DataSourceRegister" =>
    MergeStrategy.concat
  case PathList("META-INF", _ @_*) => MergeStrategy.discard
  case _                           => MergeStrategy.first
}

// combined application and test dependencies
libraryDependencies ++= appDependencies ++ testDependencies

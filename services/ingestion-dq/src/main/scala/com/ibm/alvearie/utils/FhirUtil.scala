package com.ibm.alvearie.utils

import com.ibm.fhir.model.format.Format
import com.ibm.fhir.model.parser.FHIRParser
import com.ibm.fhir.model.resource.Resource
import com.ibm.fhir.model.visitor.PathAwareVisitor
import com.ibm.fhir.path._
import com.ibm.fhir.path.evaluator.FHIRPathEvaluator

import java.io.StringReader
import java.util.NoSuchElementException
import scala.io.Source

object FhirUtil {
  def processFhirPathNode(node: FHIRPathNode): String = {

    var value: String = null

    if (node.getClass.getSimpleName.contains("FHIRPathBooleanValue")) {
      val booleanValue: FHIRPathBooleanValue =
        node.asInstanceOf[FHIRPathBooleanValue]
      if (booleanValue._boolean())
        value = "true"
      else
        value = "false"
    } else if (node.isSystemValue) {
      val nodeConverted: FHIRPathSystemValue = node.asSystemValue()
      if (
        nodeConverted.isTemporalValue && nodeConverted.asTemporalValue.isDateTimeValue
      ) {
        value = nodeConverted
          .asTemporalValue()
          .asInstanceOf[FHIRPathDateTimeValue]
          .toString
      } else if (nodeConverted.isStringValue) {
        value = nodeConverted.asStringValue.string()
      }
    } else if (node.is(classOf[FHIRPathElementNode])) {
      val tNode: FHIRPathElementNode = node.asElementNode()
      val v: FHIRPathSystemValue = tNode.getValue
      if (v != null) {
        if (v.isStringValue) {
          value = v.asStringValue().string()
        } else if (v.isTemporalValue && v.asTemporalValue.isDateTimeValue) {
          value = v.asTemporalValue.asDateTimeValue().dateTime().toString
        }
      }
    }
    value
  }

  def nodeVisitor(fhirJsonFile: String): Unit = {
    val jsonReader = Source.fromFile(fhirJsonFile).reader()
    val resourceBundle: Resource =
      FHIRParser.parser(Format.JSON).parse(jsonReader)
    val pathAwareVisitor: PathAwareVisitor = new PathAwareVisitor() {
      override protected def doVisit(
          elementName: String,
          value: String
      ): Unit = {
        println(getPath)
      }
    }
    resourceBundle.accept(pathAwareVisitor)
  }

  def fetchResourcePath(jsonString: String, path: String): String = {
    val resource: Resource =
      FHIRParser
        .parser(Format.JSON)
        .parse(
          new StringReader(jsonString)
        )
    val evaluationContext = new FHIRPathEvaluator.EvaluationContext(resource)
    try {
      //Evaluate the fhir path expression
      val node =
        FHIRPathEvaluator.evaluator
          .evaluate(
            evaluationContext,
            path
          )
          .iterator()
          .next()

      FhirUtil.processFhirPathNode(node)
    } catch {
      // if fhir path doesn't match or exist in the given resource return null
      case _: NoSuchElementException => null
    }
  }

}

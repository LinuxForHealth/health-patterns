package com.ibm.alvearie.model

case class ComplexDataStruct(
    leftSource: String,
    leftSourceColumns: Array[Column],
    rightSource: String,
    rightSourceColumns: Array[Column],
    joinType: String,
    joinCondition: String
)

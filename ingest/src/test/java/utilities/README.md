# Java Utility Methods For Zerocode Ingest Tests

## Overview
[Official Zerocode Documentation on using Java Utility Methods](https://github.com/authorjapps/zerocode/wiki#invoking-java-utility-methods)


The official documentation describes using JsonProperty & JsonCreator to pass data to/from the java utility functions.   This works well for json formatted data.   The following java data classes use JsonProperty:
- [ZerocodeString.java](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/java/utilities/ZerocodeString.java)
- [PhiDeIDCompare.java.java](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/java/utilities/PhiDeIDCompare.java)
- [OneLineData.java](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/java/utilities/OneLineData.java)

For a more generic data objects, I found out later that using a Map<String, String> object is simpler.  This class uses Map<String, String>:
- [IBMCos.java](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/java/utilities/IBMCos.java)

The java functions called by the Zerocode tests are contained in [ZerocodeUtilities.java](https://github.com/LinuxForHealth/health-patterns/blob/main/ingest/src/test/java/utilities/ZerocodeUtilities.java).   These ZerocodeUtilities functions make use of the data classes listed above to communicate with Zerocode tests.
